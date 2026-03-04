#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多模型协作系统 - 故障处理与容错机制
包含重试器、熔断器、降级管理器、健康检查器、故障转移器等核心组件
"""

import time
import random
import logging
import threading
from enum import Enum
from typing import (
    Any, Callable, Dict, List, Optional, Tuple, Type, Union
)
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
from functools import wraps

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# 异常定义
# =============================================================================

class FaultToleranceError(Exception):
    """容错系统基础异常"""
    pass


class RetryError(FaultToleranceError):
    """重试失败异常"""
    pass


class CircuitOpenError(FaultToleranceError):
    """熔断器打开异常"""
    pass


class FallbackError(FaultToleranceError):
    """降级失败异常"""
    pass


class TimeoutError(FaultToleranceError):
    """超时异常"""
    pass


class NoHealthyModelError(FaultToleranceError):
    """无健康模型异常"""
    pass


# =============================================================================
# 枚举类型
# =============================================================================

class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"      # 关闭状态，正常放行请求
    OPEN = "open"          # 打开状态，拒绝请求
    HALF_OPEN = "half_open"  # 半开状态，允许少量请求测试


class HealthStatus(Enum):
    """健康状态"""
    HEALTHY = "healthy"    # 健康
    DEGRADED = "degraded"  # 降级
    UNHEALTHY = "unhealthy"  # 不健康


class ErrorType(Enum):
    """错误类型"""
    TIMEOUT = "timeout"
    NETWORK = "network"
    RATE_LIMIT = "rate_limit"
    SERVER_ERROR = "server_error"
    CLIENT_ERROR = "client_error"
    UNKNOWN = "unknown"


# =============================================================================
# 数据类
# =============================================================================

@dataclass
class RetryConfig:
    """重试配置"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    jitter: bool = True
    jitter_range: float = 0.2


@dataclass
class CircuitBreakerConfig:
    """熔断器配置"""
    failure_threshold: float = 0.5
    recovery_timeout: float = 30.0
    window_size: float = 10.0
    min_requests: int = 5
    half_open_max_calls: int = 3


@dataclass
class TimeoutConfig:
    """超时配置"""
    total: float = 60.0
    connect: float = 10.0
    read: float = 30.0
    write: float = 10.0


@dataclass
class HealthCheckConfig:
    """健康检查配置"""
    check_interval: float = 30.0
    unhealthy_threshold: float = 50.0
    degraded_threshold: float = 80.0
    probe_timeout: float = 5.0


@dataclass
class ModelConfig:
    """模型配置"""
    model_id: str
    name: str
    priority: int = 0
    is_primary: bool = False
    health_check_endpoint: Optional[str] = None
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)


@dataclass
class RequestMetrics:
    """请求指标"""
    success_count: int = 0
    failure_count: int = 0
    total_latency: float = 0.0
    latency_samples: List[float] = field(default_factory=list)
    error_counts: Dict[ErrorType, int] = field(default_factory=dict)
    last_request_time: Optional[float] = None


@dataclass
class ModelHealth:
    """模型健康状态"""
    model_id: str
    config: ModelConfig
    status: HealthStatus = HealthStatus.HEALTHY
    health_score: float = 100.0
    metrics: RequestMetrics = field(default_factory=RequestMetrics)
    last_health_check: Optional[float] = None
    consecutive_failures: int = 0


@dataclass
class FallbackStrategy:
    """降级策略"""
    name: str
    error_types: List[ErrorType]
    fallback_func: Callable
    priority: int = 0


# =============================================================================
# 重试器 (Retrier)
# =============================================================================

