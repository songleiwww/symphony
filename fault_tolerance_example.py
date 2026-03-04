#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
故障处理与容错机制 - 实际使用示例
演示如何在多模型协作系统中集成容错机制
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import time
import random
import logging
from typing import Dict, Any, Optional

# 导入我们的容错模块
from fault_tolerance import (
    Retrier, CircuitBreaker, FallbackManager, FailoverManager,
    HealthChecker, SmartClient,
    RetryConfig, CircuitBreakerConfig, TimeoutConfig, HealthCheckConfig,
    ModelConfig, FallbackStrategy, ErrorType,
    with_retry, with_circuit_breaker,
    classify_error,
    CircuitOpenError, NoHealthyModelError
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# 模拟的模型API客户端
# =============================================================================

class MockModelClient:
    """
    模拟的模型API客户端，用于演示容错机制
    """
    
    def __init__(self, model_id: str, failure_rate: float = 0.0, avg_latency: float = 1.0):
        self.model_id = model_id
        self.failure_rate = failure_rate
        self.avg_latency = avg_latency
        self.request_count = 0
    
    def call(self, prompt: str) -> Dict[str, Any]:
        """
        模拟调用模型API
        """
        self.request_count += 1
        time.sleep(self.avg_latency * (0.5 + random.random()))  # 模拟延迟
        
        # 模拟随机失败
        if random.random() < self.failure_rate:
            error_type = random.choice([
                (ErrorType.TIMEOUT, TimeoutError("请求超时")),
                (ErrorType.NETWORK, ConnectionError("网络连接失败")),
                (ErrorType.RATE_LIMIT, Exception("429 Too Many Requests")),
                (ErrorType.SERVER_ERROR, Exception("500 Internal Server Error")),
            ])
            logger.warning(f"模型 {self.model_id} 模拟失败: {error_type[1]}")
            raise error_type[1]
        
        # 成功返回
        return {
            "model": self.model_id,
            "prompt": prompt,
            "response": f"这是来自 {self.model_id} 的响应",
            "timestamp": time.time()
        }


# =============================================================================
# 示例1: 基础使用 - 重试器
# =============================================================================

def example_retry():
    """示例: 使用重试器"""
    print("\n" + "="*70)
    print("示例1: 重试器 (Retrier)")
    print("="*70)
    
    # 创建一个会随机失败的客户端
    client = MockModelClient("test-model", failure_rate=0.4, avg_latency=0.5)
    
    # 配置重试器
    retrier = Retrier(RetryConfig(
        max_attempts=3,
        base_delay=0.5,
        max_delay=5.0,
        jitter=True
    ))
    
    # 注册可重试的异常
    retrier.register_retryable_exception(TimeoutError)
    retrier.register_retryable_exception(ConnectionError)
    
    # 执行带重试的请求
    try:
        result = retrier.execute(client.call, "Hello, world!")
        print(f"\n[OK] 请求成功:")
        print(f"  模型: {result['model']}")
        print(f"  响应: {result['response']}")
        print(f"  总请求次数: {client.request_count}")
    except Exception as e:
        print(f"\n[FAIL] 请求最终失败: {e}")
        print(f"  总请求次数: {client.request_count}")


# =============================================================================
# 示例2: 熔断器
# =============================================================================

def example_circuit_breaker():
    """示例: 使用熔断器"""
    print("\n" + "="*70)
    print("示例2: 熔断器 (Circuit Breaker)")
    print("="*70)
    
    # 创建一个高失败率的客户端
    client = MockModelClient("unstable-model", failure_rate=0.7, avg_latency=0.3)
    
    # 配置熔断器
    breaker = CircuitBreaker(
        CircuitBreakerConfig(
            failure_threshold=0.5,
            recovery_timeout=5.0,
            min_requests=3
        ),
        "unstable-service"
    )
    
    # 模拟一系列请求
    print("\n发送10个请求...")
    success_count = 0
    for i in range(10):
        try:
            result = breaker.execute(client.call, f"请求 {i+1}")
            print(f"  请求 {i+1}: [OK] 成功")
            success_count += 1
        except CircuitOpenError:
            print(f"  请求 {i+1}: [FAIL] 熔断器已打开，请求被拒绝")
        except Exception as e:
            print(f"  请求 {i+1}: [FAIL] 失败 - {e}")
    
    # 显示熔断器状态
    stats = breaker.get_stats()
    print(f"\n熔断器状态:")
    print(f"  当前状态: {stats['state']}")
    print(f"  失败率: {stats['failure_rate']:.2%}")
    print(f"  总请求数: {stats['total_requests']}")
    print(f"  成功请求: {success_count}")


# =============================================================================
# 示例3: 装饰器使用
# =============================================================================

def example_decorators():
    """示例: 使用装饰器"""
    print("\n" + "="*70)
    print("示例3: 装饰器 (Decorators)")
    print("="*70)
    
    # 创建客户端
    client = MockModelClient("decorator-model", failure_rate=0.3, avg_latency=0.3)
    
    # 使用装饰器包装函数
    @with_retry(max_attempts=3, base_delay=0.3)
    @with_circuit_breaker(name="decorator-cb", failure_threshold=0.5)
    def decorated_call(prompt: str):
        return client.call(prompt)
    
    # 测试
    print("\n使用装饰器发送请求...")
    for i in range(5):
        try:
            result = decorated_call(f"装饰器测试 {i+1}")
            print(f"  请求 {i+1}: [OK] 成功 - {result['response']}")
        except Exception as e:
            print(f"  请求 {i+1}: [FAIL] 失败 - {e}")


# =============================================================================
# 示例4: 完整的多模型故障转移系统
# =============================================================================

def example_failover_system():
    """示例: 完整的故障转移系统"""
    print("\n" + "="*70)
    print("示例4: 完整的多模型故障转移系统")
    print("="*70)
    
    # 1. 创建组件
    print("\n1. 初始化容错组件...")
    
    retrier = Retrier(RetryConfig(max_attempts=2, base_delay=0.5))
    circuit_breaker = CircuitBreaker(
        CircuitBreakerConfig(failure_threshold=0.6, recovery_timeout=10.0),
        "llm-gateway"
    )
    fallback_manager = FallbackManager()
    failover_manager = FailoverManager()
    
    # 2. 创建模拟模型客户端
    print("\n2. 创建模型客户端...")
    model_clients = {
        "gpt-4": MockModelClient("gpt-4", failure_rate=0.0, avg_latency=2.0),
        "claude-3": MockModelClient("claude-3", failure_rate=0.2, avg_latency=1.5),
        "gpt-3.5": MockModelClient("gpt-3.5", failure_rate=0.1, avg_latency=1.0),
    }
    
    # 3. 注册模型
    print("\n3. 注册模型到故障转移管理器...")
    models_config = [
        ModelConfig(model_id="gpt-4", name="GPT-4", priority=3, is_primary=True),
        ModelConfig(model_id="claude-3", name="Claude 3", priority=2),
        ModelConfig(model_id="gpt-3.5", name="GPT-3.5", priority=1),
    ]
    
    for config in models_config:
        failover_manager.register_model(config, pool_name="llm")
        print(f"   - 注册: {config.model_id} (主模型: {config.is_primary})")
    
    # 4. 设置降级策略
    print("\n4. 设置降级策略...")
    
    def cached_response_fallback(prompt: str, **kwargs):
        """使用缓存响应的降级策略"""
        return {
            "model": "cache",
            "prompt": prompt,
            "response": "这是缓存的响应（降级模式）",
            "cached": True,
            "timestamp": time.time()
        }
    
    fallback_manager.register_strategy(FallbackStrategy(
        name="cache_fallback",
        error_types=[ErrorType.NETWORK, ErrorType.TIMEOUT, ErrorType.SERVER_ERROR],
        fallback_func=cached_response_fallback,
        priority=1
    ))
    print("   - 已注册缓存降级策略")
    
    # 5. 创建智能客户端
    print("\n5. 创建智能客户端...")
    smart_client = SmartClient(
        retrier=retrier,
        circuit_breaker=circuit_breaker,
        fallback_manager=fallback_manager,
        failover_manager=failover_manager
    )
    
    # 6. 模拟一系列请求
    print("\n6. 模拟20个请求...")
    print("   (GPT-4设置为0%失败率，Claude-3 20%，GPT-3.5 10%)\n")
    
    results = []
    for i in range(20):
        try:
            # 选择当前最优模型
            current_model = failover_manager.select_model("llm")
            client = model_clients[current_model]
            
            # 使用智能客户端执行
            result = smart_client.execute(
                client.call,
                model_id=current_model,
                pool_name="llm",
                prompt=f"用户问题 {i+1}"
            )
            
            results.append((i+1, "success", result.get('model', 'unknown')))
            status_emoji = "[OK]" if not result.get('cached') else "[CACHE]"
            model_name = result.get('model', 'unknown')
            print(f"  请求 {i+1:2d}: {status_emoji} {model_name:10} - {result['response'][:30]}...")
            
        except Exception as e:
            results.append((i+1, "error", str(e)))
            print(f"  请求 {i+1:2d}: [FAIL] 失败 - {e}")
    
    # 7. 显示统计信息
    print("\n" + "="*70)
    print("统计信息")
    print("="*70)
    
    stats = failover_manager.get_stats()
    
    # 成功/失败统计
    success_count = sum(1 for r in results if r[1] == "success")
    error_count = len(results) - success_count
    print(f"\n总请求数: {len(results)}")
    print(f"成功: {success_count} ({success_count/len(results):.1%})")
    print(f"失败: {error_count} ({error_count/len(results):.1%})")
    
    # 模型使用统计
    model_usage = {}
    for r in results:
        if r[1] == "success":
            model = r[2]
            model_usage[model] = model_usage.get(model, 0) + 1
    
    print(f"\n模型使用情况:")
    for model, count in sorted(model_usage.items(), key=lambda x: -x[1]):
        print(f"  {model:10}: {count} 次")
    
    # 故障转移统计
    print(f"\n故障转移次数: {stats['failover_count']}")
    print(f"当前活跃模型: {stats['current_model']}")
    
    # 各模型健康状态
    print(f"\n模型健康状态:")
    for model_id, health_info in stats['models_health'].items():
        status = health_info['status']
        score = health_info['score']
        status_emoji = {
            "healthy": "[HEALTHY]",
            "degraded": "[DEGRADED]",
            "unhealthy": "[UNHEALTHY]"
        }.get(status, "[UNKNOWN]")
        print(f"  {status_emoji} {model_id:10}: {status:10} (评分: {score:.1f})")


# =============================================================================
# 主函数
# =============================================================================

def main():
    """运行所有示例"""
    print("\n" + "+" + "="*68 + "╗")
    print("|" + "  多模型协作系统 - 故障处理与容错机制 示例演示".center(68) + "|")
    print("╚" + "="*68 + "+")
    
    try:
        example_retry()
        example_circuit_breaker()
        example_decorators()
        example_failover_system()
        
        print("\n" + "+" + "="*68 + "╗")
        print("|" + "  所有示例演示完成！".center(68) + "|")
        print("╚" + "="*68 + "+")
        
    except KeyboardInterrupt:
        print("\n\n演示被用户中断")
    except Exception as e:
        print(f"\n\n演示出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
