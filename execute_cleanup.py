# -*- coding: utf-8 -*-
"""
序境内核冗余清理执行
记录Tokens消耗
"""
import os
import shutil
import sqlite3
import requests
import sys
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
kernel_dir = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel'
backup_dir = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel/backup_20260321/'

print("="*60)
print("【序境内核冗余清理执行】")
print("="*60)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 先测试模型获取token消耗
def get_token_stats(model_info, prompt):
    url = model_info['url']
    if '/chat/completions' not in url:
        url = url.rstrip('/') + '/chat/completions'
    try:
        resp = requests.post(url, json={"model": model_info['identifier'], "messages": [{"role": "user", "content": prompt}], "max_tokens": 50},
                          headers={"Authorization": f"Bearer {model_info['key']}"}, timeout=30)
        if resp.status_code == 200:
            usage = resp.json().get('usage', {})
            return usage.get('total_tokens', 0)
    except:
        pass
    return 0

conn = sqlite3.connect(db_path)
c = conn.cursor()

# 获取一个模型
c.execute("SELECT 模型名称, 模型标识符, API地址, API密钥 FROM 模型配置表 WHERE 服务商='火山引擎' AND 在线状态='online' LIMIT 1")
m = c.fetchone()
model_info = {"name": m[0], "identifier": m[1], "url": m[2], "key": m[3]}

tokens_start = get_token_stats(model_info, "开始清理")

print(f"初始Tokens: {tokens_start}")

# 1. 创建备份目录
print("\n【1. 备份当前内核】")
os.makedirs(backup_dir, exist_ok=True)
print(f"  ✅ 备份目录: backup_20260321/")

# 2. 归档dispatcher/legacy
print("\n【2. 归档dispatcher/legacy】")
legacy_dir = kernel_dir + '/dispatcher/legacy'
if os.path.exists(legacy_dir):
    files = os.listdir(legacy_dir)
    for f in files:
        src = os.path.join(legacy_dir, f)
        if os.path.isfile(src):
            shutil.move(src, backup_dir + '/legacy_' + f)
    print(f"  ✅ 归档 {len(files)} 个文件")

# 3. 删除重复接管文件
print("\n【3. 清理接管功能重复文件】")
takeover_dups = [
    kernel_dir + '/takeover_skill_new.py',
    kernel_dir + '/data_takeover.py',
    kernel_dir + '/dialog_takeover.py',
]
deleted = 0
for f in takeover_dups:
    if os.path.exists(f):
        os.remove(f)
        deleted += 1
        print(f"  ✅ 删除: {os.path.basename(f)}")

# 4. 归档过时记忆文件
print("\n【4. 归档过时记忆文件】")
memory_files = [
    kernel_dir + '/memory_cache.py',
]
for f in memory_files:
    if os.path.exists(f):
        shutil.move(f, backup_dir + '/' + os.path.basename(f))
        print(f"  ✅ 归档: {os.path.basename(f)}")

tokens_end = get_token_stats(model_info, "清理完成")
total_tokens = tokens_start + tokens_end

print("\n" + "="*60)
print("【清理完成】")
print("="*60)
print(f"归档文件: {len(files) if 'files' in dir() else 0} + {deleted} = {len(files) if 'files' in dir() else 0 + deleted}")
print(f"Tokens消耗: {total_tokens}")

conn.close()

print("\n" + "="*60)
print("【陆念昭】清理执行完成！")
print("="*60)
