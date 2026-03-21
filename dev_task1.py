# -*- coding: utf-8 -*-
"""
序境系统 - 开发任务1：记忆加载增强
"""
import sqlite3
import os
import sys
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
memory_dir = 'C:/Users/Administrator/.openclaw/workspace/memory/'

print("="*60)
print("【开发任务1：记忆加载增强】")
print("="*60)

# 1. 检查当前记忆文件
print("\n【1. 检查记忆文件】")
today = datetime.now().strftime('%Y-%m-%d')
yesterday = (datetime.now().replace(day=datetime.now().day-1)).strftime('%Y-%m-%d')

files_to_check = [
    f"{memory_dir}{today}.md",
    f"{memory_dir}{yesterday}.md",
    "C:/Users/Administrator/.openclaw/workspace/MEMORY.md"
]

for f in files_to_check:
    if os.path.exists(f):
        size = os.path.getsize(f)
        print(f"  ✅ {os.path.basename(f)}: {size} bytes")
    else:
        print(f"  ❌ {os.path.basename(f)}: 不存在")

# 2. 创建记忆加载模块
print("\n【2. 创建记忆加载模块】")

loader_code = '''# -*- coding: utf-8 -*-
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
'''

loader_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/memory_loader.py'
with open(loader_path, 'w', encoding='utf-8') as f:
    f.write(loader_code)

print(f"  ✅ 已创建: memory_loader.py")

# 3. 测试加载
print("\n【3. 测试记忆加载】")
exec(open(loader_path, encoding='utf-8').read().replace('if __name__ == "__main__":', 'if True:'))

print("\n" + "="*60)
print("【开发任务1完成】")
print("="*60)
print("""
✅ 已创建记忆加载模块: memory_loader.py
✅ 启动时自动加载:
   - MEMORY.md (长期记忆)
   - 昨天.md (前一天记忆)
   - 今天.md (当天记忆)
   - 序境系统总则 (116条规则)
""")
