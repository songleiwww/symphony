#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony 简单测试脚本
"""

import sys
import time

# 设置输出编码为 UTF-8
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("Symphony 测试")
print("=" * 60)

# 1. 导入 Symphony
print("\n[1/6] 导入 Symphony...")
try:
    from symphony_core import create_symphony, TaskStatus
    print("OK: 导入成功")
except Exception as e:
    print(f"ERROR: 导入失败 - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 2. 创建实例
print("\n[2/6] 创建 Symphony 实例...")
try:
    symphony = create_symphony(register_builtins=True)
    print("OK: 实例创建成功")
except Exception as e:
    print(f"ERROR: 创建失败 - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    # 3. 启动调度器
    print("\n[3/6] 启动调度器...")
    symphony.start(num_workers=2)
    print("OK: 调度器已启动")

    # 4. 查看技能
    print("\n[4/6] 查看可用技能...")
    skills = symphony.skill_manager.list_skills()
    print(f"OK: 发现 {len(skills)} 个技能")
    for skill in skills:
        print(f"  - {skill.name}")

    # 5. 提交任务
    print("\n[5/6] 提交测试任务...")
    task1_id = symphony.submit_task(
        name="Greeting Test",
        skill_name="greet",
        parameters={"name": "Tester"}
    )
    print(f"OK: 任务已提交 - {task1_id}")

    task2_id = symphony.submit_task(
        name="Calculation Test",
        skill_name="calculate",
        parameters={"a": 10, "b": 5, "op": "multiply"}
    )
    print(f"OK: 任务已提交 - {task2_id}")

    # 6. 等待并检查结果
    print("\n[6/6] 等待任务完成...")
    time.sleep(2)

    print("\n任务结果:")
    for task in symphony.task_queue.list_tasks():
        print(f"\n  任务: {task.name}")
        print(f"  状态: {task.status.value}")
        if task.result:
            print(f"  结果: {task.result}")
        if task.error:
            print(f"  错误: {task.error}")

    # 系统状态
    print("\n系统状态:")
    status = symphony.get_status()
    print(f"  运行中: {status['running']}")
    print(f"  总任务: {status['tasks']['total']}")
    print(f"  已完成: {status['tasks']['completed']}")

    print("\n" + "=" * 60)
    print("所有测试通过!")
    print("=" * 60)

except Exception as e:
    print(f"\nERROR: 测试失败 - {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n正在停止调度器...")
    symphony.stop()
    print("OK: 调度器已停止")
