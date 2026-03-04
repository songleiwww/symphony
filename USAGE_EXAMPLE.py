#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多模型协作系统 - 使用示例
演示如何使用完整的替补机制
"""

import time
import random
import logging
from typing import Dict, Any

# 设置日志
from model_manager import (
    ModelManager,
    ModelWrapper,
    CircuitBreaker,
    RetryPolicy,
    CircuitState,
    ModelStatus,
    ModelHealth,
    ModelError,
    ModelTimeoutError,
    ModelAPIError,
    CircuitBreakerOpenError,
    NoAvailableModelError,
    setup_logging
)


# =============================================================================
# 示例配置
# =============================================================================

# 示例模型配置
EXAMPLE_MODEL_CONFIGS = [
    {
        "name": "gpt-4",
        "model_type": "openai-gpt-4",
        "api_key": "sk-your-gpt4-key-here",
        "base_url": "https://api.openai.com/v1",
        "timeout": 30,
        "max_retries": 3,
        "enabled": True
    },
    {
        "name": "gpt-3.5-turbo",
        "model_type": "openai-gpt-3.5",
        "api_key": "sk-your-gpt35-key-here",
        "base_url": "https://api.openai.com/v1",
        "timeout": 30,
        "max_retries": 3,
        "enabled": True
    },
    {
        "name": "claude-3-haiku",
        "model_type": "anthropic-claude",
        "api_key": "sk-ant-your-claude-key-here",
        "base_url": "https://api.anthropic.com/v1",
        "timeout": 30,
        "max_retries": 3,
        "enabled": True
    }
]


# =============================================================================
# 示例1: 基本使用
# =============================================================================

def example_basic_usage():
    """示例1: 基本使用"""
    print("\n" + "="*60)
    print("示例1: 基本使用")
    print("="*60)
    
    # 1. 设置日志
    setup_logging({
        "level": "INFO",
        "console_output": True
    })
    
    # 2. 创建模型管理器
    manager = ModelManager(EXAMPLE_MODEL_CONFIGS)
    
    # 3. 启动健康检查（可选但推荐）
    manager.start_health_check()
    
    try:
        # 4. 定义实际的模型调用函数
        # 注意：这是模拟的，实际使用时需要替换为真实的API调用
        def call_model_api(model: ModelWrapper, prompt: str) -> str:
            """
            实际的模型API调用函数
            
            Args:
                model: 模型包装器实例
                prompt: 提示词
                
            Returns:
                模型响应
            """
            print(f"[{model.name}] 正在调用API...")
            print(f"  提示词: {prompt}")
            
            # 模拟API延迟
            time.sleep(random.uniform(0.5, 1.5))
            
            # 模拟随机失败（30%概率）
            if random.random() < 0.3:
                raise ModelAPIError(f"API调用失败: {model.name}")
            
            # 模拟成功响应
            response = f"这是来自 {model.name} 的回复: '{prompt}' 已收到"
            print(f"  响应: {response}")
            
            return response
        
        # 5. 执行调用（自动处理降级）
        print("\n执行第一次请求...")
        result1 = manager.execute(call_model_api, "你好，请介绍一下自己")
        print(f"\n最终结果: {result1}")
        
        print("\n" + "-"*60)
        print("\n执行第二次请求...")
        result2 = manager.execute(call_model_api, "什么是机器学习？")
        print(f"\n最终结果: {result2}")
        
        # 6. 查看系统状态
        print("\n" + "-"*60)
        print("\n系统状态:")
        status = manager.get_status()
        print(f"  模型链: {status['model_chain']}")
        for name, model_status in status["models"].items():
            print(f"\n  {name}:")
            print(f"    状态: {model_status['status']}")
            print(f"    健康: {model_status['health']}")
            print(f"    成功: {model_status['metrics']['success_count']}")
            print(f"    失败: {model_status['metrics']['failure_count']}")
            print(f"    成功率: {model_status['metrics']['success_rate']:.1f}%")
    
    finally:
        # 7. 停止健康检查
        manager.stop_health_check()


# =============================================================================
# 示例2: 模拟真实的OpenAI API调用
# =============================================================================

def example_real_api():
    """示例2: 模拟真实的API调用结构"""
    print("\n" + "="*60)
    print("示例2: 真实API调用结构")
    print("="*60)
    
    # 注意：这是一个框架示例，实际使用时需要安装openai库
    # pip install openai
    
    manager = ModelManager(EXAMPLE_MODEL_CONFIGS)
    manager.start_health_check()
    
    try:
        def call_openai(model: ModelWrapper, prompt: str) -> str:
            """
            真实的OpenAI API调用示例（框架）
            
            实际使用时需要取消注释并配置正确的API Key
            """
            """
            from openai import OpenAI
            
            client = OpenAI(
                api_key=model.config.api_key,
                base_url=model.config.base_url
            )
            
            response = client.chat.completions.create(
                model=model.config.model_type.replace("openai-", ""),
                messages=[{"role": "user", "content": prompt}],
                timeout=model.config.timeout
            )
            
            return response.choices[0].message.content
            """
            
            # 模拟响应
            print(f"[{model.name}] 模拟OpenAI API调用")
            time.sleep(0.5)
            return f"[{model.name}] OpenAI响应: {prompt}"
        
        def call_anthropic(model: ModelWrapper, prompt: str) -> str:
            """
            真实的Anthropic API调用示例（框架）
            """
            """
            from anthropic import Anthropic
            
            client = Anthropic(api_key=model.config.api_key)
            
            response = client.messages.create(
                model=model.config.model_type.replace("anthropic-", ""),
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            """
            
            print(f"[{model.name}] 模拟Anthropic API调用")
            time.sleep(0.5)
            return f"[{model.name}] Anthropic响应: {prompt}"
        
        # 根据模型类型选择调用函数
        def smart_call(model: ModelWrapper, prompt: str) -> str:
            """智能调用函数，根据模型类型选择不同的API"""
            if "openai" in model.config.model_type:
                return call_openai(model, prompt)
            elif "anthropic" in model.config.model_type:
                return call_anthropic(model, prompt)
            else:
                raise ValueError(f"不支持的模型类型: {model.config.model_type}")
        
        # 执行调用
        result = manager.execute(smart_call, "请写一首关于AI的短诗")
        print(f"\n最终结果: {result}")
    
    finally:
        manager.stop_health_check()


# =============================================================================
# 示例3: 监控和指标
# =============================================================================

def example_monitoring():
    """示例3: 监控和指标收集"""
    print("\n" + "="*60)
    print("示例3: 监控和指标")
    print("="*60)
    
    manager = ModelManager(EXAMPLE_MODEL_CONFIGS)
    manager.start_health_check()
    
    try:
        # 模拟多次请求
        def mock_call(model: ModelWrapper, prompt: str) -> str:
            time.sleep(random.uniform(0.1, 0.3))
            if random.random() < 0.2:
                raise ModelAPIError("随机失败")
            return f"[{model.name}] 成功"
        
        print("执行10次请求...")
        for i in range(10):
            try:
                manager.execute(mock_call, f"请求{i}")
                print(f"  请求{i}: 成功")
            except Exception as e:
                print(f"  请求{i}: 失败 - {str(e)}")
        
        # 获取详细指标
        print("\n" + "-"*60)
        print("\n详细指标:")
        status = manager.get_status()
        
        for name, model_data in status["models"].items():
            print(f"\n📊 {name}:")
            print(f"  状态: {model_data['status']}")
            print(f"  健康: {model_data['health']}")
            
            metrics = model_data['metrics']
            print(f"  总调用: {metrics['total_calls']}")
            print(f"  成功: {metrics['success_count']}")
            print(f"  失败: {metrics['failure_count']}")
            print(f"  成功率: {metrics['success_rate']:.1f}%")
            print(f"  平均延迟: {metrics['avg_latency']:.3f}s")
            print(f"  最小延迟: {metrics['min_latency']:.3f}s")
            print(f"  最大延迟: {metrics['max_latency']:.3f}s")
            
            cb = model_data['circuit_breaker']
            print(f"  熔断器状态: {cb['state']}")
            print(f"  熔断拒绝: {cb['metrics']['rejected_count']}")
        
        # 导出为JSON（用于监控系统）
        print("\n" + "-"*60)
        print("\nJSON格式指标（可用于监控）:")
        import json
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    finally:
        manager.stop_health_check()


# =============================================================================
# 示例4: 熔断器和重试策略的独立使用
# =============================================================================

def example_components():
    """示例4: 独立使用组件"""
    print("\n" + "="*60)
    print("示例4: 独立组件使用")
    print("="*60)
    
    # 1. 独立使用熔断器
    print("\n1. 熔断器独立使用:")
    cb = CircuitBreaker(
        model_name="my-service",
        failure_threshold=3,
        recovery_timeout=2
    )
    
    # 模拟失败
    for i in range(3):
        if cb.can_execute():
            print(f"  请求{i}: 执行")
            cb.on_failure(Exception(f"错误{i}"))
        else:
            print(f"  请求{i}: 被拒绝")
    
    print(f"  熔断器状态: {cb.state.value}")
    print(f"  等待恢复时间...")
    time.sleep(2.5)
    
    if cb.can_execute():
        print(f"  熔断器已恢复，可以执行请求")
    
    # 2. 独立使用重试策略
    print("\n2. 重试策略独立使用:")
    retry = RetryPolicy(
        max_retries=2,
        initial_delay=0.2,
        backoff_factor=2.0
    )
    
    attempt = 0
    def flaky_function():
        nonlocal attempt
        attempt += 1
        print(f"  尝试执行 (第{attempt}次)...")
        if attempt < 3:
            raise Exception("临时故障")
        return "成功!"
    
    try:
        result = retry.execute(flaky_function)
        print(f"  最终结果: {result}")
    except Exception as e:
        print(f"  最终失败: {e}")


# =============================================================================
# 主函数
# =============================================================================

def main():
    """主函数"""
    print("="*60)
    print("多模型协作系统 - 使用示例")
    print("="*60)
    
    # 设置基本日志
    logging.basicConfig(
        level=logging.WARNING,  # 只显示警告和错误
        format='%(levelname)s: %(message)s'
    )
    
    # 运行所有示例
    example_basic_usage()
    example_real_api()
    example_monitoring()
    example_components()
    
    print("\n" + "="*60)
    print("所有示例运行完成!")
    print("="*60)


if __name__ == "__main__":
    main()
