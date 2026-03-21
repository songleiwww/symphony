# -*- coding: utf-8 -*-
"""
序境系统 - 模型健康检测与自动切换
"""
import sqlite3
import requests
import sys
from datetime import datetime

# 修复Windows GBK编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

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
            print(f"[OK] {result['elapsed']:.1f}s")
        elif result['status'] == 'offline':
            results["offline"] += 1
            print(f"[FAIL] {result['error']}")
        else:
            results["error"] += 1
            print(f"[FAIL] {result['error']}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*50)
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
        print(f"\n【{provider} 可用替代模型】")
        for a in alternatives:
            print(f"  - {a[0]}: {a[1]}")
        return alternatives
    else:
        print(f"\n[FAIL] {provider} 没有可用的替代模型")
        return []

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "check":
            check_all_models()
        elif sys.argv[1] == "switch" and len(sys.argv) > 2:
            auto_switch(sys.argv[2])
    else:
        check_all_models()
