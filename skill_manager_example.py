#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响（Symphony）技能管理器 - 使用示例

展示如何使用技能管理器的各种功能
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from skill_manager import (
    SkillManager, SkillConfig, SkillMetadata, SkillParameter, Skill,
    SkillType, skill
)
from example_skills import (
    calculator, random_generator, string_processor, delay_simulator,
    get_all_skills
)


def example_1_basic_usage():
    """示例 1: 基本使用"""
    print("\n" + "=" * 60)
    print("示例 1: 基本使用")
    print("=" * 60)
    
    # 1. 创建配置
    config = SkillConfig(
        skill_dirs=[],
        auto_reload=False,
        default_timeout=30.0,
        default_retries=3
    )
    
    # 2. 创建技能管理器
    skill_manager = SkillManager(config=config)
    
    # 3. 创建一个简单的技能
    metadata = SkillMetadata(
        name="greeting",
        version="1.0.0",
        description="问候技能",
        tags=["greeting", "example"],
        category="example",
        enabled=True
    )
    
    parameters = [
        SkillParameter(
            name="name",
            type="string",
            description="要问候的名字",
            required=True,
            min_length=1,
            max_length=50
        ),
        SkillParameter(
            name="language",
            type="string",
            description="语言: zh, en",
            required=False,
            default="zh",
            enum=["zh", "en"]
        )
    ]
    
    def greet(name: str, language: str = "zh") -> dict:
        if language == "zh":
            return {
                "message": f"你好, {name}!",
                "language": "中文"
            }
        else:
            return {
                "message": f"Hello, {name}!",
                "language": "English"
            }
    
    greeting_skill = Skill(
        metadata=metadata,
        parameters=parameters,
        execute_func=greet
    )
    
    # 4. 注册技能
    skill_manager.loader._loaded_skills["greeting"] = greeting_skill
    
    # 5. 列出所有技能
    print("\n已加载的技能:")
    for skill_obj in skill_manager.list_skills():
        print(f"  - {skill_obj.name}: {skill_obj.metadata.description}")
    
    # 6. 执行技能
    print("\n执行技能:")
    
    # 中文问候
    result = skill_manager.execute_skill(
        "greeting",
        {"name": "交响", "language": "zh"}
    )
    print(f"  中文问候: {result.data['message']}")
    
    # 英文问候
    result = skill_manager.execute_skill(
        "greeting",
        {"name": "Symphony", "language": "en"}
    )
    print(f"  英文问候: {result.data['message']}")
    
    # 使用默认语言
    result = skill_manager.execute_skill(
        "greeting",
        {"name": "世界"}
    )
    print(f"  默认语言: {result.data['message']}")
    
    # 7. 查看统计
    print("\n技能统计:")
    stats = skill_manager.get_skill_stats("greeting")
    print(f"  总调用: {stats.total_calls}")
    print(f"  成功: {stats.success_count}")
    print(f"  平均执行时间: {stats.avg_execution_time:.4f}秒")
    
    skill_manager.shutdown()
    print("\n✓ 示例 1 完成")


def example_2_with_example_skills():
    """示例 2: 使用示例技能"""
    print("\n" + "=" * 60)
    print("示例 2: 使用示例技能")
    print("=" * 60)
    
    config = SkillConfig(skill_dirs=[])
    skill_manager = SkillManager(config=config)
    
    # 注册示例技能
    examples = [
        ("calculator", calculator),
        ("random_generator", random_generator),
        ("string_processor", string_processor),
        ("delay_simulator", delay_simulator)
    ]
    
    for name, func in examples:
        metadata = SkillMetadata(
            name=name,
            version="1.0.0",
            description=f"示例技能: {name}",
            skill_type=SkillType.PYTHON,
            enabled=True
        )
        
        # 从函数获取参数定义（简化版）
        params = []
        if hasattr(func, "SKILL_PARAMETERS"):
            for param_dict in func.SKILL_PARAMETERS:
                params.append(SkillParameter(
                    name=param_dict["name"],
                    type=param_dict.get("type", "string"),
                    description=param_dict.get("description", ""),
                    required=param_dict.get("required", True),
                    default=param_dict.get("default"),
                    enum=param_dict.get("enum", []),
                    minimum=param_dict.get("minimum"),
                    maximum=param_dict.get("maximum")
                ))
        
        skill_obj = Skill(metadata, params, func)
        skill_manager.loader._loaded_skills[name] = skill_obj
    
    print("\n已注册的示例技能:")
    for skill_obj in skill_manager.list_skills():
        print(f"  - {skill_obj.name}")
    
    # 测试计算器
    print("\n--- 计算器技能 ---")
    operations = [
        ("add", 15, 7),
        ("subtract", 20, 8),
        ("multiply", 6, 9),
        ("divide", 100, 4)
    ]
    
    for op, a, b in operations:
        result = skill_manager.execute_skill(
            "calculator",
            {"operation": op, "a": a, "b": b}
        )
        if result.success:
            print(f"  {result.data['expression']}")
    
    # 测试随机生成器
    print("\n--- 随机生成器 ---")
    result = skill_manager.execute_skill(
        "random_generator",
        {"mode": "integer", "min": 1, "max": 100, "count": 5}
    )
    if result.success:
        print(f"  随机整数: {result.data['results']}")
    
    result = skill_manager.execute_skill(
        "random_generator",
        {
            "mode": "choice",
            "choices": ["苹果", "香蕉", "橙子", "葡萄"],
            "count": 3
        }
    )
    if result.success:
        print(f"  随机选择: {result.data['results']}")
    
    # 测试字符串处理
    print("\n--- 字符串处理 ---")
    test_text = "Hello, Symphony Skill Manager!"
    
    result = skill_manager.execute_skill(
        "string_processor",
        {"operation": "upper", "text": test_text}
    )
    print(f"  大写: {result.data['result']}")
    
    result = skill_manager.execute_skill(
        "string_processor",
        {"operation": "count_words", "text": test_text}
    )
    print(f"  词数: {result.data['info']['word_count']}")
    
    result = skill_manager.execute_skill(
        "string_processor",
        {"operation": "reverse", "text": test_text}
    )
    print(f"  反转: {result.data['result']}")
    
    skill_manager.shutdown()
    print("\n✓ 示例 2 完成")


