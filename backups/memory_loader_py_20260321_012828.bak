# -*- coding: utf-8 -*-
"""
序境系统 - 记忆加载模块
解决上下文过长忘事问题
"""
import sqlite3
import os
from datetime import datetime

MEMORY_DIR = "C:/Users/Administrator/.openclaw/workspace/memory/"
DB_PATH = "C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db"

def load_memory_on_startup():
    """启动时加载记忆"""
    print("="*50)
    print("【序境系统启动加载】")
    print("="*50)
    
    loaded = []
    
    # 1. 加载长期记忆
    mem_path = "C:/Users/Administrator/.openclaw/workspace/MEMORY.md"
    if os.path.exists(mem_path):
        with open(mem_path, 'r', encoding='utf-8') as f:
            content = f.read()
            loaded.append(("MEMORY.md", len(content)))
            print(f"✅ 加载 MEMORY.md: {len(content)}字符")
    
    # 2. 加载昨天记忆
    yesterday = (datetime.now().replace(day=datetime.now().day-1)).strftime('%Y-%m-%d')
    yesterday_path = f"{MEMORY_DIR}{yesterday}.md"
    if os.path.exists(yesterday_path):
        with open(yesterday_path, 'r', encoding='utf-8') as f:
            content = f.read()
            loaded.append((f"{yesterday}.md", len(content)))
            print(f"✅ 加载 {yesterday}.md: {len(content)}字符")
    
    # 3. 加载今天记忆
    today = datetime.now().strftime('%Y-%m-%d')
    today_path = f"{MEMORY_DIR}{today}.md"
    if os.path.exists(today_path):
        with open(today_path, 'r', encoding='utf-8') as f:
            content = f.read()
            loaded.append((f"{today}.md", len(content)))
            print(f"✅ 加载 {today}.md: {len(content)}字符")
    
    # 4. 加载序境系统总则
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM 序境系统总则")
    rules_count = c.fetchone()[0]
    loaded.append(("序境系统总则", rules_count))
    print(f"✅ 加载 序境系统总则: {rules_count}条")
    conn.close()
    
    print("="*50)
    print(f"【加载完成】共 {len(loaded)} 项")
    print("="*50)
    
    return loaded

if __name__ == "__main__":
    load_memory_on_startup()
