#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多模型协作系统 - 模型管理器
实现重试机制、模型降级链、健康检查、熔断器模式
"""

import time
import random
import logging
import threading
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque

try:
    import config
except ImportError:
    print("⚠️  配置文件 config.py 未找到，使用默认配置")
    class config:
        MODEL_CHAIN = []
        CIRCUIT_BREAKER_CONFIG = {}
        RETRY_CONFIG = {}
        HEALTH_CHECK_CONFIG = {}
        LOGGING_CONFIG = {}


# =============================================================================
# 枚举定义
# =============================================================================

class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"        # 闭合状态：正常工作
    OPEN = "open"            # 打开状态：熔断，拒绝请求
    HALF_OPEN = "half_open"  # 半开状态：尝试恢复


class ModelHealth(Enum):
    """模型健康状态"""
    HEALTHY = "healthy"      # 健康
    UNHEALTHY = "unhealthy"  # 不健康
    UNKNOWN = "unknown"      # 未知


class ModelStatus(Enum):
    """模型状态"""
    ACTIVE = "active"        # 活跃（正在使用）
    STANDBY = "standby"      # 待命
    DISABLED = "disabled"    # 禁用
    FAILED = "failed"        # 故障


# =============================================================================
# 数据类定义
# =============================================================================

@dataclass
class ModelConfig:
    """模型配置"""
    name: str
    model_type: str
    api_key: str
    base_url: str
    timeout: int = 30
    max_retries: int = 3
    enabled: bool = True


@dataclass
class FailureRecord:
    """失败记录"""
    timestamp: datetime
    error: Exception


@dataclass
class CircuitBreakerMetrics:
    """熔断器指标"""
    total_requests: int = 0
    success_count: int = 0
    failure_count: int = 0
    timeout_count: int = 0
    rejected_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None


@dataclass
class ModelMetrics:
    """模型指标"""
    total_calls: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_latency: float = 0.0
    avg_latency: float = 0.0
    min_latency: float = float('inf')
    max_latency: float = 0.0
    last_call_time: Optional[datetime] = None


# =============================================================================
# 异常定义
# =============================================================================

class ModelError(Exception):
    """模型调用异常基类"""
    pass


class ModelTimeoutError(ModelError):
    """模型调用超时"""
    pass


class ModelAPIError(ModelError):
    """模型API错误"""
    pass


class CircuitBreakerOpenError(ModelError):
    """熔断器打开异常"""
    pass


class NoAvailableModelError(ModelError):
    """无可用模型异常"""
    pass


# =============================================================================
# 熔断器实现
# =============================================================================

class CircuitBreaker:
    """
    熔断器实现
    
    三种状态：
    - CLOSED: 正常工作，允许请求通过
    - OPEN: 熔断，直接拒绝请求
    - HALF_OPEN: 半开，允许少量请求通过测试
    """
    
    def __init__(
        self,
        model_name: str,
        failure_threshold: int = 5,
        failure_window: int = 60,
        recovery_timeout: int = 30,
        half_open_max_calls: int = 2,
        half_open_success_threshold: float = 0.5,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化熔断器
        
        Args:
            model_name: 模型名称
            failure_threshold: 失败次数阈值
            failure_window: 失败时间窗口（秒）
            recovery_timeout: 恢复超时（秒）
            half_open_max_calls: 半开状态最大请求数
            half_open_success_threshold: 半开状态成功率阈值
            logger: 日志记录器
        """
        self.model_name = model_name
        self.failure_threshold = failure_threshold
        self.failure_window = failure_window
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.half_open_success_threshold = half_open_success_threshold
        
        self.logger = logger or logging.getLogger(f"CircuitBreaker.{model_name}")
        
        # 状态管理
        self._state = CircuitState.CLOSED
        self._state_lock = threading.RLock()
        
        # 失败记录
        self._failures: deque = deque()
        
        # 半开状态跟踪
        self._half_open_calls = 0
        self._half_open_successes = 0
        
        # 熔断时间
        self._open_time: Optional[datetime] = None
        
        # 指标
        self.metrics = CircuitBreakerMetrics()
    
    @property
    def state(self) -> CircuitState:
        """获取当前状态"""
        with self._state_lock:
            return self._state
    
    def _cleanup_old_failures(self):
        """清理过期的失败记录"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.failure_window)
        
        while self._failures and self._failures[0].timestamp < cutoff:
            self._failures.popleft()
    
    def _transition_to_open(self):
        """切换到打开状态"""
        self._state = CircuitState.OPEN
        self._open_time = datetime.now()
        self.logger.warning(f"熔断器打开: {self.model_name}")
    
    def _transition_to_half_open(self):
        """切换到半开状态"""
        self._state = CircuitState.HALF_OPEN
        self._half_open_calls = 0
        self._half_open_successes = 0
        self.logger.info(f"熔断器进入半开状态: {self.model_name}")
    
    def _transition_to_closed(self):
        """切换到闭合状态"""
        self._state = CircuitState.CLOSED
        self._failures.clear()
        self._half_open_calls = 0
        self._half_open_successes = 0
        self.logger.info(f"熔断器恢复闭合: {self.model_name}")
    
    def _check_state_transition(self):
        """检查并执行状态转换"""
        now = datetime.now()
        
        if self._state == CircuitState.OPEN:
            # 检查是否可以进入半开状态
            if self._open_time and (now - self._open_time).total_seconds() >= self.recovery_timeout:
                self._transition_to_half_open()
        
        elif self._state == CircuitState.CLOSED:
            # 检查是否需要熔断
            self._cleanup_old_failures()
            if len(self._failures) >= self.failure_threshold:
                self._transition_to_open()
    
    def can_execute(self) -> bool:
        """
        检查是否可以执行请求
        
        Returns:
            是否可以执行
        """
        with self._state_lock:
            self._check_state_transition()
            
            if self._state == CircuitState.CLOSED:
                return True
            
            if self._state == CircuitState.HALF_OPEN:
                if self._half_open_calls < self.half_open_max_calls:
                    return True
                return False
            
            # OPEN state
            self.metrics.rejected_count += 1
            return False
    
    def on_success(self):
        """请求成功回调"""
        with self._state_lock:
            self.metrics.total_requests += 1
            self.metrics.success_count += 1
            self.metrics.last_success_time = datetime.now()
            
            if self._state == CircuitState.HALF_OPEN:
                self._half_open_calls += 1
                self._half_open_successes += 1
                
                # 检查是否可以恢复闭合
                success_rate = self._half_open_successes / self._half_open_calls
                if success_rate >= self.half_open_success_threshold:
                    self._transition_to_closed()
                elif self._half_open_calls >= self.half_open_max_calls:
                    # 半开请求用完但成功率不够，重新打开
                    self._transition_to_open()
    
    def on_failure(self, error: Exception):
        """
        请求失败回调
        
        Args:
            error: 异常对象
        """
        with self._state_lock:
            self.metrics.total_requests += 1
            self.metrics.failure_count += 1
            self.metrics.last_failure_time = datetime.now()
            
            if isinstance(error, TimeoutError):
                self.metrics.timeout_count += 1
            
            if self._state == CircuitState.CLOSED:
                self._failures.append(FailureRecord(
                    timestamp=datetime.now(),
                    error=error
                ))
                self._check_state_transition()
            
            elif self._state == CircuitState.HALF_OPEN:
                self._half_open_calls += 1
                # 半开状态下失败，立即重新打开
                self._transition_to_open()
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取熔断器指标"""
        with self._state_lock:
            return {
                "model_name": self.model_name,
                "state": self._state.value,
                "metrics": {
                    "total_requests": self.metrics.total_requests,
                    "success_count": self.metrics.success_count,
                    "failure_count": self.metrics.failure_count,
                    "timeout_count": self.metrics.timeout_count,
                    "rejected_count": self.metrics.rejected_count,
                    "last_failure_time": self.metrics.last_failure_time.isoformat() if self.metrics.last_failure_time else None,
                    "last_success_time": self.metrics.last_success_time.isoformat() if self.metrics.last_success_time else None
                },
                "current_failures": len(self._failures),
                "open_time": self._open_time.isoformat() if self._open_time else None
            }
    
    def reset(self):
        """重置熔断器"""
        with self._state_lock:
            self._state = CircuitState.CLOSED
            self._failures.clear()
            self._half_open_calls = 0
            self._half_open_successes = 0
            self._open_time = None
            self.metrics = CircuitBreakerMetrics()
            self.logger.info(f"熔断器已重置: {self.model_name}")


