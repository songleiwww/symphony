"""
序境内核 - 健康检查与故障自愈
"""

import time
import threading
from typing import Dict, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """健康检查结果"""
    model_id: str
    status: HealthStatus
    latency_ms: float = 0
    error: str = ""
    timestamp: float = field(default_factory=time.time)


class HealthChecker:
    """健康检查器"""
    
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
        self._checkers: Dict[str, Callable] = {}
    
    def register_checker(self, model_type: str, checker: Callable):
        """注册检查器"""
        self._checkers[model_type] = checker
    
    def check(self, model_config) -> HealthCheck:
        """执行健康检查"""
        try:
            # 简单检查：验证API可连接
            start = time.time()
            # 这里应该调用实际的API检查
            latency = (time.time() - start) * 1000
            
            if latency < self.timeout * 1000:
                return HealthCheck(
                    model_id=model_config.model_id,
                    status=HealthStatus.HEALTHY,
                    latency_ms=latency
                )
            else:
                return HealthCheck(
                    model_id=model_config.model_id,
                    status=HealthStatus.DEGRADED,
                    latency_ms=latency,
                    error="超时"
                )
        except Exception as e:
            return HealthCheck(
                model_id=model_config.model_id,
                status=HealthStatus.FAILED,
                error=str(e)
            )


class SelfHealer:
    """故障自愈机制"""
    
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.health_checker = HealthChecker()
        self._healing_enabled = True
        self._heal_actions: Dict[str, Callable] = {}
    
    def register_heal_action(self, status: HealthStatus, action: Callable):
        """注册自愈动作"""
        self._heal_actions[status.value] = action
    
    def auto_heal(self, model_id: str) -> bool:
        """执行自动修复"""
        if not self._healing_enabled:
            return False
        
        model = self.scheduler.models.get(model_id)
        if not model:
            return False
        
        # 执行健康检查
        health = self.health_checker.check(model)
        
        if health.status == HealthStatus.FAILED:
            # 尝试自愈
            logger.warning(f"检测到模型 {model.model_name} 故障，准备自愈")
            
            # 降级模型
            from .scheduler import ModelStatus
            model.status = ModelStatus.DEGRADE
            
            # 触发自愈动作
            heal_action = self._heal_actions.get("failed")
            if heal_action:
                heal_action(model)
            
            return True
        
        elif health.status == HealthStatus.DEGRADED:
            # 尝试恢复
            logger.info(f"模型 {model.model_name} 状态降级")
            return True
        
        return False
    
    def periodic_check(self, interval: int = 60):
        """定期健康检查"""
        def _check_loop():
            while self._healing_enabled:
                time.sleep(interval)
                for model_id in list(self.scheduler.models.keys()):
                    self.auto_heal(model_id)
        
        thread = threading.Thread(target=_check_loop, daemon=True)
        thread.start()
    
    def enable(self):
        """启用自愈"""
        self._healing_enabled = True
    
    def disable(self):
        """禁用自愈"""
        self._healing_enabled = False


# 全局健康检查器
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker
