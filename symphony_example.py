#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎼 Symphony 统一调度器 - 使用示例和演示
展示 Symphony 的各种功能和用法
"""

import time
import json
from typing import Dict, Any

# 导入 Symphony 核心
from symphony_core import (
    SymphonyCore,
    create_symphony,
    Skill,
    SkillType,
    TaskStatus
)


def example_1_basic_usage():
    """示例1: 基本用法 - 创建调度器并提交简单任务"""
    print("\n" + "=" * 70)
    print("示例1: 基本用法 - 创建调度器并提交简单任务")
    print("=" * 70)

    # 创建 Symphony 实例
    symphony = create_symphony(register_builtins=True)

    try:
        # 启动调度器
        symphony.start(num_workers=2)

        # 提交问候任务
        print("\n📝 提交问候任务...")
        task_id = symphony.submit_task(
            name="问候测试",
            description="测试内置的问候技能",
            skill_name="greet",
            parameters={"name": "Symphony 用户"},
            priority=1,
            tags=["demo", "greeting"]
        )
        print(f"   任务ID: {task_id}")

        # 提交计算任务
        print("\n🧮 提交计算任务...")
        task_id2 = symphony.submit_task(
            name="计算测试",
            description="测试内置的计算技能",
            skill_name="calculate",
            parameters={"a": 25, "b": 5, "op": "multiply"},
            priority=2,
            tags=["demo", "calculation"]
        )
        print(f"   任务ID: {task_id2}")

        # 等待任务完成
        print("\n⏳ 等待任务完成...")
        time.sleep(2)

        # 检查任务结果
        print("\n✅ 任务结果:")
        for task in symphony.task_queue.list_tasks():
            print(f"\n   任务: {task.name} ({task.task_id})")
            print(f"   状态: {task.status.value}")
            if task.result:
                print(f"   结果: {task.result}")
            if task.error:
                print(f"   错误: {task.error}")

        # 显示系统状态
        print("\n📊 系统状态:")
        status = symphony.get_status()
        print(f"   总任务数: {status['tasks']['total']}")
        print(f"   已完成: {status['tasks']['completed']}")
        print(f"   技能总数: {status['skills']['total']}")

    finally:
        symphony.stop()


def example_2_custom_skills():
    """示例2: 注册和使用自定义技能"""
    print("\n" + "=" * 70)
    print("示例2: 注册和使用自定义技能")
    print("=" * 70)

    symphony = create_symphony(register_builtins=True)

    try:
        # 定义自定义技能
        def weather_skill(city: str, unit: str = "celsius") -> Dict[str, Any]:
            """
            天气查询技能（模拟）
            """
            weather_data = {
                "北京": {"temp": 15, "condition": "晴", "humidity": 45},
                "上海": {"temp": 20, "condition": "多云", "humidity": 65},
                "深圳": {"temp": 28, "condition": "阵雨", "humidity": 75},
            }

            city_data = weather_data.get(city, {"temp": 22, "condition": "未知", "humidity": 50})

            if unit == "fahrenheit":
                city_data["temp"] = city_data["temp"] * 9/5 + 32

            return {
                "city": city,
                "temperature": city_data["temp"],
                "unit": unit,
                "condition": city_data["condition"],
                "humidity": city_data["humidity"],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

        # 注册自定义技能
        print("\n🔧 注册自定义技能...")
        weather_skill_obj = Skill(
            name="weather",
            skill_type=SkillType.CUSTOM,
            description="查询城市天气信息",
            version="1.0.0",
            handler=weather_skill,
            parameters_schema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "default": "celsius"}
                },
                "required": ["city"]
            },
            tags=["weather", "utility"]
        )
        symphony.skill_manager.register_skill(weather_skill_obj)
        print("   ✅ 天气查询技能已注册")

        # 启动调度器
        symphony.start(num_workers=2)

        # 提交天气查询任务
        print("\n🌤️  提交天气查询任务...")
        cities = ["北京", "上海", "深圳", "广州"]

        for city in cities:
            task_id = symphony.submit_task(
                name=f"天气查询 - {city}",
                description=f"查询{city}的天气信息",
                skill_name="weather",
                parameters={"city": city, "unit": "celsius"},
                priority=1,
                tags=["weather", city]
            )
            print(f"   📍 {city}: {task_id}")

        # 等待任务完成
        print("\n⏳ 等待天气查询完成...")
        time.sleep(3)

        # 显示天气结果
        print("\n🌡️  天气查询结果:")
        for task in symphony.task_queue.list_tasks():
            if "天气查询" in task.name and task.result:
                result = task.result
                print(f"\n   📍 {result['city']}")
                print(f"      温度: {result['temperature']}°{result['unit'].upper()[0]}")
                print(f"      天气: {result['condition']}")
                print(f"      湿度: {result['humidity']}%")
                print(f"      更新时间: {result['timestamp']}")

    finally:
        symphony.stop()


def example_3_task_dependencies():
    """示例3: 任务依赖关系"""
    print("\n" + "=" * 70)
    print("示例3: 任务依赖关系")
    print("=" * 70)

    symphony = create_symphony(register_builtins=True)

    try:
        # 注册更多自定义技能用于演示
        def fetch_data_skill(source: str) -> Dict[str, Any]:
            """获取数据"""
            time.sleep(0.5)  # 模拟耗时
            return {
                "source": source,
                "data": [1, 2, 3, 4, 5],
                "fetched_at": time.time()
            }

        def process_data_skill(data: list, multiplier: int = 2) -> Dict[str, Any]:
            """处理数据"""
            time.sleep(0.3)  # 模拟耗时
            processed = [x * multiplier for x in data]
            return {
                "original": data,
                "processed": processed,
                "sum": sum(processed),
                "average": sum(processed) / len(processed)
            }

        def generate_report_skill(results: Dict[str, Any]) -> str:
            """生成报告"""
            time.sleep(0.2)  # 模拟耗时
            return f"""
