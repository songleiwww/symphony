#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响v2.4 - 真实模型验证检测系统 - 改进版
防止模型欺骗、幻觉、跳过真实调用
"""

import sys
import json
import time
import requests
from datetime import datetime
from config import MODEL_CHAIN

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


MODELS = [
    {"name": "林思远", "role": "产品经理", "emoji": "📋", "provider": "zhipu"},
    {"name": "陈美琪", "role": "架构师", "emoji": "🏗️", "provider": "zhipu"},
    {"name": "王浩然", "role": "开发工程师", "emoji": "💻", "provider": "modelscope"},
    {"name": "刘心怡", "role": "测试工程师", "emoji": "🧪", "provider": "modelscope"},
    {"name": "张明远", "role": "运维工程师", "emoji": "🔧", "provider": "zhipu"},
    {"name": "赵敏", "role": "产品运营", "emoji": "📈", "provider": "zhipu"}
]

def get_model_config(provider_type):
    for m in MODEL_CHAIN:
        if m.get("enabled") and m["provider"] == provider_type:
            return m
    for m in MODEL_CHAIN:
        if m.get("enabled"):
            return m
    return None

def call_api(model_config, prompt, max_tokens=300):
    url = f"{model_config['base_url']}/chat/completions"
    headers = {"Authorization": f"Bearer {model_config['api_key']}", "Content-Type": "application/json"}
    data = {"model": model_config["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    start = time.time()
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=20)
        elapsed = time.time() - start
        if resp.status_code == 200:
            result = resp.json()
            usage = result.get("usage", {})
            content = result["choices"][0]["message"]["content"]
            return {"success": True, "content": content, "total_tokens": usage.get("total_tokens", 0), "time": elapsed, "raw": result, "status": resp.status_code}
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}", "time": elapsed}
    except Exception as e:
        return {"success": False, "error": str(e), "time": time.time() - start}

def verify_model_response(model_config, test_prompt, expected_content):
    """验证模型是否真实响应"""
    result = call_api(model_config, test_prompt)
    
    verification = {
        "success": False,
        "is_real": False,
        "details": {}
    }
    
    if result["success"]:
        verification["success"] = True
        content = result.get("content", "").strip()
        
        # 验证是否为真实响应
        is_real = (
            len(content) > 0 and
            result["total_tokens"] > 0 and
            result["time"] > 0.1
        )
        
        # 检查是否匹配预期
        matches_expected = expected_content in content
        
        verification["is_real"] = is_real and matches_expected
        verification["details"] = {
            "content": content,
            "content_length": len(content),
            "tokens": result["total_tokens"],
            "response_time": round(result["time"], 2),
            "matches_expected": matches_expected,
            "model": model_config["alias"],
            "provider": model_config["provider"]
        }
    
    return verification

def main():
    print("="*70)
    print("【交响v2.4】真实模型验证检测系统")
    print("="*70)
    
    # 分配模型
    for m in MODELS:
        config = get_model_config(m["provider"])
        m["config"] = config
        m["model_name"] = config["alias"]
        m["is_real"] = False
        m["tokens"] = 0
        print(f"  {m['emoji']} {m['name']} -> {config['alias']}")
    
    # 验证测试
    print("\n" + "="*70)
    print("📌 真实模型验证测试")
    print("="*70)
    
    test_cases = [
        {"prompt": "请简单回复：'测试成功'", "expected": "测试成功"},
        {"prompt": "回复数字：42", "expected": "42"},
        {"prompt": "请回答：OK", "expected": "OK"}
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n测试 {i}: '{test['prompt']}'")
        print("-" * 50)
        
        for m in MODELS:
            print(f"\n{m['emoji']} {m['name']}...")
            v = verify_model_response(m["config"], test["prompt"], test["expected"])
            
            if v["success"]:
                m["tokens"] += v["details"]["tokens"]
                
                if v["is_real"]:
                    status = "✅ 真实模型"
                    m["is_real"] = True
                else:
                    status = "⚠️ 异常"
                    all_passed = False
                
                print(f"  {status}")
                print(f"  回复: {v['details']['content']}")
                print(f"  Tokens: {v['details']['tokens']}")
                print(f"  耗时: {v['details']['response_time']}s")
                print(f"  匹配: {v['details']['matches_expected']}")
            else:
                print(f"  ❌ 调用失败")
                all_passed = False
    
    # 报告
    print("\n" + "="*70)
    print("📊 验证检测报告")
    print("="*70)
    
    total_tokens = sum(m["tokens"] for m in MODELS)
    real_count = sum(1 for m in MODELS if m["is_real"])
    
    print(f"\n🎯 验证结果: {real_count}/{len(MODELS)} 模型通过")
    print(f"🔢 总Token: {total_tokens}")
    print(f"\n📋 各模型状态:")
    for m in MODELS:
        status = "✅ 真实" if m["is_real"] else "❌ 异常"
        print(f"  {m['emoji']} {m['name']}: {status}")
    
    if all_passed:
        print("\n🎉 所有验证通过！模型真实调用正常。")
    else:
        print("\n⚠️ 部分验证失败，请检查模型配置。")
    
    # 保存报告
    report = {
        "title": "交响v2.4 真实模型验证检测",
        "datetime": datetime.now().isoformat(),
        "verification_passed": all_passed,
        "real_count": real_count,
        "total_models": len(MODELS),
        "models": MODELS,
        "summary": {"total_tokens": total_tokens}
    }
    
    with open("model_verification_final.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 报告已保存: model_verification_final.json")
    print("\n🎼 智韵交响，共创华章！")

if __name__ == "__main__":
    main()
