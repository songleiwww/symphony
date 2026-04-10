#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统v3.2.0 - 容灾模块升级
引入降级与熔断机制
"""
import asyncio
import time
import json
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
from threading import Lock

class CircuitState(Enum):
    """熔断状态"""
    CLOSED = "closed"       # 正常
    OPEN = "open"           # 熔断
    HALF_OPEN = "half_open"  # 半开

class ServiceHealth(Enum):
    """服务健康状态"""
    HEALTHY = "healthy"     # 健康
    DEGRADED = "degraded"   # 降级
    UNHEALTHY = "unhealthy" # 不健康

@dataclass
class HealthMetric:
    """健康指标"""
    timestamp: float
    latency: float          # 延迟(毫秒)
    success: bool          # 是否成功
    error_type: Optional[str] = None

@dataclass
class ServiceConfig:
    """服务配置"""
    service_name: str
    timeout: float = 30.0           # 超时时间
    max_retries: int = 3            # 最大重试次数
    fallback_func: Optional[Callable] = None
    critical: bool = False           # 是否关键服务

class CircuitBreaker:
    """熔断器"""
    
    def __init__(self, service_name: str, 
                 failure_threshold: int = 5,
                 success_threshold: int = 2,
                 timeout: float = 60.0):
        self.service_name = service_name
        self.failure_threshold = failure_threshold  # 失败次数阈值
        self.success_threshold = success_threshold  # 成功次数阈值
        self.timeout = timeout  # 熔断超时
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.total_requests = 0
        self.total_failures = 0
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        调用函数（带熔断）
        
        Args:
            func: 要调用的函数
            *args, **kwargs: 函数参数
        
        Returns:
            函数返回值
        
        Raises:
            Exception: 熔断时抛出异常
        """
        self.total_requests += 1
        
        # 检查熔断状态
        if self.state == CircuitState.OPEN:
            # 检查是否应该进入半开状态
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise Exception(f"熔断器打开，服务{self.service_name}暂时不可用")
        
        try:
            # 执行函数
            result = func(*args, **kwargs)
            
            # 记录成功
            self._on_success()
            
            return result
            
        except Exception as e:
            # 记录失败
            self._on_failure()
            raise e
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """异步调用"""
        self.total_requests += 1
        
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise Exception(f"熔断器打开，服务{self.service_name}暂时不可用")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """成功处理"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                print(f"[熔断] {self.service_name} 恢复关闭")
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0
    
    def _on_failure(self):
        """失败处理"""
        self.failure_count += 1
        self.total_failures += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            print(f"[熔断] {self.service_name} 打开熔断")
    
    def get_state(self) -> Dict:
        """获取状态"""
        return {
            "service": self.service_name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "total_requests": self.total_requests,
            "total_failures": self.total_failures,
            "failure_rate": f"{self.total_failures/self.total_requests*100:.2f}%" 
                          if self.total_requests > 0 else "0%"
        }

class DegradationManager:
    """降级管理器"""
    
    def __init__(self):
        self.service_configs: Dict[str, ServiceConfig] = {}
        self.degradation_levels: Dict[str, int] = {}  # 服务 -> 降级级别
        self.fallback_handlers: Dict[str, Callable] = {}
    
    def register_service(self, config: ServiceConfig):
        """注册服务"""
        self.service_configs[config.service_name] = config
        self.degradation_levels[config.service_name] = 0
        print(f"[降级] 注册服务: {config.service_name}")
    
    def register_fallback(self, service_name: str, fallback_func: Callable):
        """注册降级处理函数"""
        self.fallback_handlers[service_name] = fallback_func
    
    def degrade(self, service_name: str, level: int = 1):
        """
        降级服务
        
        Args:
            service_name: 服务名
            level: 降级级别
        """
        if service_name not in self.degradation_levels:
            return
        
        old_level = self.degradation_levels[service_name]
        self.degradation_levels[service_name] = level
        
        print(f"[降级] {service_name}: {old_level}级 -> {level}级")
    
    def recover(self, service_name: str):
        """恢复服务"""
        if service_name not in self.degradation_levels:
            return
        
        self.degradation_levels[service_name] = 0
        print(f"[降级] {service_name} 已恢复正常")
    
    def get_fallback(self, service_name: str, *args, **kwargs) -> Any:
        """获取降级处理"""
        fallback = self.fallback_handlers.get(service_name)
        
        if fallback:
            print(f"[降级] 调用降级处理: {service_name}")
            return fallback(*args, **kwargs)
        
        # 默认降级处理
        return self._default_fallback(service_name)
    
    def _default_fallback(self, service_name: str) -> Any:
        """默认降级处理"""
        config = self.service_configs.get(service_name)
        
        if config and config.critical:
            # 关键服务抛出异常
            raise Exception(f"关键服务{service_name}降级失败")
        
        # 非关键服务返回默认响应
        return {
            "status": "degraded",
            "service": service_name,
            "message": f"服务{service_name}当前降级运行",
            "data": None
        }
    
    def get_degradation_status(self) -> Dict:
        """获取降级状态"""
        return {
            service: level 
            for service, level in self.degradation_levels.items()
        }

class RateLimiter:
    """限流器"""
    
    def __init__(self, max_requests: int, time_window: float = 60.0):
        self.max_requests = max_requests
        self.time_window = time_window
        
        self.requests = deque()
        self.total_requests = 0
        self.total_rejected = 0
        self.lock = Lock()
    
    def acquire(self) -> bool:
        """
        获取限流令牌
        
        Returns:
            是否允许请求
        """
        with self.lock:
            now = time.time()
            
            # 清理过期的请求记录
            while self.requests and self.requests[0] < now - self.time_window:
                self.requests.popleft()
            
            # 检查是否超过限制
            if len(self.requests) >= self.max_requests:
                self.total_rejected += 1
                return False
            
            # 记录请求
            self.requests.append(now)
            self.total_requests += 1
            
            return True
    
    def get_status(self) -> Dict:
        """获取限流状态"""
        with self.lock:
            now = time.time()
            current = sum(1 for r in self.requests if r > now - self.time_window)
            
            return {
                "current_requests": current,
                "max_requests": self.max_requests,
                "total_requests": self.total_requests,
                "total_rejected": self.total_rejected,
                "rejection_rate": f"{self.total_rejected/self.total_requests*100:.2f}%"
                                if self.total_requests > 0 else "0%"
            }

class HealthMonitor:
    """健康监控器"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metrics: Dict[str, deque] = {}
        self.lock = Lock()
    
    def record(self, service_name: str, metric: HealthMetric):
        """记录健康指标"""
        if service_name not in self.metrics:
            self.metrics[service_name] = deque(maxlen=self.window_size)
        
        self.metrics[service_name].append(metric)
    
    def get_health(self, service_name: str) -> ServiceHealth:
        """获取服务健康状态"""
        if service_name not in self.metrics:
            return ServiceHealth.UNHEALTHY
        
        metrics = list(self.metrics[service_name])
        
        if not metrics:
            return ServiceHealth.UNHEALTHY
        
        # 计算健康指标
        total = len(metrics)
        successes = sum(1 for m in metrics if m.success)
        success_rate = successes / total
        
        latencies = [m.latency for m in metrics]
        avg_latency = sum(latencies) / len(latencies)
        
        # 判断健康状态
        if success_rate >= 0.95 and avg_latency < 100:
            return ServiceHealth.HEALTHY
        elif success_rate >= 0.8:
            return ServiceHealth.DEGRADED
        else:
            return ServiceHealth.UNHEALTHY
    
    def get_metrics(self, service_name: str) -> Dict:
        """获取指标详情"""
        if service_name not in self.metrics:
            return {}
        
        metrics = list(self.metrics[service_name])
        
        if not metrics:
            return {}
        
        successes = [m for m in metrics if m.success]
        failures = [m for m in metrics if not m.success]
        
        latencies = [m.latency for m in metrics]
        
        return {
            "total_requests": len(metrics),
            "success_count": len(successes),
            "failure_count": len(failures),
            "success_rate": f"{len(successes)/len(metrics)*100:.2f}%",
            "avg_latency": f"{sum(latencies)/len(latencies):.2f}ms",
            "max_latency": f"{max(latencies):.2f}ms"
        }

