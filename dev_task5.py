# -*- coding: utf-8 -*-
"""
序境系统 - 开发任务5：静态分析与安全清理
"""
import sqlite3
import os
import sys
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
symphony_dir = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/'

print("="*60)
print("【开发任务5：静态分析与安全清理】")
print("="*60)

# 1. 代码分析
print("\n【1. 代码静态分析】")

# 扫描Python文件
python_files = []
for root, dirs, files in os.walk(symphony_dir):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            size = os.path.getsize(path)
            python_files.append({'path': path, 'name': f, 'size': size})

print(f"  Python文件: {len(python_files)}个")

# 2. 识别冗余/死亡代码
print("\n【2. 识别潜在问题】")

issues = []

# 检查空文件
for pf in python_files:
    if pf['size'] == 0:
        issues.append({'type': '空文件', 'file': pf['name'], 'severity': 'warn'})

# 检查大文件
for pf in python_files:
    if pf['size'] > 50000:  # 50KB+
        issues.append({'type': '大文件', 'file': pf['name'], 'size': pf['size'], 'severity': 'info'})

# 检查临时文件
temp_patterns = ['_backup', '_old', '_temp', '__pycache__']
for pf in python_files:
    for tp in temp_patterns:
        if tp in pf['name']:
            issues.append({'type': '临时文件', 'file': pf['name'], 'severity': 'info'})

print(f"  发现问题: {len(issues)}项")
for i in issues[:10]:
    print(f"    [{i['severity']}] {i['type']}: {i['file']}")

# 3. 创建清理脚本
print("\n【3. 创建安全清理脚本】")

cleanup_script = '''# -*- coding: utf-8 -*-
"""
序境系统 - 安全清理模块
"""
import os
import shutil
from datetime import datetime

SYMPHONY_DIR = "C:/Users/Administrator/.openclaw/workspace/skills/symphony/"

def analyze_code():
    """分析代码健康度"""
    print("="*50)
    print("【代码健康度分析】")
    print("="*50)
    
    issues = {"空文件": [], "大文件": [], "临时文件": [], "孤立文件": []}
    
    for root, dirs, files in os.walk(SYMPHONY_DIR):
        # 跳过特殊目录
        if '__pycache__' in root or '.git' in root:
            continue
            
        for f in files:
            if not f.endswith('.py'):
                continue
                
            path = os.path.join(root, f)
            size = os.path.getsize(path)
            
            if size == 0:
                issues["空文件"].append(path)
            elif size > 50000:
                issues["大文件"].append((path, size))
            if '_backup' in f or '_old' in f or '_temp' in f:
                issues["临时文件"].append(path)
    
    for key, vals in issues.items():
        print(f"\\n{key}: {len(vals)}")
        for v in vals[:5]:
            if isinstance(v, tuple):
                print(f"  - {os.path.basename(v[0])} ({v[1]} bytes)")
            else:
                print(f"  - {os.path.basename(v)}")
    
    return issues

def safe_cleanup(dry_run=True):
    """安全清理（默认只报告不删除）"""
    issues = analyze_code()
    
    if dry_run:
        print("\\n【预览待清理】")
        for path in issues["空文件"] + issues["临时文件"]:
            print(f"  将删除: {path}")
        print("\\n使用 cleanup(dry_run=False) 执行清理")
    else:
        print("\\n【执行清理】")
        count = 0
        for path in issues["空文件"] + issues["临时文件"]:
            try:
                os.remove(path)
                count += 1
                print(f"  ✅ 删除: {path}")
            except Exception as e:
                print(f"  ❌ 失败: {path} - {e}")
        print(f"\\n共清理 {count} 个文件")

if __name__ == "__main__":
    analyze_code()
'''

cleanup_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/safe_cleanup.py'
with open(cleanup_path, 'w', encoding='utf-8') as f:
    f.write(cleanup_script)

print(f"  ✅ 已创建: safe_cleanup.py")

# 4. 运行分析
print("\n【4. 运行健康度分析】")
exec(open(cleanup_path, encoding='utf-8').read().replace('if __name__ == "__main__":', 'if True:'))

print("\n" + "="*60)
print("【开发任务5完成】")
print("="*60)
print("""
✅ 分析脚本: safe_cleanup.py
✅ 运行方式: python safe_cleanup.py
✅ 支持dry_run模式（预览不删除）

建议：先用dry_run预览，确认后再执行清理。
""")