📊 数据处理报告
================
数据源: {results.get('source', 'unknown')}
原始数据: {results.get('original', [])}
处理后数据: {results.get('processed', [])}
总和: {results.get('sum', 0)}
平均值: {results.get('average', 0):.2f}
生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()

        # 注册技能
        fetch_skill = Skill(
            name="fetch_data",
            skill_type=SkillType.CUSTOM,
            handler=fetch_data_skill,
            description="获取源数据"
        )

        process_skill = Skill(
            name="process_data",
            skill_type=SkillType.CUSTOM,
            handler=process_data_skill,
            description="处理数据"
        )

        report_skill = Skill(
            name="generate_report",
            skill_type=SkillType.CUSTOM,
            handler=generate_report_skill,
            description="生成报告"
        )

        symphony.skill_manager.register_skill(fetch_skill)
        symphony.skill_manager.register_skill(process_skill)
        symphony.skill_manager.register_skill(report_skill)

        # 启动调度器
        symphony.start(num_workers=3)

        print("\n🔗 创建有依赖关系的任务...")

        # 任务1: 获取数据
        task1_id = symphony.submit_task(
            name="1. 获取数据",
            skill_name="fetch_data",
            parameters={"source": "database_A"},
            priority=3
        )
        print(f"   任务1: {task1_id}")

        # 任务2: 处理数据（依赖任务1）
        task2_id = symphony.submit_task(
            name="2. 处理数据",
            skill_name="process_data",
            parameters={"data": [1, 2, 3], "multiplier": 3},
            priority=2,
            dependencies=[task1_id]
        )
        print(f"   任务2: {task2_id} (依赖: {task1_id})")

        # 任务3: 生成报告（依赖任务2）
        task3_id = symphony.submit_task(
            name="3. 生成报告",
            skill_name="generate_report",
            parameters={"results": {}},
            priority=1,
            dependencies=[task2_id]
        )
        print(f"   任务3: {task3_id} (依赖: {task2_id})")

        # 等待任务完成
        print("\n⏳ 等待任务链执行...")
        time.sleep(3)

        # 显示执行顺序
        print("\n📋 任务执行状态:")
        for task in sorted(symphony.task_queue.list_tasks(), key=lambda t: t.created_at):
            emoji = "✅" if task.status == TaskStatus.COMPLETED else "⏳"
            print(f"   {emoji} {task.name} - {task.status.value}")
            if task.dependencies:
                print(f"      依赖: {task.dependencies}")

    finally:
        symphony.stop()


