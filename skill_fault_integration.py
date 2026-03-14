#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能管理器与故障处理系统集成示例

展示如何将技能管理器与现有的 fault_tolerance.py 集成使用
"""

import sys
import os
import time
import random
import logging
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from skill_manager import (
    SkillManager, SkillConfig, SkillMetadata, SkillParameter, Skill,
    SkillType, SkillExecutionResult
)
from fault_tolerance import (
    Retrier, CircuitBreaker, FallbackManager, FailoverManager,
    SmartClient, RetryConfig, CircuitBreakerConfig, HealthCheckConfig,
    ModelConfig, ModelHealth, HealthStatus, ErrorType,
    RetryError, CircuitOpenError, FallbackError, NoHealthyModelError,
    with_retry, with_circuit_breaker, classify_error
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# 示例 1: 基础集成 - 为技能添加重试和熔断器
# =============================================================================

def example_1_basic_integration():
    """示例 1: 基础集成 - 为技能添加重试和熔断器"""
    print("\n" + "=" * 60)
    print("示例 1: 基础集成 - 重试和熔断器")
    print("=" * 60)
    
    # 1. 创建容错组件
    retry_config = RetryConfig(
        max_attempts=3,
        base_delay=0.5,
        backoff_factor=2.0
    )
    retrier = Retrier(retry_config)
    
    circuit_config = CircuitBreakerConfig(
        failure_threshold=0.5,
        recovery_timeout=5.0,
        min_requests=3
    )
    circuit_breaker = CircuitBreaker(circuit_config, "skill_circuit")
    
    fallback_manager = FallbackManager()
    
    # 2. 创建配置了容错组件的技能管理器
    config = SkillConfig(
        skill_dirs=[],
        auto_reload=False,
        enable_circuit_breaker=True,
        enable_fallback=True
    )
    
    skill_manager = SkillManager(
        config=config,
        retrier=retrier,
        circuit_breaker=circuit_breaker,
        fallback_manager=fallback_manager
    )
    
    # 3. 创建一个不可靠的技能（用于测试）
    call_count = 0
    
    def flaky_skill_func() -> dict:
        nonlocal call_count
        call_count += 1
        # 前 2 次调用失败，之后成功
        if call_count <= 2:
            logger.warning(f"技能执行失败 (尝试 {call_count}/3)")
            raise ConnectionError("网络连接失败")
        logger.info(f"技能执行成功 (尝试 {call_count}/3)")
        return {"status": "success", "attempt": call_count}
    
    def fallback_func() -> dict:
        return {"status": "fallback", "data": "使用降级数据"}
    
    metadata = SkillMetadata(
        name="flaky_service",
        version="1.0.0",
        description="不可靠的服务",
        skill_type=SkillType.PYTHON,
        enabled=True
    )
    
    skill_obj = Skill(metadata, [], flaky_skill_func)
    skill_obj.set_fallback(fallback_func)
    skill_manager.loader._loaded_skills["flaky_service"] = skill_obj
    
    # 4. 使用 SmartClient 直接包装技能执行
    print("\n使用 SmartClient 执行技能:")
    
    smart_client = SmartClient(
        retrier=retrier,
        circuit_breaker=circuit_breaker,
        fallback_manager=fallback_manager
    )
    
    # 定义包装函数
    def wrapped_execute():
        return skill_manager.execute_skill("flaky_service", {})
    
    try:
        result = smart_client.execute(wrapped_execute, use_retries=True, use_circuit_breaker=True)
        print(f"  最终结果: {result.data if result.success else result.error}")
    except Exception as e:
        print(f"  执行出错: {e}")
    
    # 5. 显示熔断器状态
    print(f"\n熔断器状态:")
    stats = circuit_breaker.get_stats()
    print(f"  状态: {stats['state']}")
    print(f"  失败率: {stats['failure_rate']:.2%}")
    print(f"  总请求: {stats['total_requests']}")
    
    skill_manager.shutdown()
    print("\n✓ 示例 1 完成")


# =============================================================================
# 示例 2: 使用故障转移 - 多个技能实例
# =============================================================================

def example_2_failover():
    """示例 2: 使用故障转移 - 多个技能实例"""
    print("\n" + "=" * 60)
    print("示例 2: 故障转移 - 多技能实例")
    print("=" * 60)
    
    # 1. 创建组件
    health_checker = HealthChecker(HealthCheckConfig(
        check_interval=10.0,
        unhealthy_threshold=50.0,
        degraded_threshold=80.0
    ))
    
    failover_manager = FailoverManager(health_checker)
    
    # 2. 注册多个"模型"（这里我们模拟不同的技能实例）
    model_configs = [
        ModelConfig(
            model_id="skill_instance_a",
            name="技能实例 A",
            priority=3,
            is_primary=True
        ),
        ModelConfig(
            model_id="skill_instance_b",
            name="技能实例 B",
            priority=2
        ),
        ModelConfig(
            model_id="skill_instance_c",
            name="技能实例 C",
            priority=1
        )
    ]
    
    for model_config in model_configs:
        failover_manager.register_model(model_config, pool_name="skill_pool")
    
    # 3. 模拟技能执行和失败
    print("\n模拟技能执行和故障转移:")
    
    # 先记录一些成功请求
    for i in range(2):
        model_id = failover_manager.select_model("skill_pool")
        failover_manager.on_model_success(model_id, latency=0.5)
        print(f"  请求 {i+1}: {model_id} 成功")
    
    # 记录主实例失败
    print("\n模拟主实例失败:")
    failover_manager.on_model_failure(
        "skill_instance_a",
        ErrorType.NETWORK,
        latency=2.0
    )
    failover_manager.on_model_failure(
        "skill_instance_a",
        ErrorType.NETWORK,
        latency=2.0
    )
    failover_manager.on_model_failure(
        "skill_instance_a",
        ErrorType.NETWORK,
        latency=2.0
    )
    
    # 触发故障转移
    print("\n触发故障转移:")
    try:
        new_model = failover_manager.failover("skill_pool")
        print(f"  故障转移到: {new_model}")
    except NoHealthyModelError as e:
        print(f"  故障转移失败: {e}")
    
    # 4. 显示状态
    print("\n当前状态:")
    stats = failover_manager.get_stats()
    print(f"  当前模型: {stats['current_model']}")
    print(f"  故障转移次数: {stats['failover_count']}")
    print(f"\n  模型健康状态:")
    for mid, health in stats['models_health'].items():
        print(f"    {mid}: {health['status']} (评分: {health['score']:.1f})")
    
    print("\n✓ 示例 2 完成")


# =============================================================================
# 示例 3: 完整集成 - 使用所有容错机制
# =============================================================================

def example_3_complete_integration():
    """示例 3: 完整集成 - 使用所有容错机制"""
    print("\n" + "=" * 60)
    print("示例 3: 完整集成 - 所有容错机制")
    print("=" * 60)
    
    # 1. 创建所有组件
    retry_config = RetryConfig(
        max_attempts=3,
        base_delay=0.3,
        backoff_factor=2.0
    )
    retrier = Retrier(retry_config)
    retrier.register_retryable_exception(ConnectionError)
    retrier.register_retryable_exception(TimeoutError)
    
    circuit_config = CircuitBreakerConfig(
        failure_threshold=0.6,
        recovery_timeout=10.0,
        min_requests=5
    )
    circuit_breaker = CircuitBreaker(circuit_config, "complete_skill")
    
    fallback_manager = FallbackManager()
    
    # 注册降级策略
    def cache_fallback(**kwargs):
        return {"source": "cache", "data": "缓存数据", "time": time.time()}
    
    def default_fallback(**kwargs):
        return {"source": "default", "data": "默认降级数据"}
    
    fallback_manager.register_strategy(FallbackStrategy(
        name="cache_strategy",
        error_types=[ErrorType.NETWORK, ErrorType.TIMEOUT],
        fallback_func=cache_fallback,
        priority=2
    ))
    
    fallback_manager.set_default_fallback(default_fallback)
    
    # 2. 创建技能管理器
    config = SkillConfig(
        skill_dirs=[],
        auto_reload=False,
        enable_circuit_breaker=True,
        enable_fallback=True,
        enable_failover=True
    )
    
    skill_manager = SkillManager(
        config=config,
        retrier=retrier,
        circuit_breaker=circuit_breaker,
        fallback_manager=fallback_manager
    )
    
    # 3. 创建测试技能
    execution_count = 0
    failure_pattern = [True, True, False, True, False, False, False]
    
    def unreliable_skill() -> dict:
        nonlocal execution_count
        execution_count += 1
        
        idx = (execution_count - 1) % len(failure_pattern)
        should_fail = failure_pattern[idx]
        
        if should_fail:
            error_type = random.choice([
                ConnectionError("网络连接失败"),
                TimeoutError("请求超时")
            ])
            logger.warning(f"执行 #{execution_count}: 失败 ({type(error_type).__name__})")
            raise error_type
        
        logger.info(f"执行 #{execution_count}: 成功")
        return {
            "source": "live",
            "data": f"实时数据 #{execution_count}",
            "time": time.time()
        }
    
    metadata = SkillMetadata(
        name="unreliable_api",
        version="1.0.0",
        description="不可靠的 API",
        skill_type=SkillType.PYTHON,
        enabled=True,
        timeout=10.0,
        retries=3
    )
    
    skill_obj = Skill(metadata, [], unreliable_skill)
    skill_manager.loader._loaded_skills["unreliable_api"] = skill_obj
    
    # 4. 模拟多次执行
    print("\n模拟多次技能执行:")
    print("-" * 60)
    print(f"失败模式: {failure_pattern}")
    print("-" * 60)
    
    results = []
    for i in range(7):
        result = skill_manager.execute_skill("unreliable_api", {})
        results.append(result)
        
        status = "✓ 成功" if result.success else "✗ 失败"
        source = ""
        if result.from_fallback:
            source = " (降级)"
        elif result.from_cache:
            source = " (缓存)"
        
        data_str = ""
        if result.success and result.data:
            if isinstance(result.data, dict):
                data_str = f" | {result.data.get('source', 'unknown')}"
        
        print(f"  执行 {i+1}: {status}{source}{data_str}")
        if not result.success:
            print(f"    错误: {result.error}")
    
    # 5. 统计汇总
    print("\n" + "-" * 60)
    print("统计汇总:")
    success_count = sum(1 for r in results if r.success)
    fallback_count = sum(1 for r in results if r.from_fallback)
    print(f"  总执行: {len(results)}")
    print(f"  成功: {success_count}")
    print(f"  失败: {len(results) - success_count}")
    print(f"  使用降级: {fallback_count}")
    
    # 6. 熔断器状态
    print("\n熔断器状态:")
    cb_stats = circuit_breaker.get_stats()
    print(f"  状态: {cb_stats['state']}")
    print(f"  失败率: {cb_stats['failure_rate']:.2%}")
    print(f"  成功次数: {cb_stats['success_count']}")
    print(f"  失败次数: {cb_stats['failure_count']}")
    
    # 7. 技能统计
    print("\n技能统计:")
    skill_stats = skill_manager.get_skill_stats("unreliable_api")
    if skill_stats:
        print(f"  总调用: {skill_stats.total_calls}")
        print(f"  成功: {skill_stats.success_count}")
        print(f"  失败: {skill_stats.failure_count}")
        print(f"  平均执行时间: {skill_stats.avg_execution_time:.4f}秒")
    
    skill_manager.shutdown()
    print("\n✓ 示例 3 完成")


# =============================================================================
# 示例 4: 使用装饰器包装技能
# =============================================================================

def example_4_decorator_integration():
    """示例 4: 使用装饰器包装技能"""
    print("\n" + "=" * 60)
    print("示例 4: 装饰器集成")
    print("=" * 60)
    
    # 1. 使用装饰器创建具有容错能力的函数
    @with_retry(
        max_attempts=3,
        base_delay=0.5,
        retryable_exceptions=[ConnectionError, TimeoutError]
    )
    @with_circuit_breaker(
        name="decorated_skill",
        failure_threshold=0.5,
        recovery_timeout=5.0
    )
    def decorated_skill_function(should_fail: bool = False) -> dict:
        """使用装饰器的技能函数"""
        if should_fail:
            raise ConnectionError("模拟连接失败")
        return {"status": "success", "data": "装饰器技能执行成功"}
    
    # 2. 测试
    print("\n测试带装饰器的技能:")
    
    # 成功执行
    try:
        result = decorated_skill_function(should_fail=False)
        print(f"  成功执行: {result}")
    except Exception as e:
        print(f"  执行失败: {e}")
    
    # 失败执行（会重试）
    print("\n测试失败重试:")
    try:
        result = decorated_skill_function(should_fail=True)
        print(f"  结果: {result}")
    except RetryError as e:
        print(f"  重试耗尽: {e}")
    
    print("\n✓ 示例 4 完成")


# =============================================================================
# 主函数
# =============================================================================

def main():
    """运行所有集成示例"""
    print("\n" + "=" * 60)
    print("技能管理器与故障处理系统集成 - 示例")
    print("=" * 60)
    
    examples = [
        example_1_basic_integration,
        example_2_failover,
        example_3_complete_integration,
        example_4_decorator_integration
    ]
    
    for example in examples:
        try:
            example()
            # 示例之间稍作暂停
            time.sleep(0.5)
        except Exception as e:
            logger.exception(f"示例执行出错: {example.__name__}")
            print(f"\n✗ 示例执行出错: {e}")
    
    print("\n" + "=" * 60)
    print("所有集成示例完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
