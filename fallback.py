
"""
Symphony Fallback - 服务降级策略
"""
from typing import Callable, Any, Optional
import logging

logger = logging.getLogger(__name__)

class FallbackManager:
    """降级管理器"""
    def __init__(self):
        self.fallbacks = {}
    
    def register(self, key: str, fallback: Callable):
        """注册降级函数"""
        self.fallbacks[key] = fallback
    
    def execute(self, key: str, *args, **kwargs) -> Any:
        """执行降级"""
        if key in self.fallbacks:
            logger.info(f"Executing fallback for {key}")
            return self.fallbacks[key](*args, **kwargs)
        raise KeyError(f"No fallback found for {key}")

# 全局降级管理器
fallback_manager = FallbackManager()

def with_fallback(fallback_key: str):
    """降级装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Primary call failed: {e}, using fallback")
                return fallback_manager.execute(fallback_key, *args, **kwargs)
        return wrapper
    return decorator