class Retrier:
    """
    重试器 - 实现指数退避重试机制
    """
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self._retryable_exceptions: List[Type[Exception]] = []
    
    def register_retryable_exception(self, exception_type: Type[Exception]):
        """注册可重试的异常类型"""
        if exception_type not in self._retryable_exceptions:
            self._retryable_exceptions.append(exception_type)
    
    def should_retry(self, exception: Exception) -> bool:
        """判断是否应该重试"""
        return any(isinstance(exception, exc_type) 
                  for exc_type in self._retryable_exceptions)
    
    def calculate_delay(self, attempt: int) -> float:
        """
        计算第N次重试的延迟时间（指数退避 + 抖动）
        """
        delay = self.config.base_delay * (self.config.backoff_factor ** attempt)
        delay = min(delay, self.config.max_delay)
        
        if self.config.jitter:
            jitter_amount = delay * self.config.jitter_range
            delay += random.uniform(-jitter_amount, jitter_amount)
            delay = max(delay, self.config.base_delay * 0.5)
        
        return delay
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        执行函数，失败时自动重试
        """
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if not self.should_retry(e):
                    logger.warning(f"不可重试的异常: {e}")
                    raise
                
                if attempt < self.config.max_attempts - 1:
                    delay = self.calculate_delay(attempt)
                    logger.warning(
                        f"尝试 {attempt + 1}/{self.config.max_attempts} 失败: {e}. "
                        f"{delay:.2f}秒后重试..."
                    )
                    time.sleep(delay)
                else:
                    logger.error(f"所有重试都失败了: {e}")
        
        raise RetryError(f"重试 {self.config.max_attempts} 次后仍然失败") from last_exception
    
    def __call__(self, func: Callable) -> Callable:
        """装饰器支持"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.execute(func, *args, **kwargs)
        return wrapper


# =============================================================================
# 熔断器 (CircuitBreaker)
# =============================================================================

class CircuitBreaker:
    """
    熔断器 - 实现熔断机制，避免级联失败
    """
    
    def __init__(
        self,
        config: Optional[CircuitBreakerConfig] = None,
        name: str = "default"
    ):
        self.config = config or CircuitBreakerConfig()
        self.name = name
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._half_open_calls = 0
        self._last_failure_time: Optional[float] = None
        self._last_state_change_time = time.time()
        self._request_window: deque = deque()  # 存储 (timestamp, is_success)
        self._lock = threading.RLock()
    
    @property
    def state(self) -> CircuitState:
        return self._state
    
    def _update_state(self, new_state: CircuitState):
        """更新熔断器状态"""
        with self._lock:
            if self._state != new_state:
                logger.warning(
                    f"熔断器 '{self.name}' 状态变更: {self._state.value} -> {new_state.value}"
                )
                self._state = new_state
                self._last_state_change_time = time.time()
                
                if new_state == CircuitState.HALF_OPEN:
                    self._half_open_calls = 0
    
    def _cleanup_old_requests(self):
        """清理时间窗口外的旧请求"""
        now = time.time()
        cutoff = now - self.config.window_size
        
        while self._request_window and self._request_window[0][0] < cutoff:
            self._request_window.popleft()
    
    def _calculate_failure_rate(self) -> float:
        """计算失败率"""
        self._cleanup_old_requests()
        
        if len(self._request_window) < self.config.min_requests:
            return 0.0
        
        total = len(self._request_window)
        failures = sum(1 for ts, is_success in self._request_window if not is_success)
        return failures / total
    
    def on_success(self):
        """记录成功"""
        with self._lock:
            now = time.time()
            self._request_window.append((now, True))
            self._success_count += 1
            
            if self._state == CircuitState.HALF_OPEN:
                self._half_open_calls += 1
                failure_rate = self._calculate_failure_rate()
                
                if failure_rate < self.config.failure_threshold:
                    self._update_state(CircuitState.CLOSED)
                    self._failure_count = 0
    
    def on_failure(self, exception: Optional[Exception] = None):
        """记录失败"""
        with self._lock:
            now = time.time()
            self._request_window.append((now, False))
            self._failure_count += 1
            self._last_failure_time = now
            
            if self._state == CircuitState.CLOSED:
                failure_rate = self._calculate_failure_rate()
                if failure_rate >= self.config.failure_threshold:
                    self._update_state(CircuitState.OPEN)
            
            elif self._state == CircuitState.HALF_OPEN:
                self._update_state(CircuitState.OPEN)
    
    def _check_state_transition(self):
        """检查是否需要状态转换"""
        if self._state == CircuitState.OPEN:
            if (self._last_failure_time and 
                time.time() - self._last_failure_time >= self.config.recovery_timeout):
                self._update_state(CircuitState.HALF_OPEN)
    
    def can_execute(self) -> bool:
        """判断是否可以执行请求"""
        with self._lock:
            self._check_state_transition()
            
            if self._state == CircuitState.CLOSED:
                return True
            elif self._state == CircuitState.HALF_OPEN:
                if self._half_open_calls < self.config.half_open_max_calls:
                    return True
                return False
            else:  # OPEN
                return False
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        执行函数，熔断器保护
        """
        if not self.can_execute():
            raise CircuitOpenError(
                f"熔断器 '{self.name}' 处于 {self._state.value} 状态，请求被拒绝"
            )
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure(e)
            raise
    
    def __call__(self, func: Callable) -> Callable:
        """装饰器支持"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.execute(func, *args, **kwargs)
        return wrapper
    
    def reset(self):
        """重置熔断器到初始状态"""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._half_open_calls = 0
            self._last_failure_time = None
            self._request_window.clear()
            logger.info(f"熔断器 '{self.name}' 已重置")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            self._cleanup_old_requests()
            return {
                "name": self.name,
                "state": self._state.value,
                "failure_rate": self._calculate_failure_rate(),
                "total_requests": len(self._request_window),
                "success_count": self._success_count,
                "failure_count": self._failure_count,
                "last_state_change": self._last_state_change_time
            }


