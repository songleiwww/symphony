#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响v2.1 - 核心模型协作改进会议
主题：模型兼容、数据同步、模型适配
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
    {"name": "王浩然", "role": "开发工程师", "emoji": "💻", "provider": "modelscope"},
    {"name": "刘心怡", "role": "测试工程师", "emoji": "🧪", "provider": "zhipu"},
    {"name": "张明远", "role": "运维工程师", "emoji": "🔧", "provider": "modelscope"},
    {"name": "赵敏", "role": "产品运营", "emoji": "📈", "provider": "modelscope"}
]


def get_model_config(provider_type: str):
    """获取指定类型的模型配置"""
    for m in MODEL_CHAIN:
        if m.get("enabled") and m["provider"] == provider_type:
            return m
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
        "max_tokens": 800,
        "temperature": 0.7
    }
    
    start = time.time()
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=60)
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
    print("【交响v2.1】核心模型协作改进会议")
    print("主题：模型兼容、数据同步、模型适配")
    print("="*70)
    
    # 分配模型
    print("\n📡 分配模型...")
    for m in MODELS:
        config = get_model_config(m["provider"])
        m["config"] = config
        m["model_name"] = config["alias"]
        m["tokens"] = 0
        m["time"] = 0
        print(f"  {m['emoji']} {m['name']} -> {config['alias']}")
    
    # 第一轮：模型兼容性问题分析
    print("\n" + "="*70)
    print("📌 第一轮：模型兼容性分析")
    print("="*70)
    
    prompts_round1 = [
        "作为产品经理，分析交响多模型协作中模型兼容性问题及解决方案",
        "作为架构师，设计跨模型协作的统一接口架构方案",
        "作为开发工程师，编写模型适配器的代码框架",
        "作为测试工程师，制定模型兼容性测试策略",
        "作为运维工程师，提出多模型环境管理方案",
        "作为产品运营，分析不同模型的适用场景"
    ]
    
    all_discussions = []
    
    for i, m in enumerate(MODELS):
        print(f"\n{m['emoji']} {m['name']} ({m['role']}) 发言...")
        
        result = call_api(m["config"], prompts_round1[i])
        
        if result["success"]:
            m["tokens"] += result["total_tokens"]
            m["time"] += result["time"]
            
            print(f"  ✅ Tokens: {result['total_tokens']} | 耗时: {result['time']:.1f}s")
            print(f"  📝 {result['content'][:200]}...")
            
            all_discussions.append({
                "name": m["name"],
                "role": m["role"],
                "emoji": m["emoji"],
                "topic": "模型兼容性",
                "content": result["content"]
            })
        else:
            print(f"  ❌ {result.get('error', 'Unknown')}")
    
    # 第二轮：数据同步方案
    print("\n" + "="*70)
    print("📌 第二轮：数据同步方案")
    print("="*70)
    
    prompts_round2 = [
        "作为产品经理，设计多模型数据同步的用户体验方案",
        "作为架构师，设计实时数据同步的技术架构",
        "作为开发工程师，实现数据同步的核心代码逻辑",
        "作为测试工程师，设计数据一致性测试方案",
        "作为运维工程师，制定数据同步监控告警策略",
        "作为产品运营，分析数据同步对用户的影响"
    ]
    
    for i, m in enumerate(MODELS):
        print(f"\n{m['emoji']} {m['name']} ({m['role']}) 发言...")
        
        result = call_api(m["config"], prompts_round2[i])
        
        if result["success"]:
            m["tokens"] += result["total_tokens"]
            m["time"] += result["time"]
            
            print(f"  ✅ Tokens: {result['total_tokens']} | 耗时: {result['time']:.1f}s")
            print(f"  📝 {result['content'][:200]}...")
            
            all_discussions.append({
                "name": m["name"],
                "role": m["role"],
                "emoji": m["emoji"],
                "topic": "数据同步",
                "content": result["content"]
            })
        else:
            print(f"  ❌ {result.get('error', 'Unknown')}")
    
    # 第三轮：模型适配优化
    print("\n" + "="*70)
    print("📌 第三轮：模型适配优化")
    print("="*70)
    
    prompts_round3 = [
        "作为产品经理，规划模型适配的产品路线图",
        "作为架构师，设计模型适配层的架构",
        "作为开发工程师，编写模型动态适配代码",
        "作为测试工程师，制定模型适配验收标准",
        "作为运维工程师，设计模型自动扩缩容方案",
        "作为产品运营，总结模型适配优化建议"
    ]
    
    for i, m in enumerate(MODELS):
        print(f"\n{m['emoji']} {m['name']} ({m['role']}) 发言...")
        
        result = call_api(m["config"], prompts_round3[i])
        
        if result["success"]:
            m["tokens"] += result["total_tokens"]
            m["time"] += result["time"]
            
            print(f"  ✅ Tokens: {result['total_tokens']} | 耗时: {result['time']:.1f}s")
            print(f"  📝 {result['content'][:200]}...")
            
            all_discussions.append({
                "name": m["name"],
                "role": m["role"],
                "emoji": m["emoji"],
                "topic": "模型适配",
                "content": result["content"]
            })
        else:
            print(f"  ❌ {result.get('error', 'Unknown')}")
    
    # 最终报告
    print("\n" + "="*70)
    print("📊 核心模型协作改进会议报告")
    print("="*70)
    
    total_tokens = sum(m["tokens"] for m in MODELS)
    total_time = sum(m["time"] for m in MODELS)
    
    print(f"\n🎯 参会: {len(MODELS)} 位专家")
    print(f"💬 讨论主题: 模型兼容、数据同步、模型适配")
    print(f"🔢 总Token消耗: {total_tokens}")
    print(f"⏱️  总耗时: {total_time:.1f}s")
    
    print("\n📋 各位专家贡献:")
    sorted_models = sorted(MODELS, key=lambda x: x["tokens"], reverse=True)
    for m in sorted_models:
        print(f"  {m['emoji']} {m['name']}: {m['tokens']} tokens | {m['time']:.1f}s")
    
    # 保存报告
    report = {
        "title": "交响v2.1 核心模型协作改进会议",
        "datetime": datetime.now().isoformat(),
        "topics": ["模型兼容", "数据同步", "模型适配"],
        "models": MODELS,
        "discussions": all_discussions,
        "summary": {
            "total_models": len(MODELS),
            "total_tokens": total_tokens,
            "total_time": round(total_time, 2)
        }
    }
    
    with open("core_model_improvement_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 报告已保存: core_model_improvement_report.json")
    print("\n" + "="*70)
    print("🎼 智韵交响，共创华章！")
    print("="*70)


if __name__ == "__main__":
    main()
