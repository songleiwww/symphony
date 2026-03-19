import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# Get 陆念昭 binding
print("=== 陆念昭官方绑定 ===")
c.execute("""
    SELECT r.id, r.姓名, r.官职, r.所属官署, m.模型名称, m.模型标识符, m.服务商, m.API地址
    FROM 官署角色表 r
    JOIN 模型配置表 m ON r.模型配置表_ID = m.id
    WHERE r.id = 'role-1'
""")
row = c.fetchone()
if row:
    print(f"角色ID: {row[0]}")
    print(f"姓名: {row[1]}")
    print(f"官职: {row[2]}")
    print(f"所属官署: {row[3]}")
    print(f"模型名称: {row[4]}")
    print(f"模型标识符: {row[5]}")
    print(f"服务商: {row[6]}")
    print(f"API地址: {row[7]}")

print("\n=== 测试正确调度 ===")

# Test correct dispatch - use role-1 binding
c.execute("""
    SELECT m.模型标识符, m.API地址, m.API密钥
    FROM 官署角色表 r
    JOIN 模型配置表 m ON r.模型配置表_ID = m.id
    WHERE r.id = 'role-1'
""")
row = c.fetchone()
if row:
    api_id, api_url, api_key = row
    print(f"模型: {api_id}")
    print(f"API: {api_url}")
    
    # Test call
    import requests
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": api_id, "messages": [{"role": "user", "content": "分析当前经济形势"}], "max_tokens": 150}
    
    try:
        resp = requests.post(api_url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            content = result["choices"][0]["message"]["content"]
            print(f"\n✅ 正确调度成功!")
            print(f"响应: {content[:200]}...")
        else:
            print(f"❌ HTTP {resp.status_code}")
    except Exception as e:
        print(f"❌ 错误: {e}")

conn.close()
