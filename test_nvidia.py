# -*- coding: utf-8 -*-
"""
序境系统 - 英伟达模型在线检测
陆念昭调度测试
"""
import sqlite3
import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 检查英伟达API配置
print("="*60)
print("【陆念昭调度】英伟达模型在线检测")
print("="*60)

c.execute("SELECT API地址, API密钥 FROM 模型配置表 WHERE 服务商='英伟达' LIMIT 1")
row = c.fetchone()
api_url = row[0] if row else None
api_key = row[1] if row else None

print(f"\n【API配置】")
print(f"  URL: {api_url}")
print(f"  Key: {api_key[:30]}...")

# 确保URL正确
if '/chat/completions' not in api_url:
    api_url = api_url.rstrip('/') + '/chat/completions'
    print(f"  修正URL: {api_url}")

# 获取所有英伟达模型
c.execute("SELECT id, 模型名称, 模型标识符 FROM 模型配置表 WHERE 服务商='英伟达'")
models = c.fetchall()

print(f"\n【测试模型】共{len(models)}个")
print("-"*60)

results = []
for mid, mname, identifier in models:
    print(f"\n测试: {mname}")
    print(f"  标识符: {identifier}")
    
    try:
        resp = requests.post(
            api_url,
            json={"model": identifier, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 10},
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=20
        )
        status = resp.status_code
        print(f"  状态码: {status}")
        
        if status == 200:
            print(f"  ✅ 在线")
            results.append((mid, mname, identifier, "online"))
        else:
            print(f"  ❌ 不在线: {resp.text[:50]}")
            results.append((mid, mname, identifier, "offline"))
    except Exception as e:
        print(f"  ❌ 错误: {str(e)[:30]}")
        results.append((mid, mname, identifier, "offline"))

print("\n" + "="*60)
print("【汇总】")
print("="*60)

online_count = sum(1 for r in results if r[3] == "online")
offline_count = sum(1 for r in results if r[3] == "offline")

for r in results:
    status = "✅" if r[3] == "online" else "❌"
    print(f"{status} {r[1]}: {r[3]}")

print(f"\n在线: {online_count}/{len(results)}")
print(f"不在线: {offline_count}/{len(results)}")

# 更新数据库
print("\n【更新状态】")
for mid, mname, identifier, status in results:
    c.execute("UPDATE 模型配置表 SET 在线状态=? WHERE id=?", (status, mid))
    print(f"  {mname}: {status}")

conn.commit()
conn.close()

print("\n" + "="*60)
print("【陆念昭】检测完成！")
print("="*60)