class DisasterRecoveryManager:
    """灾难恢复管理器"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.degradation_manager = DegradationManager()
        self.rate_limiter = RateLimiter(max_requests=100, time_window=60)
        self.health_monitor = HealthMonitor()
    
    def register_service(self, service_name: str, 
                       failure_threshold: int = 5,
                       is_critical: bool = False):
        """注册服务"""
        # 创建熔断器
        breaker = CircuitBreaker(
            service_name,
            failure_threshold=failure_threshold
        )
        self.circuit_breakers[service_name] = breaker
        
        # 注册到降级管理器
        config = ServiceConfig(
            service_name=service_name,
            critical=is_critical
        )
        self.degradation_manager.register_service(config)
    
    def register_fallback(self, service_name: str, fallback_func: Callable):
        """注册降级处理"""
        self.degradation_manager.register_fallback(service_name, fallback_func)
    
    async def execute(self, service_name: str, 
                    func: Callable, *args, **kwargs) -> Any:
        """
        执行服务调用
        
        Args:
            service_name: 服务名
            func: 要调用的函数
            *args, **kwargs: 函数参数
        
        Returns:
            执行结果
        """
        # 1. 限流检查
        if not self.rate_limiter.acquire():
            print(f"[限流] 服务{service_name}请求被限流")
            return self.degradation_manager.get_fallback(service_name)
        
        # 2. 获取熔断器
        breaker = self.circuit_breakers.get(service_name)
        
        if not breaker:
            # 未注册的服务的直接调用
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                return self.degradation_manager.get_fallback(service_name)
        
        # 3. 熔断器调用
        start_time = time.time()
        success = False
        error_type = None
        
        try:
            result = await breaker.call_async(func, *args, **kwargs)
            success = True
            return result
            
        except Exception as e:
            error_type = type(e).__name__
            print(f"[错误] 服务{service_name}: {str(e)}")
            
            # 调用降级处理
            return self.degradation_manager.get_fallback(service_name)
            
        finally:
            # 4. 记录健康指标
            latency = (time.time() - start_time) * 1000  # 转换为毫秒
            metric = HealthMetric(
                timestamp=time.time(),
                latency=latency,
                success=success,
                error_type=error_type
            )
            self.health_monitor.record(service_name, metric)
            
            # 5. 检查健康状态，自动降级
            health = self.health_monitor.get_health(service_name)
            if health == ServiceHealth.DEGRADED:
                self.degradation_manager.degrade(service_name, level=1)
            elif health == ServiceHealth.UNHEALTHY:
                self.degradation_manager.degrade(service_name, level=2)
    
    def get_status(self) -> Dict:
        """获取容灾状态"""
        return {
            "circuit_breakers": {
                name: breaker.get_state() 
                for name, breaker in self.circuit_breakers.items()
            },
            "degradation": self.degradation_manager.get_degradation_status(),
            "rate_limiter": self.rate_limiter.get_status(),
            "health": {
                name: self.health_monitor.get_health(name).value
                for name in self.health_monitor.metrics.keys()
            }
        }


# 测试代码
if __name__ == "__main__":
    async def test_service():
        """测试服务"""
        await asyncio.sleep(0.1)
        return {"data": "success"}
    
    async def main():
        # 创建容灾管理器
        recovery = DisasterRecoveryManager()
        
        # 注册服务
        recovery.register_service("model_api", failure_threshold=3, is_critical=True)
        recovery.register_service("search_api", failure_threshold=5)
        
        # 注册降级处理
        recovery.register_fallback("model_api", lambda: {"status": "fallback", "data": None})
        
        # 执行测试
        for i in range(10):
            result = await recovery.execute("model_api", test_service)
            print(f"请求{i+1}: {result}")
        
        # 获取状态
        print("\n=== 容灾状态 ===")
        status = recovery.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    
    asyncio.run(main())
