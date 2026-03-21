# -*- coding: utf-8 -*-
"""
序境系统 - 开发任务6：健康检测与自动切换
"""
import sqlite3
import requests
import sys
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("="*60)
print("【开发任务6：健康检测与自动切换】")
print("="*60)

# 1. 创建健康检测表
print("\n【1. 创建健康检测表】")

health_check_sql = """
CREATE TABLE IF NOT EXISTS 模型健康检测表 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    模型名称 TEXT NOT NULL,
    服务商 TEXT NOT NULL,
    检测时间 TEXT NOT NULL,
    状态 TEXT DEFAULT 'unknown',  -- online/offline/error
    响应时间 REAL DEFAULT 0,
    错误信息 TEXT,
    连续失败次数 INTEGER DEFAULT 0
)
"""

try:
    c.execute(health_check_sql)
    print("  ✅ 模型健康检测表已创建")
except Exception as e:
    print(f"  ⚠️ {e}")

# 2. 创建健康检测脚本
print("\n【2. 创建健康检测脚本】")

health_script = '''# -*- coding: utf-8 -*-
"""
序境系统 - 模型健康检测与自动切换
"""
import sqlite3
import requests
import sys
from datetime import datetime

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db"

def health_check_model(model_info):
    """检测单个模型健康状态"""
    url = model_info["api_url"]
    if "/chat/completions" not in url:
        url = url.rstrip("/") + "/chat/completions"
    
    start = datetime.now()
    try:
        resp = requests.post(url, json={
            "model": model_info["identifier"],
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 5
        }, headers={"Authorization": f"Bearer {model_info['api_key']}"}, timeout=15)
        
        elapsed = (datetime.now() - start).total_seconds()
        
        if resp.status_code == 200:
            return {"status": "online", "elapsed": elapsed, "error": None}
        else:
            return {"status": "offline", "elapsed": elapsed, "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        elapsed = (datetime.now() - start).total_seconds()
        return {"status": "error", "elapsed": elapsed, "error": str(e)}

def check_all_models():
    """检测所有模型健康状态"""
    print("="*50)
    print("【模型健康检测】")
    print("="*50)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 获取所有在线模型
    c.execute("SELECT id, 模型名称, 模型标识符, API地址, API密钥, 服务商 FROM 模型配置表 WHERE 在线状态='online'")
    models = c.fetchall()
    
    results = {"online": 0, "offline": 0, "error": 0}
    
    for m in models:
        model_info = {
            "id": m[0], "name": m[1], "identifier": m[2],
            "api_url": m[3], "api_key": m[4], "provider": m[5]
        }
        
        print(f"检测: {model_info['name']}...", end=" ")
        result = health_check_model(model_info)
        
        # 记录到数据库
        c.execute("""INSERT INTO 模型健康检测表 
            (模型名称, 服务商, 检测时间, 状态, 响应时间, 错误信息) 
            VALUES (?, ?, ?, ?, ?, ?)""",
            (model_info['name'], model_info['provider'], 
             datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
             result['status'], result['elapsed'], result['error']))
        
        if result['status'] == 'online':
            results["online"] += 1
            print(f"✅ {result['elapsed']:.1f}s")
        elif result['status'] == 'offline':
            results["offline"] += 1
            print(f"❌ {result['error']}")
        else:
            results["error"] += 1
            print(f"❌ {result['error']}")
    
    conn.commit()
    conn.close()
    
    print("\\n" + "="*50)
    print("【检测结果】")
    print("="*50)
    print(f"在线: {results['online']}")
    print(f"离线: {results['offline']}")
    print(f"错误: {results['error']}")
    
    return results

def auto_switch(provider):
    """自动切换到同服务商其他可用模型"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 查找同服务商可用的其他模型
    c.execute("""SELECT 模型名称, 模型标识符 FROM 模型配置表 
        WHERE 服务商=? AND 在线状态='online' 
        ORDER BY 评分 DESC LIMIT 3""", (provider,))
    
    alternatives = c.fetchall()
    conn.close()
    
    if alternatives:
        print(f"\\n【{provider} 可用替代模型】")
        for a in alternatives:
            print(f"  - {a[0]}: {a[1]}")
        return alternatives
    else:
        print(f"\\n❌ {provider} 没有可用的替代模型")
        return []

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "check":
            check_all_models()
        elif sys.argv[1] == "switch" and len(sys.argv) > 2:
            auto_switch(sys.argv[2])
    else:
        check_all_models()
'''

health_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/health_check.py'
with open(health_path, 'w', encoding='utf-8') as f:
    f.write(health_script)

print(f"  ✅ 已创建: health_check.py")

# 3. 快速测试
print("\n【3. 快速测试健康检测】")
c.execute("SELECT 模型名称, 模型标识符, API地址, API密钥, 服务商 FROM 模型配置表 WHERE 在线状态='online' LIMIT 3")
test_models = c.fetchall()

for m in test_models:
    name, identifier, url, key, provider = m
    if '/chat/completions' not in url:
        url = url.rstrip('/') + '/chat/completions'
    
    print(f"  检测: {name}...", end=" ")
    try:
        resp = requests.post(url, json={"model": identifier, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5},
                          headers={"Authorization": f"Bearer {key}"}, timeout=10)
        if resp.status_code == 200:
            print("✅ online")
        else:
            print(f"❌ {resp.status_code}")
    except Exception as e:
        print(f"❌ 错误")

conn.close()

print("\n" + "="*60)
print("【开发任务6完成】")
print("="*60)
print("""
✅ 健康检测表: 模型健康检测表
✅ 检测脚本: health_check.py
✅ 自动切换: 同服务商可用模型列表

使用:
  python health_check.py check    # 检测所有模型
  python health_check.py switch 服务商  # 查看可切换模型
""")