# =============================================================================
# 降级管理器 (FallbackManager)
# =============================================================================

class FallbackManager:
    """
    降级管理器 - 管理多种降级策略
    """
    
    def __init__(self):
        self._strategies: List[FallbackStrategy] = []
        self._default_fallback: Optional[Callable] = None
    
    def register_strategy(self, strategy: FallbackStrategy):
        """注册降级策略"""
        self._strategies.append(strategy)
        self._strategies.sort(key=lambda s: s.priority, reverse=True)
    
    def set_default_fallback(self, func: Callable):
        """设置默认降级函数"""
        self._default_fallback = func
    
    def get_fallback(
        self,
        error_type: ErrorType,
        context: Optional[Dict] = None
    ) -> Optional[Callable]:
        """获取合适的降级函数"""
        for strategy in self._strategies:
            if error_type in strategy.error_types:
                return strategy.fallback_func
        return self._default_fallback
    
    def execute_fallback(
        self,
        error_type: ErrorType,
        context: Optional[Dict] = None,
        *args,
        **kwargs
    ) -> Any:
        """执行降级"""
        fallback = self.get_fallback(error_type, context)
        if fallback:
            try:
                return fallback(*args, **kwargs)
            except Exception as e:
                logger.error(f"降级执行失败: {e}")
                raise FallbackError(f"降级失败: {e}") from e
        raise FallbackError(f"没有找到适用于 {error_type.value} 的降级策略")


# =============================================================================
# 健康检查器 (HealthChecker)
# =============================================================================

