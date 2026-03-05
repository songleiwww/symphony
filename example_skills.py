#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例技能模块
展示如何使用技能装饰器创建技能
"""

import random
import time
from typing import Dict, Any, List
from skill_manager import skill


# =============================================================================
# 示例技能 1: 计算器
# =============================================================================

@skill(
    name="calculator",
    version="1.0.0",
    description="简单的计算器技能，支持基本运算",
    tags=["math", "calculator", "utility"],
    category="utility",
    parameters=[
        {
            "name": "operation",
            "type": "string",
            "description": "运算类型: add, subtract, multiply, divide",
            "required": True,
            "enum": ["add", "subtract", "multiply", "divide"]
        },
        {
            "name": "a",
            "type": "number",
            "description": "第一个操作数",
            "required": True
        },
        {
            "name": "b",
            "type": "number",
            "description": "第二个操作数",
            "required": True
        }
    ]
)
def calculator(operation: str, a: float, b: float) -> Dict[str, Any]:
    """计算器技能执行函数"""
    result = 0.0
    
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("除数不能为零")
        result = a / b
    
    return {
        "operation": operation,
        "a": a,
        "b": b,
        "result": result,
        "expression": f"{a} {operation} {b} = {result}"
    }


# =============================================================================
# 示例技能 2: 随机数生成器
# =============================================================================

@skill(
    name="random_generator",
    version="1.0.0",
    description="生成随机数或随机选择",
    tags=["random", "utility", "generator"],
    category="utility",
    parameters=[
        {
            "name": "mode",
            "type": "string",
            "description": "模式: integer, float, choice",
            "required": True,
            "enum": ["integer", "float", "choice"]
        },
        {
            "name": "min",
            "type": "number",
            "description": "最小值（integer/float模式）",
            "required": False,
            "default": 0
        },
        {
            "name": "max",
            "type": "number",
            "description": "最大值（integer/float模式）",
            "required": False,
            "default": 100
        },
        {
            "name": "choices",
            "type": "array",
            "description": "选项列表（choice模式）",
            "required": False,
            "default": []
        },
        {
            "name": "count",
            "type": "number",
            "description": "生成数量",
            "required": False,
            "default": 1,
            "minimum": 1,
            "maximum": 100
        }
    ]
)
def random_generator(
    mode: str,
    min: float = 0,
    max: float = 100,
    choices: List[Any] = None,
    count: int = 1
) -> Dict[str, Any]:
    """随机数生成器执行函数"""
    if choices is None:
        choices = []
    
    results = []
    
    for _ in range(count):
        if mode == "integer":
            results.append(random.randint(int(min), int(max)))
        elif mode == "float":
            results.append(random.uniform(min, max))
        elif mode == "choice":
            if not choices:
                raise ValueError("choice模式需要提供choices列表")
            results.append(random.choice(choices))
    
    return {
        "mode": mode,
        "count": count,
        "results": results,
        "first_result": results[0] if results else None
    }


# =============================================================================
# 示例技能 3: 字符串处理
# =============================================================================

@skill(
    name="string_processor",
    version="1.0.0",
    description="字符串处理工具",
    tags=["string", "text", "utility"],
    category="utility",
    parameters=[
        {
            "name": "operation",
            "type": "string",
            "description": "操作类型: upper, lower, reverse, length, count_words, capitalize",
            "required": True,
            "enum": ["upper", "lower", "reverse", "length", "count_words", "capitalize"]
        },
        {
            "name": "text",
            "type": "string",
            "description": "输入文本",
            "required": True,
            "min_length": 0,
            "max_length": 10000
        }
    ]
)
def string_processor(operation: str, text: str) -> Dict[str, Any]:
    """字符串处理执行函数"""
    result = ""
    info = {}
    
    if operation == "upper":
        result = text.upper()
    elif operation == "lower":
        result = text.lower()
    elif operation == "reverse":
        result = text[::-1]
    elif operation == "length":
        result = str(len(text))
        info["length"] = len(text)
    elif operation == "count_words":
        words = text.split()
        result = str(len(words))
        info["word_count"] = len(words)
        info["char_count"] = len(text)
    elif operation == "capitalize":
        result = text.capitalize()
    
    return {
        "operation": operation,
        "input": text,
        "result": result,
        "info": info
    }


# =============================================================================
# 示例技能 4: 延迟模拟（用于测试重试和超时）
# =============================================================================

@skill(
    name="delay_simulator",
    version="1.0.0",
    description="模拟延迟的技能，用于测试容错机制",
    tags=["test", "utility", "simulation"],
    category="test",
    parameters=[
        {
            "name": "delay",
            "type": "number",
            "description": "延迟秒数",
            "required": False,
            "default": 1.0,
            "minimum": 0,
            "maximum": 60
        },
        {
            "name": "should_fail",
            "type": "boolean",
            "description": "是否应该失败",
            "required": False,
            "default": False
        },
        {
            "name": "fail_rate",
            "type": "number",
            "description": "失败概率 (0-1)",
            "required": False,
            "default": 0.0,
            "minimum": 0.0,
            "maximum": 1.0
        }
    ]
)
def delay_simulator(
    delay: float = 1.0,
    should_fail: bool = False,
    fail_rate: float = 0.0
) -> Dict[str, Any]:
    """延迟模拟器执行函数"""
    start_time = time.time()
    
    # 模拟延迟
    time.sleep(delay)
    
    # 检查是否失败
    actual_fail = should_fail or (random.random() < fail_rate)
    
    if actual_fail:
        raise RuntimeError("模拟的技能执行失败")
    
    execution_time = time.time() - start_time
    
    return {
        "delay": delay,
        "execution_time": execution_time,
        "success": True,
        "message": "延迟模拟完成"
    }


# =============================================================================
# 技能元数据导出
# =============================================================================

# 导出所有技能的元数据，供技能管理器使用
ALL_SKILLS = [
    calculator,
    random_generator,
    string_processor,
    delay_simulator
]


def get_all_skills() -> List:
    """获取所有技能函数"""
    return ALL_SKILLS
