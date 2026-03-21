"""
序境多模型协作调度系统 v2.0
实现差异化分工、动态路由、加权融合
自适应调度算法 + 热更新支持
"""

import sqlite3
import requests
import random
import json
import os
import time
from datetime import datetime
from pathlib import Path

class XujingDispatcher:
    def __init__(self, db_path):
        self.db_path = db_path
        self.config_path = os.path.join(os.path.dirname(__file__), 'config', 'adaptive_scheduler.py')
        self.experts = self.load_experts()
        self.config = self.load_config()
        self.last_modified = 0
    
    def load_experts(self):
        """从专家模型池加载可用模型
        根据序境系统总则第22条规则实现去重:
        - 相同服务商 + 相同API地址 + 相同模型标识符 = 重复
        - 相同服务商 + 相同模型标识符 = 真重复
        - 保留第一个，标记后续为重复
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT 能力分类, 模型, 引擎, API地址, API密钥, 评分 FROM 专家模型池表 WHERE 状态="在线" ORDER BY 评分 DESC')
        experts = {}
        
        # 序境系统第22条 - 模型去重
        # key1: (provider, url, identifier) -> full duplicate check
        seen_full = set()
        # key2: (provider, identifier) -> true duplicate check
        seen_provider_model = set()
        duplicate_count = 0
        true_duplicate_count = 0
        
        for r in c.fetchall():
            cat = r[0]
            model_name = r[1]
            provider = r[2]  # 引擎字段存储服务商
            url = r[3]
            
            # 去重键
            full_key = (provider, url, model_name)
            provider_model_key = (provider, model_name)
            
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
            
            if cat not in experts:
                experts[cat] = []
            experts[cat].append({
                'model': r[1],
                'engine': r[2],
                'url': r[3],
                'key': r[4],
                'score': r[5]
            })
        
        conn.close()
        
        if duplicate_count > 0 or true_duplicate_count > 0:
            print(f"[XujingDispatcher][序境第22条] 专家池去重: {duplicate_count} 完全重复, {true_duplicate_count} 真重复 已移除")
        
        return experts
    
    def load_config(self):
        """加载自适应调度配置"""
        try:
            if os.path.exists(self.config_path):
                config = {}
                exec(open(self.config_path, encoding='utf-8').read(), config)
                return config
        except Exception as e:
            print(f"Config load error: {e}")
        return {}
    
    def check_hot_update(self):
        """热更新检查"""
        try:
            mtime = os.path.getmtime(self.config_path)
            if mtime > self.last_modified:
                self.config = self.load_config()
                self.last_modified = mtime
                return True
        except:
            pass
        return False
    
    def classify_task_complexity(self, prompt):
        """根据prompt识别任务复杂度"""
        prompt_lower = prompt.lower()
        complexity_config = self.config.get('TASK_COMPLEXITY', {})
        
        for level, config in complexity_config.items():
            keywords = config.get('keywords', [])
            if any(k in prompt_lower for k in keywords):
                return level, config
        
        return "中等", complexity_config.get("中等", {"max_tokens": 4000})
    
    def classify_task(self, prompt):
        """根据prompt分类任务类型"""
        prompt_lower = prompt.lower()
        if any(k in prompt_lower for k in ['代码', 'code', '编程', '程序']):
            return '代码生成'
        elif any(k in prompt_lower for k in ['创意', '写诗', '写作', '故事', '文章']):
            return '创意生成'
        else:
            return '逻辑推理'
    
    def select_expert(self, task_type, complexity=None):
        """选择最适合的专家模型（自适应）"""
        # 检查热更新
        self.check_hot_update()
        
        # 根据复杂度选择模型
        if complexity:
            preferred = self.config.get('TASK_COMPLEXITY', {}).get(complexity, {}).get('preferred_models', [])
            if preferred and task_type in self.experts:
                for p in preferred:
                    for exp in self.experts[task_type]:
                        if p in exp['model']:
                            return exp
        
        # 默认逻辑
        if task_type in self.experts and self.experts[task_type]:
            return self.experts[task_type][0]
        if '逻辑推理' in self.experts:
            return self.experts['逻辑推理'][0]
        return None
    
    def dispatch(self, prompt, task_type=None):
        """调度主函数"""
        # 检查热更新
        self.check_hot_update()
        
        if task_type is None:
            task_type = self.classify_task(prompt)
        
        # 识别复杂度
        complexity, complexity_config = self.classify_task_complexity(prompt)
        
        expert = self.select_expert(task_type, complexity)
        if not expert:
            return {'error': 'No available expert'}
        
        # 获取tokens配置（不限制）
        tokens_config = self.config.get('TOKENS_CONFIG', {})
        max_tokens = tokens_config.get('max_tokens') or complexity_config.get('max_tokens', 4000)
        
        # 调用模型
        try:
            url = expert['url']
            # 修复: 如果URL不包含/chat/completions，自动添加
            if "/chat/completions" not in url:
                url = url.rstrip("/") + "/chat/completions"
            r = requests.post(
                url,
                json={
                    'model': expert['model'], 
                    'messages': [{'role': 'user', 'content': prompt}], 
                    'max_tokens': max_tokens,
                    'temperature': tokens_config.get('default_temperature', 0.7)
                },
                headers={'Authorization': f'Bearer {expert["key"]}', 'Content-Type': 'application/json'},
                timeout=60
            )
            result = r.json()['choices'][0]['message']['content'] if r.status_code == 200 else r.text
            return {
                'status': r.status_code,
                'task_type': task_type,
                'complexity': complexity,
                'model': expert['model'],
                'engine': expert['engine'],
                'score': expert['score'],
                'max_tokens': max_tokens,
                'result': result
            }
        except Exception as e:
            # 故障转移：尝试备用模型
            if '逻辑推理' in self.experts and self.experts['逻辑推理']:
                backup = self.experts['逻辑推理'][0]
                try:
                    url = backup['url']
                    # 修复: 如果URL不包含/chat/completions，自动添加
                    if "/chat/completions" not in url:
                        url = url.rstrip("/") + "/chat/completions"
                    r = requests.post(
                        url,
                        json={'model': backup['model'], 'messages': [{'role': 'user', 'content': prompt}], 'max_tokens': max_tokens},
                        headers={'Authorization': f'Bearer {backup["key"]}', 'Content-Type': 'application/json'},
                        timeout=60
                    )
                    result = r.json()['choices'][0]['message']['content'] if r.status_code == 200 else r.text
                    return {
                        'status': r.status_code,
                        'task_type': task_type,
                        'complexity': complexity,
                        'model': backup['model'],
                        'engine': backup['engine'],
                        'fallback': True,
                        'result': result
                    }
                except:
                    pass
            return {'error': str(e)}

# 测试
if __name__ == '__main__':
    dispatcher = XujingDispatcher(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db')
    result = dispatcher.dispatch('你好，请介绍一下序境系统')
    print(result)