class HealthChecker:
    """
    健康检查器 - 监控模型健康状态
    """
    
    def __init__(self, config: Optional[HealthCheckConfig] = None):
        self.config = config or HealthCheckConfig()
        self._models: Dict[str, ModelHealth] = {}
        self._lock = threading.RLock()
        self._running = False
        self._check_thread: Optional[threading.Thread] = None
    
    def register_model(self, model_id: str, config: ModelConfig):
        """注册模型"""
        with self._lock:
            self._models[model_id] = ModelHealth(
                model_id=model_id,
                config=config
            )
            logger.info(f"注册模型: {model_id}")
    
    def _calculate_health_score(self, model_health: ModelHealth) -> float:
        """
        计算健康评分（0-100）
        综合考虑成功率、延迟、错误率等因素
        """
        metrics = model_health.metrics
        total_requests = metrics.success_count + metrics.failure_count
        
        if total_requests == 0:
            return 100.0
        
        # 成功率权重: 40%
        success_rate = metrics.success_count / total_requests
        success_score = success_rate * 40
        
        # 延迟权重: 30% (根据P95延迟计算)
        latency_score = 30.0
        if metrics.latency_samples:
            sorted_latencies = sorted(metrics.latency_samples)
            p95_index = int(len(sorted_latencies) * 0.95)
            p95_latency = sorted_latencies[min(p95_index, len(sorted_latencies) - 1)]
            
            # 假设理想延迟 < 2秒，超过10秒得0分
            if p95_latency < 2:
                latency_score = 30
            elif p95_latency > 10:
                latency_score = 0
            else:
                latency_score = 30 * (1 - (p95_latency - 2) / 8)
        
        # 错误类型权重: 20%
        error_score = 20.0
        rate_limit_count = metrics.error_counts.get(ErrorType.RATE_LIMIT, 0)
        server_error_count = metrics.error_counts.get(ErrorType.SERVER_ERROR, 0)
        if rate_limit_count > 0 or server_error_count > 0:
            error_penalty = min((rate_limit_count + server_error_count) / total_requests, 1.0)
            error_score = 20 * (1 - error_penalty)
        
        # 连续失败惩罚: 10%
        consecutive_score = 10.0
        if model_health.consecutive_failures >= 3:
            consecutive_score = max(0, 10 - model_health.consecutive_failures * 2)
        
        total_score = success_score + latency_score + error_score + consecutive_score
        return max(0, min(100, total_score))
    
    def _update_health_status(self, model_health: ModelHealth):
        """更新健康状态"""
        score = model_health.health_score
        
        if score >= self.config.degraded_threshold:
            new_status = HealthStatus.HEALTHY
        elif score >= self.config.unhealthy_threshold:
            new_status = HealthStatus.DEGRADED
        else:
            new_status = HealthStatus.UNHEALTHY
        
        if model_health.status != new_status:
            logger.warning(
                f"模型 {model_health.model_id} 健康状态变更: "
                f"{model_health.status.value} -> {new_status.value} "
                f"(评分: {score:.1f})"
            )
            model_health.status = new_status
    
    def record_request(
        self,
        model_id: str,
        success: bool,
        latency: float,
        error_type: Optional[ErrorType] = None
    ):
        """记录请求结果"""
        with self._lock:
            if model_id not in self._models:
                return
            
            model_health = self._models[model_id]
            metrics = model_health.metrics
            
            metrics.last_request_time = time.time()
            metrics.total_latency += latency
            metrics.latency_samples.append(latency)
            
            # 保留最近1000个延迟样本
            if len(metrics.latency_samples) > 1000:
                metrics.latency_samples = metrics.latency_samples[-1000:]
            
            if success:
                metrics.success_count += 1
                model_health.consecutive_failures = 0
            else:
                metrics.failure_count += 1
                model_health.consecutive_failures += 1
                if error_type:
                    metrics.error_counts[error_type] = metrics.error_counts.get(error_type, 0) + 1
            
            # 重新计算健康评分
            model_health.health_score = self._calculate_health_score(model_health)
            self._update_health_status(model_health)
    
    def get_health_score(self, model_id: str) -> float:
        """获取健康评分"""
        with self._lock:
            if model_id in self._models:
                return self._models[model_id].health_score
            return 0.0
    
    def get_health_status(self, model_id: str) -> HealthStatus:
        """获取健康状态"""
        with self._lock:
            if model_id in self._models:
                return self._models[model_id].status
            return HealthStatus.UNHEALTHY
    
    def get_healthy_models(self) -> List[str]:
        """获取所有健康模型列表"""
        with self._lock:
            return [
                model_id for model_id, health in self._models.items()
                if health.status == HealthStatus.HEALTHY
            ]
    
    def get_model_health(self, model_id: str) -> Optional[ModelHealth]:
        """获取模型健康详情"""
        with self._lock:
            return self._models.get(model_id)
    
    def get_all_models_health(self) -> Dict[str, ModelHealth]:
        """获取所有模型健康状态"""
        with self._lock:
            return dict(self._models)
    
    def reset_metrics(self, model_id: Optional[str] = None):
        """重置指标"""
        with self._lock:
            if model_id:
                if model_id in self._models:
                    self._models[model_id].metrics = RequestMetrics()
                    self._models[model_id].consecutive_failures = 0
                    self._models[model_id].health_score = 100.0
                    self._models[model_id].status = HealthStatus.HEALTHY
            else:
                for mid in self._models:
                    self.reset_metrics(mid)
    
    def start_background_check(self):
        """启动后台健康检查"""
        if self._running:
            return
        
        self._running = True
        self._check_thread = threading.Thread(
            target=self._background_check_loop,
            daemon=True
        )
        self._check_thread.start()
        logger.info("后台健康检查已启动")
    
    def stop_background_check(self):
        """停止后台健康检查"""
        self._running = False
        if self._check_thread:
            self._check_thread.join(timeout=5.0)
        logger.info("后台健康检查已停止")
    
    def _background_check_loop(self):
        """后台检查循环"""
        while self._running:
            try:
                # 这里可以实现主动健康检查逻辑
                # 例如发送探测请求到各模型
                time.sleep(self.config.check_interval)
            except Exception as e:
                logger.error(f"后台健康检查出错: {e}")
                time.sleep(self.config.check_interval)


