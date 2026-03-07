#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v2.4.0 - 模型搜索能力测试
测试每个模型获取最新信息的能力
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


VERSION = "2.4.0"

# 测试的模型
TEST_MODELS = [
    {"id": 0, "name": "林思远", "role": "产品经理", "company": "智谱AI", "model": "GLM-4-Flash"},
    {"id": 1, "name": "陈美琪", "role": "架构师", "company": "智谱AI", "model": "GLM-Z1-Flash"},
    {"id": 10, "name": "张明远", "role": "运维工程师", "company": "ModelScope", "model": "Qwen3-235B"},
    {"id": 12, "name": "赵敏", "role": "产品运营", "company": "ModelScope", "model": "MiniMax-M2.5"},
    {"id": 14, "name": "吴铭", "role": "安全工程师", "company": "ModelScope", "model": "GLM-5"},
    {"id": 15, "name": "周建", "role": "推理专家", "company": "ModelScope", "model": "DeepSeek R1"},
]


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_index: int, prompt: str, max_tokens=200):
    enabled = get_enabled_models()
    if model_index >= len(enabled):
        return None
    
    model = enabled[model_index]
    url = model["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model["api_key"], "Content-Type": "application/json"}
    data = {"model": model["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=15)
        if r.status_code == 200:
            j = r.json()
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": j.get("usage", {}).get("total_tokens", 0)}
    except:
        pass
    return None


# 搜索测试问题
SEARCH_QUERIES = [
    "2026年AI最新发展趋势是什么？",
    "Python 3.13最新特性有哪些？",
    "最新的大语言模型排行榜2026",
]


def test_search_capability():
    """测试搜索能力"""
    
    print("=" * 80)
    print(f"🎼 Symphony v{VERSION} - 模型搜索能力测试")
    print("=" * 80)
    
    # 测试每个模型
    results = []
    
    for m in TEST_MODELS:
        print(f"\n{'─' * 60}")
        print(f"👤 {m['name']} | {m['role']} | {m['company']} {m['model']}")
        print(f"{'─' * 60}")
        
        # 用搜索类问题测试
        query = SEARCH_QUERIES[TEST_MODELS.index(m) % len(SEARCH_QUERIES)]
        print(f"🔍 测试问题: {query}")
        
        result = call_api(m["id"], query)
        
        if result and result.get("success"):
            tokens = result.get("tokens", 0)
            content = result.get("content", "")
            
            # 检查是否包含最新信息关键词
            keywords = ["2025", "2026", "最新", "recent", "latest", "new"]
            has_fresh = any(kw in content for kw in keywords)
            
            print(f"\n📝 回答 ({tokens} tokens):")
            print(f"   {content[:150]}...")
            
            print(f"\n📊 搜索能力评估:")
            print(f"   • Token消耗: {tokens}")
            print(f"   • 包含最新信息: {'✅ 是' if has_fresh else '⚠️ 否'}")
            
            m["tokens"] = tokens
            m["has_fresh"] = has_fresh
            m["answer"] = content[:100]
            results.append(m)
        else:
            print(f"   ❌ 调用失败")
            m["tokens"] = 0
            m["has_fresh"] = False
            m["error"] = "调用失败"
            results.append(m)
        
        time.sleep(0.5)
    
    # 总结
    print("\n" + "=" * 80)
    print("📊 搜索能力排名")
    print("=" * 80)
    
    total_tokens = sum(m.get("tokens", 0) for m in results)
    successful = len([m for m in results if m.get("tokens", 0) > 0])
    fresh_count = len([m for m in results if m.get("has_fresh", False)])
    
    print(f"\n| 排名 | 姓名 | 角色 | 公司 | 模型 | Token | 最新信息 |")
    print(f"|------|------|------|------|------|-------|----------|")
    
    sorted_results = sorted(results, key=lambda x: x.get("tokens", 0), reverse=True)
    
    for i, m in enumerate(sorted_results):
        token = m.get("tokens", 0)
        fresh = "✅" if m.get("has_fresh") else "⚠️"
        print(f"| {i+1} | {m['name']} | {m['role']} | {m['company'][:4]} | {m['model'][:12]} | {token} | {fresh} |")
    
    print(f"\n统计: 成功{successful}/{len(TEST_MODELS)}, 含最新信息{fresh_count}个, 总Token{total_tokens}")
    
    return {
        "version": VERSION,
        "datetime": datetime.now().isoformat(),
        "results": results,
        "summary": {"successful": successful, "fresh_count": fresh_count, "total_tokens": total_tokens}
    }


if __name__ == "__main__":
    report = test_search_capability()
    
    with open("search_test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 报告已保存: search_test_report.json")
    print("\nSymphony - 智韵交响，共创华章！")
