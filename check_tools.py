# -*- coding: utf-8 -*-
"""
序境系统 - 工具失效检测
"""
import sys
import os
import importlib.util
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony')
sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("【工具失效检测】")
print("="*60)

# 检查各目录的Python文件
dirs_to_check = [
    ("Kernel/", "C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel"),
    ("Kernel/core/", "C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel/core"),
    ("Kernel/dispatcher/", "C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel/dispatcher"),
    ("Kernel/evolution/", "C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel/evolution"),
    ("Kernel/monitor/", "C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel/monitor"),
    ("Kernel/rules/", "C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel/rules"),
]

all_files = []
for name, path in dirs_to_check:
    if os.path.exists(path):
        files = [f for f in os.listdir(path) if f.endswith('.py') and not f.startswith('__')]
        all_files.extend([(name, f) for f in files])

print(f"\n【检测 {len(all_files)} 个Python文件】")
print("-"*60)

# 尝试导入每个模块
working = []
broken = []

for dir_name, file_name in all_files:
    module_name = file_name.replace('.py', '')
    path = [p for p, n in dirs_to_check if n.endswith(dir_name.rstrip('/'))][0] if dir_name else "C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel"
    
    full_path = os.path.join(path, file_name)
    
    try:
        spec = importlib.util.spec_from_file_location(module_name, full_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            working.append(file_name)
            print(f"  ✅ {file_name}")
    except Exception as e:
        broken.append((file_name, str(e)[:50]))
        print(f"  ❌ {file_name}: {str(e)[:40]}")

print("\n" + "="*60)
print(f"【汇总】")
print(f"  正常: {len(working)}个")
print(f"  失效: {len(broken)}个")

if broken:
    print("\n【失效文件】")
    for f, e in broken:
        print(f"  ❌ {f}: {e}")

print("="*60)