# =============================================================================
# 故障转移器 (FailoverManager)
# =============================================================================

class FailoverManager:
    """
    故障转移管理器 - 管理模型池和自动故障转移
    """
    
    def __init__(self, health_checker: Optional[HealthChecker] = None):
        self.health_checker = health_checker or HealthChecker()
        self._model_pools: Dict[str, List[str]] = {}  # 池子名 -> 模型ID列表
        self._current_model: Optional[str] = None
        self._lock = threading.RLock()
        self._failover_count = 0
    
    def register_model_pool(self, pool_name: str, model_ids: List[str]):
        """注册模型池"""
        with self._lock:
            self._model_pools[pool_name] = model_ids
            logger.info(f"注册模型池 '{pool_name}': {model_ids}")
    
    def register_model(self, model_config: ModelConfig, pool_name: str = "default"):
        """注册单个模型"""
        self.health_checker.register_model(model_config.model_id, model_config)
        
        with self._lock:
            if pool_name not in self._model_pools:
                self._model_pools[pool_name] = []
            if model_config.model_id not in self._model_pools[pool_name]:
                self._model_pools[pool_name].append(model_config.model_id)
                # 按优先级排序
                pool_models = self._model_pools[pool_name]
                pool_models.sort(key=lambda mid: (
                    -self._get_model_priority(mid),
                    self._is_model_primary(mid)
                ), reverse=True)
    
    def _get_model_priority(self, model_id: str) -> int:
        """获取模型优先级"""
        health = self.health_checker.get_model_health(model_id)
        return health.config.priority if health else 0
    
    def _is_model_primary(self, model_id: str) -> bool:
        """判断是否为主模型"""
        health = self.health_checker.get_model_health(model_id)
        return health.config.is_primary if health else False
    
    def _select_best_model(self, pool_name: str = "default") -> Optional[str]:
        """选择最优模型"""
        with self._lock:
            if pool_name not in self._model_pools:
                return None
            
            pool_models = self._model_pools[pool_name]
            healthy_models = self.health_checker.get_healthy_models()
            
            # 优先选择健康的、高优先级的模型
            candidates = []
            for model_id in pool_models:
                if model_id in healthy_models:
                    score = self.health_checker.get_health_score(model_id)
                    priority = self._get_model_priority(model_id)
                    is_primary = self._is_model_primary(model_id)
                    candidates.append((
                        -priority,  # 优先级高的排前面（负号用于升序排列）
                        -int(is_primary),  # 主模型排前面
                        -score,  # 评分高的排前面
                        model_id
                    ))
            
            if candidates:
                candidates.sort()
                return candidates[0][3]
            
            # 如果没有健康模型，尝试降级状态的模型
            for model_id in pool_models:
                status = self.health_checker.get_health_status(model_id)
                if status == HealthStatus.DEGRADED:
                    logger.warning(f"使用降级状态的模型: {model_id}")
                    return model_id
            
            return None
    
    def select_model(self, pool_name: str = "default") -> str:
        """选择模型"""
        with self._lock:
            model_id = self._select_best_model(pool_name)
            if not model_id:
                raise NoHealthyModelError(f"模型池 '{pool_name}' 中没有可用的模型")
            
            self._current_model = model_id
            return model_id
    
    def failover(self, pool_name: str = "default") -> str:
        """执行故障转移"""
        with self._lock:
            old_model = self._current_model
            new_model = self._select_best_model(pool_name)
            
            if not new_model:
                raise NoHealthyModelError(f"故障转移失败: 没有可用的备用模型")
            
            if new_model != old_model:
                self._failover_count += 1
                self._current_model = new_model
                logger.warning(
                    f"故障转移: {old_model} -> {new_model} "
                    f"(累计故障转移次数: {self._failover_count})"
                )
            
            return new_model
    
    def on_model_failure(
        self,
        model_id: str,
        error_type: ErrorType,
        latency: float
    ):
        """记录模型失败"""
        self.health_checker.record_request(model_id, False, latency, error_type)
    
    def on_model_success(self, model_id: str, latency: float):
        """记录模型成功"""
        self.health_checker.record_request(model_id, True, latency)
    
    @property
    def current_model(self) -> Optional[str]:
        return self._current_model
    
    @property
    def failover_count(self) -> int:
        return self._failover_count
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            return {
                "current_model": self._current_model,
                "failover_count": self._failover_count,
                "model_pools": dict(self._model_pools),
                "models_health": {
                    mid: {
                        "status": h.status.value,
                        "score": h.health_score
                    }
                    for mid, h in self.health_checker.get_all_models_health().items()
                }
            }


