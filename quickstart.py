#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎼 Symphony 快速启动脚本
5分钟上手 Symphony 统一调度器
"""

import time
import sys

print("=" * 70)
print("🎼 Symphony 统一调度器 - 快速启动")
print("=" * 70)

# 1. 导入 Symphony
print("\n📥 1. 导入 Symphony...")
try:
    from symphony_core import create_symphony, TaskStatus
    print("   ✅ 导入成功!")
except ImportError as e:
    print(f"   ❌ 导入失败: {e}")
    print("   请确保在 multi_agent_demo 目录下运行")
    sys.exit(1)

# 2. 创建实例
print("\n🏗️  2. 创建 Symphony 实例...")
symphony = create_symphony(register_builtins=True)
print("   ✅ 实例创建成功!")

try:
    # 3. 启动调度器
    print("\n🚀 3. 启动调度器 (2个工作线程)...")
    symphony.start(num_workers=2)
    print("   ✅ 调度器已启动!")

    # 4. 查看可用技能
    print("\n📦 4. 查看可用技能...")
    skills = symphony.skill_manager.list_skills()
    print(f"   共发现 {len(skills)} 个技能:")
    for skill in skills:
        print(f"      - {skill.name} ({skill.skill_type.value})")
        if skill.description:
            print(f"        {skill.description}")

    # 5. 提交第一个任务
    print("\n📝 5. 提交第一个任务...")
    task1_id = symphony.submit_task(
        name="问候任务",
        description="测试内置的问候技能",
        skill_name="greet",
        parameters={"name": "Symphony 用户"},
        priority=1,
        tags=["quickstart", "first-task"]
    )
    print(f"   ✅ 任务已提交! ID: {task1_id}")

    # 6. 提交计算任务
    print("\n🧮 6. 提交计算任务...")
    task2_id = symphony.submit_task(
        name="计算任务",
        description="25 * 4 = ?",
        skill_name="calculate",
        parameters={"a": 25, "b": 4, "op": "multiply"},
        priority=2,
        tags=["quickstart", "calculation"]
    )
    print(f"   ✅ 任务已提交! ID: {task2_id}")

    # 7. 等待任务完成
    print("\n⏳ 7. 等待任务完成 (2秒)...")
    time.sleep(2)

    # 8. 查看结果
    print("\n🎉 8. 查看任务结果:")
    for task in symphony.task_queue.list_tasks():
        print(f"\n   📋 任务: {task.name}")
        print(f"      ID: {task.task_id}")
        print(f"      状态: {task.status.value}")
        print(f"      优先级: {task.priority}")

        if task.status == TaskStatus.COMPLETED:
            print(f"      ✅ 结果: {task.result}")
        elif task.status == TaskStatus.FAILED:
            print(f"      ❌ 错误: {task.error}")

        if task.tags:
            print(f"      标签: {', '.join(task.tags)}")

    # 9. 查看系统状态
    print("\n📊 9. 系统状态概览:")
    status = symphony.get_status()
    print(f"   🎯 运行状态: {'运行中' if status['running'] else '已停止'}")
    print(f"   👷 工作线程: {status['workers']}")
    print(f"   📋 总任务数: {status['tasks']['total']}")
    print(f"   ✅ 已完成: {status['tasks']['completed']}")
    print(f"   ❌ 失败: {status['tasks']['failed']}")
    print(f"   🔧 技能总数: {status['skills']['total']}")

    # 10. 查看指标
    print("\n📈 10. 运行指标:")
    metrics = symphony.get_metrics()
    print(f"   技能调用统计:")
    for skill, count in metrics['skill_calls'].items():
        print(f"      - {skill}: {count} 次")
    print(f"   平均任务耗时: {metrics['avg_task_duration']:.3f} 秒")

    print("\n" + "=" * 70)
    print("✨ 快速启动完成!")
    print("=" * 70)
    print("\n📚 下一步:")
    print("   1. 运行 'python symphony_example.py' 查看更多示例")
    print("   2. 阅读 'SYMPHONY_README.md' 了解完整文档")
    print("   3. 查看 'symphony_core.py' 了解核心实现")
    print("   4. 创建你自己的自定义技能!")

finally:
    # 停止调度器
    print("\n🛑 正在停止调度器...")
    symphony.stop()
    print("   ✅ 调度器已停止")

print("\n🎼 感谢使用 Symphony!")
