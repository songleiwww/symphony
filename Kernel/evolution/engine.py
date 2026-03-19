# -*- coding: utf-8 -*-
"""
自进化引擎 - Self-Evolution Engine

序境系统自进化核心模块，统一调度所有进化能力

功能：
- 决策数据收集
- 进化阈值触发
- 闭环反馈
- 分布式探索

使用方式：
    from evolution import SelfEvolutionEngine
    
    engine = SelfEvolutionEngine()
    engine.start()
"""
import time
import json
from typing import Dict, Any, List, Optional
from .decision_logger import DecisionLogger
from .evolution_trigger import EvolutionTrigger
from .feedback_loop import FeedbackLoopEngine
from .branch_executor import BranchExecutor


class SelfEvolutionEngine:
    """
    自进化引擎
    
    整合所有自进化模块，提供统一的进化能力
    """
    
    def __init__(self):
        # 初始化各模块
        self.decision_logger = DecisionLogger()
        self.evolution_trigger = EvolutionTrigger(threshold=100)
        self.feedback_engine = FeedbackLoopEngine()
        self.branch_executor = BranchExecutor(strategy="hybrid")
        
        # 状态
        self.is_running = False
        self.stats = {
            "total_decisions": 0,
            "evolutions_triggered": 0,
            "feedback_loops": 0,
            "branches_explored": 0
        }
    
    def start(self):
        """启动自进化引擎"""
        self.is_running = True
        return {"status": "started", "timestamp": time.time()}
    
    def stop(self):
        """停止自进化引擎"""
        self.is_running = False
        return {"status": "stopped", "timestamp": time.time()}
    
    def record_decision(self, input_data: Dict, output_data: Dict, tool_calls: List = None) -> str:
        """
        记录决策
        
        参数:
            input_data: 输入数据
            output_data: 输出数据
            tool_calls: 工具调用列表
        
        返回:
            决策ID
        """
        if not self.is_running:
            return None
        
        # 记录决策
        decision_id = self.decision_logger.start_decision(
            input_data=input_data,
            tags=["auto_evolution"]
        )
        
        # 记录工具调用
        if tool_calls:
            for tc in tool_calls:
                call_id = self.decision_logger.tool_logger.start_call(
                    tc.get("name", "unknown"),
                    tc.get("args", {})
                )
                self.decision_logger.tool_logger.end_call(
                    call_id,
                    tc.get("result", {})
                )
        
        # 结束决策
        self.decision_logger.end_decision(
            output_data=output_data,
            effect_score=output_data.get("effect_score", 0.5)
        )
        
        self.stats["total_decisions"] += 1
        
        # 检查是否触发进化
        if self.evolution_trigger.record_valid_decision():
            self.stats["evolutions_triggered"] += 1
            self._trigger_evolution()
        
        return decision_id
    
    def _trigger_evolution(self):
        """触发进化"""
        # 获取历史决策
        # 评估效果
        # 调整策略
        # 探索新分支
        
        self.stats["branches_explored"] += 1
    
    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "is_running": self.is_running,
            "stats": self.stats.copy(),
            "trigger_progress": self.evolution_trigger.get_progress()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()
    
    def reset(self):
        """重置引擎"""
        self.evolution_trigger.reset()
        self.stats = {
            "total_decisions": 0,
            "evolutions_triggered": 0,
            "feedback_loops": 0,
            "branches_explored": 0
        }


# 全局实例
_evolution_engine = None

def get_evolution_engine() -> SelfEvolutionEngine:
    """获取全局自进化引擎"""
    global _evolution_engine
    if _evolution_engine is None:
        _evolution_engine = SelfEvolutionEngine()
    return _evolution_engine


# 便捷函数
def start_evolution():
    """启动自进化引擎"""
    return get_evolution_engine().start()

def stop_evolution():
    """停止自进化引擎"""
    return get_evolution_engine().stop()

def record_decision(input_data: Dict, output_data: Dict, tool_calls: List = None) -> str:
    """记录决策"""
    return get_evolution_engine().record_decision(input_data, output_data, tool_calls)

def get_evolution_status() -> Dict[str, Any]:
    """获取进化状态"""
    return get_evolution_engine().get_status()


if __name__ == "__main__":
    # 测试
    engine = SelfEvolutionEngine()
    print("SelfEvolutionEngine: OK")
    
    # 启动
    result = engine.start()
    print("Start:", result)
    
    # 记录决策
    decision_id = engine.record_decision(
        input_data={"task": "test"},
        output_data={"result": "success", "effect_score": 0.8}
    )
    print("Decision ID:", decision_id)
    
    # 获取状态
    status = engine.get_status()
    print("Status:", status)