# =============================================================================
# 智能客户端 (SmartClient)
# =============================================================================

class SmartClient:
    """
    智能客户端 - 整合所有容错机制的统一客户端
    """
    
    def __init__(
        self,
        retrier: Optional[Retrier] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        fallback_manager: Optional[FallbackManager] = None,
        failover_manager: Optional[FailoverManager] = None
    ):
        self.retrier = retrier or Retrier()
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self.fallback_manager = fallback_manager or FallbackManager()
        self.failover_manager = failover_manager or FailoverManager()
        
        # 注册默认的可重试异常
        self.retrier.register_retryable_exception(TimeoutError)
        self.retrier.register_retryable_exception(ConnectionError)
    
    def execute(
        self,
        func: Callable,
        model_id: Optional[str] = None,
        pool_name: str = "default",
        use_retries: bool = True,
        use_circuit_breaker: bool = True,
        use_failover: bool = True,
        fallback_context: Optional[Dict] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        执行请求，应用所有容错机制
        """
        start_time = time.time()
        current_model = model_id
        
        if not current_model and use_failover:
            current_model = self.failover_manager.select_model(pool_name)
        
        error_type: Optional[ErrorType] = None
        
        try:
            def wrapped_func():
                return func(*args, **kwargs)
            
            if use_circuit_breaker:
                wrapped_func = self.circuit_breaker(wrapped_func)
            
            if use_retries:
                wrapped_func = self.retrier(wrapped_func)
            
            result = wrapped_func()
            
            latency = time.time() - start_time
            if current_model:
                self.failover_manager.on_model_success(current_model, latency)
            
            return result
            
        except CircuitOpenError:
            error_type = ErrorType.UNKNOWN
            logger.error("熔断器打开，请求被拒绝")
            
            if use_failover:
                try:
                    current_model = self.failover_manager.failover(pool_name)
                    # 使用新模型重试
                    return self.execute(
                        func, current_model, pool_name,
                        use_retries=False, use_circuit_breaker=False,
                        use_failover=False, *args, **kwargs
                    )
                except Exception as e:
                    logger.error(f"故障转移后仍然失败: {e}")
            
            raise
            
        except TimeoutError as e:
            error_type = ErrorType.TIMEOUT
            logger.error(f"请求超时: {e}")
            
        except ConnectionError as e:
            error_type = ErrorType.NETWORK
            logger.error(f"网络错误: {e}")
            
        except Exception as e:
            error_type = ErrorType.UNKNOWN
            logger.error(f"请求失败: {e}")
            
        finally:
            latency = time.time() - start_time
            if current_model and error_type:
                self.failover_manager.on_model_failure(current_model, error_type, latency)
        
        # 尝试降级
        if error_type:
            try:
                return self.fallback_manager.execute_fallback(
                    error_type, fallback_context, *args, **kwargs
                )
            except FallbackError:
                pass
        
        # 如果配置了故障转移，尝试切换模型
        if use_failover and error_type in [ErrorType.TIMEOUT, ErrorType.NETWORK, ErrorType.SERVER_ERROR]:
            try:
                current_model = self.failover_manager.failover(pool_name)
                return self.execute(
                    func, current_model, pool_name,
                    use_retries=False, use_circuit_breaker=False,
                    use_failover=False, *args, **kwargs
                )
            except Exception as e:
                logger.error(f"故障转移后仍然失败: {e}")
        
        raise


# =============================================================================
# 工具函数
# =============================================================================

def classify_error(exception: Exception) -> ErrorType:
    """分类错误类型"""
    exc_str = str(exception).lower()
    
    if isinstance(exception, TimeoutError):
        return ErrorType.TIMEOUT
    elif isinstance(exception, ConnectionError):
        return ErrorType.NETWORK
    elif "429" in exc_str or "rate limit" in exc_str or "too many requests" in exc_str:
        return ErrorType.RATE_LIMIT
    elif "500" in exc_str or "502" in exc_str or "503" in exc_str or "server error" in exc_str:
        return ErrorType.SERVER_ERROR
    elif "400" in exc_str or "401" in exc_str or "403" in exc_str or "404" in exc_str:
        return ErrorType.CLIENT_ERROR
    else:
        return ErrorType.UNKNOWN


# =============================================================================
# 便捷装饰器
# =============================================================================

def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    retryable_exceptions: Optional[List[Type[Exception]]] = None
):
    """
    重试装饰器
    """
    def decorator(func: Callable):
        config = RetryConfig(max_attempts=max_attempts, base_delay=base_delay)
        retrier = Retrier(config)
        
        if retryable_exceptions:
            for exc_type in retryable_exceptions:
                retrier.register_retryable_exception(exc_type)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return retrier.execute(func, *args, **kwargs)
        return wrapper
    return decorator


def with_circuit_breaker(
    name: str = "default",
    failure_threshold: float = 0.5,
    recovery_timeout: float = 30.0
):
    """
    熔断器装饰器
    """
    def decorator(func: Callable):
        config = CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout
        )
        breaker = CircuitBreaker(config, name)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.execute(func, *args, **kwargs)
        return wrapper
    return decorator


def with_circuit_breaker(
    name: str = "default",
    failure_threshold: float = 0.5,
    recovery_timeout: float = 30.0
):
    """
    熔断器装饰器
    """
    def decorator(func: Callable):
        config = CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout
        )
        breaker = CircuitBreaker(config, name)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.execute(func, *args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# 主函数（示例）
# =============================================================================

def main():
    """示例用法"""
    print("=" * 60)
    print("多模型协作系统 - 故障处理与容错机制 示例")
    print("=" * 60)
    
    # 1. 创建各个组件
    print("\n1. 初始化组件...")
    
    retrier = Retrier(RetryConfig(max_attempts=3, base_delay=1.0))
    circuit_breaker = CircuitBreaker(
        CircuitBreakerConfig(failure_threshold=0.5, recovery_timeout=10.0),
        "model_gateway"
    )
    fallback_manager = FallbackManager()
    failover_manager = FailoverManager()
    
    # 2. 注册模型
    print("\n2. 注册模型...")
    
    models = [
        ModelConfig(model_id="gpt-4", name="GPT-4", priority=3, is_primary=True),
        ModelConfig(model_id="claude-3", name="Claude 3", priority=2),
        ModelConfig(model_id="gpt-3.5", name="GPT-3.5", priority=1),
    ]
    
    for model in models:
        failover_manager.register_model(model, pool_name="llm")
        print(f"   - 已注册: {model.model_id} (优先级: {model.priority})")
    
    # 3. 注册降级策略
    print("\n3. 设置降级策略...")
    
    def cache_fallback(*args, **kwargs):
        return {"type": "cached", "data": "使用缓存数据"}
    
    fallback_manager.register_strategy(FallbackStrategy(
        name="cache_fallback",
        error_types=[ErrorType.NETWORK, ErrorType.TIMEOUT],
        fallback_func=cache_fallback,
        priority=1
    ))
    print("   - 已注册缓存降级策略")
    
    # 4. 创建智能客户端
    print("\n4. 创建智能客户端...")
    smart_client = SmartClient(
        retrier=retrier,
        circuit_breaker=circuit_breaker,
        fallback_manager=fallback_manager,
        failover_manager=failover_manager
    )
    print("   - 智能客户端已创建")
    
    # 5. 模拟一些请求和错误
    print("\n5. 模拟请求...")
    
    # 记录一些成功的请求
    for i in range(3):
        model_id = failover_manager.select_model("llm")
        failover_manager.on_model_success(model_id, latency=1.5 + random.random())
        print(f"   - 请求 {i+1}: {model_id} 成功")
    
    # 显示状态
    print("\n6. 当前状态:")
    stats = failover_manager.get_stats()
    print(f"   - 当前模型: {stats['current_model']}")
    print(f"   - 故障转移次数: {stats['failover_count']}")
    print(f"   - 模型健康状态:")
    for mid, health in stats['models_health'].items():
        print(f"     {mid}: {health['status']} (评分: {health['score']:.1f})")
    
    print("\n" + "=" * 60)
    print("示例演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()