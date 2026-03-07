#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响v2.3 - 核心系统改进开发
主题：冗余设计、异常处理、资源管理、优雅降级、调度逻辑
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
    {"name": "刘心怡", "role": "测试工程师", "emoji": "🧪", "provider": "modelscope"},
    {"name": "张明远", "role": "运维工程师", "emoji": "🔧", "provider": "modelscope"},
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

def call_api(model_config, prompt, max_tokens=400):
    url = f"{model_config['base_url']}/chat/completions"
    headers = {"Authorization": f"Bearer {model_config['api_key']}", "Content-Type": "application/json"}
    data = {"model": model_config["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    start = time.time()
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=25)
        elapsed = time.time() - start
        if resp.status_code == 200:
            result = resp.json()
            usage = result.get("usage", {})
            return {"success": True, "content": result["choices"][0]["message"]["content"], "total_tokens": usage.get("total_tokens", 0), "time": elapsed}
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}", "time": elapsed}
    except Exception as e:
        return {"success": False, "error": str(e), "time": time.time() - start}

def main():
    print("="*70)
    print("【交响v2.3】核心系统改进开发")
    print("主题：冗余设计、异常处理、资源管理、优雅降级、调度逻辑")
    print("="*70)
    
    for m in MODELS:
        config = get_model_config(m["provider"])
        m["config"] = config
        m["model_name"] = config["alias"]
        m["tokens"] = 0
        m["time"] = 0
        print(f"  {m['emoji']} {m['name']} -> {config['alias']}")
    
    discussions = []
    
    # 第一轮：冗余设计
    print("\n" + "="*70)
    print("📌 第一轮：冗余设计方案")
    print("="*70)
    
    prompts1 = [
        "作为产品经理，设计交响模型冗余的产品方案（简洁3点）",
        "作为架构师，设计多模型冗余架构（核心3点）",
        "作为开发工程师，编写模型降级切换代码框架",
        "作为测试工程师，制定冗余切换测试用例",
        "作为运维工程师，设计冗余监控告警方案",
        "作为产品运营，分析冗余设计的用户价值"
    ]
    
    for i, m in enumerate(MODELS):
        print(f"\n{m['emoji']} {m['name']} 发言...")
        result = call_api(m["config"], prompts1[i])
        if result["success"]:
            m["tokens"] += result["total_tokens"]
            m["time"] += result["time"]
            print(f"  ✅ {result['total_tokens']} tokens | {result['time']:.1f}s")
            discussions.append({"name": m["name"], "role": m["role"], "topic": "冗余设计", "content": result["content"]})
        else:
            print(f"  ❌ {result.get('error', 'Unknown')}")
    
    # 第二轮：异常处理与资源管理
    print("\n" + "="*70)
    print("📌 第二轮：异常处理与资源管理")
    print("="*70)
    
    prompts2 = [
        "作为产品经理，异常处理的产品设计方案（3点）",
        "作为架构师，异常处理架构设计（核心3点）",
        "作为开发工程师，编写Python异常处理代码示例",
        "作为测试工程师，异常场景测试策略",
        "作为运维工程师，资源管理监控方案",
        "作为产品运营，总结异常处理改进建议"
    ]
    
    for i, m in enumerate(MODELS):
        print(f"\n{m['emoji']} {m['name']} 发言...")
        result = call_api(m["config"], prompts2[i])
        if result["success"]:
            m["tokens"] += result["total_tokens"]
            m["time"] += result["time"]
            print(f"  ✅ {result['total_tokens']} tokens | {result['time']:.1f}s")
            discussions.append({"name": m["name"], "role": m["role"], "topic": "异常处理", "content": result["content"]})
        else:
            print(f"  ❌ {result.get('error', 'Unknown')}")
    
    # 第三轮：优雅降级与调度逻辑
    print("\n" + "="*70)
    print("📌 第三轮：优雅降级与调度逻辑")
    print("="*70)
    
    prompts3 = [
        "作为产品经理，优雅降级产品策略（3点）",
        "作为架构师，优雅降级架构设计（核心3点）",
        "作为开发工程师，编写调度逻辑伪代码",
        "作为测试工程师，调度逻辑测试方法",
        "作为运维工程师，模型可调度性分析方法",
        "作为产品运营，总结改进建议"
    ]
    
    for i, m in enumerate(MODELS):
        print(f"\n{m['emoji']} {m['name']} 发言...")
        result = call_api(m["config"], prompts3[i])
        if result["success"]:
            m["tokens"] += result["total_tokens"]
            m["time"] += result["time"]
            print(f"  ✅ {result['total_tokens']} tokens | {result['time']:.1f}s")
            discussions.append({"name": m["name"], "role": m["role"], "topic": "调度优化", "content": result["content"]})
        else:
            print(f"  ❌ {result.get('error', 'Unknown')}")
    
    # 报告
    print("\n" + "="*70)
    print("📊 核心系统改进开发报告")
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
        "title": "交响v2.3 核心系统改进开发",
        "datetime": datetime.now().isoformat(),
        "topics": ["冗余设计", "异常处理", "资源管理", "优雅降级", "调度逻辑"],
        "models": MODELS,
        "discussions": discussions,
        "summary": {"total_tokens": total_tokens, "total_time": round(total_time, 2)}
    }
    
    with open("core_system_improvement_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 报告已保存: core_system_improvement_report.json")
    print("\n🎼 智韵交响，共创华章！")

if __name__ == "__main__":
    main()
