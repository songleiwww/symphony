#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响v2.2 - 调度与容错机制改进会议
快速版本，使用精简响应
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
    {"name": "王浩然", "role": "开发工程师", "emoji": "💻", "provider": "zhipu"},
    {"name": "刘心怡", "role": "测试工程师", "emoji": "🧪", "provider": "zhipu"},
    {"name": "张明远", "role": "运维工程师", "emoji": "🔧", "provider": "modelscope"},
    {"name": "赵敏", "role": "产品运营", "emoji": "📈", "provider": "modelscope"}
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
    headers = {
        "Authorization": f"Bearer {model_config['api_key']}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_config["model_id"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    start = time.time()
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        elapsed = time.time() - start
        if resp.status_code == 200:
            result = resp.json()
            usage = result.get("usage", {})
            return {
                "success": True,
                "content": result["choices"][0]["message"]["content"],
                "total_tokens": usage.get("total_tokens", 0),
                "time": elapsed
            }
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}", "time": elapsed}
    except Exception as e:
        return {"success": False, "error": str(e), "time": time.time() - start}

def main():
    print("="*70)
    print("【交响v2.2】调度与容错机制改进会议")
    print("="*70)
    
    for m in MODELS:
        config = get_model_config(m["provider"])
        m["config"] = config
        m["model_name"] = config["alias"]
        m["tokens"] = 0
        m["time"] = 0
        print(f"  {m['emoji']} {m['name']} -> {config['alias']}")
    
    # 第一轮：调度问题分析
    print("\n" + "="*70)
    print("📌 第一轮：调度机制问题分析")
    print("="*70)
    
    prompts1 = [
        "作为产品经理，简述交响模型调度的主要问题（3点）",
        "作为架构师，分析当前调度架构的问题（3点）",
        "作为开发工程师，列出调度代码的问题（3点）",
        "作为测试工程师，指出调度测试问题（3点）",
        "作为运维工程师，分析调度运维问题（3点）",
        "作为产品运营，分析调度用户体验问题（3点）"
    ]
    
    discussions = []
    for i, m in enumerate(MODELS):
        print(f"\n{m['emoji']} {m['name']} 发言...")
        result = call_api(m["config"], prompts1[i])
        if result["success"]:
            m["tokens"] += result["total_tokens"]
            m["time"] += result["time"]
            print(f"  ✅ {result['total_tokens']} tokens | {result['time']:.1f}s")
            print(f"  📝 {result['content'][:150]}...")
            discussions.append({"name": m["name"], "role": m["role"], "topic": "调度问题", "content": result["content"]})
        else:
            print(f"  ❌ {result.get('error', 'Unknown')}")
    
    # 第二轮：容错机制
    print("\n" + "="*70)
    print("📌 第二轮：容错机制改进")
    print("="*70)
    
    prompts2 = [
        "作为产品经理，简述容错机制产品方案（3点）",
        "作为架构师，设计容错架构方案（3点）",
        "作为开发工程师，编写容错代码逻辑（精简）",
        "作为测试工程师，制定容错测试策略（3点）",
        "作为运维工程师，设计告警监控方案（3点）",
        "作为产品运营，总结容错改进建议（3点）"
    ]
    
    for i, m in enumerate(MODELS):
        print(f"\n{m['emoji']} {m['name']} 发言...")
        result = call_api(m["config"], prompts2[i])
        if result["success"]:
            m["tokens"] += result["total_tokens"]
            m["time"] += result["time"]
            print(f"  ✅ {result['total_tokens']} tokens | {result['time']:.1f}s")
            print(f"  📝 {result['content'][:150]}...")
            discussions.append({"name": m["name"], "role": m["role"], "topic": "容错机制", "content": result["content"]})
        else:
            print(f"  ❌ {result.get('error', 'Unknown')}")
    
    # 报告
    print("\n" + "="*70)
    print("📊 会议报告")
    print("="*70)
    
    total_tokens = sum(m["tokens"] for m in MODELS)
    total_time = sum(m["time"] for m in MODELS)
    
    print(f"\n🎯 参会: {len(MODELS)} 位专家")
    print(f"🔢 总Token: {total_tokens}")
    print(f"⏱️  总耗时: {total_time:.1f}s")
    
    print("\n📋 贡献排名:")
    for m in sorted(MODELS, key=lambda x: x["tokens"], reverse=True):
        print(f"  {m['emoji']} {m['name']}: {m['tokens']} tokens")
    
    report = {
        "title": "交响v2.2 调度与容错机制改进",
        "datetime": datetime.now().isoformat(),
        "models": MODELS,
        "discussions": discussions,
        "summary": {"total_tokens": total_tokens, "total_time": round(total_time, 2)}
    }
    
    with open("dispatch_fault_tolerance_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 报告已保存: dispatch_fault_tolerance_report.json")
    print("\n🎼 智韵交响，共创华章！")

if __name__ == "__main__":
    main()