def example_3_search_and_filter():
    """示例 3: 搜索和过滤技能"""
    print("\n" + "=" * 60)
    print("示例 3: 搜索和过滤技能")
    print("=" * 60)
    
    config = SkillConfig(skill_dirs=[])
    skill_manager = SkillManager(config=config)
    
    # 创建一些测试技能
    test_skills = [
        ("math_calculator", "数学计算器", ["math", "calculator"], "utility"),
        ("math_geometry", "几何计算", ["math", "geometry"], "utility"),
        ("text_analyzer", "文本分析", ["text", "nlp"], "ai"),
        ("text_translator", "文本翻译", ["text", "translation"], "utility"),
        ("image_editor", "图片编辑", ["image", "graphics"], "media"),
        ("file_manager", "文件管理", ["file", "system"], "utility")
    ]
    
    for name, desc, tags, category in test_skills:
        metadata = SkillMetadata(
            name=name,
            version="1.0.0",
            description=desc,
            tags=tags,
            category=category,
            skill_type=SkillType.PYTHON,
            enabled=True
        )
        
        skill_obj = Skill(metadata, [], lambda: {"ok": True})
        skill_manager.loader._loaded_skills[name] = skill_obj
    
    print("\n所有技能:")
    for skill_obj in skill_manager.list_skills():
        print(f"  - {skill_obj.name} ({skill_obj.metadata.category})")
    
    # 按分类过滤
    print("\n按分类 'utility' 过滤:")
    utility_skills = skill_manager.list_skills_by_category("utility")
    for skill_obj in utility_skills:
        print(f"  - {skill_obj.name}")
    
    # 搜索
    print("\n搜索 'math':")
    math_skills = skill_manager.search_skills("math")
    for skill_obj in math_skills:
        print(f"  - {skill_obj.name}: {skill_obj.metadata.description}")
    
    print("\n搜索 'text':")
    text_skills = skill_manager.search_skills("text")
    for skill_obj in text_skills:
        print(f"  - {skill_obj.name}: {skill_obj.metadata.description}")
    
    skill_manager.shutdown()
    print("\n✓ 示例 3 完成")


