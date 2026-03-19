"""
闭环反馈引擎模块 - Feedback Loop Engine

负责基于历史决策效果评估、自动参数调整、策略更新与灰度发布。
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import random


class StrategyStatus(Enum):
    """策略状态枚举"""
    DRAFT = "draft"
    TESTING = "testing"
    ACTIVE = "active"
    ROLLBACK = "rollback"
    ARCHIVED = "archived"


class DecisionOutcome(Enum):
    """决策结果枚举"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


@dataclass
class DecisionRecord:
    """决策记录"""
    decision_id: str
    timestamp: float
    context: Dict[str, Any]
    decision: Dict[str, Any]
    outcome: DecisionOutcome
    response_time_ms: float
    resource_usage: float  # 资源消耗评分 (0-1)
    accuracy: float  # 准确率 (0-1)
    notes: str = ""


@dataclass
class Strategy:
    """策略配置"""
    name: str
    version: str
    params: Dict[str, Any]
    status: StrategyStatus
    rollout_percent: float = 0.0
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EffectScore:
    """效果评分"""
    accuracy_score: float  # 准确性评分
    efficiency_score: float  # 效率评分
    stability_score: float  # 稳定性评分
    overall_score: float  # 综合评分
    sample_count: int  # 样本数量
    confidence: float  # 置信度
    details: Dict[str, Any] = field(default_factory=dict)


