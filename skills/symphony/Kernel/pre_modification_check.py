#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修改前扫描工具 - 防线1
所有修改核心文件/数据库前必须执行，检查不通过禁止修改
"""
import os
import sys
import re

# 配置
SYMPHONY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_DB = os.path.join(SYMPHONY_ROOT, 'data', 'symphony.db')
KNOWN_PITFALLS = [
    (r"DROP TABLE.*\*", "禁止使用DROP TABLE *删除所有表"),
    (r"sqlite3\.connect.*backup.*\.db", "禁止直接连接备份目录数据库作为运行库"),
    (r"C:/Users/Administrator/\.openclaw/skills/symphony", "禁止使用错误的根路径，必须包含workspace"),
    (r"DB_PATH.*=.*[\"'].*\.db[\"']", "禁止硬编码数据库路径，必须从统一配置读取")
]

def check_utf8_encoding():
    """检查所有核心Python文件是否有UTF-8编码声明"""
    errors = []
    kernel_files = [f for f in os.listdir(os.path.join(SYMPHONY_ROOT, 'Kernel')) if f.endswith('.py')]
    for f in kernel_files:
        path = os.path.join(SYMPHONY_ROOT, 'Kernel', f)
        with open(path, 'r', encoding='utf-8', errors='replace') as fp:
            first_line = fp.readline()
            if not first_line.startswith('# -*- coding: utf-8 -*-'):
                errors.append(f"文件 {f} 缺少UTF-8编码声明")
    return errors

def check_db_backup_exists():
    """检查数据库是否已备份"""
    backup_dir = os.path.join(SYMPHONY_ROOT, 'backup')
    backups = [f for f in os.listdir(backup_dir) if 'backup' in f and f.endswith('.db')]
    if not backups:
        return ["数据库未备份，禁止修改操作"]
    latest = max(backups, key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)))
    latest_time = os.path.getmtime(os.path.join(backup_dir, latest))
    import time
    if time.time() - latest_time > 3600:  # 1小时内没有新备份
        return ["数据库备份已过时，请先备份再修改"]
    return []

def check_pitfalls():
    """扫描是否存在已知坑点"""
    errors = []
    for root, _, files in os.walk(SYMPHONY_ROOT):
        for f in files:
            if f.endswith('.py') and 'backup' not in root:
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8', errors='replace') as fp:
                    content = fp.read()
                    for pattern, msg in KNOWN_PITFALLS:
                        if re.search(pattern, content):
                            errors.append(f"文件 {os.path.relpath(path, SYMPHONY_ROOT)}: {msg}")
    return errors

def main():
    print("🔍 开始修改前扫描（防线1）...")
    all_errors = []
    
    # 检查编码
    enc_errors = check_utf8_encoding()
    all_errors.extend(enc_errors)
    
    # 检查备份
    backup_errors = check_db_backup_exists()
    all_errors.extend(backup_errors)
    
    # 检查坑点
    pit_errors = check_pitfalls()
    all_errors.extend(pit_errors)
    
    if all_errors:
        print("❌ 扫描不通过，禁止修改操作：")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("✅ 扫描通过，可以执行修改操作")
        sys.exit(0)

if __name__ == "__main__":
    main()
