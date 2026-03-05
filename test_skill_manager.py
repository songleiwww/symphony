#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能管理器测试
测试技能发现、加载、调用、参数验证和错误处理
"""

import sys
import io
import os
import time
import logging
from pathlib import Path

# 修复Windows编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from skill_manager import (
    SkillManager, SkillConfig, SkillMetadata, SkillParameter, Skill,
    SkillType, SkillStatus, SkillExecutionResult,
    SkillNotFoundError, SkillParameterError, SkillExecutionError
)
from fault_tolerance import RetryConfig, CircuitBreakerConfig
from example_skills import (
    calculator, random_generator, string_processor, delay_simulator
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_basic_functionality():
    """测试基本功能"""
    print("\n" + "=" * 60)
    print("测试 1: 基本功能")
    print("=" * 60)
    
    # 创建技能管理器
    config = SkillConfig(
        skill_dirs=[],
        auto_reload=False
    )
    
    skill_manager = SkillManager(config=config)
    
    # 创建计算器技能
    calc_metadata = SkillMetadata(
        name="test_calculator",
        version="1.0.0",
        description="测试计算器",
        tags=["test", "math"],
        skill_type=SkillType.PYTHON,
        category="test",
        enabled=True
    )
    
    calc_parameters = [
        SkillParameter(
            name="operation",
            type="string",
            description="运算类型",
            required=True,
            enum=["add", "subtract"]
        ),
        SkillParameter(
            name="a",
            type="number",
            description="操作数A",
            required=True
        ),
        SkillParameter(
            name="b",
            type="number",
            description="操作数B",
            required=True
        )
    ]
    
    def calc_execute(operation: str, a: float, b: float) -> dict:
        if operation == "add":
            return {"result": a + b}
        elif operation == "subtract":
            return {"result": a - b}
        else:
            raise ValueError(f"不支持的运算: {operation}")
    
    calc_skill = Skill(
        metadata=calc_metadata,
        parameters=calc_parameters,
        execute_func=calc_execute
    )
    
    # 手动添加到管理器
    skill_manager.loader._loaded_skills["test_calculator"] = calc_skill
    
    # 测试技能列表
    skills = skill_manager.list_skills()
    assert len(skills) == 1
    assert skills[0].name == "test_calculator"
    print("✓ 技能列表测试通过")
    
    # 测试技能获取
    skill = skill_manager.get_skill("test_calculator")
    assert skill is not None
    assert skill.name == "test_calculator"
    print("✓ 技能获取测试通过")
    
    # 测试搜索
    search_results = skill_manager.search_skills("calculator")
    assert len(search_results) == 1
    print("✓ 技能搜索测试通过")
    
    # 测试执行
    result = skill_manager.execute_skill(
        "test_calculator",
        {"operation": "add", "a": 2, "b": 3}
    )
    assert result.success
    assert result.data["result"] == 5
    print(f"✓ 技能执行测试通过: 2 + 3 = {result.data['result']}")
    
    skill_manager.shutdown()
    print("✓ 基本功能测试完成")


def test_parameter_validation():
    """测试参数验证"""
    print("\n" + "=" * 60)
    print("测试 2: 参数验证")
    print("=" * 60)
    
    config = SkillConfig(skill_dirs=[])
    skill_manager = SkillManager(config=config)
    
    # 创建带参数验证的技能
    metadata = SkillMetadata(
        name="test_param_validation",
        version="1.0.0",
        description="参数验证测试",
        skill_type=SkillType.PYTHON,
        enabled=True
    )
    
    parameters = [
        SkillParameter(
            name="required_param",
            type="string",
            description="必填参数",
            required=True,
            min_length=2,
            max_length=10
        ),
        SkillParameter(
            name="optional_param",
            type="number",
            description="可选参数",
            required=False,
            default=42,
            minimum=0,
            maximum=100
        ),
        SkillParameter(
            name="enum_param",
            type="string",
            description="枚举参数",
            required=True,
            enum=["option1", "option2", "option3"]
        )
    ]
    
    def execute_func(required_param: str, optional_param: int, enum_param: str) -> dict:
        return {
            "required": required_param,
            "optional": optional_param,
            "enum": enum_param
        }
    
    skill = Skill(
        metadata=metadata,
        parameters=parameters,
        execute_func=execute_func
    )
    
    skill_manager.loader._loaded_skills["test_param_validation"] = skill
    
    # 测试 1: 缺少必填参数
    result = skill_manager.execute_skill(
        "test_param_validation",
        {"enum_param": "option1"}
    )
    assert not result.success
    print("✓ 缺少必填参数验证通过")
    
    # 测试 2: 参数太短
    result = skill_manager.execute_skill(
        "test_param_validation",
        {"required_param": "a", "enum_param": "option1"}
    )
    assert not result.success
    print("✓ 最小长度验证通过")
    
    # 测试 3: 参数太长
    result = skill_manager.execute_skill(
        "test_param_validation",
        {"required_param": "this is way too long", "enum_param": "option1"}
    )
    assert not result.success
    print("✓ 最大长度验证通过")
    
    # 测试 4: 枚举值不匹配
    result = skill_manager.execute_skill(
        "test_param_validation",
        {"required_param": "test", "enum_param": "invalid_option"}
    )
    assert not result.success
    print("✓ 枚举值验证通过")
    
    # 测试 5: 数值超出范围
    result = skill_manager.execute_skill(
        "test_param_validation",
        {"required_param": "test", "enum_param": "option1", "optional_param": 150}
    )
    assert not result.success
    print("✓ 数值范围验证通过")
    
    # 测试 6: 有效参数 + 默认值
    result = skill_manager.execute_skill(
        "test_param_validation",
        {"required_param": "test", "enum_param": "option1"}
    )
    assert result.success
    assert result.data["optional"] == 42
    print("✓ 默认值应用测试通过")
    
    # 测试 7: 完全有效的参数
    result = skill_manager.execute_skill(
        "test_param_validation",
        {
            "required_param": "hello",
            "optional_param": 50,
            "enum_param": "option2"
        }
    )
    assert result.success
    assert result.data["required"] == "hello"
    assert result.data["optional"] == 50
    assert result.data["enum"] == "option2"
    print("✓ 完全有效参数测试通过")
    
    skill_manager.shutdown()
    print("✓ 参数验证测试完成")


def test_error_handling():
    """测试错误处理"""
    print("\n" + "=" * 60)
    print("测试 3: 错误处理")
    print("=" * 60)
    
    config = SkillConfig(skill_dirs=[])
    skill_manager = SkillManager(config=config)
    
    # 测试 1: 技能不存在
    result = skill_manager.execute_skill("nonexistent_skill", {})
    assert not result.success
    assert "未找到" in result.error or "not found" in result.error.lower()
    print("✓ 技能不存在错误处理通过")
    
    # 创建会抛出异常的技能
    metadata = SkillMetadata(
        name="test_error_skill",
        version="1.0.0",
        description="错误测试技能",
        skill_type=SkillType.PYTHON,
        enabled=True
    )
    
    def error_execute() -> dict:
        raise RuntimeError("这是一个测试错误")
    
    skill = Skill(
        metadata=metadata,
        parameters=[],
        execute_func=error_execute
    )
    
    skill_manager.loader._loaded_skills["test_error_skill"] = skill
    
    # 测试 2: 技能执行错误
    result = skill_manager.execute_skill("test_error_skill", {})
    assert not result.success
    assert "测试错误" in result.error
    print("✓ 技能执行错误处理通过")
    
    # 测试 3: 降级函数
    def fallback_func() -> dict:
        return {"result": "这是降级结果", "from_fallback": True}
    
    skill_manager.register_skill_fallback("test_error_skill", fallback_func)
    
    result = skill_manager.execute_skill("test_error_skill", {})
    assert result.success
    assert result.from_fallback
    assert result.data["from_fallback"] is True
    print("✓ 降级函数测试通过")
    
    skill_manager.shutdown()
    print("✓ 错误处理测试完成")


def test_statistics():
    """测试统计功能"""
    print("\n" + "=" * 60)
    print("测试 4: 统计功能")
    print("=" * 60)
    
    config = SkillConfig(skill_dirs=[])
    skill_manager = SkillManager(config=config)
    
    # 创建简单技能
    metadata = SkillMetadata(
        name="test_stats_skill",
        version="1.0.0",
        description="统计测试技能",
        skill_type=SkillType.PYTHON,
        enabled=True
    )
    
    execution_count = 0
    
    def stats_execute(should_fail: bool = False) -> dict:
        nonlocal execution_count
        execution_count += 1
        if should_fail:
            raise RuntimeError("故意失败")
        return {"count": execution_count}
    
    skill = Skill(
        metadata=metadata,
        parameters=[
            SkillParameter(
                name="should_fail",
                type="boolean",
                required=False,
                default=False
            )
        ],
        execute_func=stats_execute
    )
    
    skill_manager.loader._loaded_skills["test_stats_skill"] = skill
    
    # 执行几次成功调用
    for i in range(3):
        result = skill_manager.execute_skill("test_stats_skill", {})
        assert result.success
    
    # 执行几次失败调用
    for i in range(2):
        result = skill_manager.execute_skill("test_stats_skill", {"should_fail": True})
        assert not result.success
    
    # 检查统计
    stats = skill_manager.get_skill_stats("test_stats_skill")
    assert stats is not None
    assert stats.total_calls == 5
    assert stats.success_count == 3
    assert stats.failure_count == 2
    assert stats.avg_execution_time > 0
    
    print(f"✓ 统计测试通过:")
    print(f"  - 总调用: {stats.total_calls}")
    print(f"  - 成功: {stats.success_count}")
    print(f"  - 失败: {stats.failure_count}")
    print(f"  - 平均执行时间: {stats.avg_execution_time:.6f}秒")
    
    # 检查所有统计
    all_stats = skill_manager.get_all_stats()
    assert "test_stats_skill" in all_stats
    
    skill_manager.shutdown()
    print("✓ 统计功能测试完成")


def test_example_skills():
    """测试示例技能"""
    print("\n" + "=" * 60)
    print("测试 5: 示例技能")
    print("=" * 60)
    
    config = SkillConfig(skill_dirs=[])
    skill_manager = SkillManager(config=config)
    
    # 测试计算器技能
    calc_metadata = SkillMetadata(
        name="calculator",
        version="1.0.0",
        description="计算器",
        skill_type=SkillType.PYTHON,
        enabled=True
    )
    
    calc_params = [
        SkillParameter(
            name="operation", type="string", required=True,
            enum=["add", "subtract", "multiply", "divide"]
        ),
        SkillParameter(name="a", type="number", required=True),
        SkillParameter(name="b", type="number", required=True)
    ]
    
    calc_skill = Skill(calc_metadata, calc_params, calculator)
    skill_manager.loader._loaded_skills["calculator"] = calc_skill
    
    # 测试加法
    result = skill_manager.execute_skill(
        "calculator",
        {"operation": "add", "a": 10, "b": 5}
    )
    assert result.success
    assert result.data["result"] == 15
    print(f"✓ 计算器加法: 10 + 5 = {result.data['result']}")
    
    # 测试除法
    result = skill_manager.execute_skill(
        "calculator",
        {"operation": "divide", "a": 10, "b": 2}
    )
    assert result.success
    assert result.data["result"] == 5
    print(f"✓ 计算器除法: 10 / 2 = {result.data['result']}")
    
    # 测试字符串处理技能
    string_metadata = SkillMetadata(
        name="string_processor",
        version="1.0.0",
        description="字符串处理",
        skill_type=SkillType.PYTHON,
        enabled=True
    )
    
    string_params = [
        SkillParameter(
            name="operation", type="string", required=True,
            enum=["upper", "lower", "reverse", "length", "count_words", "capitalize"]
        ),
        SkillParameter(name="text", type="string", required=True)
    ]
    
    string_skill = Skill(string_metadata, string_params, string_processor)
    skill_manager.loader._loaded_skills["string_processor"] = string_skill
    
    # 测试大写转换
    result = skill_manager.execute_skill(
        "string_processor",
        {"operation": "upper", "text": "Hello World"}
    )
    assert result.success
    assert result.data["result"] == "HELLO WORLD"
    print(f"✓ 字符串大写: 'Hello World' -> '{result.data['result']}'")
    
    # 测试词数统计
    result = skill_manager.execute_skill(
        "string_processor",
        {"operation": "count_words", "text": "This is a test sentence"}
    )
    assert result.success
    assert result.data["info"]["word_count"] == 5
    print(f"✓ 词数统计: '{result.data['input']}' -> {result.data['info']['word_count']} 词")
    
    skill_manager.shutdown()
    print("✓ 示例技能测试完成")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("交响（Symphony）技能管理器 - 完整测试套件")
    print("=" * 60)
    
    tests = [
        test_basic_functionality,
        test_parameter_validation,
        test_error_handling,
        test_statistics,
        test_example_skills
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            logger.exception(f"测试失败: {test.__name__}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试总结: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
