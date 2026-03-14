#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响v2.0 - 真实模型协作技能进化会议
研究如何改善协作问题，提升用户体验
"""

import sys
import json
import time
import requests
from datetime import datetime
from config import MODEL_CHAIN

# Windows编码修复
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# =============================================================================
# 6位专家模型配置
# =============================================================================

MODELS = [
    {"name": "林思远", "role": "产品经理", "emoji": "📋", "provider": "zhipu"},
    {"name": "陈美琪", "role": "架构师", "emoji": "🏗️", "provider": "zhipu"},
    {"name": "王浩然", "role": "开发工程师", "emoji": "💻", "provider": "zhipu"},
    {"name": "刘心怡", "role": "测试工程师", "emoji": "🧪", "provider": "zhipu"},
    {"name": "张明远", "role": "运维工程师", "emoji": "🔧", "provider": "modelscope"},
    {"name": "赵敏", "role": "产品运营", "emoji": "📈", "provider": "modelscope"}
]


def get_model_config(provider_type: str):
    """获取指定类型的模型配置"""
    for m in MODEL_CHAIN:
        if m.get("enabled") and m["provider"] == provider_type:
            return m
    # 备用：返回第一个可用的
    for m in MODEL_CHAIN:
        if m.get("enabled"):
            return m
    return None


def call_api(model_config: dict, prompt: str) -> dict:
    """调用真实API"""
    url = f"{model_config['base_url']}/chat/completions"
    headers = {
        "Authorization": f"Bearer {model_config['api_key']}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model_config["model_id"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 600,
        "temperature": 0.7
    }
    
    start = time.time()
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=45)
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            result = resp.json()
            usage = result.get("usage", {})
            return {
                "success": True,
                "content": result["choices"][0]["message"]["content"],
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
                "time": elapsed
            }
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}", "time": elapsed}
    except Exception as e:
        return {"success": False, "error": str(e), "time": time.time() - start}


def main():
    print("="*70)
    print("【交响v2.0】协作技能进化会议")
    print("主题：真实模型协作技能进化与友好改善")
    print("="*70)
    
    # 分配模型
    print("\n📡 分配模型...")
    for m in MODELS:
        config = get_model_config(m["provider"])
        m["config"] = config
        m["model_name"] = config["alias"]
        print(f"  {m['emoji']} {m['name']} -> {config['alias']}")
    
    # 第一轮：问题分析
    print("\n" + "="*70)
    print("📌 第一轮：分析当前协作问题")
    print("="*70)
    
    prompts_round1 = [
        "作为产品经理，分析交响当前使用真实模型协作的主要问题和用户体验痛点",
        "作为架构师，分析交响多模型协作的技术架构问题",
        "作为开发工程师，列出代码层面的协作问题",
        "作为测试工程师，指出协作流程中的测试问题",
        "作为运维工程师，分析部署和运维中的协作问题",
        "作为产品运营，从用户角度分析协作体验问题"
    ]
    
    all_discussions = []
    
    for i, m in enumerate(MODELS):
        print(f"\n{m['emoji']} {m['name']} ({m['role']}) 发言...")
        
        result = call_api(m["config"], prompts_round1[i])
        
        if result["success"]:
            m["tokens"] = m.get("tokens", 0) + result["total_tokens"]
            m["time"] = m.get("time", 0) + result["time"]
            
            print(f"  ✅ Tokens: {result['total_tokens']} | 耗时: {result['time']:.1f}s")
            print(f"  📝 {result['content'][:150]}...")
            
            all_discussions.append({
                "name": m["name"],
                "role": m["role"],
                "emoji": m["emoji"],
                "round": 1,
                "content": result["content"]
            })
        else:
            print(f"  ❌ {result.get('error', 'Unknown')}")
    
    # 第二轮：解决方案
    print("\n" + "="*70)
    print("📌 第二轮：提出改善方案")
    print("="*70)
    
    prompts_round2 = [
        "作为产品经理，提出改善交响协作用户体验的具体方案",
        "作为架构师，提出技术架构优化方案",
        "作为开发工程师，提出代码层面的优化方案",
        "作为测试工程师，提出测试流程改进方案",
        "作为运维工程师，提出运维协作优化方案",
        "作为产品运营，提出用户协作体验改进方案"
    ]
    
    for i, m in enumerate(MODELS):
        print(f"\n{m['emoji']} {m['name']} ({m['role']}) 发言...")
        
        result = call_api(m["config"], prompts_round2[i])
        
        if result["success"]:
            m["tokens"] = m.get("tokens", 0) + result["total_tokens"]
            m["time"] = m.get("time", 0) + result["time"]
            
            print(f"  ✅ Tokens: {result['total_tokens']} | 耗时: {result['time']:.1f}s")
            print(f"  📝 {result['content'][:150]}...")
            
            all_discussions.append({
                "name": m["name"],
                "role": m["role"],
                "emoji": m["emoji"],
                "round": 2,
                "content": result["content"]
            })
        else:
            print(f"  ❌ {result.get('error', 'Unknown')}")
    
    # 第三轮：总结
    print("\n" + "="*70)
    print("📌 第三轮：总结改进建议")
    print("="*70)
    
    summary_prompt = "作为产品运营，总结交响协作技能进化的核心建议（简洁总结3点）"
    
    m = MODELS[5]  # 赵敏
    print(f"\n{m['emoji']} {m['name']} ({m['role']}) 总结...")
    
    result = call_api(m["config"], summary_prompt)
    
    if result["success"]:
        m["tokens"] = m.get("tokens", 0) + result["total_tokens"]
        m["time"] = m.get("time", 0) + result["time"]
        
        print(f"  ✅ Tokens: {result['total_tokens']} | 耗时: {result['time']:.1f}s")
        print(f"\n  📋 总结:")
        print(f"  {result['content']}")
        
        all_discussions.append({
            "name": m["name"],
            "role": m["role"],
            "emoji": m["emoji"],
            "round": 3,
            "content": result["content"]
        })
    
    # 最终报告
    print("\n" + "="*70)
    print("📊 协作技能进化会议报告")
    print("="*70)
    
    total_tokens = sum(m.get("tokens", 0) for m in MODELS)
    total_time = sum(m.get("time", 0) for m in MODELS)
    
    print(f"\n🎯 参会: {len(MODELS)} 位专家")
    print(f"💬 讨论轮次: 3 轮")
    print(f"🔢 总Token消耗: {total_tokens}")
    print(f"⏱️  总耗时: {total_time:.1f}s")
    
    print("\n📋 各位专家贡献:")
    for m in MODELS:
        print(f"  {m['emoji']} {m['name']}: {m.get('tokens', 0)} tokens")
    
    # 保存报告
    report = {
        "title": "交响v2.0 协作技能进化会议",
        "datetime": datetime.now().isoformat(),
        "models": MODELS,
        "discussions": all_discussions,
        "summary": {
            "total_models": len(MODELS),
            "total_tokens": total_tokens,
            "total_time": round(total_time, 2)
        }
    }
    
    with open("collaboration_evolution_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 报告已保存: collaboration_evolution_report.json")
    print("\n" + "="*70)
    print("🎼 智韵交响，共创华章！")
    print("="*70)


if __name__ == "__main__":
    main()
