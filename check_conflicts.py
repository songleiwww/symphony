# -*- coding: utf-8 -*-
"""
序境系统 - 内核冲突分析
"""
import os
import sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

kernel_dir = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel'

print("="*60)
print("【序境内核冲突分析】")
print("="*60)

# 1. 功能分类
categories = {
    "调度器": ["scheduler", "dispatcher", "router", "combiner"],
    "记忆系统": ["memory", "cache"],
    "接管功能": ["takeover"],
    "进化功能": ["evolution", "self_", "evolve"],
    "监控功能": ["monitor", "health", "fault"],
    "规则引擎": ["rule"],
    "会话管理": ["session"],
}

# 2. 扫描文件
files = []
for root, dirs, filenames in os.walk(kernel_dir):
    # 跳过特殊目录
    if '__pycache__' in root or 'backup' in root:
        continue
    for f in filenames:
        if f.endswith('.py'):
            files.append(os.path.join(root, f))

print(f"\n扫描文件: {len(files)}个")

# 3. 识别冲突
conflicts = defaultdict(list)

# 调度器冲突
dispatchers = [f for f in files if any(x in f.lower() for x in ['scheduler', 'dispatcher', 'router'])]
print(f"\n【调度器】{len(dispatchers)}个")
for d in dispatchers:
    print(f"  - {d.replace(kernel_dir, '')}")
    conflicts['调度器'].append(d)

# 记忆冲突
memories = [f for f in files if 'memory' in f.lower() or 'cache' in f.lower()]
print(f"\n【记忆系统】{len(memories)}个")
for m in memories:
    print(f"  - {m.replace(kernel_dir, '')}")
    conflicts['记忆系统'].append(m)

# 接管冲突
takeovers = [f for f in files if 'takeover' in f.lower()]
print(f"\n【接管功能】{len(takeovers)}个")
for t in takeovers:
    print(f"  - {t.replace(kernel_dir, '')}")
    conflicts['接管功能'].append(t)

# 进化冲突
evolutions = [f for f in files if 'evolution' in f.lower() or 'self_' in f.lower()]
print(f"\n【进化功能】{len(evolutions)}个")
for e in evolutions:
    print(f"  - {e.replace(kernel_dir, '')}")
    conflicts['进化功能'].append(e)

# 4. 冲突报告
print("\n" + "="*60)
print("【冲突汇总】")
print("="*60)

print(f"""
| 类别 | 数量 | 风险 |
|------|------|------|
| 调度器 | {len(conflicts['调度器'])} | 高 - 多调度器可能冲突 |
| 记忆系统 | {len(conflicts['记忆系统'])} | 中 - 数据可能不一致 |
| 接管功能 | {len(conflicts['接管功能'])} | 高 - 重复接管 |
| 进化功能 | {len(conflicts['进化功能'])} | 中 - 逻辑冲突 |
""")

# 5. 建议
print("【冲突建议】")
print("-"*60)

recommendations = """
1. 调度器整合
   - 保留: core/scheduler.py (统一调度)
   - 合并: adaptive_scheduler.py, batch_scheduler.py
   - 归档: dispatcher/legacy/*

2. 记忆系统整合
   - 保留: memory/working_memory.py (工作记忆)
   - 归档: memory_cache.py (已过时)
   - 统一: evolution/memory_system_v2.py

3. 接管功能整合
   - 保留: skills/takeover_skill.py (最新版)
   - 归档: data_takeover.py, dialog_takeover.py
   - 删除: takeover_skill_new.py (重复)

4. 进化功能整合
   - 保留: evolution/self_evolver.py
   - 归档: self_evolution.py, self_optimization.py
"""

print(recommendations)

# 6. 保存报告
report_path = kernel_dir + '/CONFLICT_REPORT.txt'
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("序境内核冲突分析报告\n")
    f.write("="*60 + "\n")
    f.write(f"扫描时间: 2026-03-21 01:42\n")
    f.write(f"扫描文件: {len(files)}个\n\n")
    for cat, items in conflicts.items():
        f.write(f"\n{cat}: {len(items)}个\n")
        for item in items:
            f.write(f"  - {item}\n")
    f.write(recommendations)

print(f"\n✅ 已保存冲突报告: CONFLICT_REPORT.txt")