def example_4_error_handling_and_fallback():
    """示例 4: 错误处理和降级"""
    print("\n" + "=" * 60)
    print("示例 4: 错误处理和降级")
    print("=" * 60)
    
    config = SkillConfig(skill_dirs=[])
    skill_manager = SkillManager(config=config)
    
    # 创建一个会失败的技能
    metadata = SkillMetadata(
        name="unreliable_service",
        version="1.0.0",
        description="不可靠的服务",
        skill_type=SkillType.PYTHON,
        enabled=True
    )
    
    call_count = 0
    
    def unreliable_service() -> dict:
        nonlocal call_count
        call_count += 1
        # 前几次调用失败，之后成功
        if call_count <= 2:
            raise RuntimeError(f"服务暂时不可用 (尝试 {call_count}/3)")
        return {"status": "success", "data": "重要数据"}
    
    def fallback_service() -> dict:
        return {
            "status": "degraded",
            "data": "缓存的旧数据",
            "from_fallback": True
        }
    
    skill_obj = Skill(metadata, [], unreliable_service)
    skill_manager.loader._loaded_skills["unreliable_service"] = skill_obj
    
    # 注册降级函数
    skill_manager.register_skill_fallback("unreliable_service", fallback_service)
    
    print("\n测试降级机制:")
    for i in range(4):
        result = skill_manager.execute_skill("unreliable_service", {})
        status = "✓ 成功" if result.success else "✗ 失败"
        source = " (降级)" if result.from_fallback else ""
        print(f"  尝试 {i+1}: {status}{source}")
        if result.success:
            print(f"    数据: {result.data['data']}")
    
    # 测试参数验证错误
    print("\n测试参数验证:")
    metadata2 = SkillMetadata(
        name="param_test",
        version="1.0.0",
        description="参数测试",
        skill_type=SkillType.PYTHON,
        enabled=True
    )
    
    params = [
        SkillParameter(
            name="required_field",
            type="string",
            required=True,
            min_length=3
        )
    ]
    
    skill_obj2 = Skill(metadata2, params, lambda x: {"ok": True})
    skill_manager.loader._loaded_skills["param_test"] = skill_obj2
    
    # 缺少必填参数
    result = skill_manager.execute_skill("param_test", {})
    print(f"  缺少必填参数: {'✗ 正确拦截' if not result.success else '✗ 未拦截'}")
    
    # 参数太短
    result = skill_manager.execute_skill("param_test", {"required_field": "ab"})
    print(f"  参数太短: {'✗ 正确拦截' if not result.success else '✗ 未拦截'}")
    
    # 有效参数
    result = skill_manager.execute_skill("param_test", {"required_field": "valid"})
    print(f"  有效参数: {'✓ 通过' if result.success else '✗ 失败'}")
    
    skill_manager.shutdown()
    print("\n✓ 示例 4 完成")


def example_5_using_decorator():
    """示例 5: 使用装饰器创建技能"""
    print("\n" + "=" * 60)
    print("示例 5: 使用装饰器创建技能")
    print("=" * 60)
    
    config = SkillConfig(skill_dirs=[])
    skill_manager = SkillManager(config=config)
    
    # 使用装饰器定义技能
    @skill(
        name="decorated_skill",
        version="1.0.0",
        description="使用装饰器创建的技能",
        tags=["decorator", "example"],
        category="example",
        parameters=[
            {
                "name": "input",
                "type": "string",
                "description": "输入文本",
                "required": True
            },
            {
                "name": "multiplier",
                "type": "number",
                "description": "重复次数",
                "required": False,
                "default": 2,
                "minimum": 1,
                "maximum": 10
            }
        ]
    )
    def decorated_skill(input: str, multiplier: int = 2) -> dict:
        """使用装饰器的技能函数"""
        return {
            "original": input,
            "result": input * multiplier,
            "multiplier": multiplier,
            "length": len(input) * multiplier
        }
    
    # 手动创建技能对象
    metadata = SkillMetadata(
        name="decorated_skill",
        version="1.0.0",
        description="使用装饰器创建的技能",
        tags=["decorator", "example"],
        category="example",
        skill_type=SkillType.PYTHON,
        enabled=True
    )
    
    parameters = [
        SkillParameter("input", "string", "输入文本", True),
        SkillParameter("multiplier", "number", "重复次数", False, 2, minimum=1, maximum=10)
    ]
    
    skill_obj = Skill(metadata, parameters, decorated_skill)
    skill_manager.loader._loaded_skills["decorated_skill"] = skill_obj
    
    # 测试
    print("\n执行装饰器技能:")
    result = skill_manager.execute_skill(
        "decorated_skill",
        {"input": "Symphony! ", "multiplier": 3}
    )
    
    if result.success:
        print(f"  原始: {result.data['original']}")
        print(f"  结果: {result.data['result']}")
        print(f"  长度: {result.data['length']}")
    
    # 查看装饰器元数据
    print("\n装饰器元数据:")
    if hasattr(decorated_skill, "SKILL_METADATA"):
        print(f"  名称: {decorated_skill.SKILL_METADATA['name']}")
        print(f"  版本: {decorated_skill.SKILL_METADATA['version']}")
        print(f"  描述: {decorated_skill.SKILL_METADATA['description']}")
    
    skill_manager.shutdown()
    print("\n✓ 示例 5 完成")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("交响（Symphony）技能管理器 - 使用示例")
    print("=" * 60)
    
    examples = [
        example_1_basic_usage,
        example_2_with_example_skills,
        example_3_search_and_filter,
        example_4_error_handling_and_fallback,
        example_5_using_decorator
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n✗ 示例执行出错: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("所有示例完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
