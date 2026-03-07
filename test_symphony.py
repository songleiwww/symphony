#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v1.4.1 - 集成测试
"""
import sys
import json
import time
import requests
import threading
from datetime import datetime
from config import MODEL_CHAIN

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


VERSION = "1.4.1"


def test_symphony_system():
    """测试Symphony系统"""
    
    print("=" * 80)
    print(f"🎼 Symphony v{VERSION} - 集成测试")
    print("=" * 80)
    
    total_tokens = 0
    test_results = []
    
    # 测试1: 检查配置
    print("\n🧪 测试1: 配置检查")
    enabled = [m for m in MODEL_CHAIN if m.get("enabled")]
    if len(enabled) > 0:
        print(f"   ✅ 配置正常 - {len(enabled)}个模型可用")
        test_results.append({"test": "配置检查", "status": "PASS"})
    else:
        print(f"   ❌ 配置异常 - 无可用模型")
        test_results.append({"test": "配置检查", "status": "FAIL"})
    
    # 测试2: API调用
    print("\n🧪 测试2: API调用测试")
    model = enabled[0]
    url = model["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model["api_key"], "Content-Type": "application/json"}
    data = {"model": model["model_id"], "messages": [{"role": "user", "content": "测试"}], "max_tokens": 20}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=15)
        if r.status_code == 200:
            j = r.json()
            tokens = j.get("usage", {}).get("total_tokens", 0)
            total_tokens += tokens
            print(f"   ✅ API调用成功 - {tokens} tokens")
            test_results.append({"test": "API调用", "status": "PASS", "tokens": tokens})
        else:
            print(f"   ❌ API调用失败 - HTTP {r.status_code}")
            test_results.append({"test": "API调用", "status": "FAIL"})
    except Exception as e:
        print(f"   ❌ API调用异常 - {str(e)[:50]}")
        test_results.append({"test": "API调用", "status": "FAIL", "error": str(e)})
    
    # 测试3: 多模型协作
    print("\n🧪 测试3: 多模型协作测试")
    
    def call_model(idx, prompt):
        if idx >= len(enabled):
            return None
        m = enabled[idx]
        url = m["base_url"] + "/chat/completions"
        headers = {"Authorization": "Bearer " + m["api_key"], "Content-Type": "application/json"}
        data = {"model": m["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": 30}
        try:
            r = requests.post(url, headers=headers, json=data, timeout=15)
            if r.status_code == 200:
                return r.json()
        except:
            pass
        return None
    
    results = {}
    lock = threading.Lock()
    
    def test_model(idx):
        result = call_model(idx, "测试协作")
        with lock:
            if result:
                results[idx] = {"success": True, "tokens": result.get("usage", {}).get("total_tokens", 0)}
            else:
                results[idx] = {"success": False, "tokens": 0}
    
    # 并行测试3个模型
    threads = []
    for i in range(min(3, len(enabled))):
        t = threading.Thread(target=test_model, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    success_count = sum(1 for r in results.values() if r["success"])
    tokens_sum = sum(r["tokens"] for r in results.values())
    total_tokens += tokens_sum
    
    if success_count >= 2:
        print(f"   ✅ 多模型协作成功 - {success_count}/3模型响应 - {tokens_sum} tokens")
        test_results.append({"test": "多模型协作", "status": "PASS", "tokens": tokens_sum})
    else:
        print(f"   ❌ 多模型协作失败 - 仅{success_count}/3模型响应")
        test_results.append({"test": "多模型协作", "status": "FAIL"})
    
    # 总结
    print("\n" + "=" * 80)
    print("📋 测试总结")
    print("=" * 80)
    
    pass_count = sum(1 for t in test_results if t["status"] == "PASS")
    
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎵 Symphony v{VERSION} 集成测试
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 测试结果:
""")
    
    for t in test_results:
        status = "✅" if t["status"] == "PASS" else "❌"
        tokens = f" ({t.get('tokens', 0)} tokens)" if t.get("tokens") else ""
        print(f"  {status} {t['test']}{tokens}")
    
    print(f"""
📈 统计:
  • 测试通过: {pass_count}/{len(test_results)}
  • 总Token: {total_tokens}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    return {
        "version": VERSION,
        "datetime": datetime.now().isoformat(),
        "test_results": test_results,
        "pass_count": pass_count,
        "total_tests": len(test_results),
        "total_tokens": total_tokens
    }


if __name__ == "__main__":
    report = test_symphony_system()
    
    with open("test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 测试报告已保存: test_report.json")
    print("\nSymphony - 智韵交响，共创华章！")
