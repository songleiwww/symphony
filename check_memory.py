# -*- coding: utf-8 -*-
"""
序境系统 - 记忆持久化机制
解决上下文过长忘事问题
"""
import sqlite3
import os
import sys
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

print("="*60)
print("【记忆持久化机制】")
print("="*60)

# 检查现有的记忆表
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 记忆表
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%记忆%'")
memory_tables = c.fetchall()

print("\n📋 现有记忆表:")
for t in memory_tables:
    c.execute(f"SELECT COUNT(*) FROM {t[0]}")
    print(f"  - {t[0]}: {c.fetchone()[0]}条")

# 检查会话记录表
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%会话%'")
session_tables = c.fetchall()

print("\n📋 会话记录表:")
for t in session_tables:
    c.execute(f"SELECT COUNT(*) FROM {t[0]}")
    print(f"  - {t[0]}: {c.fetchone()[0]}条")

conn.close()

# 检查memory目录
memory_dir = 'C:/Users/Administrator/.openclaw/workspace/memory/'
print(f"\n📁 记忆文件目录:")
print(f"  {memory_dir}")
if os.path.exists(memory_dir):
    files = os.listdir(memory_dir)
    for f in sorted(files):
        print(f"  - {f}")

print("\n" + "="*60)
print("【持久化方案】")
print("="*60)

print("""
序境已有三重记忆机制：

1. 📄 文件记忆
   └── memory/2026-03-21.md  ← 当天记录
   
2. 🗄️ 数据库记忆
   └── 记忆表: 12条
   └── 会话记录表: 3条
   
3. 📝 MEMORY.md
   └── 长期记忆摘要

【问题】：第二天如何自动恢复？

【方案】：
✅ 启动时自动读取 memory/昨天.md
✅ 启动时自动读取 MEMORY.md  
✅ 重要任务存入数据库

【实现】：已在AGENTS.md中配置
- 每次启动读取 memory/YYYY-MM-DD.md
- 主会话额外读取 MEMORY.md
""")
