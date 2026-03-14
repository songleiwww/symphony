#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型管理器 - 真实模型调用版本
使用 real_model_caller.py 进行真实模型调用
"""

import time
import logging
import threading
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta

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

try:
    from real_model_caller import RealModelCaller, ModelCallResult
    REAL_MODEL_AVAILABLE = True
except ImportError:
    print("⚠️  real_model_caller.py 未找到，使用模拟调用")
    REAL_MODEL_AVAILABLE = False


# =============================================================================
# 枚举定义
# =============================================================================

class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class ModelHealth(Enum):
    """模型健康状态"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ModelStatus(Enum):
    """模型状态"""
    ACTIVE = "active"
    STANDBY = "standby"
    DISABLED = "disabled"
    FAILED = "failed"


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
# 熔断器实现
# =============================================================================

class CircuitBreaker:
    """熔断器"""
    
    def __init__(
        self,
        model_name: str,
        failure_threshold: int = 5,
        failure_window: int = 60,
        recovery_timeout: int = 30,
        half_open_max_calls: int = 2,
        half_open_success_threshold: float = 0.5
    ):
        self.model_name = model_name
        self.failure_threshold = failure_threshold
        self.failure_window = failure_window
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.half_open_success_threshold = half_open_success_threshold
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0
        self.half_open_successes = 0
        self._lock = threading.RLock()
    
    def can_execute(self) -> bool:
        """检查是否可以执行"""
        with self._lock:
            if self.state == CircuitState.CLOSED:
                return True
            elif self.state == CircuitState.OPEN:
                if (self.last_failure_time and 
                    datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)):
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                    self.half_open_successes = 0
                    return True
                return False
            elif self.state == CircuitState.HALF_OPEN:
                return self.half_open_calls < self.half_open_max_calls
            return False
    
    def on_success(self):
        """成功回调"""
        with self._lock:
            if self.state == CircuitState.CLOSED:
                self.failure_count = 0
            elif self.state == CircuitState.HALF_OPEN:
                self.half_open_calls += 1
                self.half_open_successes += 1
                success_rate = self.half_open_successes / self.half_open_calls
                if success_rate >= self.half_open_success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
    
    def on_failure(self, exception: Exception):
        """失败回调"""
        with self._lock:
            self.last_failure_time = datetime.now()
            
            if self.state == CircuitState.CLOSED:
                self.failure_count += 1
                if self.failure_count >= self.failure_threshold:
                    self.state = CircuitState.OPEN
            elif self.state == CircuitState.HALF_OPEN:
                self.half_open_calls += 1
                self.state = CircuitState.OPEN
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取指标"""
        with self._lock:
            return {
                "state": self.state.value,
                "failure_count": self.failure_count,
                "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None
            }
    
    def reset(self):
        """重置"""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.last_failure_time = None
            self.half_open_calls = 0
            self.half_open_successes = 0


# =============================================================================
# 重试策略
# =============================================================================

class RetryPolicy:
    """重试策略"""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_delay: float = 30.0,
        jitter_factor: float = 0.1
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
        self.jitter_factor = jitter_factor
        self.logger = logging.getLogger("RetryPolicy")
    
    def calculate_delay(self, attempt: int) -> float:
        """计算延迟"""
        delay = self.initial_delay * (self.backoff_factor ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter_factor > 0:
            import random
            jitter = random.uniform(-self.jitter_factor, self.jitter_factor)
            delay = delay * (1 + jitter)
        
        return max(delay, 0)
    
    def execute(
        self,
        func: Callable,
        *args,
        retryable_exceptions: Optional[List[type]] = None,
        **kwargs
    ) -> Any:
        """执行函数，失败时自动重试"""
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
# 真实模型包装器
# =============================================================================

class RealModelWrapper:
    """真实模型包装器"""
    
    def __init__(
        self,
        model_config: Dict,
        circuit_breaker: CircuitBreaker,
        retry_policy: RetryPolicy,
        real_caller: Optional[RealModelCaller] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.model_config = model_config
        self.circuit_breaker = circuit_breaker
        self.retry_policy = retry_policy
        self.real_caller = real_caller
        self.logger = logger or logging.getLogger(f"RealModel.{model_config['name']}")
        
        self._status = ModelStatus.STANDBY
        self._health = ModelHealth.UNKNOWN
        self._consecutive_failures = 0
        self._consecutive_successes = 0
        self._lock = threading.RLock()
        
        self.metrics = ModelMetrics()
    
    @property
    def name(self) -> str:
        return self.model_config['name']
    
    @property
    def status(self) -> ModelStatus:
        return self._status
    
    @property
    def health(self) -> ModelHealth:
        return self._health
    
    def is_available(self) -> bool:
        """检查模型是否可用"""
        with self._lock:
            return (
                self.model_config.get('enabled', True) and
                self._status != ModelStatus.DISABLED and
                self._health != ModelHealth.UNHEALTHY
            )
    
    def _update_metrics(self, success: bool, latency: float):
        """更新指标"""
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
        """更新健康状态"""
        with self._lock:
            health_check_config = (
                config.HEALTH_CHECK_CONFIG 
                if hasattr(config, 'HEALTH_CHECK_CONFIG') 
                else {}
            )
            failure_threshold = health_check_config.get('failure_threshold', 3)
            success_threshold = health_check_config.get('success_threshold', 2)
            
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
    
    def call(self, prompt: str) -> ModelCallResult:
        """
        调用真实模型
        
        Args:
            prompt: 提示词
            
        Returns:
            ModelCallResult
        """
        start_time = time.time()
        
        if not self.circuit_breaker.can_execute():
            error_msg = f"熔断器已打开，拒绝请求: {self.name}"
            self.logger.error(error_msg)
            return ModelCallResult(
                success=False,
                model_name=self.model_config['model_id'],
                model_alias=self.model_config['alias'],
                provider=self.model_config['provider'],
                prompt=prompt,
                error=error_msg,
                latency=time.time() - start_time,
                timestamp=datetime.now()
            )
        
        try:
            if self.real_caller and REAL_MODEL_AVAILABLE:
                result = self.retry_policy.execute(
                    self.real_caller.call_model,
                    self.model_config['model_id'],
                    prompt
                )
            else:
                time.sleep(0.5)
                result = ModelCallResult(
                    success=True,
                    model_name=self.model_config['model_id'],
                    model_alias=self.model_config['alias'],
                    provider=self.model_config['provider'],
                    prompt=prompt,
                    response=f"模拟响应: {prompt[:50]}...",
                    latency=time.time() - start_time,
                    timestamp=datetime.now(),
                    prompt_tokens=10,
                    completion_tokens=20,
                    total_tokens=30
                )
            
            latency = time.time() - start_time
            self._update_metrics(True, latency)
            self._update_health(True)
            self.circuit_breaker.on_success()
            
            self.logger.info(
                f"真实模型调用成功: {self.name}, 延迟: {latency:.3f}s"
            )
            
            return result
        
        except Exception as e:
            latency = time.time() - start_time
            self._update_metrics(False, latency)
            self._update_health(False)
            self.circuit_breaker.on_failure(e)
            
            self.logger.error(
                f"真实模型调用失败: {self.name}, 错误: {str(e)}, 延迟: {latency:.3f}s"
            )
            
            return ModelCallResult(
                success=False,
                model_name=self.model_config['model_id'],
                model_alias=self.model_config['alias'],
                provider=self.model_config['provider'],
                prompt=prompt,
                error=str(e),
                latency=latency,
                timestamp=datetime.now()
            )
    
    def set_status(self, status: ModelStatus):
        """设置模型状态"""
        with self._lock:
            old_status = self._status
            self._status = status
            self.logger.info(f"模型状态变更: {self.name}: {old_status.value} -> {status.value}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取模型指标"""
        with self._lock:
            return {
                "name": self.name,
                "model_id": self.model_config['model_id'],
                "alias": self.model_config['alias'],
                "provider": self.model_config['provider'],
                "status": self._status.value,
                "health": self._health.value,
                "enabled": self.model_config.get('enabled', True),
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
# 真实模型管理器
# =============================================================================

class RealModelManager:
    """真实模型管理器"""
    
    def __init__(
        self,
        model_configs: Optional[List[Dict]] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.logger = logger or logging.getLogger("RealModelManager")
        
        if model_configs is None:
            model_configs = config.MODEL_CHAIN if hasattr(config, 'MODEL_CHAIN') else []
        
        self._models: Dict[str, RealModelWrapper] = {}
        self._model_chain: List[str] = []
        self._lock = threading.RLock()
        
        self._health_check_thread: Optional[threading.Thread] = None
        self._health_check_running = False
        self._health_check_interval = (
            config.HEALTH_CHECK_CONFIG.get('check_interval', 30)
            if hasattr(config, 'HEALTH_CHECK_CONFIG') else 30
        )
        
        self.real_caller = None
        if REAL_MODEL_AVAILABLE:
            try:
                self.real_caller = RealModelCaller()
                self.logger.info("✅ 真实模型调用器已初始化")
            except Exception as e:
                self.logger.warning(f"⚠️  真实模型调用器初始化失败: {e}")
        
        self._initialize_models(model_configs)
    
    def _initialize_models(self, model_configs: List[Dict]):
        """初始化模型"""
        cb_config = (
            config.CIRCUIT_BREAKER_CONFIG 
            if hasattr(config, 'CIRCUIT_BREAKER_CONFIG') 
            else {}
        )
        retry_config = (
            config.RETRY_CONFIG 
            if hasattr(config, 'RETRY_CONFIG') 
            else {}
        )
        
        for cfg in model_configs:
            circuit_breaker = CircuitBreaker(
                model_name=cfg['name'],
                failure_threshold=cb_config.get('failure_threshold', 5),
                failure_window=cb_config.get('failure_window', 60),
                recovery_timeout=cb_config.get('recovery_timeout', 30),
                half_open_max_calls=cb_config.get('half_open_max_calls', 2),
                half_open_success_threshold=cb_config.get('half_open_success_threshold', 0.5)
            )
            
            retry_policy = RetryPolicy(
                max_retries=retry_config.get('max_retries', 3),
                initial_delay=retry_config.get('initial_delay', 1.0),
                backoff_factor=retry_config.get('backoff_factor', 2.0),
                max_delay=retry_config.get('max_delay', 30.0),
                jitter_factor=retry_config.get('jitter_factor', 0.1)
            )
            
            model = RealModelWrapper(
                model_config=cfg,
                circuit_breaker=circuit_breaker,
                retry_policy=retry_policy,
                real_caller=self.real_caller
            )
            
            self._models[model.name] = model
            self._model_chain.append(model.name)
            
            self.logger.info(f"✅ 已加载真实模型: {model.name} ({model.model_config['alias']})")
    
    def call_model(self, model_name: str, prompt: str) -> ModelCallResult:
        """调用指定模型"""
        with self._lock:
            if model_name not in self._models:
                return ModelCallResult(
                    success=False,
                    model_name=model_name,
                    model_alias="Unknown",
                    provider="unknown",
                    prompt=prompt,
                    error=f"模型不存在: {model_name}",
                    latency=0.0,
                    timestamp=datetime.now()
                )
            
            model = self._models[model_name]
            return model.call(prompt)
    
    def call_with_fallback(self, prompt: str) -> ModelCallResult:
        """带降级的模型调用"""
        with self._lock:
            tried_models = []
            
            for model_name in self._model_chain:
                model = self._models[model_name]
                
                if model.name in tried_models:
                    continue
                
                tried_models.append(model.name)
                
                if model.is_available():
                    self.logger.info(f"尝试使用真实模型: {model.name}")
                    result = model.call(prompt)
                    
                    if result.success:
                        return result
                    else:
                        self.logger.warning(f"真实模型调用失败: {model.name}，尝试下一个模型")
                        continue
            
            return ModelCallResult(
                success=False,
                model_name="none",
                model_alias="none",
                provider="none",
                prompt=prompt,
                error=f"所有真实模型都已尝试且失败: {tried_models}",
                latency=0.0,
                timestamp=datetime.now()
            )
    
    def start_health_check(self):
        """启动健康检查"""
        if self._health_check_running:
            self.logger.warning("健康检查已在运行中")
            return
        
        self._health_check_running = True
        self._health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True,
            name="RealModelHealthCheck"
        )
        self._health_check_thread.start()
        self.logger.info("✅ 真实模型健康检查已启动")
    
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
                    if model.status != ModelStatus.ACTIVE:
                        model.set_status(ModelStatus.ACTIVE)
                        self.logger.info(f"真实模型切换为活跃: {model_name}")
                    active_found = True
                else:
                    if model.status == ModelStatus.ACTIVE:
                        model.set_status(ModelStatus.STANDBY)
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        with self._lock:
            return {
                "mode": "real_model",
                "total_models": len(self._model_chain),
                "model_chain": self._model_chain,
                "real_caller_available": REAL_MODEL_AVAILABLE,
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
            self.logger.info("所有真实模型已重置")


# =============================================================================
# 主程序
# =============================================================================

def main():
    """主程序"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 80)
    print("🤖 真实模型管理器 - Real Model Manager")
    print("=" * 80)
    
    manager = RealModelManager()
    
    print(f"\n✅ 已加载 {len(manager._model_chain)} 个真实模型")
    
    print("\n📋 状态:")
    status = manager.get_status()
    print(f"   真实调用器: {'✅ 可用' if status['real_caller_available'] else '❌ 不可用'}")
    print(f"   模型数量: {status['total_models']}")
    
    print("\n" + "=" * 80)
    print("测试真实模型调用...")
    print("=" * 80)
    
    result = manager.call_with_fallback("你好，请介绍一下你自己")
    
    if result.success:
        print(f"\n✅ 调用成功!")
        print(f"   模型: {result.model_alias} ({result.provider})")
        print(f"   延迟: {result.latency:.2f}秒")
        print(f"   Token: {result.prompt_tokens}+{result.completion_tokens}={result.total_tokens}")
        print(f"\n📝 响应: {result.response}")
    else:
        print(f"\n❌ 调用失败!")
        print(f"   错误: {result.error}")
    
    print("\n" + "=" * 80)
    print("完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
