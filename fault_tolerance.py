#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
🎼 交响 Symphony 容错机制 v1.0
============================================================================
基于团队讨论结果实现：林思远/陈美琪/王浩然/张明远/赵敏/刘心怡
============================================================================
"""

import time
import logging
from enum import Enum
from typing import Optional, List, Callable, Any
from dataclasses import dataclass
from functools import wraps

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Symphony")

# =============================================================================
# 异常定义
# =============================================================================

class FaultToleranceError(Exception):
    """容错基础异常"""
    pass

class ModelFailureError(FaultToleranceError):
    """模型调用失败"""
    pass

class CircuitBreakerOpenError(FaultToleranceError):
    """熔断器开启"""
    pass

class AllModelsFailedError(FaultToleranceError):
    """所有模型都失败"""
    pass

# =============================================================================
# 错误码定义
# =============================================================================

class ErrorCode(Enum):
    SUCCESS = 0
    NETWORK_TIMEOUT = 1001
    MODEL_ERROR = 1002
    CIRCUIT_BREAKER = 1003
    ALL_FAILED = 1004
    UNKNOWN = 9999

# =============================================================================
# 熔断器
# =============================================================================

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5      # 失败次数阈值
    success_threshold: int = 3       # 恢复需要成功次数
    timeout: float = 60.0            # 熔断超时时间(秒)
    half_open_requests: int = 3     # 半开状态允许的请求数

class CircuitBreaker:
    """熔断器 - 基于团队讨论方案"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.failure_count = 0
        self.success_count = 0
        self.state = "closed"  # closed, open, half-open
        self.last_failure_time = None
        
    def record_success(self):
        """记录成功"""
        self.success_count += 1
        if self.state == "half-open":
            if self.success_count >= self.config.success_threshold:
                self._reset()
                
    def record_failure(self):
        """记录失败"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.config.failure_threshold:
            self._trip()
            
    def _trip(self):
        """熔断开启"""
        self.state = "open"
        logger.warning(f"CircuitBreaker [{self.name}] OPENED")
        
    def _reset(self):
        """重置"""
        self.state = "closed"
        self.failure_count = 0
        self.success_count = 0
        logger.info(f"CircuitBreaker [{self.name}] RESET")
        
    def can_execute(self) -> bool:
        """是否可以执行"""
        if self.state == "closed":
            return True
        elif self.state == "open":
            if time.time() - self.last_failure_time > self.config.timeout:
                self.state = "half-open"
                self.success_count = 0
                return True
            return False
        else:  # half-open
            return self.success_count < self.config.half_open_requests

# =============================================================================
# Fallback策略 - 三级梯队
# =============================================================================

@dataclass
class ModelConfig:
    model_id: str
    priority: int
    is_backup: bool = False

class FallbackStrategy:
    """Fallback策略 - 三级模型梯队"""
    
    def __init__(self):
        # 三级梯队配置
        self.tiers = {
            1: [],  # 主模型
            2: [],  # 轻量模型
            3: []   # 规则引擎/缓存
        }
        self.current_tier = 1
        
    def add_model(self, model_id: str, priority: int, tier: int = 1):
        """添加模型"""
        if tier in self.tiers:
            self.tiers[tier].append(ModelConfig(model_id, priority, tier > 1))
            
    def get_current_model(self) -> Optional[ModelConfig]:
        """获取当前模型"""
        for model in sorted(self.tiers.get(self.current_tier, []), key=lambda x: x.priority):
            return model
        return None
        
    def fallback(self):
        """降级到下一级"""
        if self.current_tier < 3:
            self.current_tier += 1
            logger.info(f"Fallback to tier {self.current_tier}")
        else:
            raise AllModelsFailedError("All models failed")
            
    def reset(self):
        """重置"""
        self.current_tier = 1

# =============================================================================
# 统一异常处理
# =============================================================================

class ExceptionHandler:
    """统一异常处理 - 标准化错误码"""
    
    @staticmethod
    def handle_network_timeout(e: Exception) -> dict:
        return {
            "code": ErrorCode.NETWORK_TIMEOUT.value,
            "message": "网络超时",
            "detail": str(e)
        }
        
    @staticmethod
    def handle_model_error(e: Exception) -> dict:
        return {
            "code": ErrorCode.MODEL_ERROR.value,
            "message": "模型错误",
            "detail": str(e)
        }
        
    @staticmethod
    def handle_circuit_breaker(e: Exception) -> dict:
        return {
            "code": ErrorCode.CIRCUIT_BREAKER.value.value,
            "message": "熔断器开启",
            "detail": str(e)
        }
        
    @staticmethod
    def handle_unknown(e: Exception) -> dict:
        return {
            "code": ErrorCode.UNKNOWN.value,
            "message": "未知错误",
            "detail": str(e)
        }

# =============================================================================
# 容错执行器
# =============================================================================

class FaultTolerantExecutor:
    """容错执行器 - 整合所有容错机制"""
    
    def __init__(self):
        self.fallback_strategy = FallbackStrategy()
        self.circuit_breakers = {}
        self.retry_config = {
            "max_retries": 2,
            "backoff_factor": 2,  # 指数退避
            "initial_delay": 1    # 初始延迟(秒)
        }
        
    def add_circuit_breaker(self, name: str, config: CircuitBreakerConfig = None):
        """添加熔断器"""
        self.circuit_breakers[name] = CircuitBreaker(name, config)
        
    def execute_with_fault_tolerance(
        self, 
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """执行带容错的函数"""
        
        # 获取当前模型
        model_config = self.fallback_strategy.get_current_model()
        if not model_config:
            raise AllModelsFailedError("No available model")
            
        # 检查熔断器
        breaker = self.circuit_breakers.get(model_config.model_id)
        if breaker and not breaker.can_execute():
            self.fallback_strategy.fallback()
            return self.execute_with_fault_tolerance(func, *args, **kwargs)
            
        # 重试配置
        max_retries = self.retry_config["max_retries"]
        delay = self.retry_config["initial_delay"]
        
        for attempt in range(max_retries + 1):
            try:
                result = func(*args, **kwargs)
                
                # 记录成功
                if breaker:
                    breaker.record_success()
                    
                return result
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                # 记录失败
                if breaker:
                    breaker.record_failure()
                    
                # 指数退避
                if attempt < max_retries:
                    time.sleep(delay)
                    delay *= self.retry_config["backoff_factor"]
                    
                # 尝试降级
                if attempt == max_retries:
                    try:
                        self.fallback_strategy.fallback()
                        return self.execute_with_fault_tolerance(func, *args, **kwargs)
                    except AllModelsFailedError:
                        return ExceptionHandler.handle_unknown(e)
                        
        raise AllModelsFailedError("All retry attempts failed")

# =============================================================================器 - 简单易
# 装饰用
# =============================================================================

def fault_tolerant(executor: FaultTolerantExecutor = None):
    """容错装饰器"""
    _executor = executor or FaultTolerantExecutor()
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return _executor.execute_with_fault_tolerance(func, *args, **kwargs)
        return wrapper
    return decorator

# =============================================================================
# 使用示例
# =============================================================================

if __name__ == "__main__":
    # 创建执行器
    executor = FaultTolerantExecutor()
    
    # 配置三级模型梯队
    executor.fallback_strategy.add_model("ark-code-latest", 1, 1)
    executor.fallback_strategy.add_model("deepseek-v3.2", 2, 1)
    executor.fallback_strategy.add_model("doubao-seed-2.0-code", 1, 2)
    executor.fallback_strategy.add_model("glm-4.7", 1, 3)
    
    # 添加熔断器
    executor.add_circuit_breaker("ark-code-latest")
    executor.add_circuit_breaker("deepseek-v3.2")
    
    # 测试函数
    @fault_tolerant(executor)
    def call_model(prompt: str) -> str:
        # 这里调用实际的模型API
        return f"Model response: {prompt}"
    
    # 执行
    result = call_model("Hello Symphony!")
    print(f"Result: {result}")
    
    print("容错机制已就绪！")