# =============================================================================
# 重试机制实现
# =============================================================================

class RetryPolicy:
    """
    重试策略（指数退避）
    
    支持：
    - 指数退避延迟
    - 随机抖动
    - 最大延迟限制
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_delay: float = 30.0,
        jitter_factor: float = 0.1,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化重试策略
        
        Args:
            max_retries: 最大重试次数
            initial_delay: 初始延迟（秒）
            backoff_factor: 退避倍数
            max_delay: 最大延迟（秒）
            jitter_factor: 抖动因子（0-1）
            logger: 日志记录器
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
        self.jitter_factor = jitter_factor
        self.logger = logger or logging.getLogger("RetryPolicy")
    
    def calculate_delay(self, attempt: int) -> float:
        """
        计算第n次重试的延迟时间
        
        Args:
            attempt: 重试次数（从0开始）
            
        Returns:
            延迟时间（秒）
        """
        # 指数退避
        delay = self.initial_delay * (self.backoff_factor ** attempt)
        
        # 限制最大延迟
        delay = min(delay, self.max_delay)
        
        # 添加随机抖动
        if self.jitter_factor > 0:
            jitter = random.uniform(-self.jitter_factor, self.jitter_factor)
            delay = delay * (1 + jitter)
        
        # 确保延迟不为负
        delay = max(delay, 0)
        
        return delay
    
    def execute(
        self,
        func: Callable,
        *args,
        retryable_exceptions: Optional[List[type]] = None,
        **kwargs
    ) -> Any:
        """
        执行函数，失败时自动重试
        
        Args:
            func: 要执行的函数
            *args: 函数位置参数
            retryable_exceptions: 可重试的异常类型列表
            **kwargs: 函数关键字参数
            
        Returns:
            函数返回值
            
        Raises:
            Exception: 最终失败时抛出最后一次异常
        """
        if retryable_exceptions is None:
            retryable_exceptions = [Exception]
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            
            except tuple(retryable_exceptions) as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self.calculate_delay(attempt)
                    self.logger.warning(
                        f"执行失败 (尝试 {attempt + 1}/{self.max_retries + 1}): {str(e)}. "
                        f"{delay:.2f}秒后重试..."
                    )
                    time.sleep(delay)
                else:
                    self.logger.error(
                        f"执行失败，已达到最大重试次数 ({self.max_retries + 1}): {str(e)}"
                    )
        
        raise last_exception


# =============================================================================
# 模型包装器
# =============================================================================

class ModelWrapper:
    """
    模型包装器
    
    封装单个模型的调用、健康检查、指标收集等功能
    """
    
    def __init__(
        self,
        config: ModelConfig,
        circuit_breaker: CircuitBreaker,
        retry_policy: RetryPolicy,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化模型包装器
        
        Args:
            config: 模型配置
            circuit_breaker: 熔断器
            retry_policy: 重试策略
            logger: 日志记录器
        """
        self.config = config
        self.circuit_breaker = circuit_breaker
        self.retry_policy = retry_policy
        self.logger = logger or logging.getLogger(f"Model.{config.name}")
        
        # 状态管理
        self._status = ModelStatus.STANDBY
        self._health = ModelHealth.UNKNOWN
        self._lock = threading.RLock()
        
        # 指标
        self.metrics = ModelMetrics()
        
        # 健康检查相关
        self._consecutive_failures = 0
        self._consecutive_successes = 0
        self._health_check_config = config.HEALTH_CHECK_CONFIG if hasattr(config, 'HEALTH_CHECK_CONFIG') else {}
    
    @property
    def name(self) -> str:
        """获取模型名称"""
        return self.config.name
    
    @property
    def status(self) -> ModelStatus:
        """获取模型状态"""
        with self._lock:
            return self._status
    
    @property
    def health(self) -> ModelHealth:
        """获取健康状态"""
        with self._lock:
            return self._health
    
    def is_available(self) -> bool:
        """
        检查模型是否可用
        
        Returns:
            是否可用
        """
        if not self.config.enabled:
            return False
        
        with self._lock:
            if self._status == ModelStatus.DISABLED:
                return False
            if self._health == ModelHealth.UNHEALTHY:
                return False
        
        return self.circuit_breaker.can_execute()
    
    def _update_metrics(self, success: bool, latency: float):
        """
        更新指标
        
        Args:
            success: 是否成功
            latency: 延迟（秒）
        """
        with self._lock:
            self.metrics.total_calls += 1
            self.metrics.total_latency += latency
            self.metrics.avg_latency = self.metrics.total_latency / self.metrics.total_calls
            self.metrics.min_latency = min(self.metrics.min_latency, latency)
            self.metrics.max_latency = max(self.metrics.max_latency, latency)
            self.metrics.last_call_time = datetime.now()
            
            if success:
                self.metrics.success_count += 1
            else:
                self.metrics.failure_count += 1
    
    def _update_health(self, success: bool):
        """
        更新健康状态
        
        Args:
            success: 是否成功
        """
        failure_threshold = self._health_check_config.get('failure_threshold', 3)
        success_threshold = self._health_check_config.get('success_threshold', 2)
        
        with self._lock:
            if success:
                self._consecutive_successes += 1
                self._consecutive_failures = 0
                
                if self._consecutive_successes >= success_threshold:
                    self._health = ModelHealth.HEALTHY
            else:
                self._consecutive_failures += 1
                self._consecutive_successes = 0
                
                if self._consecutive_failures >= failure_threshold:
                    self._health = ModelHealth.UNHEALTHY
    
    def call(
        self,
        func: Callable,
        *args,
        retryable_exceptions: Optional[List[type]] = None,
        **kwargs
    ) -> Any:
        """
        调用模型
        
        Args:
            func: 实际调用函数
            *args: 位置参数
            retryable_exceptions: 可重试的异常类型
            **kwargs: 关键字参数
            
        Returns:
            调用结果
            
        Raises:
            CircuitBreakerOpenError: 熔断器打开
            NoAvailableModelError: 模型不可用
            Exception: 调用失败
        """
        start_time = time.time()
        
        # 检查熔断器
        if not self.circuit_breaker.can_execute():
            raise CircuitBreakerOpenError(
                f"熔断器已打开，拒绝请求: {self.name}"
            )
        
        try:
            # 执行调用（带重试）
            result = self.retry_policy.execute(
                func,
                *args,
                retryable_exceptions=retryable_exceptions,
                **kwargs
            )
            
            # 成功处理
            latency = time.time() - start_time
            self._update_metrics(True, latency)
            self._update_health(True)
            self.circuit_breaker.on_success()
            
            self.logger.info(
                f"模型调用成功: {self.name}, 延迟: {latency:.3f}s"
            )
            
            return result
        
        except Exception as e:
            # 失败处理
            latency = time.time() - start_time
            self._update_metrics(False, latency)
            self._update_health(False)
            self.circuit_breaker.on_failure(e)
            
            self.logger.error(
                f"模型调用失败: {self.name}, 错误: {str(e)}, 延迟: {latency:.3f}s"
            )
            
            raise
    
    def set_status(self, status: ModelStatus):
        """
        设置模型状态
        
        Args:
            status: 新状态
        """
        with self._lock:
            old_status = self._status
            self._status = status
            self.logger.info(f"模型状态变更: {self.name}: {old_status.value} -> {status.value}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取模型指标"""
        with self._lock:
            return {
                "name": self.name,
                "model_type": self.config.model_type,
                "status": self._status.value,
                "health": self._health.value,
                "enabled": self.config.enabled,
                "metrics": {
                    "total_calls": self.metrics.total_calls,
                    "success_count": self.metrics.success_count,
                    "failure_count": self.metrics.failure_count,
                    "success_rate": (
                        self.metrics.success_count / self.metrics.total_calls * 100
                        if self.metrics.total_calls > 0 else 0
                    ),
                    "avg_latency": self.metrics.avg_latency,
                    "min_latency": self.metrics.min_latency if self.metrics.min_latency != float('inf') else 0,
                    "max_latency": self.metrics.max_latency,
                    "last_call_time": self.metrics.last_call_time.isoformat() if self.metrics.last_call_time else None
                },
                "circuit_breaker": self.circuit_breaker.get_metrics()
            }
    
    def reset(self):
        """重置模型状态"""
        with self._lock:
            self._status = ModelStatus.STANDBY
            self._health = ModelHealth.UNKNOWN
            self._consecutive_failures = 0
            self._consecutive_successes = 0
            self.metrics = ModelMetrics()
        
        self.circuit_breaker.reset()
        self.logger.info(f"模型已重置: {self.name}")


# =============================================================================
# 模型管理器
# =============================================================================

class ModelManager:
    """
    模型管理器
    
    负责管理多个模型，实现：
    - 模型降级链
    - 自动故障转移
    - 健康检查
    """
    
    def __init__(
        self,
        model_configs: Optional[List[Dict]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化模型管理器
        
        Args:
            model_configs: 模型配置列表
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger("ModelManager")
        
        # 加载配置
        if model_configs is None:
            model_configs = config.MODEL_CHAIN if hasattr(config, 'MODEL_CHAIN') else []
        
        # 初始化组件
        self._models: Dict[str, ModelWrapper] = {}
        self._model_chain: List[str] = []
        self._lock = threading.RLock()
        
        # 健康检查线程
        self._health_check_thread: Optional[threading.Thread] = None
        self._health_check_running = False
        self._health_check_interval = (
            config.HEALTH_CHECK_CONFIG.get('check_interval', 30)
            if hasattr(config, 'HEALTH_CHECK_CONFIG') else 30
        )
        
        # 初始化模型
        self._initialize_models(model_configs)
    
    def _initialize_models(self, model_configs: List[Dict]):
        """
        初始化模型
        
        Args:
            model_configs: 模型配置列表
        """
        cb_config = (
            config.CIRCUIT_BREAKER_CONFIG if hasattr(config, 'CIRCUIT_BREAKER_CONFIG') else {}
        )
        retry_config = (
            config.RETRY_CONFIG if hasattr(config, 'RETRY_CONFIG') else {}
        )
        
        for cfg in model_configs:
            model_config = ModelConfig(
                name=cfg['name'],
                model_type=cfg['model_type'],
                api_key=cfg['api_key'],
                base_url=cfg['base_url'],
                timeout=cfg.get('timeout', 30),
                max_retries=cfg.get('max_retries', 3),
                enabled=cfg.get('enabled', True)
            )
            
            # 创建熔断器
            circuit_breaker = CircuitBreaker(
                model_name=model_config.name,
                failure_threshold=cb_config.get('failure_threshold', 5),
                failure_window=cb_config.get('failure_window', 60),
                recovery_timeout=cb_config.get('recovery_timeout', 30),
                half_open_max_calls=cb_config.get('half_open_max_calls', 2),
                half_open_success_threshold=cb_config.get('half_open_success_threshold', 0.5)
            )
            
            # 创建重试策略
            retry_policy = RetryPolicy(
                max_retries=retry_config.get('max_retries', 3),
                initial_delay=retry_config.get('initial_delay', 1.0),
                backoff_factor=retry_config.get('backoff_factor', 2.0),
                max_delay=retry_config.get('max_delay', 30.0),
                jitter_factor=retry_config.get('jitter_factor', 0.1)
            )
            
            # 创建模型包装器
            model = ModelWrapper(
                config=model_config,
                circuit_breaker=circuit_breaker,
                retry_policy=retry_policy
            )
            
            self._models[model_config.name] = model
            self._model_chain.append(model_config.name)
            
            self.logger.info(f"已加载模型: {model_config.name} ({model_config.model_type})")
        
        # 设置第一个模型为活跃状态
        if self._model_chain:
            self._models[self._model_chain[0]].set_status(ModelStatus.ACTIVE)
    
    def get_available_model(self) -> Optional[ModelWrapper]:
        """
        获取可用的模型
        
        Returns:
            可用的模型包装器，如果没有可用模型返回None
        """
        with self._lock:
            for model_name in self._model_chain:
                model = self._models[model_name]
                if model.is_available():
                    return model
            
            return None
    
    def execute(
        self,
        func: Callable,
        *args,
        model_selector: Optional[Callable[[ModelWrapper], bool]] = None,
        **kwargs
    ) -> Any:
        """
        执行模型调用，自动降级
        
        Args:
            func: 实际调用函数，签名为 func(model: ModelWrapper, *args, **kwargs)
            *args: 位置参数
            model_selector: 可选的模型选择器函数
            **kwargs: 关键字参数
            
        Returns:
            调用结果
            
        Raises:
            NoAvailableModelError: 没有可用模型
        """
        tried_models = []
        
        while True:
            model = self.get_available_model()
            
            if model is None:
                raise NoAvailableModelError(
                    f"没有可用的模型，已尝试: {tried_models}"
                )
            
            if model.name in tried_models:
                # 已尝试过所有模型
                raise NoAvailableModelError(
                    f"所有模型都已尝试且失败: {tried_models}"
                )
            
            tried_models.append(model.name)
            
            try:
                self.logger.info(f"尝试使用模型: {model.name}")
                return func(model, *args, **kwargs)
            
            except CircuitBreakerOpenError:
                self.logger.warning(f"熔断器已打开: {model.name}，尝试下一个模型")
                continue
            
            except Exception as e:
                self.logger.error(f"模型调用失败: {model.name}, 错误: {str(e)}")
                
                # 检查是否应该尝试下一个模型
                if isinstance(e, (ModelTimeoutError, ModelAPIError)):
                    self.logger.info(f"尝试降级到下一个模型")
                    continue
                
                # 其他错误直接抛出
                raise
    
    def start_health_check(self):
        """启动健康检查"""
        if self._health_check_running:
            self.logger.warning("健康检查已在运行中")
            return
        
        self._health_check_running = True
        self._health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True,
            name="ModelHealthCheck"
        )
        self._health_check_thread.start()
        self.logger.info("健康检查已启动")
    
    def stop_health_check(self):
        """停止健康检查"""
        self._health_check_running = False
        if self._health_check_thread:
            self._health_check_thread.join(timeout=5)
            self.logger.info("健康检查已停止")
    
    def _health_check_loop(self):
        """健康检查循环"""
        while self._health_check_running:
            try:
                self._perform_health_check()
            except Exception as e:
                self.logger.error(f"健康检查执行失败: {str(e)}")
            
            time.sleep(self._health_check_interval)
    
    def _perform_health_check(self):
        """执行健康检查"""
        with self._lock:
            active_found = False
            
            for model_name in self._model_chain:
                model = self._models[model_name]
                
                if not active_found and model.is_available():
                    # 设置为活跃状态
                    if model.status != ModelStatus.ACTIVE:
                        model.set_status(ModelStatus.ACTIVE)
                        self.logger.info(f"模型切换为活跃: {model_name}")
                    active_found = True
                else:
                    # 设置为待命状态
                    if model.status == ModelStatus.ACTIVE:
                        model.set_status(ModelStatus.STANDBY)
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        with self._lock:
            return {
                "total_models": len(self._model_chain),
                "model_chain": self._model_chain,
                "models": {
                    name: model.get_metrics()
                    for name, model in self._models.items()
                },
                "health_check_running": self._health_check_running
            }
    
    def reset_all(self):
        """重置所有模型"""
        with self._lock:
            for model in self._models.values():
                model.reset()
            
            # 重新设置第一个模型为活跃
            if self._model_chain:
                self._models[self._model_chain[0]].set_status(ModelStatus.ACTIVE)
        
        self.logger.info("所有模型已重置")


# =============================================================================
# 日志设置
# =============================================================================

def setup_logging(config_dict: Optional[Dict] = None):
    """
    设置日志
    
    Args:
        config_dict: 日志配置字典
    """
    if config_dict is None:
        config_dict = config.LOGGING_CONFIG if hasattr(config, 'LOGGING_CONFIG') else {}
    
    log_level = getattr(logging, config_dict.get('level', 'INFO'))
    log_format = config_dict.get(
        'format',
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    date_format = config_dict.get('date_format', '%Y-%m-%d %H:%M:%S')
    
    handlers = []
    if config_dict.get('console_output', True):
        handlers.append(logging.StreamHandler())
    
    log_file = config_dict.get('log_file')
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )


# =============================================================================
# 示例用法
# =============================================================================

def example_usage():
    """示例用法"""
    # 设置日志
    setup_logging()
    
    # 创建模型管理器
    manager = ModelManager()
    
    # 启动健康检查
    manager.start_health_check()
    
    try:
        # 定义模拟的模型调用函数
        def mock_model_call(model: ModelWrapper, prompt: str) -> str:
            """模拟模型调用"""
            print(f"[{model.name}] 处理请求: {prompt}")
            
            # 模拟随机失败
            import random
            if random.random() < 0.3:
                raise ModelAPIError(f"模拟API错误: {model.name}")
            
            return f"[{model.name}] 响应: 这是对 '{prompt}' 的回复"
        
        # 执行调用
        result = manager.execute(mock_model_call, "你好，请介绍一下自己")
        print(f"\n最终结果: {result}")
        
        # 打印状态
        print("\n系统状态:")
        import json
        print(json.dumps(manager.get_status(), indent=2, ensure_ascii=False))
    
    finally:
        # 停止健康检查
        manager.stop_health_check()


if __name__ == "__main__":
    example_usage()
