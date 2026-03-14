#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
health_checker.py - 健康检查器
实现模型状态监控和自动恢复机制
"""
import time
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime, timedelta
from enum import Enum


class ModelStatus(Enum):
    """模型状态枚举"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthChecker:
    """健康检查器 - 模型状态监控"""
    
    def __init__(
        self,
        check_interval: int = 60,
        failure_threshold: int = 3,
        recovery_threshold: int = 2
    ):
        """
        初始化健康检查器
        
        Args:
            check_interval: 检查间隔（秒）
            failure_threshold: 失败阈值
            recovery_threshold: 恢复阈值
        """
        self.check_interval = check_interval
        self.failure_threshold = failure_threshold
        self.recovery_threshold = recovery_threshold
        
        # 模型状态
        self.model_status: Dict[str, ModelStatus] = {}
        # 失败计数
        self.failure_counts: Dict[str, int] = {}
        # 成功计数（用于恢复）
        self.success_counts: Dict[str, int] = {}
        # 最后检查时间
        self.last_check: Dict[str, datetime] = {}
        # 最后心跳
        self.last_heartbeat: Dict[str, datetime] = {}
    
    def record_call(
        self,
        model_name: str,
        success: bool,
        response_time: Optional[float] = None
    ) -> None:
        """
        记录模型调用结果
        
        Args:
            model_name: 模型名称
            success: 是否成功
            response_time: 响应时间
        """
        now = datetime.now()
        self.last_heartbeat[model_name] = now
        
        if success:
            self.failure_counts[model_name] = 0
            self.success_counts[model_name] = self.success_counts.get(model_name, 0) + 1
            
            # 检查是否可以恢复
            if self.model_status.get(model_name) == ModelStatus.UNHEALTHY:
                if self.success_counts[model_name] >= self.recovery_threshold:
                    self.model_status[model_name] = ModelStatus.HEALTHY
                    self.success_counts[model_name] = 0
        else:
            self.failure_counts[model_name] = self.failure_counts.get(model_name, 0) + 1
            self.success_counts[model_name] = 0
            
            # 检查是否需要降级
            if self.failure_counts[model_name] >= self.failure_threshold:
                self.model_status[model_name] = ModelStatus.UNHEALTHY
            elif self.failure_counts[model_name] >= 1:
                self.model_status[model_name] = ModelStatus.DEGRADED
    
    def get_status(self, model_name: str) -> ModelStatus:
        """
        获取模型状态
        
        Args:
            model_name: 模型名称
        
        Returns:
            模型状态
        """
        return self.model_status.get(model_name, ModelStatus.UNKNOWN)
    
    def is_healthy(self, model_name: str) -> bool:
        """
        检查模型是否健康
        
        Args:
            model_name: 模型名称
        
        Returns:
            是否健康
        """
        status = self.get_status(model_name)
        return status in [ModelStatus.HEALTHY, ModelStatus.DEGRADED]
    
    def get_available_models(self, all_models: List[str]) -> List[str]:
        """
        获取可用的模型列表
        
        Args:
            all_models: 所有模型列表
        
        Returns:
            可用模型列表
        """
        return [m for m in all_models if self.is_healthy(m)]
    
    def heartbeat(self, model_name: str) -> Dict[str, Any]:
        """
        发送心跳
        
        Args:
            model_name: 模型名称
        
        Returns:
            心跳结果
        """
        now = datetime.now()
        self.last_heartbeat[model_name] = now
        
        return {
            "model": model_name,
            "status": self.get_status(model_name).value,
            "timestamp": now.isoformat(),
            "failure_count": self.failure_counts.get(model_name, 0)
        }
    
    def get_health_report(self) -> Dict[str, Any]:
        """
        获取健康报告
        
        Returns:
            健康报告
        """
        now = datetime.now()
        
        models = []
        for model_name in self.model_status:
            status = self.model_status[model_name]
            last_hb = self.last_heartbeat.get(model_name)
            
            models.append({
                "name": model_name,
                "status": status.value,
                "failure_count": self.failure_counts.get(model_name, 0),
                "success_count": self.success_counts.get(model_name, 0),
                "last_heartbeat": last_hb.isoformat() if last_hb else None,
                "seconds_since_heartbeat": (now - last_hb).total_seconds() if last_hb else None
            })
        
        return {
            "timestamp": now.isoformat(),
            "total_models": len(self.model_status),
            "healthy": sum(1 for s in self.model_status.values() if s == ModelStatus.HEALTHY),
            "degraded": sum(1 for s in self.model_status.values() if s == ModelStatus.DEGRADED),
            "unhealthy": sum(1 for s in self.model_status.values() if s == ModelStatus.UNHEALTHY),
            "models": models
        }


class AutoRecovery:
    """自动恢复机制"""
    
    def __init__(self, health_checker: HealthChecker):
        self.health_checker = health_checker
        self.recovery_actions: Dict[str, Callable] = {}
        self.recovery_history: List[Dict[str, Any]] = []
    
    def register_recovery_action(
        self,
        model_name: str,
        action: Callable
    ) -> None:
        """
        注册恢复动作
        
        Args:
            model_name: 模型名称
            action: 恢复动作函数
        """
        self.recovery_actions[model_name] = action
    
    def attempt_recovery(self, model_name: str) -> Dict[str, Any]:
        """
        尝试恢复
        
        Args:
            model_name: 模型名称
        
        Returns:
            恢复结果
        """
        status = self.health_checker.get_status(model_name)
        
        if status != ModelStatus.UNHEALTHY:
            return {
                "model": model_name,
                "recovery_needed": False,
                "reason": f"模型状态为 {status.value}"
            }
        
        action = self.recovery_actions.get(model_name)
        if not action:
            return {
                "model": model_name,
                "recovery_needed": True,
                "action_available": False
            }
        
        try:
            result = action()
            self.recovery_history.append({
                "model": model_name,
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "result": str(result)
            })
            return {
                "model": model_name,
                "recovery_needed": True,
                "action_available": True,
                "success": True
            }
        except Exception as e:
            self.recovery_history.append({
                "model": model_name,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            })
            return {
                "model": model_name,
                "recovery_needed": True,
                "action_available": True,
                "success": False,
                "error": str(e)
            }


# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("🦊 健康检查器测试")
    print("=" * 60)
    
    # 创建健康检查器
    checker = HealthChecker(failure_threshold=3, recovery_threshold=2)
    
    # 模拟模型调用
    print("\n模拟模型调用...")
    
    # 模型1：正常
    for i in range(5):
        checker.record_call("model_healthy", True)
    
    # 模型2：部分失败后恢复
    checker.record_call("model_recovery", False)
    checker.record_call("model_recovery", False)
    checker.record_call("model_recovery", False)
    print(f"  model_recovery 状态: {checker.get_status('model_recovery').value}")
    
    # 恢复
    checker.record_call("model_recovery", True)
    checker.record_call("model_recovery", True)
    print(f"  model_recovery 恢复后: {checker.get_status('model_recovery').value}")
    
    # 获取健康报告
    print("\n健康报告:")
    report = checker.get_health_report()
    print(f"  总模型数: {report['total_models']}")
    print(f"  健康: {report['healthy']}")
    print(f"  降级: {report['degraded']}")
    print(f"  不健康: {report['unhealthy']}")
    
    print("\n✅ 健康检查器测试完成")
