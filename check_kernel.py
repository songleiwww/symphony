# -*- coding: utf-8 -*-
"""
序境系统 - 内核工具检测
陆念昭调度检查失效工具
"""
import sys
import os
import sqlite3
import importlib
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
kernel_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel'

print("="*60)
print("【陆念昭调度】内核工具检测")
print("="*60)

# 检查内核目录结构
print("\n【1. 内核目录结构】")
for root, dirs, files in os.walk(kernel_path):
    level = root.replace(kernel_path, '').count(os.sep)
    indent = ' ' * 2 * level
    print(f"{indent}{os.path.basename(root)}/")
    if level < 2:
        for f in files:
            if f.endswith('.py'):
                print(f"{indent}  {f}")

# 检查数据库中的工具配置
print("\n【2. 检查模型配置表】")
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 检查各服务商模型数量
c.execute("SELECT 服务商, COUNT(*) FROM 模型配置表 GROUP BY 服务商")
print("\n各服务商模型数量:")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]}")

# 检查官署角色表
c.execute("SELECT COUNT(*) FROM 官署角色表")
print(f"\n官署角色表: {c.fetchone()[0]}个")

# 检查序境系统总则
c.execute("SELECT COUNT(*) FROM 序境系统总则")
print(f"序境系统总则: {c.fetchone()[0]}条")

conn.close()

# 检查核心模块导入
print("\n【3. 核心模块导入测试】")
modules_to_check = [
    ("dynamic_dispatcher", "调度器"),
    ("kernel_loader", "内核加载器"),
    ("config_manager", "配置管理器"),
]

sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony')

for module_name, desc in modules_to_check:
    try:
        # 尝试导入
        spec = importlib.util.find_spec(module_name)
        if spec:
            print(f"  ✅ {module_name} ({desc}): 已安装")
        else:
            print(f"  ❌ {module_name} ({desc}): 未找到")
    except Exception as e:
        print(f"  ❌ {module_name} ({desc}): 错误 {str(e)[:30]}")

# 检查关键文件
print("\n【4. 关键文件检查】")
key_files = [
    "C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel/kernel_loader.py",
    "C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel/config_manager.py",
    "C:/Users/Administrator/.openclaw/workspace/skills/symphony/dynamic_dispatcher.py",
    "C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db",
]

for f in key_files:
    exists = os.path.exists(f)
    status = "✅" if exists else "❌"
    print(f"  {status} {os.path.basename(f)}")

print("\n" + "="*60)
print("【检测完成】")
print("="*60)
