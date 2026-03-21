# -*- coding: utf-8 -*-
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
        print(f"\n{key}: {len(vals)}")
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
        print("\n【预览待清理】")
        for path in issues["空文件"] + issues["临时文件"]:
            print(f"  将删除: {path}")
        print("\n使用 cleanup(dry_run=False) 执行清理")
    else:
        print("\n【执行清理】")
        count = 0
        for path in issues["空文件"] + issues["临时文件"]:
            try:
                os.remove(path)
                count += 1
                print(f"  ✅ 删除: {path}")
            except Exception as e:
                print(f"  ❌ 失败: {path} - {e}")
        print(f"\n共清理 {count} 个文件")

if __name__ == "__main__":
    analyze_code()
