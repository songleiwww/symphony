# -*- coding: utf-8 -*-
"""
序境系统 - 动态调度器 v3.0
根据每次执行动态分析模型表现，动态淘汰
"""
import sqlite3
import requests
import json
import os
import time
from datetime import datetime
from collections import defaultdict

class DynamicDispatcher:
    """动态调度器 - 根据任务分析动态选择模型"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.model_stats = defaultdict(lambda: {"success": 0, "fail": 0, "latency": []})
        self.load_models()
    
    def load_models(self):
        """从数据库加载模型配置
        根据序境系统总则第22条规则实现去重:
        - 相同服务商 + 相同API地址 + 相同模型标识符 = 重复
        - 相同服务商 + 相同模型标识符 = 真重复
        - 保留第一个，标记后续为重复
        """
        conn = sqlite3.connect(self.db_path)
        conn.text_factory = str
        c = conn.cursor()
        
        # 加载在线模型
        c.execute('SELECT id, 模型名称, 模型标识符, 模型类型, 服务商, API地址, API密钥 FROM 模型配置表 WHERE 在线状态="online"')
        all_candidates = []
        for r in c.fetchall():
            all_candidates.append({
                "id": r[0],
                "name": r[1],
                "identifier": r[2],
                "type": r[3],
                "provider": r[4],
                "url": r[5],
                "key": r[6]
            })
        
        # 序境系统第22条 - 模型去重
        # key1: (provider, url, identifier) -> full duplicate check
        seen_full = set()
        # key2: (provider, identifier) -> true duplicate check
        seen_provider_model = set()
        self.models = []
        duplicate_count = 0
        true_duplicate_count = 0
        
        for model in all_candidates:
            provider = model["provider"]
            identifier = model["identifier"]
            url = model["url"]
            
            # 去重键
            full_key = (provider, url, identifier)
            provider_model_key = (provider, identifier)
            
            # 检查重复
            if full_key in seen_full:
                duplicate_count += 1
                continue  # 跳过重复，保留第一个
            
            if provider_model_key in seen_provider_model:
                true_duplicate_count += 1
                continue  # 跳过真重复，保留第一个
            
            # 添加到已见集合
            seen_full.add(full_key)
            seen_provider_model.add(provider_model_key)
            self.models.append(model)
        
        # 加载专家模型池
        c.execute('SELECT 能力分类, 模型, 引擎, API地址, API密钥, 评分 FROM 专家模型池表 WHERE 状态="在线"')
        self.experts = defaultdict(list)
        # 专家模型池也应用相同去重规则
        seen_expert_full = set()
        seen_expert_pm = set()
        expert_duplicate = 0
        expert_true_duplicate = 0
        
        for r in c.fetchall():
            model_name = r[1]
            engine = r[2]
            url = r[3]
            provider = r[2]  # 专家模型池中 engine 就是服务商
            
            full_key = (provider, url, model_name)
            pm_key = (provider, model_name)
            
            if full_key in seen_expert_full:
                expert_duplicate += 1
                continue
            if pm_key in seen_expert_pm:
                expert_true_duplicate += 1
                continue
            
            seen_expert_full.add(full_key)
            seen_expert_pm.add(pm_key)
            
            self.experts[r[0]].append({
                "model": r[1],
                "engine": r[2],
                "url": r[3],
                "key": r[4],
                "score": r[5]
            })
        
        conn.close()
        total_dup = duplicate_count + expert_duplicate
        total_true_dup = true_duplicate_count + expert_true_duplicate
        print(f"[DynamicDispatcher] 加载模型: 原始 {len(all_candidates)} -> 去重后 {len(self.models)} 个")
        if total_dup > 0:
            print(f"[序境第22条] 移除重复模型: {duplicate_count} 个(完全重复), {true_duplicate_count} 个(真重复)")
        if expert_duplicate > 0:
            print(f"[序境第22条] 专家池去重: {expert_duplicate} 个(完全重复), {expert_true_duplicate} 个(真重复)")
        print(f"[DynamicDispatcher] 专家分类: {len(self.experts)} 类")
    
    def analyze_task(self, prompt):
        """分析任务类型和复杂度"""
        prompt_lower = prompt.lower()
        
        # 任务类型分析
        task_type = "通用对话"
        if any(k in prompt_lower for k in ['代码', 'code', '编程', 'program', 'function', 'def ', 'class ']):
            task_type = "代码生成"
        elif any(k in prompt_lower for k in ['创意', '写诗', '故事', '文章', '写作', 'creative']):
            task_type = "创意生成"
        elif any(k in prompt_lower for k in ['分析', '推理', '逻辑', 'reason', 'analyze']):
            task_type = "逻辑推理"
        
        # 复杂度分析
        complexity = "简单"
        if len(prompt) > 1000 or any(k in prompt_lower for k in ['详细', '完整', '深入', 'comprehensive']):
            complexity = "复杂"
        elif len(prompt) > 500:
            complexity = "中等"
        
        return {"type": task_type, "complexity": complexity}
    
    def select_model(self, task_info):
        """根据任务分析动态选择模型"""
        task_type = task_info["type"]
        complexity = task_info["complexity"]
        
        # 优先选择同类专家模型
        if task_type in self.experts:
            candidates = self.experts[task_type]
        else:
            # 回退到所有在线模型
            candidates = self.models
        
        if not candidates:
            return None, "无可用模型"
        
        # 动态评分选择
        best_model = None
        best_score = -1
        
        for model in candidates:
            # 计算动态分数
            stats = self.model_stats.get(model.get("model") or model.get("name"), {"success": 0, "fail": 0, "latency": []})
            
            success_rate = stats["success"] / max(stats["success"] + stats["fail"], 1)
            avg_latency = sum(stats["latency"]) / max(len(stats["latency"]), 1) if stats["latency"] else 1000
            
            # 基础分数 + 动态调整
            base_score = model.get("score", 8.0) if model.get("score") else 8.0
            dynamic_bonus = success_rate * 2  # 成功率越高加分
            latency_penalty = max(0, (avg_latency - 500) / 100)  # 延迟越高扣分
            
            final_score = base_score + dynamic_bonus - latency_penalty
            
            if final_score > best_score:
                best_score = final_score
                best_model = model
        
        return best_model, "OK"
    
    def execute(self, prompt, model=None):
        """执行任务并记录结果"""
        # 分析任务
        task_info = self.analyze_task(prompt)
        
        # 选择模型
        if model is None:
            model, msg = self.select_model(task_info)
            if not model:
                return {"error": msg}
        
        # 调用模型
        start_time = time.time()
        try:
            url = model.get("url") or model.get("API地址")
            key = model.get("key") or model.get("API密钥")
            # 优先使用模型标识符，其次使用模型名称
            model_name = model.get("identifier") or model.get("模型标识符") or model.get("model") or model.get("模型名称")
            
            # 修复: 如果URL不包含/chat/completions，自动添加
            if "/chat/completions" not in url:
                url = url.rstrip("/") + "/chat/completions"
            
            response = requests.post(
                url,
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2000
                },
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                timeout=30
            )
            
            latency = time.time() - start_time
            result = response.json()
            
            # 记录成功
            self.model_stats[model_name]["success"] += 1
            self.model_stats[model_name]["latency"].append(latency)
            # 保留最近10次延迟记录
            self.model_stats[model_name]["latency"] = self.model_stats[model_name]["latency"][-10:]
            
            return {
                "status": "success",
                "model": model_name,
                "task_type": task_info["type"],
                "complexity": task_info["complexity"],
                "latency": latency,
                "result": result
            }
            
        except Exception as e:
            latency = time.time() - start_time
            model_name = model.get("model") or model.get("名称") or "unknown"
            
            # 记录失败
            self.model_stats[model_name]["fail"] += 1
            
            return {
                "status": "error",
                "model": model_name,
                "error": str(e),
                "latency": latency
            }
    
    def get_stats(self):
        """获取模型统计"""
        return dict(self.model_stats)
    
    def eliminate_poor_performers(self, threshold=3):
        """淘汰表现差的模型"""
        eliminated = []
        for model_name, stats in list(self.model_stats.items()):
            if stats["fail"] >= threshold:
                fail_rate = stats["fail"] / (stats["success"] + stats["fail"])
                if fail_rate > 0.5:
                    eliminated.append(model_name)
                    del self.model_stats[model_name]
        return eliminated


# 测试
if __name__ == "__main__":
    db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
    dispatcher = DynamicDispatcher(db_path)
    
    # 测试任务分析
    test_tasks = [
        "写一首关于春天的诗",
        "帮我写一个Python函数计算斐波那契数列",
        "分析当前经济形势",
        "Hello world"
    ]
    
    print("\n=== 动态调度测试 ===")
    for prompt in test_tasks:
        task_info = dispatcher.analyze_task(prompt)
        model, _ = dispatcher.select_model(task_info)
        model_name = model.get("model") if model else "None"
        print(f"任务: {prompt[:20]}...")
        print(f"  类型: {task_info['type']}, 复杂度: {task_info['complexity']}")
        print(f"  选择模型: {model_name}")