class FeedbackLoopEngine:
    """
    闭环反馈引擎
    
    功能：
    - 效果评估：基于历史决策效果进行多维度评分
    - 策略更新：支持自动或人工审批后生效
    - 灰度发布：新策略先在小范围验证
    """
    
    DEFAULT_PARAMS = {
        "temperature": 0.7,
        "max_tokens": 2048,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "retry_count": 3,
        "timeout_ms": 30000,
        "cache_enabled": True,
    }
    
    def __init__(self):
        self.strategies: Dict[str, Strategy] = {}
        self.current_strategy_name: str = "default"
        self.decision_history: List[DecisionRecord] = []
        self.pending_approvals: Dict[str, Strategy] = {}
        self.auto_adjust_enabled: bool = True
        self.min_samples_for_adjustment: int = 10
        self.adjustment_threshold: float = 0.1  # 调整阈值
        
        # 初始化默认策略
        self._init_default_strategy()
    
    def _init_default_strategy(self):
        """初始化默认策略"""
        default_strategy = Strategy(
            name="default",
            version="1.0.0",
            params=self.DEFAULT_PARAMS.copy(),
            status=StrategyStatus.ACTIVE,
            rollout_percent=1.0,
            metadata={
                "description": "默认策略",
                "author": "system"
            }
        )
        self.strategies["default"] = default_strategy
    
    def evaluate_effect(self, decision_records: List[DecisionRecord]) -> EffectScore:
        """
        评估效果，返回多维度评分
        
        Args:
            decision_records: 决策记录列表
            
        Returns:
            EffectScore: 效果评分对象
        """
        if not decision_records:
            return EffectScore(
                accuracy_score=0.0,
                efficiency_score=0.0,
                stability_score=0.0,
                overall_score=0.0,
                sample_count=0,
                confidence=0.0
            )
        
        # 计算准确性评分
        success_count = sum(1 for r in outcome in decision_records if r.outcome == DecisionOutcome.SUCCESS)
        accuracy = success_count / len(decision_records)
        
        # 计算效率评分 (基于响应时间)
        response_times = [r.response_time_ms for r in decision_records]
        avg_response_time = sum(response_times) / len(response_times)
        # 将响应时间转换为评分 (越快越好)
        efficiency = max(0, 1 - (avg_response_time / 60000))  # 60秒为满分
        
        # 计算资源使用效率
        resource_usage = sum(r.resource_usage for r in decision_records) / len(decision_records)
        resource_efficiency = 1 - resource_usage
        
        # 计算稳定性 (基于准确性的方差)
        accuracies = [r.accuracy for r in decision_records]
        variance = self._calculate_variance(accuracies)
        stability = max(0, 1 - variance)  # 方差越小越稳定
        
        # 计算综合评分 (加权平均)
        overall = (
            accuracy * 0.4 +
            (efficiency * 0.3 + resource_efficiency * 0.2) +
            stability * 0.1
        )
        
        # 计算置信度 (样本越多置信度越高)
        confidence = min(1.0, len(decision_records) / 100)
        
        details = {
            "success_rate": success_count / len(decision_records),
            "avg_response_time_ms": avg_response_time,
            "variance": variance,
            "sample_size": len(decision_records),
        }
        
        return EffectScore(
            accuracy_score=accuracy,
            efficiency_score=efficiency,
            stability_score=stability,
            overall_score=overall,
            sample_count=len(decision_records),
            confidence=confidence,
            details=details
        )
    
    def _calculate_variance(self, values: List[float]) -> float:
        """计算方差"""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def adjust_params(self, effect_score: EffectScore) -> Dict[str, Any]:
        """
        根据效果调整参数
        
        Args:
            effect_score: 效果评分
            
        Returns:
            调整后的参数字典
        """
        current_params = self.get_current_strategy()["params"].copy()
        
        # 检查是否满足调整条件
        if effect_score.sample_count < self.min_samples_for_adjustment:
            return current_params
        
        # 根据评分调整参数
        adjusted_params = current_params.copy()
        
        # 准确性调整
        if effect_score.accuracy_score < 0.7:
            # 准确性低，降低temperature使结果更确定
            adjusted_params["temperature"] = max(0.1, current_params.get("temperature", 0.7) - 0.1)
        elif effect_score.accuracy_score > 0.9:
            # 准确性很高，可以适当提高temperature增加多样性
            adjusted_params["temperature"] = min(1.0, current_params.get("temperature", 0.7) + 0.05)
        
        # 效率调整
        if effect_score.efficiency_score < 0.5:
            # 效率低，增加超时时间，减少max_tokens
            adjusted_params["timeout_ms"] = min(120000, current_params.get("timeout_ms", 30000) + 5000)
            adjusted_params["max_tokens"] = max(512, current_params.get("max_tokens", 2048) - 256)
        elif effect_score.efficiency_score > 0.8:
            # 效率高，可以适当增加max_tokens
            adjusted_params["max_tokens"] = min(4096, current_params.get("max_tokens", 2048) + 256)
        
        # 稳定性调整
        if effect_score.stability_score < 0.6:
            # 稳定性低，增加retry_count
            adjusted_params["retry_count"] = min(5, current_params.get("retry_count", 3) + 1)
        
        # 检查是否有显著变化
        has_significant_change = False
        for key in adjusted_params:
            if key in current_params and abs(adjusted_params[key] - current_params[key]) > self.adjustment_threshold:
                has_significant_change = True
                break
        
        return adjusted_params
    
    def create_new_strategy(
        self,
        name: str,
        params: Dict[str, Any],
        based_on: str = None,
        metadata: Dict[str, Any] = None
    ) -> Strategy:
        """
        创建新策略
        
        Args:
            name: 策略名称
            params: 策略参数
            based_on: 基于的策略名称
            metadata: 附加元数据
            
        Returns:
            创建的策略对象
        """
        # 获取基础版本号
        base_version = "1.0.0"
        if based_on and based_on in self.strategies:
            base_strategy = self.strategies[based_on]
            parts = base_strategy.version.split(".")
            if len(parts) == 3:
                patch = int(parts[2]) + 1
                base_version = f"{parts[0]}.{parts[1]}.{patch}"
        
        strategy = Strategy(
            name=name,
            version=base_version,
            params=params,
            status=StrategyStatus.DRAFT,
            rollout_percent=0.0,
            metadata=metadata or {}
        )
        
        self.strategies[name] = strategy
        return strategy
    
    def publish_strategy(
        self,
        strategy: Dict[str, Any],
        rollout_percent: float = 0.05,
        require_approval: bool = True
    ) -> Dict[str, Any]:
        """
        发布策略，支持灰度发布
        
        Args:
            strategy: 策略字典 (包含name和params)
            rollout_percent: 发布百分比 (0.05 = 5%)
            require_approval: 是否需要人工审批
            
        Returns:
            发布结果
        """
        strategy_name = strategy.get("name", self.current_strategy_name)
        
        if strategy_name not in self.strategies:
            # 如果策略不存在，创建一个新策略
            self.create_new_strategy(
                name=strategy_name,
                params=strategy.get("params", self.DEFAULT_PARAMS.copy())
            )
        
        target_strategy = self.strategies[strategy_name]
        
        # 如果需要审批，加入待审批队列
        if require_approval and self.auto_adjust_enabled:
            self.pending_approvals[strategy_name] = target_strategy
            return {
                "status": "pending_approval",
                "strategy_name": strategy_name,
                "message": "策略已提交，等待人工审批"
            }
        
        # 直接发布
        return self._do_publish(target_strategy, rollout_percent)
    
    def _do_publish(self, strategy: Strategy, rollout_percent: float) -> Dict[str, Any]:
        """执行策略发布"""
        # 更新策略状态
        if rollout_percent >= 1.0:
            strategy.status = StrategyStatus.ACTIVE
            # 将其他策略设为非活跃
            for name, s in self.strategies.items():
                if name != strategy.name and s.status == StrategyStatus.ACTIVE:
                    s.status = StrategyStatus.ARCHIVED
        else:
            strategy.status = StrategyStatus.TESTING
        
        strategy.rollout_percent = rollout_percent
        strategy.updated_at = time.time()
        
        # 如果是全面发布，更新当前策略
        if rollout_percent >= 1.0:
            self.current_strategy_name = strategy.name
        
        return {
            "status": "published",
            "strategy_name": strategy.name,
            "version": strategy.version,
            "rollout_percent": rollout_percent,
            "message": f"策略 {strategy.name} v{strategy.version} 已发布，灰度比例 {rollout_percent*100}%"
        }
    
    def approve_strategy(self, strategy_name: str, rollout_percent: float = 0.05) -> Dict[str, Any]:
        """
        审批并发布策略
        
        Args:
            strategy_name: 策略名称
            rollout_percent: 发布百分比
            
        Returns:
            发布结果
        """
        if strategy_name not in self.pending_approvals:
            return {
                "status": "error",
                "message": f"策略 {strategy_name} 不在待审批队列中"
            }
        
        strategy = self.pending_approvals.pop(strategy_name)
        return self._do_publish(strategy, rollout_percent)
    
    def rollback_strategy(self, strategy_name: str = None) -> Dict[str, Any]:
        """
        回滚策略
        
        Args:
            strategy_name: 要回滚的策略名称，默认回滚当前策略
        """
        target_name = strategy_name or self.current_strategy_name
        
        if target_name not in self.strategies:
            return {
                "status": "error",
                "message": f"策略 {target_name} 不存在"
            }
        
        strategy = self.strategies[target_name]
        strategy.status = StrategyStatus.ROLLBACK
        strategy.rollout_percent = 0.0
        strategy.updated_at = time.time()
        
        # 切换到默认策略
        if target_name == self.current_strategy_name:
            self.current_strategy_name = "default"
        
        return {
            "status": "rolled_back",
            "strategy_name": target_name,
            "message": f"策略 {target_name} 已回滚"
        }
    
    def get_current_strategy(self) -> Dict[str, Any]:
        """
        获取当前策略
        
        Returns:
            当前策略字典
        """
        if self.current_strategy_name not in self.strategies:
            self.current_strategy_name = "default"
        
        strategy = self.strategies[self.current_strategy_name]
        
        return {
            "name": strategy.name,
            "version": strategy.version,
            "params": strategy.params,
            "status": strategy.status.value,
            "rollout_percent": strategy.rollout_percent,
            "created_at": strategy.created_at,
            "updated_at": strategy.updated_at,
            "metadata": strategy.metadata
        }
    
    def get_strategy(self, name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定策略
        
        Args:
            name: 策略名称
            
        Returns:
            策略字典，不存在则返回None
        """
        if name not in self.strategies:
            return None
        
        strategy = self.strategies[name]
        
        return {
            "name": strategy.name,
            "version": strategy.version,
            "params": strategy.params,
            "status": strategy.status.value,
            "rollout_percent": strategy.rollout_percent,
            "created_at": strategy.created_at,
            "updated_at": strategy.updated_at,
            "metadata": strategy.metadata
        }
    
    def list_strategies(self) -> List[Dict[str, Any]]:
        """
        列出所有策略
        
        Returns:
            策略列表
        """
        return [
            {
                "name": s.name,
                "version": s.version,
                "status": s.status.value,
                "rollout_percent": s.rollout_percent,
                "created_at": s.created_at,
                "updated_at": s.updated_at,
            }
            for s in self.strategies.values()
        ]
    
    def record_decision(self, decision: DecisionRecord):
        """
        记录决策
        
        Args:
            decision: 决策记录
        """
        self.decision_history.append(decision)
        
        # 保持历史记录在合理范围内
        max_history = 10000
        if len(self.decision_history) > max_history:
            self.decision_history = self.decision_history[-max_history:]
    
    def get_recent_decisions(self, limit: int = 100) -> List[DecisionRecord]:
        """
        获取最近的决策记录
        
        Args:
            limit: 返回数量限制
            
        Returns:
            决策记录列表
        """
        return self.decision_history[-limit:]
    
    def auto_evaluate_and_adjust(self) -> Dict[str, Any]:
        """
        自动评估并调整策略
        
        Returns:
            调整结果
        """
        if not self.auto_adjust_enabled:
            return {"status": "disabled", "message": "自动调整已禁用"}
        
        # 获取最近的决定记录
        recent_decisions = self.get_recent_decisions(self.min_samples_for_adjustment)
        
        if len(recent_decisions) < self.min_samples_for_adjustment:
            return {
                "status": "insufficient_data",
                "message": f"样本数量不足，需要 {self.min_samples_for_adjustment} 个样本",
                "sample_count": len(recent_decisions)
            }
        
        # 评估效果
        effect_score = self.evaluate_effect(recent_decisions)
        
        # 调整参数
        new_params = self.adjust_params(effect_score)
        current_params = self.get_current_strategy()["params"]
        
        # 检查是否有变化
        if new_params != current_params:
            # 创建新策略版本
            current = self.get_current_strategy()
            new_strategy = self.create_new_strategy(
                name=f"auto_adjust_{int(time.time())}",
                params=new_params,
                based_on=current["name"],
                metadata={
                    "description": "自动调整策略",
                    "reason": f"accuracy={effect_score.accuracy_score:.2f}, efficiency={effect_score.efficiency_score:.2f}, stability={effect_score.stability_score:.2f}"
                }
            )
            
            # 自动发布进行测试
            result = self.publish_strategy(
                {"name": new_strategy.name, "params": new_params},
                rollout_percent=0.05,
                require_approval=False
            )
            
            return {
                "status": "adjusted",
                "effect_score": {
                    "accuracy": effect_score.accuracy_score,
                    "efficiency": effect_score.efficiency_score,
                    "stability": effect_score.stability_score,
                    "overall": effect_score.overall_score,
                    "confidence": effect_score.confidence
                },
                "previous_params": current_params,
                "new_params": new_params,
                "publish_result": result
            }
        
        return {
            "status": "no_change",
            "message": "参数无需调整",
            "effect_score": {
                "accuracy": effect_score.accuracy_score,
                "efficiency": effect_score.efficiency_score,
                "stability": effect_score.stability_score,
                "overall": effect_score.overall_score
            }
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取引擎统计信息
        
        Returns:
            统计信息字典
        """
        recent = self.get_recent_decisions(100)
        effect = self.evaluate_effect(recent)
        
        return {
            "total_strategies": len(self.strategies),
            "total_decisions": len(self.decision_history),
            "current_strategy": self.get_current_strategy()["name"],
            "pending_approvals": list(self.pending_approvals.keys()),
            "auto_adjust_enabled": self.auto_adjust_enabled,
            "recent_effect": {
                "accuracy": effect.accuracy_score,
                "efficiency": effect.efficiency_score,
                "stability": effect.stability_score,
                "overall": effect.overall_score,
                "sample_count": effect.sample_count
            }
        }
    
    def enable_auto_adjust(self, enabled: bool = True):
        """启用/禁用自动调整"""
        self.auto_adjust_enabled = enabled
    
    def to_dict(self) -> Dict[str, Any]:
        """
        导出引擎状态为字典
        
        Returns:
            状态字典
        """
        return {
            "strategies": self.list_strategies(),
            "current_strategy": self.current_strategy_name,
            "statistics": self.get_statistics()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeedbackLoopEngine":
        """
        从字典恢复引擎状态
        
        Args:
            data: 状态字典
            
        Returns:
            FeedbackLoopEngine实例
        """
        engine = cls()
        
        # 恢复策略
        for strategy_data in data.get("strategies", []):
            strategy = Strategy(
                name=strategy_data["name"],
                version=strategy_data["version"],
                params=strategy_data.get("params", engine.DEFAULT_PARAMS.copy()),
                status=StrategyStatus(strategy_data.get("status", "draft")),
                rollout_percent=strategy_data.get("rollout_percent", 0.0),
                created_at=strategy_data.get("created_at", time.time()),
                updated_at=strategy_data.get("updated_at", time.time()),
                metadata=strategy_data.get("metadata", {})
            )
            engine.strategies[strategy_data["name"]] = strategy
        
        # 恢复当前策略
        if "current_strategy" in data:
            engine.current_strategy_name = data["current_strategy"]
        
        return engine


# 便捷函数
def create_sample_decision(
    decision_id: str,
    outcome: DecisionOutcome,
    accuracy: float = 0.8,
    response_time_ms: float = 1000,
    resource_usage: float = 0.3
) -> DecisionRecord:
    """创建示例决策记录"""
    return DecisionRecord(
        decision_id=decision_id,
        timestamp=time.time(),
        context={"sample": True},
        decision={"action": "test"},
        outcome=outcome,
        response_time_ms=response_time_ms,
        resource_usage=resource_usage,
        accuracy=accuracy
    )


# 示例用法
if __name__ == "__main__":
    # 创建引擎实例
    engine = FeedbackLoopEngine()
    
    # 记录一些测试决策
    for i in range(20):
        outcome = DecisionOutcome.SUCCESS if random.random() > 0.2 else DecisionOutcome.FAILURE
        decision = create_sample_decision(
            decision_id=f"dec_{i}",
            outcome=outcome,
            accuracy=0.7 + random.random() * 0.3,
            response_time_ms=500 + random.random() * 2000,
            resource_usage=random.random() * 0.5
        )
        engine.record_decision(decision)
    
    # 获取当前策略
    print("当前策略:", engine.get_current_strategy())
    
    # 评估效果
    recent = engine.get_recent_decisions(20)
    effect = engine.evaluate_effect(recent)
    print(f"\n效果评分:")
    print(f"  准确性: {effect.accuracy_score:.2%}")
    print(f"  效率: {effect.efficiency_score:.2%}")
    print(f"  稳定性: {effect.stability_score:.2%}")
    print(f"  综合: {effect.overall_score:.2%}")
    print(f"  置信度: {effect.confidence:.2%}")
    
    # 自动调整
    result = engine.auto_evaluate_and_adjust()
    print(f"\n自动调整结果: {result}")
    
    # 获取统计信息
    print(f"\n统计信息: {engine.get_statistics()}")
