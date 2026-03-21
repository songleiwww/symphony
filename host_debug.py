# -*- coding: utf-8 -*-
import sqlite3
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
kernel_dir = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/'

print('='*60)
print('【宿主Debug检查】')
print('='*60)

# 1. 数据库检查
print('\n1. 数据库状态:')
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('SELECT COUNT(*) FROM 模型配置表')
models = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM 模型配置表 WHERE 在线状态="online"')
online = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM 官署角色表')
roles = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM 序境系统总则')
rules = c.fetchone()[0]

print(f'  模型配置: {models}条 (在线:{online})')
print(f'  官署角色: {roles}条')
print(f'  序境总则: {rules}条')

# 2. 核心文件检查
print('\n2. 核心文件:')
core_files = [
    'Kernel/core/scheduler.py',
    'Kernel/memory/working_memory.py', 
    'Kernel/skills/takeover_skill.py',
    'Kernel/health/kernel_health.py',
]
for f in core_files:
    path = kernel_dir + f
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f'  ✅ {f}: {size}字节')
    else:
        print(f'  ❌ {f}: 不存在')

# 3. 备份检查
print('\n3. 备份目录:')
backup_dirs = ['Kernel/backup', 'Kernel/backup_20260319', 'Kernel/backup_20260321']
for b in backup_dirs:
    path = kernel_dir + b
    if os.path.exists(path):
        files = os.listdir(path)
        print(f'  ✅ {b}: {len(files)}个文件')
    else:
        print(f'  ⚠️ {b}: 不存在')

# 4. 调度器检查
print('\n4. 调度器状态:')
dispatchers = ['Kernel/dispatcher/adaptive_scheduler.py', 'Kernel/dispatcher/batch_scheduler.py', 'Kernel/core/unified_scheduler.py']
for d in dispatchers:
    path = kernel_dir + d
    if os.path.exists(path):
        print(f'  ✅ {d}')
    else:
        print(f'  ❌ {d}')

conn.close()

print('\n' + '='*60)
print('【Debug完成】')
print('='*60)
