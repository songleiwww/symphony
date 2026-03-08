#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响系统清理脚本
删除测试、老版本、不使用的文件
"""
import os
import shutil
import glob

# 交响目录
symphony_dir = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony'

# 需要删除的文件模式
delete_patterns = [
    # 测试文件
    'test_*.py', 'test_*.json',
    '*_test.py', '*_test.json',
    'debug_test*.py', 'debug_test*.json',
    # 老版本 v0.x
    'v0*.py', 'v0*.md', 'v0*.json',
    # 老版本 v1.x (保留v1.0.0)
    'v1[0-9]_*.py', 'v1[0-9]_*.md', 'v1[0-9]_*.json',
    # 老版本 v2.x
    'v2*.py', 'v2*.md', 'v2*.json',
    # 老版本 v3.0-3.8
    'v3[0-8]*',
    # 临时文件
    '__pycache__', '*.pyc',
    # 备份文件
    '*.bak', '*.backup',
    # 重复文件
    '*_old.py', '*_backup.py',
    '*_fix.py', '*_v2.py', '*_v3.py', '*_v4.py',
]

# 需要保留的目录和文件
keep_files = [
    'config.py', 'model_manager.py', 'skill_manager.py', 
    'fault_tolerance.py', 'memory_system.py', 'symphony_core.py',
    'mcp_manager.py', 'rate_limit_manager.py',
    'requirements.txt', 'README.md', 'VERSION.md',
    # 保留最新的开发文件
    'v390', 'v391', 'v392', 'v393', 'v394', 'v395', 'v396', 'v397',
    # 保留核心文档
    'SKILL.md', 'docs/', 'examples/', 'tests/',
]

# 需要保留的文件（精确匹配）
keep_exact = [
    'config.py', 'model_manager.py', 'skill_manager.py',
    'fault_tolerance.py', 'memory_system.py', 'symphony_core.py',
    'mcp_manager.py', 'rate_limit_manager.py', 'retry_manager.py',
    'requirements.txt', 'README.md', 'VERSION.md', 'CHANGELOG.md',
    'SKILL.md', 'Dockerfile', 'setup.py', 'package.json',
    '.gitignore', 'LICENSE', 'CITATION.cff',
    # 青丘相关
    'qingqiu_conf_v3925.py', 'qingqiu_conf_v3925.json',
    'symphony_enhance_v3924.py', 'symphony_enhance_v3924.json',
    'hunter_suggestion_v3926.py', 'hunter_suggestion_v3926.json',
    # v3.9.x
    'multi_turn_v3921.py', 'multi_turn_v3921.json',
    'multi_turn_large_v3922.py', 'multi_turn_large_v3922.json',
    'data_flywheel_v3923.py', 'data_flywheel_v3923.json',
    'vector_adaptive_v3918.py', 'vector_adaptive_v3918.json',
    'vector_collab_v3920.py', 'vector_collab_v3920.json',
    'improvement_plan_v3913.py', 'improvement_plan_v3913.json',
    'openclaw_integration_v395.py', 'openclaw_integration_v395.json',
    'dialog_config_v3912.py',
    'smart_symphony_v3919.py', 'smart_symphony_v3919.json',
    'scheduling_strategy_v393.py', 'scheduling_strategy_v393.json',
    'segmented_processing_v394.py', 'segmented_processing_v394.json',
]

# 目录保留
keep_dirs = ['.git', '.github', 'adapter', 'avatars', 'docs', 'examples', 'outputs', 'symphony_long_term_memory', 'symphony_memory', 'tests', 'test_memory_temp', 'todo']

deleted_count = 0
kept_count = 0

print("="*60)
print("交响系统清理开始")
print("="*60)

# 获取所有文件
all_files = []
for root, dirs, files in os.walk(symphony_dir):
    # 保留特定目录
    dirs[:] = [d for d in dirs if d in keep_dirs]
    for f in files:
        all_files.append(os.path.join(root, f))

# 分析文件
for filepath in all_files:
    filename = os.path.basename(filepath)
    rel_path = os.path.relpath(filepath, symphony_dir)
    
    # 精确保留
    if filename in keep_exact:
        kept_count += 1
        continue
    
    # 检查是否匹配删除模式
    should_delete = False
    for pattern in delete_patterns:
        if '*' in pattern:
            if glob.fnmatch.fnmatch(filename, pattern):
                should_delete = True
                break
        else:
            if filename == pattern:
                should_delete = True
                break
    
    if should_delete:
        try:
            os.remove(filepath)
            print(f"删除: {rel_path}")
            deleted_count += 1
        except Exception as e:
            print(f"删除失败: {rel_path} - {e}")
    else:
        kept_count += 1

print()
print("="*60)
print("清理完成")
print("="*60)
print(f"保留文件: {kept_count}")
print(f"删除文件: {deleted_count}")
print("="*60)

# 清理空的__pycache__目录
for root, dirs, files in os.walk(symphony_dir, topdown=False):
    for d in dirs:
        if d == '__pycache__':
            try:
                os.rmdir(os.path.join(root, d))
                print(f"删除目录: {os.path.join(root, d)}")
            except:
                pass
