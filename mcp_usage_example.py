#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP工具管理器 - 使用示例
展示如何在实际项目中集成和使用MCP管理器
"""

import time
import sys
import os

# 确保可以导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_manager import (
    MCPManager, create_mcp_manager,
    ToolSchema, ParameterSchema, ToolStatus, ParameterType,
    ToolExecutionResult
)
from fault_tolerance import (
    RetryConfig, CircuitBreakerConfig, HealthCheckConfig,
    FallbackStrategy, ErrorType, FallbackManager
)


# =============================================================================
# 示例1：基础使用
# =============================================================================

def example_basic_usage():
    """示例1：基础使用 - 注册和执行简单工具"""
    print("\n" + "=" * 60)
    print("示例1：基础使用")
    print("=" * 60)
    
    # 1. 创建MCP管理器
    mcp = create_mcp_manager()
    
    # 2. 定义工具模式
    greet_schema = ToolSchema(
        name="greet",
        description="向用户打招呼",
        parameters=[
            ParameterSchema(
                name="name",
                type=ParameterType.STRING,
                required=True,
                description="用户名称",
                min_length=1,
                max_length=50
            ),
            ParameterSchema(
                name="language",
                type=ParameterType.STRING,
                required=False,
                description="语言 (zh/en)",
                default="zh",
                enum=["zh", "en"]
            )
        ],
        returns=ParameterSchema(
            name="greeting",
            type=ParameterType.STRING,
            description="问候语"
        ),
        category="utils",
        tags=["greeting", "i18n"]
    )
    
    # 3. 实现工具函数
    def greet(name: str, language: str = "zh") -> str:
        """问候函数"""
        if language == "zh":
            return f"你好，{name}！欢迎使用MCP工具管理器。"
        else:
            return f"Hello, {name}! Welcome to MCP Tool Manager."
    
    # 4. 注册工具
    mcp.register_tool(greet_schema, greet)
    print("✓ 已注册工具: greet")
    
    # 5. 执行工具
    print("\n执行工具: greet(name='张三', language='zh')")
    result = mcp.execute_tool("greet", {"name": "张三", "language": "zh"})
    
    if result.success:
        print(f"✓ 成功！结果: {result.result}")
        print(f"  耗时: {result.latency:.4f}秒")
    else:
        print(f"✗ 失败: {result.error}")
    
    # 6. 使用英文
    print("\n执行工具: greet(name='John', language='en')")
    result = mcp.execute_tool("greet", {"name": "John", "language": "en"})
    
    if result.success:
        print(f"✓ 成功！结果: {result.result}")
    
    # 7. 测试参数验证
    print("\n测试参数验证 (name长度为0):")
    result = mcp.execute_tool("greet", {"name": ""})
    if not result.success:
        print(f"✓ 正确拦截参数错误: {result.error}")
    
    return mcp


# =============================================================================
# 示例2：使用装饰器
# =============================================================================

def example_decorator():
    """示例2：使用装饰器注册工具"""
    print("\n" + "=" * 60)
    print("示例2：使用装饰器")
    print("=" * 60)
    
    # 1. 创建MCP管理器
    mcp = create_mcp_manager()
    
    # 2. 使用装饰器注册工具
    @mcp.tool(
        name="calculate",
        description="基础数学运算",
        parameters=[
            ParameterSchema(
                name="operation",
                type=ParameterType.STRING,
                required=True,
                enum=["add", "subtract", "multiply", "divide"]
            ),
            ParameterSchema(
                name="a",
                type=ParameterType.NUMBER,
                required=True
            ),
            ParameterSchema(
                name="b",
                type=ParameterType.NUMBER,
                required=True
            )
        ],
        returns=ParameterSchema(
            name="result",
            type=ParameterType.NUMBER
        ),
        category="math",
        tags=["calculator", "basic"]
    )
    def calculate(operation: str, a: float, b: float) -> float:
        """执行基础数学运算"""
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            if b == 0:
                raise ValueError("除数不能为零")
            return a / b
        else:
            raise ValueError(f"未知操作: {operation}")
    
    print("✓ 已使用装饰器注册工具: calculate")
    
    # 3. 测试各种运算
    test_cases = [
        ("add", 10, 5),
        ("subtract", 10, 5),
        ("multiply", 10, 5),
        ("divide", 10, 5),
    ]
    
    for op, a, b in test_cases:
        result = mcp.execute_tool("calculate", {"operation": op, "a": a, "b": b})
        if result.success:
            print(f"✓ {op}({a}, {b}) = {result.result}")
        else:
            print(f"✗ {op}({a}, {b}) 失败: {result.error}")
    
    return mcp


# =============================================================================
# 示例3：集成容错机制
# =============================================================================

def example_fault_tolerance():
    """示例3：集成容错机制（重试、熔断器、降级）"""
    print("\n" + "=" * 60)
    print("示例3：集成容错机制")
    print("=" * 60)
    
    # 1. 创建自定义配置的MCP管理器
    retry_config = RetryConfig(
        max_attempts=3,
        base_delay=0.5,
        backoff_factor=2.0
    )
    
    circuit_config = CircuitBreakerConfig(
        failure_threshold=0.3,
        recovery_timeout=5.0,
        window_size=10.0
    )
    
    mcp = create_mcp_manager(
        retry_config=retry_config,
        circuit_config=circuit_config
    )
    
    # 2. 创建一个不稳定的服务模拟
    call_count = 0
    
    def unstable_service() -> str:
        """不稳定的服务，前3次调用失败，之后成功"""
        nonlocal call_count
        call_count += 1
        
        if call_count <= 3:
            print(f"  [服务] 第 {call_count} 次调用失败")
            raise ConnectionError("网络连接失败")
        else:
            print(f"  [服务] 第 {call_count} 次调用成功")
            return f"成功（第{call_count}次调用）"
    
    # 3. 注册工具，启用重试
    unstable_schema = ToolSchema(
        name="unstable_service",
        description="不稳定的服务（演示重试机制）",
        parameters=[],
        returns=ParameterSchema(name="result", type=ParameterType.STRING)
    )
    
    mcp.register_tool(
        unstable_schema,
        unstable_service,
        use_retries=True,
        use_circuit_breaker=True
    )
    print("✓ 已注册工具: unstable_service（启用重试）")
    
    # 4. 执行工具（演示重试）
    print("\n执行工具（应该会重试，最终成功）:")
    result = mcp.execute_tool("unstable_service", {})
    
    if result.success:
        print(f"✓ 最终成功！结果: {result.result}")
    else:
        print(f"✗ 失败: {result.error}")
    
    # 5. 设置降级策略
    print("\n设置降级策略...")
    
    def cache_fallback(*args, **kwargs) -> str:
        """缓存降级"""
        return "使用缓存数据（降级）"
    
    fallback_strategy = FallbackStrategy(
        name="cache_fallback",
        error_types=[ErrorType.NETWORK, ErrorType.TIMEOUT],
        fallback_func=cache_fallback,
        priority=1
    )
    
    mcp.smart_client.fallback_manager.register_strategy(fallback_strategy)
    print("✓ 已注册缓存降级策略")
    
    # 6. 创建总是失败的服务
    def always_fails() -> str:
        """总是失败的服务"""
        raise ConnectionError("服务不可用")
    
    fail_schema = ToolSchema(
        name="always_fail",
        description="总是失败的服务（演示降级）",
        parameters=[],
        returns=ParameterSchema(name="result", type=ParameterType.STRING)
    )
    
    mcp.register_tool(fail_schema, always_fails, use_retries=False)
    print("✓ 已注册工具: always_fail")
    
    # 7. 执行并演示降级
    print("\n执行总是失败的服务（应该使用降级）:")
    result = mcp.execute_tool("always_fail", {})
    
    if result.success:
        print(f"✓ 降级成功！结果: {result.result}")
        print(f"  使用降级: {result.used_fallback}")
    else:
        print(f"✗ 失败（降级也失败）: {result.error}")
    
    return mcp


# =============================================================================
# 示例4：工具发现和指标
# =============================================================================

def example_discovery_and_metrics():
    """示例4：工具发现和指标监控"""
    print("\n" + "=" * 60)
    print("示例4：工具发现和指标监控")
    print("=" * 60)
    
    # 1. 创建MCP管理器并注册多个工具
    mcp = create_mcp_manager()
    
    # 注册一些工具
    tools_to_register = [
        ("tool_a", "工具A", "category1", ["tag1", "tag2"]),
        ("tool_b", "工具B", "category1", ["tag2", "tag3"]),
        ("tool_c", "工具C", "category2", ["tag1", "tag3"]),
    ]
    
    for name, desc, category, tags in tools_to_register:
        schema = ToolSchema(
            name=name,
            description=desc,
            parameters=[],
            returns=ParameterSchema(name="result", type=ParameterType.STRING),
            category=category,
            tags=tags
        )
        
        # 创建简单的实现
        def make_func(n):
            def f():
                time.sleep(0.01)  # 模拟一些延迟
                return f"结果来自 {n}"
            return f
        
        mcp.register_tool(schema, make_func(name))
    
    print(f"✓ 已注册 {len(tools_to_register)} 个工具")
    
    # 2. 列出所有工具
    print("\n所有工具:")
    all_tools = mcp.list_tools()
    for tool in all_tools:
        print(f"  - {tool.name}: {tool.description} (类别: {tool.category})")
    
    # 3. 按类别筛选
    print("\n类别 'category1' 的工具:")
    cat1_tools = mcp.list_tools(category="category1")
    for tool in cat1_tools:
        print(f"  - {tool.name}")
    
    # 4. 按标签筛选
    print("\n标签 'tag2' 的工具:")
    tag2_tools = mcp.list_tools(tags=["tag2"])
    for tool in tag2_tools:
        print(f"  - {tool.name}")
    
    # 5. 执行一些调用以生成指标
    print("\n执行工具调用以生成指标...")
    for i in range(10):
        tool_name = f"tool_{chr(ord('a') + i % 3)}"
        mcp.execute_tool(tool_name, {})
    
    # 6. 显示指标
    print("\n工具指标:")
    stats = mcp.get_stats()
    
    print(f"  总调用次数: {stats['total_calls']}")
    print(f"  成功率: {stats['success_rate']:.1f}%")
    
    print("\n  各工具详细指标:")
    for tool_name, tool_info in stats['tools'].items():
        metrics = tool_info['metrics']
        print(f"    {tool_name}:")
        print(f"      调用次数: {metrics['total_calls']}")
        print(f"      平均延迟: {metrics['avg_latency']:.4f}秒")
    
    # 7. 获取单个工具的详细指标
    print("\n单个工具的详细指标 (tool_a):")
    metrics = mcp.get_tool_metrics("tool_a")
    if metrics:
        print(f"  总调用: {metrics.total_calls}")
        print(f"  成功: {metrics.success_count}")
        print(f"  失败: {metrics.failure_count}")
        print(f"  最小延迟: {metrics.min_latency:.4f}秒")
        print(f"  最大延迟: {metrics.max_latency:.4f}秒")
    
    return mcp


# =============================================================================
# 示例5：完整的实际应用场景
# =============================================================================

def example_real_world():
    """示例5：完整的实际应用场景 - 天气查询工具集"""
    print("\n" + "=" * 60)
    print("示例5：完整应用 - 天气查询工具集")
    print("=" * 60)
    
    # 1. 创建MCP管理器
    mcp = create_mcp_manager()
    
    # 2. 定义天气查询相关工具
    # 工具1：城市搜索
    @mcp.tool(
        name="search_city",
        description="搜索城市",
        parameters=[
            ParameterSchema(
                name="query",
                type=ParameterType.STRING,
                required=True,
                description="搜索关键词",
                min_length=1,
                max_length=50
            )
        ],
        returns=ParameterSchema(
            name="cities",
            type=ParameterType.ARRAY,
            description="匹配的城市列表"
        ),
        category="weather",
        tags=["search", "location"]
    )
    def search_city(query: str) -> list:
        """模拟搜索城市"""
        cities_db = {
            "beijing": {"name": "北京", "country": "中国", "id": "101010100"},
            "shanghai": {"name": "上海", "country": "中国", "id": "101020100"},
            "guangzhou": {"name": "广州", "country": "中国", "id": "101280101"},
            "shenzhen": {"name": "深圳", "country": "中国", "id": "101280601"},
            "newyork": {"name": "纽约", "country": "美国", "id": "USNY0001"},
            "london": {"name": "伦敦", "country": "英国", "id": "UKXX0001"},
            "tokyo": {"name": "东京", "country": "日本", "id": "JAXX0001"},
        }
        
        results = []
        query_lower = query.lower()
        
        for key, city in cities_db.items():
            if (query_lower in key or 
                query_lower in city["name"].lower() or
                query_lower in city["country"].lower()):
                results.append(city)
        
        return results
    
    # 工具2：获取当前天气
    @mcp.tool(
        name="get_current_weather",
        description="获取当前天气",
        parameters=[
            ParameterSchema(
                name="city_id",
                type=ParameterType.STRING,
                required=True,
                description="城市ID"
            ),
            ParameterSchema(
                name="units",
                type=ParameterType.STRING,
                required=False,
                description="温度单位",
                default="metric",
                enum=["metric", "imperial"]
            )
        ],
        returns=ParameterSchema(
            name="weather",
            type=ParameterType.OBJECT,
            description="天气数据"
        ),
        category="weather",
        tags=["current", "weather"]
    )
    def get_current_weather(city_id: str, units: str = "metric") -> dict:
        """模拟获取当前天气"""
        import random
        
        # 模拟网络延迟
        time.sleep(0.1)
        
        # 随机生成天气数据
        conditions = ["晴朗", "多云", "阴天", "小雨", "雷阵雨"]
        condition = random.choice(conditions)
        
        temp = random.uniform(10, 35)
        humidity = random.uniform(30, 90)
        wind_speed = random.uniform(0, 20)
        
        if units == "imperial":
            temp = temp * 9/5 + 32
            wind_speed = wind_speed * 2.237
        
        return {
            "city_id": city_id,
            "condition": condition,
            "temperature": round(temp, 1),
            "humidity": round(humidity, 1),
            "wind_speed": round(wind_speed, 1),
            "units": units,
            "timestamp": time.time()
        }
    
    # 工具3：获取天气预报
    @mcp.tool(
        name="get_forecast",
        description="获取天气预报",
        parameters=[
            ParameterSchema(
                name="city_id",
                type=ParameterType.STRING,
                required=True,
                description="城市ID"
            ),
            ParameterSchema(
                name="days",
                type=ParameterType.INTEGER,
                required=False,
                description="预报天数",
                default=3,
                minimum=1,
                maximum=7
            )
        ],
        returns=ParameterSchema(
            name="forecast",
            type=ParameterType.ARRAY,
            description="天气预报列表"
        ),
        category="weather",
        tags=["forecast", "prediction"]
    )
    def get_forecast(city_id: str, days: int = 3) -> list:
        """模拟获取天气预报"""
        import random
        
        forecast = []
        conditions = ["晴朗", "多云", "阴天", "小雨"]
        
        for i in range(days):
            condition = random.choice(conditions)
            high = random.uniform(20, 35)
            low = random.uniform(10, 20)
            
            forecast.append({
                "day": i + 1,
                "condition": condition,
                "high": round(high, 1),
                "low": round(low, 1),
                "date": time.strftime("%Y-%m-%d", time.localtime(time.time() + i * 86400))
            })
        
        return forecast
    
    print("✓ 已注册天气查询工具集")
    
    # 3. 使用工具
    print("\n--- 使用天气查询工具 ---")
    
    # 搜索城市
    print("\n1. 搜索城市 '北京':")
    result = mcp.execute_tool("search_city", {"query": "北京"})
    if result.success and result.result:
        city = result.result[0]
        print(f"   找到城市: {city['name']} ({city['country']})")
        city_id = city['id']
        
        # 获取当前天气
        print(f"\n2. 获取 {city['name']} 的当前天气:")
        result = mcp.execute_tool("get_current_weather", {"city_id": city_id})
        if result.success:
            weather = result.result
            print(f"   天气状况: {weather['condition']}")
            print(f"   温度: {weather['temperature']}°")
            print(f"   湿度: {weather['humidity']}%")
            print(f"   风速: {weather['wind_speed']}")
        
        # 获取天气预报
        print(f"\n3. 获取 {city['name']} 的3天预报:")
        result = mcp.execute_tool("get_forecast", {"city_id": city_id, "days": 3})
        if result.success:
            for day in result.result:
                print(f"   {day['date']}: {day['condition']}, {day['low']}° ~ {day['high']}°")
    
    # 4. 显示统计
    print("\n--- 统计信息 ---")
    stats = mcp.get_stats()
    print(f"总调用次数: {stats['total_calls']}")
    print(f"成功率: {stats['success_rate']:.1f}%")
    
    return mcp


# =============================================================================
# 主函数
# =============================================================================

def main():
    """运行所有示例"""
    print("=" * 60)
    print("MCP工具管理器 - 使用示例集")
    print("=" * 60)
    
    try:
        # 运行所有示例
        example_basic_usage()
        example_decorator()
        example_fault_tolerance()
        example_discovery_and_metrics()
        example_real_world()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
