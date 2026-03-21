# -*- coding: utf-8 -*-
"""
序境系统 - 自动化回归测试
自动测试所有在线模型
"""
import sqlite3
import requests
import sys
import json
from datetime import datetime

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db"

def test_model(model_info):
    """测试单个模型"""
    url = model_info["api_url"]
    if "/chat/completions" not in url:
        url = url.rstrip("/") + "/chat/completions"
    
    try:
        resp = requests.post(url, json={
            "model": model_info["identifier"],
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 10
        }, headers={"Authorization": f"Bearer {model_info['api_key']}"}, timeout=30)
        
        if resp.status_code == 200:
            return {"status": "pass", "model": model_info["name"], "provider": model_info["provider"]}
        else:
            return {"status": "fail", "model": model_info["name"], "error": resp.status_code, "provider": model_info["provider"]}
    except Exception as e:
        return {"status": "error", "model": model_info["name"], "error": str(e), "provider": model_info["provider"]}

def run_tests():
    """运行所有测试"""
    print("="*50)
    print("【序境系统自动化回归测试】")
    print("="*50)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, 模型名称, 模型标识符, API地址, API密钥, 服务商 FROM 模型配置表 WHERE 在线状态='online'")
    models = c.fetchall()
    
    results = {"pass": 0, "fail": 0, "error": 0, "tests": []}
    
    for m in models:
        model_info = {
            "id": m[0], "name": m[1], "identifier": m[2],
            "api_url": m[3], "api_key": m[4], "provider": m[5]
        }
        print(f"测试: {model_info['name']}...", end=" ")
        result = test_model(model_info)
        
        results["tests"].append(result)
        
        if result["status"] == "pass":
            results["pass"] += 1
            print("✅")
        elif result["status"] == "fail":
            results["fail"] += 1
            print(f"❌ {result.get('error')}")
        else:
            results["error"] += 1
            print(f"❌ {result.get('error')}")
    
    conn.close()
    
    print("\n" + "="*50)
    print("【测试结果】")
    print("="*50)
    print(f"通过: {results['pass']}/{len(models)}")
    print(f"失败: {results['fail']}")
    print(f"错误: {results['error']}")
    
    # 保存结果
    with open("test_results.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    return results

if __name__ == "__main__":
    run_tests()
