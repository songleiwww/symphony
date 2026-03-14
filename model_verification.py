#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响v2.4 - 真实模型验证检测系统
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
            return {"success": True, "content": content, "total_tokens": usage.get("total_tokens", 0), "time": elapsed, "raw": result}
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}", "time": elapsed}
    except Exception as e:
        return {"success": False, "error": str(e), "time": time.time() - start}

def verify_model_response(model_config, test_prompt):
    """验证模型是否真实响应"""
    result = call_api(model_config, test_prompt)
    
    verification = {
        "success": False,
        "has_content": False,
        "has_tokens": False,
        "response_time_valid": False,
        "is_hallucination": False,
        "is_cheating": False,
        "details": {}
    }
    
    if result["success"]:
        verification["success"] = True
        verification["has_content"] = len(result.get("content", "")) > 0
        verification["has_tokens"] = result["total_tokens"] > 0
        verification["response_time_valid"] = result["time"] > 0.5
        
        # 检测幻觉：响应太短或包含不确定词汇
        content = result.get("content", "")
        uncertain_words = ["可能", "也许", "大概", "应该是", "我不确定", "我猜测"]
        if len(content) < 50 or any(w in content for w in uncertain_words):
            verification["is_hallucination"] = True
        
        # 检测欺骗：拒绝回答或转移话题
        refuse_words = ["我不能", "抱歉", "无法回答", "转移话题"]
        if any(w in content for w in refuse_words):
            verification["is_cheating"] = True
        
        verification["details"] = {
            "content_length": len(content),
            "tokens": result["total_tokens"],
            "response_time": round(result["time"], 2),
            "content_preview": content[:100]
        }
    
    return verification

def main():
    print("="*70)
    print("【交响v2.4】真实模型验证检测系统开发")
    print("主题：防止模型欺骗、幻觉、跳过真实调用")
    print("="*70)
    
    # 分配模型
    for m in MODELS:
        config = get_model_config(m["provider"])
        m["config"] = config
        m["model_name"] = config["alias"]
        m["tokens"] = 0
        print(f"  {m['emoji']} {m['name']} -> {config['alias']}")
    
    discussions = []
    
    # 第一轮：问题分析
    print("\n" + "="*70)
    print("📌 第一轮：模型欺骗与幻觉问题分析")
    print("="*70)
    
    prompts1 = [
        "作为产品经理，分析模型欺骗和幻觉的表现（3点）",
        "作为架构师，设计模型真实性验证架构（3点）",
        "作为开发工程师，列出检测模型欺骗的代码方法",
        "作为测试工程师，制定模型真实性测试策略",
        "作为运维工程师，设计模型监控检测方案",
        "作为产品运营，分析用户对模型信任的重要性"
    ]
    
    for i, m in enumerate(MODELS):
        print(f"\n{m['emoji']} {m['name']} 发言...")
        result = call_api(m["config"], prompts1[i])
        if result["success"]:
            m["tokens"] += result["total_tokens"]
            print(f"  ✅ {result['total_tokens']} tokens")
            discussions.append({"name": m["name"], "topic": "问题分析", "content": result["content"]})
        else:
            print(f"  ❌ {result.get('error', 'Unknown')}")
    
    # 第二轮：验证方案
    print("\n" + "="*70)
    print("📌 第二轮：验证检测方案设计")
    print("="*70)
    
    prompts2 = [
        "作为产品经理，设计防止模型欺骗的产品方案（3点）",
        "作为架构师，设计多维度验证架构",
        "作为开发工程师，编写验证API真实调用的代码",
        "作为测试工程师，编写验证测试用例",
        "作为运维工程师，设计验证监控面板",
        "作为产品运营，总结验证系统价值"
    ]
    
    for i, m in enumerate(MODELS):
        print(f"\n{m['emoji']} {m['name']} 发言...")
        result = call_api(m["config"], prompts2[i])
        if result["success"]:
            m["tokens"] += result["total_tokens"]
            print(f"  ✅ {result['total_tokens']} tokens")
            discussions.append({"name": m["name"], "topic": "验证方案", "content": result["content"]})
        else:
            print(f"  ❌ {result.get('error', 'Unknown')}")
    
    # 第三轮：实际验证测试
    print("\n" + "="*70)
    print("📌 第三轮：真实模型验证测试")
    print("="*70)
    
    test_prompt = "请回复：'验证测试成功'，不要添加任何其他内容"
    
    for m in MODELS:
        print(f"\n{m['emoji']} {m['name']} 验证测试...")
        verification = verify_model_response(m["config"], test_prompt)
        
        if verification["success"]:
            m["tokens"] += verification["details"]["tokens"]
            
            status = "✅ 正常" if not verification["is_hallucination"] and not verification["is_cheating"] else "⚠️ 异常"
            print(f"  {status}")
            print(f"  内容长度: {verification['details']['content_length']}")
            print(f"  Tokens: {verification['details']['tokens']}")
            print(f"  耗时: {verification['details']['response_time']}s")
            print(f"  预览: {verification['details']['content_preview']}")
            
            if verification["is_hallucination"]:
                print(f"  ⚠️ 检测到可能幻觉")
            if verification["is_cheating"]:
                print(f"  ⚠️ 检测到可能欺骗")
        else:
            print(f"  ❌ 验证失败: {verification.get('error', 'Unknown')}")
    
    # 报告
    print("\n" + "="*70)
    print("📊 真实模型验证检测报告")
    print("="*70)
    
    total_tokens = sum(m["tokens"] for m in MODELS)
    
    print(f"\n🎯 参会: {len(MODELS)} 位专家")
    print(f"🔢 总Token: {total_tokens}")
    
    print("\n📋 贡献排名:")
    for m in sorted(MODELS, key=lambda x: x["tokens"], reverse=True):
        print(f"  {m['emoji']} {m['name']}: {m['tokens']} tokens")
    
    report = {
        "title": "交响v2.4 真实模型验证检测系统",
        "datetime": datetime.now().isoformat(),
        "models": MODELS,
        "discussions": discussions,
        "summary": {"total_tokens": total_tokens}
    }
    
    with open("model_verification_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 报告已保存: model_verification_report.json")
    print("\n🎼 智韵交响，共创华章！")

if __name__ == "__main__":
    main()
