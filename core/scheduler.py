#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能调度引擎 - 序境系统核心调度器
"""
import time
import random
from typing import List, Dict, Optional, Tuple
from Kernel.kernel_loader import get_kernel
from core.model_call_manager import get_model_manager
from core.task_manager import Task, TaskStatus

class Scheduler:
    def __init__(self):
        self.kernel = get_kernel()
        self.model_manager = get_model_manager()
        self.scheduling_history: List[Dict] = []
        
    def analyze_task(self, task: Task) -> Dict:
        """分析任务特征"""
        task_content = task.content.lower()
        
        # 任务类型识别
        task_types = {
            "代码开发": ["代码", "编程", "开发", "python", "java", "函数", "调试", "bug", "算法"],
            "文案写作": ["写", "文案", "报告", "总结", "文章", "邮件", "内容", "创作"],
            "数据分析": ["分析", "数据", "统计", "报表", "可视化", "趋势", "预测"],
            "设计创作": ["设计", "图像", "UI", "海报", "绘图", "艺术", "生成图片"],
            "技术研究": ["搜索", "查询", "研究", "资料", "学习", "调研", "技术"],
            "系统管理": ["配置", "管理", "权限", "备份", "更新", "部署", "运维"]
        }
        
        matched_types = []
        for task_type, keywords in task_types.items():
            for keyword in keywords:
                if keyword in task_content:
                    matched_types.append(task_type)
                    break
        
        # 任务优先级判断
        priority = 3  # 默认普通优先级
        if any(key in task_content for key in ["紧急", "立刻", "马上", "优先", "重要"]):
            priority = 1
        elif any(key in task_content for key in ["明天", "后天", "不急", "有空"]):
            priority = 5
        
        # 任务复杂度估计
        complexity = 2  # 默认中等复杂度
        if len(task_content) > 500 or any(key in task_content for key in ["复杂", "大型", "系统", "架构"]):
            complexity = 3
        elif len(task_content) < 100:
            complexity = 1
        
        return {
            "task_types": matched_types if matched_types else ["通用任务"],
            "priority": priority,
            "complexity": complexity,
            "estimated_duration": complexity * 30  # 预估时间（秒）
        }
    
    def match_roles(self, task_features: Dict, count: int = 1) -> List[Dict]:
        """匹配最适合的官属角色"""
        task_types = task_features["task_types"]
        complexity = task_features["complexity"]
        priority = task_features["priority"]
        
        # 角色评分
        scored_roles = []
        for role in self.kernel.roles:
            score = 0
            
            # 专长匹配
            role_skills = role.get("专长", [])
            for task_type in task_types:
                if task_type in role_skills:
                    score += 10
            
            # 等级匹配：高复杂度任务优先选高等级角色
            role_level = role.get("角色等级", 1)
            if complexity >= 3 and role_level >= 3:
                score += 5
            elif complexity <= 1 and role_level <= 2:
                score += 3  # 简单任务优先低等级角色，节省高等级资源
            
            # 模型在线状态
            model_name = role.get("模型名称")
            if model_name in self.kernel.models and self.kernel.models[model_name].get("online", True):
                score += 5
            
            # 最近调用频率（避免频繁调用同一个模型）
            recent_calls = [h for h in self.scheduling_history 
                          if h.get("role_id") == role.get("id") 
                          and time.time() - h.get("timestamp", 0) < 60]
            if len(recent_calls) == 0:
                score += 3
            elif len(recent_calls) >= 3:
                score -= 5  # 1分钟内调用超过3次，降低优先级
            
            scored_roles.append({
                "role": role,
                "score": score,
                "role_id": role.get("id"),
                "role_name": role.get("姓名"),
                "model_name": role.get("模型名称")
            })
        
        # 按得分排序
        scored_roles.sort(key=lambda x: x["score"], reverse=True)
        
        # 返回前N个得分最高的角色
        return scored_roles[:count]
    
    def schedule_task(self, task: Task, require_roles: int = 1) -> Tuple[bool, List[Dict], str]:
        """调度任务"""
        try:
            # 1. 分析任务
            task_features = self.analyze_task(task)
            task.features = task_features
            
            # 2. 匹配角色
            matched_roles = self.match_roles(task_features, require_roles)
            
            if not matched_roles:
                return False, [], "没有找到合适的执行角色"
            
            # 3. 检查模型可用性
            available_roles = []
            for role_info in matched_roles:
                model_name = role_info["model_name"]
                if model_name in self.kernel.models and self.kernel.models[model_name].get("online", True):
                    available_roles.append(role_info)
            
            if not available_roles:
                return False, [], "所有匹配角色的模型均不可用"
            
            # 4. 记录调度历史
            for role_info in available_roles:
                self.scheduling_history.append({
                    "task_id": task.task_id,
                    "role_id": role_info["role_id"],
                    "model_name": role_info["model_name"],
                    "score": role_info["score"],
                    "timestamp": time.time()
                })
            
            # 5. 更新任务状态
            task.status = TaskStatus.SCHEDULED
            task.assigned_roles = [r["role_id"] for r in available_roles]
            
            return True, available_roles, f"成功调度 {len(available_roles)} 个角色执行任务"
            
        except Exception as e:
            return False, [], f"调度失败: {str(e)}"
    
    def optimize_scheduling_strategy(self):
        """优化调度策略（基于历史数据）"""
        # 分析最近100次调度历史，优化匹配规则
        recent_history = self.scheduling_history[-100:]
        if len(recent_history) < 20:
            return "调度历史不足，暂不优化"
        
        # 统计各角色成功率
        role_success = {}
        for record in recent_history:
            role_id = record.get("role_id")
            success = record.get("success", True)
            if role_id not in role_success:
                role_success[role_id] = {"total": 0, "success": 0}
            role_success[role_id]["total"] += 1
            if success:
                role_success[role_id]["success"] += 1
        
        # 计算成功率，调整后续调度权重
        optimization_report = []
        for role_id, stats in role_success.items():
            if stats["total"] >= 5:
                success_rate = stats["success"] / stats["total"]
                role = self.kernel.get_role_by_id(role_id)
                if role:
                    optimization_report.append({
                        "role_name": role.get("姓名"),
                        "success_rate": f"{success_rate:.1%}",
                        "total_calls": stats["total"]
                    })
        
        return optimization_report

# 单例实例
_scheduler_instance: Optional[Scheduler] = None

def get_scheduler() -> Scheduler:
    """获取调度器单例"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = Scheduler()
    return _scheduler_instance

if __name__ == "__main__":
    # 测试调度器
    scheduler = get_scheduler()
    
    # 创建测试任务
    test_task = Task(
        task_id="test_001",
        content="请用Python写一个多线程爬虫，抓取知乎热榜数据",
        created_by="user"
    )
    
    # 调度任务
    success, roles, msg = scheduler.schedule_task(test_task, require_roles=2)
    
    print(f"调度结果: {success}, {msg}")
    if success:
        print("\n分配的角色:")
        for i, role in enumerate(roles):
            print(f"{i+1}. {role['role_name']} (得分: {role['score']})")
    
    # 优化建议
    optimization = scheduler.optimize_scheduling_strategy()
    print(f"\n调度优化建议: {optimization}")