def example_4_priority_queuing():
    """示例4: 优先级队列"""
    print("\n" + "=" * 70)
    print("示例4: 优先级队列")
    print("=" * 70)

    symphony = create_symphony(register_builtins=True)

    try:
        # 注册一个模拟耗时的技能
        def slow_skill(task_name: str, delay: float = 0.5) -> str:
            """模拟耗时操作"""
            time.sleep(delay)
            return f"{task_name} 完成于 {time.strftime('%H:%M:%S')}"

        slow_skill_obj = Skill(
            name="slow_task",
            skill_type=SkillType.CUSTOM,
            handler=slow_skill
        )
        symphony.skill_manager.register_skill(slow_skill_obj)

        # 启动调度器（只用1个工作线程，便于观察优先级）
        symphony.start(num_workers=1)

        print("\n🎯 提交不同优先级的任务...")
        print("   (优先级数字越大，优先级越高)")

        # 按低到高的顺序提交，但高优先级会先执行
        tasks_info = [
            ("低优先级任务", 0),
            ("中优先级任务", 5),
            ("高优先级任务", 10),
            ("紧急任务", 100),
        ]

        submitted_tasks = []
        for name, priority in tasks_info:
            task_id = symphony.submit_task(
                name=name,
                skill_name="slow_task",
                parameters={"task_name": name, "delay": 0.3},
                priority=priority
            )
            submitted_tasks.append((task_id, name, priority))
            print(f"   📤 {name} (优先级: {priority}) -> {task_id}")

        # 等待任务完成
        print("\n⏳ 等待任务执行（观察执行顺序）...")
        time.sleep(2)

        # 显示实际执行顺序（按完成时间）
        print("\n📊 实际执行顺序:")
        completed_tasks = [
            t for t in symphony.task_queue.list_tasks()
            if t.status == TaskStatus.COMPLETED and t.completed_at
        ]
        completed_tasks.sort(key=lambda t: t.completed_at)

        for i, task in enumerate(completed_tasks, 1):
            print(f"   {i}. {task.name} (优先级: {task.priority})")

    finally:
        symphony.stop()


def example_5_error_handling():
    """示例5: 错误处理和重试"""
    print("\n" + "=" * 70)
    print("示例5: 错误处理和重试")
    print("=" * 70)

    symphony = create_symphony(register_builtins=True)

    try:
        # 注册一个会随机失败的技能
        fail_count = 0

        def flaky_skill(task_name: str, fail_rate: float = 0.5) -> str:
            """不稳定的技能，会随机失败"""
            nonlocal fail_count

            import random
            if random.random() < fail_rate:
                fail_count += 1
                raise RuntimeError(f"模拟失败 #{fail_count}")

            return f"{task_name} 成功执行!"

        flaky_skill_obj = Skill(
            name="flaky_skill",
            skill_type=SkillType.CUSTOM,
            handler=flaky_skill
        )
        symphony.skill_manager.register_skill(flaky_skill_obj)

        # 启动调度器
        symphony.start(num_workers=2)

        print("\n🔄 提交会自动重试的任务...")

        # 提交任务，设置最大重试次数
        task_id = symphony.submit_task(
            name="不稳定任务",
            description="这个任务会随机失败，但会自动重试",
            skill_name="flaky_skill",
            parameters={"task_name": "测试任务", "fail_rate": 0.6},
            max_retries=5,
            priority=1
        )
        print(f"   任务ID: {task_id}")
        print(f"   最大重试次数: 5")

        # 等待任务完成
        print("\n⏳ 等待任务执行（可能会重试几次）...")
        time.sleep(4)

        # 检查任务状态
        task = symphony.task_queue.get_task_status(task_id)
        if task:
            print(f"\n📋 任务最终状态:")
            print(f"   名称: {task.name}")
            print(f"   状态: {task.status.value}")
            print(f"   重试次数: {task.retry_count}/{task.max_retries}")

            if task.result:
                print(f"   ✅ 结果: {task.result}")
            if task.error:
                print(f"   ❌ 错误: {task.error}")

        # 显示系统错误统计
        print("\n📊 系统错误统计:")
        metrics = symphony.get_metrics()
        if metrics['error_counts']:
            for error, count in metrics['error_counts'].items():
                print(f"   {error}: {count}次")
        else:
            print("   无错误记录")

    finally:
        symphony.stop()


