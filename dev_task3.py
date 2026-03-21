# -*- coding: utf-8 -*-
"""
序境系统 - 开发任务3：自动化回归测试
为在线模型编写测试脚本
"""
import sqlite3
import requests
import sys
import json
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("="*60)
print("【开发任务3：自动化回归测试】")
print("="*60)

# 1. 获取所有在线模型
print("\n【1. 获取在线模型】")
c.execute("SELECT id, 模型名称, 模型标识符, API地址, API密钥, 服务商 FROM 模型配置表 WHERE 在线状态='online'")
models = c.fetchall()
print(f"  在线模型: {len(models)}个")

# 2. 生成测试脚本
print("\n【2. 生成测试脚本】")

test_script = '''# -*- coding: utf-8 -*-
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
    
    print("\\n" + "="*50)
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
'''

test_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/auto_test.py'
with open(test_path, 'w', encoding='utf-8') as f:
    f.write(test_script)

print(f"  ✅ 已创建: auto_test.py")

# 3. 快速测试（只测3个）
print("\n【3. 快速验证测试】")
c.execute("SELECT 模型名称, 模型标识符, API地址, API密钥, 服务商 FROM 模型配置表 WHERE 在线状态='online' LIMIT 3")
test_models = c.fetchall()

pass_count = 0
for m in test_models:
    name, identifier, url, key, provider = m
    if '/chat/completions' not in url:
        url = url.rstrip('/') + '/chat/completions'
    
    print(f"  测试: {name}...", end=" ")
    try:
        resp = requests.post(url, json={"model": identifier, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 10},
                          headers={"Authorization": f"Bearer {key}"}, timeout=15)
        if resp.status_code == 200:
            print("✅")
            pass_count += 1
        else:
            print(f"❌ {resp.status_code}")
    except Exception as e:
        print(f"❌ 错误")

print(f"\n  快速测试: {pass_count}/3 通过")

conn.close()

print("\n" + "="*60)
print("【开发任务3完成】")
print("="*60)
print("""
✅ 测试脚本: auto_test.py
✅ 运行方式: python auto_test.py
✅ 可集成到CI/CD

后续迭代前运行此测试，确保核心功能正常。
""")
