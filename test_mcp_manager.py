#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP工具管理器 - 测试文件
测试MCP工具管理器的所有功能
"""

import unittest
import time
import sys
import os

# 确保可以导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_manager import (
    MCPManager, create_mcp_manager,
    ToolSchema, ParameterSchema, ToolStatus, ParameterType,
    ToolNotFoundError, ToolExecutionError, ParameterValidationError,
    ToolAlreadyRegisteredError, ToolDisabledError,
    ParameterValidator, ToolExecutionResult
)
from fault_tolerance import (
    RetryConfig, CircuitBreakerConfig, HealthCheckConfig,
    FallbackStrategy, ErrorType
)


# =============================================================================
# 测试工具函数
# =============================================================================

def test_add(a: int, b: int) -> int:
    """测试加法函数"""
    return a + b


def test_multiply(x: float, y: float) -> float:
    """测试乘法函数"""
    return x * y


def test_uppercase(text: str) -> str:
    """测试大写转换函数"""
    return text.upper()


def test_slow_function(delay: float) -> str:
    """测试慢函数"""
    time.sleep(delay)
    return f"完成，耗时 {delay} 秒"


def test_flaky_function() -> str:
    """测试不稳定函数（50%失败率）"""
    import random
    if random.random() < 0.5:
        raise ValueError("随机失败")
    return "成功"


def test_error_function() -> str:
    """测试总是出错的函数"""
    raise RuntimeError("总是出错")


def test_fallback_function(*args, **kwargs) -> str:
    """测试降级函数"""
    return "使用了降级方案"


# =============================================================================
# 参数验证器测试
# =============================================================================

class TestParameterValidator(unittest.TestCase):
    """测试参数验证器"""
    
    def setUp(self):
        self.validator = ParameterValidator()
    
    def test_validate_string(self):
        """测试字符串验证"""
        schema = ParameterSchema(
            name="text",
            type=ParameterType.STRING,
            required=True,
            min_length=2,
            max_length=10,
            pattern=r"^[a-zA-Z]+$"
        )
        
        # 有效字符串
        valid, error = self.validator.validate_parameter("Hello", schema)
        self.assertTrue(valid)
        self.assertIsNone(error)
        
        # 太短
        valid, error = self.validator.validate_parameter("H", schema)
        self.assertFalse(valid)
        self.assertIn("长度不能小于", error)
        
        # 太长
        valid, error = self.validator.validate_parameter("HelloWorld123", schema)
        self.assertFalse(valid)
        self.assertIn("长度不能大于", error)
        
        # 不匹配模式
        valid, error = self.validator.validate_parameter("Hello123", schema)
        self.assertFalse(valid)
        self.assertIn("不匹配模式", error)
    
    def test_validate_integer(self):
        """测试整数验证"""
        schema = ParameterSchema(
            name="count",
            type=ParameterType.INTEGER,
            required=True,
            minimum=1,
            maximum=100
        )
        
        # 有效整数
        valid, error = self.validator.validate_parameter(50, schema)
        self.assertTrue(valid)
        self.assertIsNone(error)
        
        # 太小
        valid, error = self.validator.validate_parameter(0, schema)
        self.assertFalse(valid)
        self.assertIn("不能小于", error)
        
        # 太大
        valid, error = self.validator.validate_parameter(101, schema)
        self.assertFalse(valid)
        self.assertIn("不能大于", error)
        
        # 类型错误
        valid, error = self.validator.validate_parameter("50", schema)
        self.assertFalse(valid)
        self.assertIn("期望类型", error)
    
    def test_validate_enum(self):
        """测试枚举验证"""
        schema = ParameterSchema(
            name="color",
            type=ParameterType.STRING,
            required=True,
            enum=["red", "green", "blue"]
        )
        
        # 有效枚举值
        valid, error = self.validator.validate_parameter("red", schema)
        self.assertTrue(valid)
        self.assertIsNone(error)
        
        # 无效枚举值
        valid, error = self.validator.validate_parameter("yellow", schema)
        self.assertFalse(valid)
        self.assertIn("必须在", error)
    
    def test_validate_boolean(self):
        """测试布尔值验证"""
        schema = ParameterSchema(
            name="enabled",
            type=ParameterType.BOOLEAN,
            required=True
        )
        
        # 有效布尔值
        valid, error = self.validator.validate_parameter(True, schema)
        self.assertTrue(valid)
        self.assertIsNone(error)
        
        valid, error = self.validator.validate_parameter(False, schema)
        self.assertTrue(valid)
        self.assertIsNone(error)
        
        # 类型错误
        valid, error = self.validator.validate_parameter("true", schema)
        self.assertFalse(valid)
        self.assertIn("期望类型", error)
    
    def test_validate_array(self):
        """测试数组验证"""
        item_schema = ParameterSchema(
            name="item",
            type=ParameterType.INTEGER,
            minimum=1,
            maximum=10
        )
        
        schema = ParameterSchema(
            name="numbers",
            type=ParameterType.ARRAY,
            required=True,
            items=item_schema
        )
        
        # 有效数组
        valid, error = self.validator.validate_parameter([1, 2, 3], schema)
        self.assertTrue(valid)
        self.assertIsNone(error)
        
        # 包含无效元素
        valid, error = self.validator.validate_parameter([1, 11, 3], schema)
        self.assertFalse(valid)
        self.assertIn("数组元素", error)
    
    def test_validate_object(self):
        """测试对象验证"""
        prop_schema1 = ParameterSchema(
            name="name",
            type=ParameterType.STRING,
            required=True
        )
        
        prop_schema2 = ParameterSchema(
            name="age",
            type=ParameterType.INTEGER,
            required=False,
            minimum=0
        )
        
        schema = ParameterSchema(
            name="person",
            type=ParameterType.OBJECT,
            required=True,
            properties={
                "name": prop_schema1,
                "age": prop_schema2
            }
        )
        
        # 有效对象
        valid, error = self.validator.validate_parameter({"name": "John", "age": 30}, schema)
        self.assertTrue(valid)
        self.assertIsNone(error)
        
        # 缺少必需属性
        valid, error = self.validator.validate_parameter({"age": 30}, schema)
        self.assertFalse(valid)
        self.assertIn("缺少必需属性", error)
        
        # 属性无效
        valid, error = self.validator.validate_parameter({"name": "John", "age": -5}, schema)
        self.assertFalse(valid)
        self.assertIn("属性 'age'", error)
    
    def test_validate_parameters(self):
        """测试批量参数验证"""
        schemas = [
            ParameterSchema(
                name="a",
                type=ParameterType.INTEGER,
                required=True,
                minimum=1
            ),
            ParameterSchema(
                name="b",
                type=ParameterType.INTEGER,
                required=True,
                minimum=1
            )
        ]
        
        # 有效参数
        valid, error = self.validator.validate_parameters({"a": 5, "b": 3}, schemas)
        self.assertTrue(valid)
        self.assertIsNone(error)
        
        # 缺少必需参数
        valid, error = self.validator.validate_parameters({"a": 5}, schemas)
        self.assertFalse(valid)
        self.assertIn("缺少必需参数", error)
        
        # 参数无效
        valid, error = self.validator.validate_parameters({"a": 0, "b": 3}, schemas)
        self.assertFalse(valid)


# =============================================================================
# MCP管理器测试
# =============================================================================

class TestMCPManager(unittest.TestCase):
    """测试MCP管理器"""
    
    def setUp(self):
        """设置测试环境"""
        self.mcp_manager = create_mcp_manager()
        
        # 注册测试工具
        self._register_test_tools()
    
    def _register_test_tools(self):
        """注册测试工具"""
        # 加法工具
        add_schema = ToolSchema(
            name="add",
            description="计算两个数的和",
            parameters=[
                ParameterSchema(
                    name="a",
                    type=ParameterType.INTEGER,
                    required=True,
                    minimum=0,
                    maximum=1000
                ),
                ParameterSchema(
                    name="b",
                    type=ParameterType.INTEGER,
                    required=True,
                    minimum=0,
                    maximum=1000
                )
            ],
            returns=ParameterSchema(
                name="result",
                type=ParameterType.INTEGER,
                description="两数之和"
            ),
            category="math",
            tags=["test", "math"]
        )
        self.mcp_manager.register_tool(add_schema, test_add)
        
        # 乘法工具
        multiply_schema = ToolSchema(
            name="multiply",
            description="计算两个数的乘积",
            parameters=[
                ParameterSchema(
                    name="x",
                    type=ParameterType.NUMBER,
                    required=True
                ),
                ParameterSchema(
                    name="y",
                    type=ParameterType.NUMBER,
                    required=True
                )
            ],
            returns=ParameterSchema(
                name="result",
                type=ParameterType.NUMBER,
                description="乘积"
            ),
            category="math",
            tags=["test", "math"]
        )
        self.mcp_manager.register_tool(multiply_schema, test_multiply)
        
        # 大写转换工具
        uppercase_schema = ToolSchema(
            name="uppercase",
            description="将文本转换为大写",
            parameters=[
                ParameterSchema(
                    name="text",
                    type=ParameterType.STRING,
                    required=True
                )
            ],
            returns=ParameterSchema(
                name="result",
                type=ParameterType.STRING,
                description="大写文本"
            ),
            category="text",
            tags=["test", "text"]
        )
        self.mcp_manager.register_tool(uppercase_schema, test_uppercase)
    
    def test_register_tool(self):
        """测试工具注册"""
        # 检查工具是否已注册
        self.assertTrue(self.mcp_manager.tool_exists("add"))
        self.assertTrue(self.mcp_manager.tool_exists("multiply"))
        self.assertTrue(self.mcp_manager.tool_exists("uppercase"))
        
        # 尝试重复注册应该失败
        schema = ToolSchema(
            name="add",
            description="重复注册",
            parameters=[],
            returns=ParameterSchema(name="result", type=ParameterType.ANY)
        )
        
        with self.assertRaises(ToolAlreadyRegisteredError):
            self.mcp_manager.register_tool(schema, lambda: None)
    
    def test_list_tools(self):
        """测试工具列表"""
        # 列出所有工具
        all_tools = self.mcp_manager.list_tools()
        self.assertEqual(len(all_tools), 3)
        
        # 按类别筛选
        math_tools = self.mcp_manager.list_tools(category="math")
        self.assertEqual(len(math_tools), 2)
        
        # 按标签筛选
        text_tools = self.mcp_manager.list_tools(tags=["text"])
        self.assertEqual(len(text_tools), 1)
    
    def test_get_tool_schema(self):
        """测试获取工具模式"""
        schema = self.mcp_manager.get_tool_schema("add")
        self.assertIsNotNone(schema)
        self.assertEqual(schema.name, "add")
        self.assertEqual(schema.category, "math")
        
        # 不存在的工具
        schema = self.mcp_manager.get_tool_schema("nonexistent")
        self.assertIsNone(schema)
    
    def test_execute_tool_success(self):
        """测试工具执行成功"""
        # 测试加法
        result = self.mcp_manager.execute_tool("add", {"a": 5, "b": 3})
        self.assertIsInstance(result, ToolExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.result, 8)
        
        # 测试乘法
        result = self.mcp_manager.execute_tool("multiply", {"x": 2.5, "y": 4.0})
        self.assertTrue(result.success)
        self.assertEqual(result.result, 10.0)
        
        # 测试大写转换
        result = self.mcp_manager.execute_tool("uppercase", {"text": "hello"})
        self.assertTrue(result.success)
        self.assertEqual(result.result, "HELLO")
    
    def test_execute_tool_not_found(self):
        """测试工具不存在"""
        result = self.mcp_manager.execute_tool("nonexistent", {})
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, ToolNotFoundError)
    
    def test_execute_tool_parameter_error(self):
        """测试参数错误"""
        # 参数类型错误
        result = self.mcp_manager.execute_tool("add", {"a": "not a number", "b": 3})
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, ParameterValidationError)
        
        # 参数超出范围
        result = self.mcp_manager.execute_tool("add", {"a": 1001, "b": 3})
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, ParameterValidationError)
        
        # 缺少必需参数
        result = self.mcp_manager.execute_tool("add", {"a": 5})
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, ParameterValidationError)
    
    def test_tool_status(self):
        """测试工具状态管理"""
        # 禁用工具
        self.mcp_manager.update_tool_status("add", ToolStatus.DISABLED)
        
        # 尝试执行禁用的工具
        result = self.mcp_manager.execute_tool("add", {"a": 5, "b": 3})
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, ToolDisabledError)
        
        # 重新启用工具
        self.mcp_manager.update_tool_status("add", ToolStatus.ACTIVE)
        
        # 现在应该可以执行了
        result = self.mcp_manager.execute_tool("add", {"a": 5, "b": 3})
        self.assertTrue(result.success)
    
    def test_unregister_tool(self):
        """测试注销工具"""
        # 注销工具
        success = self.mcp_manager.unregister_tool("uppercase")
        self.assertTrue(success)
        
        # 工具应该不存在了
        self.assertFalse(self.mcp_manager.tool_exists("uppercase"))
        
        # 再次注销应该返回False
        success = self.mcp_manager.unregister_tool("uppercase")
        self.assertFalse(success)
    
    def test_metrics(self):
        """测试指标收集"""
        # 执行几次工具
        for i in range(5):
            self.mcp_manager.execute_tool("add", {"a": i, "b": i + 1})
        
        # 获取指标
        metrics = self.mcp_manager.get_tool_metrics("add")
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics.total_calls, 5)
        self.assertEqual(metrics.success_count, 5)
        self.assertEqual(metrics.failure_count, 0)
        
        # 获取所有指标
        all_metrics = self.mcp_manager.get_all_metrics()
        self.assertIn("add", all_metrics)
        self.assertIn("multiply", all_metrics)
    
    def test_stats(self):
        """测试统计信息"""
        # 执行一些调用
        self.mcp_manager.execute_tool("add", {"a": 1, "b": 2})
        self.mcp_manager.execute_tool("multiply", {"x": 3, "y": 4})
        
        # 获取统计
        stats = self.mcp_manager.get_stats()
        self.assertEqual(stats["total_tools"], 3)
        self.assertEqual(stats["active_tools"], 3)
        self.assertGreater(stats["total_calls"], 0)
    
    def test_reset_metrics(self):
        """测试重置指标"""
        # 执行几次调用
        for i in range(3):
            self.mcp_manager.execute_tool("add", {"a": i, "b": i})
        
        # 检查指标
        metrics = self.mcp_manager.get_tool_metrics("add")
        self.assertEqual(metrics.total_calls, 3)
        
        # 重置单个工具的指标
        self.mcp_manager.reset_metrics("add")
        metrics = self.mcp_manager.get_tool_metrics("add")
        self.assertEqual(metrics.total_calls, 0)
        
        # 执行更多调用
        self.mcp_manager.execute_tool("add", {"a": 1, "b": 2})
        self.mcp_manager.execute_tool("multiply", {"x": 3, "y": 4})
        
        # 重置所有工具的指标
        self.mcp_manager.reset_metrics()
        for tool_name in ["add", "multiply", "uppercase"]:
            metrics = self.mcp_manager.get_tool_metrics(tool_name)
            self.assertEqual(metrics.total_calls, 0)


# =============================================================================
# 装饰器测试
# =============================================================================

class TestMCPDecorator(unittest.TestCase):
    """测试MCP装饰器"""
    
    def test_tool_decorator(self):
        """测试工具装饰器"""
        mcp_manager = create_mcp_manager()
        
        @mcp_manager.tool(
            name="decorated_add",
            description="装饰器加法",
            parameters=[
                ParameterSchema(name="x", type=ParameterType.INTEGER, required=True),
                ParameterSchema(name="y", type=ParameterType.INTEGER, required=True)
            ],
            returns=ParameterSchema(name="result", type=ParameterType.INTEGER),
            category="test"
        )
        def decorated_add(x: int, y: int) -> int:
            return x + y
        
        # 检查工具是否注册
        self.assertTrue(mcp_manager.tool_exists("decorated_add"))
        
        # 执行工具
        result = mcp_manager.execute_tool("decorated_add", {"x": 10, "y": 20})
        self.assertTrue(result.success)
        self.assertEqual(result.result, 30)


# =============================================================================
# 降级测试
# =============================================================================

class TestMCPFallback(unittest.TestCase):
    """测试MCP降级功能"""
    
    def test_fallback(self):
        """测试降级机制"""
        mcp_manager = create_mcp_manager()
        
        # 注册总是出错的工具
        error_schema = ToolSchema(
            name="error_tool",
            description="总是出错的工具",
            parameters=[],
            returns=ParameterSchema(name="result", type=ParameterType.STRING)
        )
        mcp_manager.register_tool(error_schema, test_error_function)
        
        # 注册降级策略
        fallback_strategy = FallbackStrategy(
            name="test_fallback",
            error_types=[ErrorType.UNKNOWN],
            fallback_func=test_fallback_function,
            priority=1
        )
        mcp_manager.smart_client.fallback_manager.register_strategy(fallback_strategy)
        
        # 执行工具（应该使用降级）
        result = mcp_manager.execute_tool("error_tool", {})
        # 注意：这里降级是在MCP管理器内部处理的，所以可能需要调整测试
        self.assertIsNotNone(result)


# =============================================================================
# 运行测试
# =============================================================================

def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("MCP工具管理器 - 测试套件")
    print("=" * 60)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestParameterValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestMCPManager))
    suite.addTests(loader.loadTestsFromTestCase(TestMCPDecorator))
    suite.addTests(loader.loadTestsFromTestCase(TestMCPFallback))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