def example_6_metrics_and_monitoring():
    """示例6: 指标收集和监控"""
    print("\n" + "=" * 70)
    print("示例6: 指标收集和监控")
    print("=" * 70)

    symphony = create_symphony(register_builtins=True)

    try:
        # 注册一些技能用于产生指标
        def fast_skill() -> str:
            time.sleep(0.1)
            return "fast"

        def medium_skill() -> str:
            time.sleep(0.3)
            return "medium"

        def slow_skill() -> str:
            time.sleep(0.5)
            return "slow"

        for name, handler in [("fast", fast_skill), ("medium", medium_skill), ("slow", slow_skill)]:
            skill = Skill(
                name=name,
                skill_type=SkillType.CUSTOM,
                handler=handler
            )
            symphony.skill_manager.register_skill(skill)

        # 启动调度器
        symphony.start(num_workers=3)

        print("\n📈 提交多个任务以生成指标...")

        # 提交多个任务
        skill_names = ["fast", "medium", "slow", "greet", "calculate"]
        for i in range(10):
            skill_name = skill_names[i % len(skill_names)]
            params = {}
            if skill_name == "greet":
                params = {"name": f"User{i}"}
            elif skill_name == "calculate":
                params = {"a": i, "b": i * 2, "op": "add"}

            symphony.submit_task(
                name=f"任务-{i}",
                skill_name=skill_name,
                parameters=params
            )

        # 等待任务完成
        print("\n⏳ 等待任务完成...")
        time.sleep(3)

        # 显示详细指标
        print("\n📊 Symphony 指标详情:")
        status = symphony.get_status()
        metrics = symphony.get_metrics()

        print(f"\n   🎯 总体统计:")
        print(f"      总任务数: {status['tasks']['total']}")
        print(f"      已完成: {status['tasks']['completed']}")
        print(f"      失败: {status['tasks']['failed']}")
        print(f"      成功率: {status['tasks']['completed']/status['tasks']['total']*100:.1f}%" if status['tasks']['total'] > 0 else "      成功率: N/A")

        print(f"\n   ⏱️  时间统计:")
        print(f"      总耗时: {metrics['total_duration']:.2f}s")
        print(f"      平均任务耗时: {metrics['avg_task_duration']:.3f}s")

        print(f"\n   🔧 技能调用统计:")
        for skill, count in sorted(metrics['skill_calls'].items(), key=lambda x: -x[1]):
            print(f"      {skill}: {count}次")

        print(f"\n   💾 系统状态:")
        print(f"      工作线程: {status['workers']}")
        print(f"      技能总数: {status['skills']['total']}")
        print(f"      内置技能: {status['skills']['builtin']}")
        print(f"      自定义技能: {status['skills']['custom']}")

        # 导出指标为JSON
        print(f"\n💾 导出指标为JSON:")
        metrics_json = json.dumps(metrics, indent=2, ensure_ascii=False)
        print("   " + metrics_json[:200] + "..." if len(metrics_json) > 200 else "   " + metrics_json)

    finally:
        symphony.stop()


def main():
    """运行所有示例"""
    print("🎼" * 35)
    print("🎼" + " " * 31 + "🎼")
    print("🎼    Symphony 统一调度器 - 完整演示    🎼")
    print("🎼" + " " * 31 + "🎼")
    print("🎼" * 35)

    examples = [
        ("基本用法", example_1_basic_usage),
        ("自定义技能", example_2_custom_skills),
        ("任务依赖", example_3_task_dependencies),
        ("优先级队列", example_4_priority_queuing),
        ("错误处理", example_5_error_handling),
        ("指标监控", example_6_metrics_and_monitoring),
    ]

    for i, (name, func) in enumerate(examples, 1):
        try:
            print(f"\n\n{'='*70}")
            print(f"🎬 开始示例 {i}/{len(examples)}: {name}")
            print('='*70)
            func()
            print(f"\n✅ 示例 {i} 完成!")
        except Exception as e:
            print(f"\n❌ 示例 {i} 执行出错: {e}")
            import traceback
            traceback.print_exc()

        # 示例之间的短暂停顿
        if i < len(examples):
            time.sleep(1)

    print("\n" + "="*70)
    print("🎉 所有示例演示完成!")
    print("="*70)
    print("\n📚 更多信息:")
    print("   - 查看 symphony_core.py 了解核心实现")
    print("   - 查看 SYMPHONY_README.md 了解完整文档")
    print("   - 运行单个示例: 修改 main() 函数")


if __name__ == "__main__":
    # 可以取消注释下面的行来单独运行某个示例
    # example_1_basic_usage()
    # example_2_custom_skills()
    # example_3_task_dependencies()
    # example_4_priority_queuing()
    # example_5_error_handling()
    # example_6_metrics_and_monitoring()

    main()
