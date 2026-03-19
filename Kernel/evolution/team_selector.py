# -*- coding: utf-8 -*-
"""
序境系统 - 进化团队调度模块
集成模型组队、自适应、自进化能力到内核
"""

import os
import sys
from typing import Dict, List, Optional
from datetime import datetime

kernel_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, kernel_path)


class EvolutionTeam:
    """
    进化团队 - 根据任务类型自动组队
    
    团队类型:
    - evolution: 系统进化
    - takeover: 接管处理
    - self_adaptive: 自适应优化
    - long_term: 长效保持
    """
    
    # 模型配置
    MODEL_TEAMS = {
        "evolution": {
            "name": "进化团队",
            "description": "负责系统架构升级、功能迭代",
            "primary": "ark-code-latest",      # 火山引擎 - 代码生成
            "secondary": "deepseek-v3.2",      # 深度思考
            "support": "Qwen2.5-72B",         # 阿里 - 大模型
            "roles": ["架构师", "开发者", "测试员"]
        },
        "takeover": {
            "name": "接管团队",
            "description": "处理用户接管请求、关键词识别",
            "primary": "glm-4-flash",          # 智谱 - 快速响应
            "secondary": "Llama 3.3 70B",       # 英伟达 - 理解力强
            "support": "ark-code-latest",
            "roles": ["接待员", "分析员", "执行员"]
        },
        "self_adaptive": {
            "name": "自适应团队",
            "description": "自动优化、参数调优、规则调整",
            "primary": "deepseek-v3.2",         # 深度推理
            "secondary": "Llama 3.1 70B",      # 英伟达
            "support": "GLM-4-Flash",
            "roles": ["优化师", "调参员", "监控员"]
        },
        "long_term": {
            "name": "长效团队",
            "description": "记忆保持、知识沉淀、状态维护",
            "primary": "Qwen2.5-72B",          # 阿里 - 长文本
            "secondary": "glm-4-flash",
            "support": "ark-code-latest",
            "roles": ["记忆管理员", "知识库管理员", "状态监控员"]
        },
        "integration": {
            "name": "集成团队",
            "description": "内核集成、模块整合、冲突解决",
            "primary": "ark-code-latest",       # 代码集成
            "secondary": "deepseek-v3.2",       # 逻辑分析
            "support": "Llama 3.1 70B",
            "roles": ["集成工程师", "架构师", "审查员"]
        }
    }
    
    def __init__(self):
        self.current_team = None
        self.team_history = []
        self.stats = {
            "total_tasks": 0,
            "by_type": {}
        }
    
    def select_team(self, task_type: str) -> Dict:
        """
        选择进化团队
        
        Args:
            task_type: 任务类型 (evolution/takeover/self_adaptive/long_term/integration)
        
        Returns:
            团队配置
        """
        team = self.MODEL_TEAMS.get(task_type, self.MODEL_TEAMS["integration"])
        
        self.current_team = {
            "type": task_type,
            "team": team,
            "selected_at": datetime.now().isoformat(),
            "status": "ready"
        }
        
        self.team_history.append(self.current_team)
        self.stats["total_tasks"] += 1
        self.stats["by_type"][task_type] = self.stats["by_type"].get(task_type, 0) + 1
        
        return self.current_team
    
    def get_team_status(self) -> Dict:
        """获取团队状态"""
        return {
            "current": self.current_team,
            "available_teams": list(self.MODEL_TEAMS.keys()),
            "stats": self.stats,
            "history_count": len(self.team_history)
        }
    
    def auto_adapt(self, context: Dict) -> Dict:
        """
        自适应调度 - 根据上下文自动选择团队
        
        Args:
            context: 上下文信息
        
        Returns:
            适配的团队
        """
        # 分析任务复杂度
        complexity = context.get("complexity", 5)
        
        # 根据关键词判断任务类型
        keywords = context.get("keywords", [])
        
        if any(k in keywords for k in ["进化", "升级", "开发", "架构"]):
            return self.select_team("evolution")
        elif any(k in keywords for k in ["接管", "调度", "symphony"]):
            return self.select_team("takeover")
        elif any(k in keywords for k in ["优化", "调优", "自适应"]):
            return self.select_team("self_adaptive")
        elif any(k in keywords for k in ["记忆", "保持", "长期"]):
            return self.select_team("long_term")
        elif any(k in keywords for k in ["集成", "冲突", "内核"]):
            return self.select_team("integration")
        else:
            # 默认使用集成团队
            return self.select_team("integration")


# 全局进化团队实例
_evolution_team: Optional[EvolutionTeam] = None


def get_evolution_team() -> EvolutionTeam:
    """获取进化团队实例"""
    global _evolution_team
    if _evolution_team is None:
        _evolution_team = EvolutionTeam()
    return _evolution_team


def dispatch_team(task_type: str = None, context: Dict = None) -> Dict:
    """
    调度团队 - 便捷函数
    
    Usage:
        result = dispatch_team("evolution")
        result = dispatch_team(context={"keywords": ["接管"]})
    """
    team = get_evolution_team()
    
    if context:
        return team.auto_adapt(context)
    elif task_type:
        return team.select_team(task_type)
    else:
        return team.select_team("integration")


# 导出
__all__ = [
    'EvolutionTeam',
    'get_evolution_team',
    'dispatch_team'
]


if __name__ == '__main__':
    print("=== 序境进化团队调度系统 ===\n")
    
    team = get_evolution_team()
    
    # 测试不同团队
    test_tasks = [
        ("evolution", {"keywords": ["系统升级"]}),
        ("takeover", {"keywords": ["接管"]}),
        ("self_adaptive", {"keywords": ["参数调优"]}),
        (None, {"keywords": ["集成", "冲突"]})
    ]
    
    for task_type, context in test_tasks:
        if task_type:
            result = team.select_team(task_type)
        else:
            result = team.auto_adapt(context)
        
        print(f"任务类型: {task_type or 'auto'}")
        print(f"  团队: {result['team']['name']}")
        print(f"  主模型: {result['team']['primary']}")
        print(f"  角色: {result['team']['roles']}")
        print()
    
    # 状态
    print("团队状态:")
    print(team.get_team_status())
