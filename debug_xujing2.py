# -*- coding: utf-8 -*-
"""
序境系统 - 综合Debug任务 v2
陆念昭调度多模型进行系统诊断
"""
import sys
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony')

from dynamic_dispatcher import DynamicDispatcher
import requests
import sqlite3
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

# 直接从数据库读取配置
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("="*50)
print("【陆念昭调度】序境系统综合Debug")
print("="*50)

# 任务1：检查模型配置表
c.execute("SELECT COUNT(*) FROM 模型配置表")
model_count = c.fetchone()[0]
print(f"\n【模型配置表】: {model_count}个")

# 任务2：检查官署角色表
c.execute("SELECT COUNT(*) FROM 官署角色表")
role_count = c.fetchone()[0]
print(f"【官署角色表】: {role_count}个")

# 任务3：检查序境系统总则
c.execute("SELECT COUNT(*) FROM 序境系统总则")
rule_count = c.fetchone()[0]
print(f"【序境系统总则】: {rule_count}条")

# 任务4：检查在线状态
c.execute("SELECT 服务商, COUNT(*) FROM 模型配置表 WHERE 在线状态='online' GROUP BY 服务商")
online_stats = c.fetchall()
print(f"\n【在线状态】:")
for provider, count in online_stats:
    print(f"  {provider}: {count}个")

# 检查对齐
print(f"\n【对齐检查】:")
print(f"  模型配置表: {model_count}")
print(f"  官署角色表: {role_count}")
if model_count == role_count:
    print(f"  ✅ 对齐")
else:
    print(f"  ❌ 差{abs(model_count - role_count)}个")

conn.close()

print("\n" + "="*50)
print("【陆念昭】: 诸员辛苦了，序境系统综合Debug完成！")
print("="*50)
