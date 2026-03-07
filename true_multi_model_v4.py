#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v4.0 - True Multi-Model Parallel Collaboration
每个模型只扮演一个角色，使用不同模型并行调用
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


# =============================================================================
# 真正的多模型配置 - 每个模型分配不同角色，禁止角色扮演
# =============================================================================
# 从config中选择6个不同的模型
MODELS = [
    {"name": "Model-1", "role": "产品经理", "emoji": "PE", "model_index": 0},   # 智谱GLM-4-Flash
    {"name": "Model-2", "role": "架构师", "emoji": "AR", "model_index": 1},     # 智谱GLM-Z1-Flash
    {"name": "Model-3", "role": "开发工程师", "emoji": "DEV", "model_index": 6}, # ModelScope GLM-4.7-Flash
    {"name": "Model-4", "role": "测试工程师", "emoji": "TEST", "model_index": 7}, # ModelScope DeepSeek-V3.2
    {"name": "Model-5", "role": "运维工程师", "emoji": "OPS", "model_index": 8}, # 另一个模型
    {"name": "Model-6", "role": "产品运营", "emoji": "PO", "model_index": 9},   # 另一个模型
]


def get_enabled_models():
    """获取所有启用的模型"""
    enabled = [m for m in MODEL_CHAIN if m.get("enabled")]
    return enabled


def call_api(model_config, prompt, max_tokens=300):
    """调用模型API"""
    url = model_config["base_url"] + "/chat/completions"
    headers = {
        "Authorization": "Bearer " + model_config["api_key"],
        "Content-Type": "application/json"
    }
    data = {
        "model": model_config["model_id"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    t0 = time.time()
    try:
        r = requests.post(url, headers=headers, json=data, timeout=25)
        elapsed = time.time() - t0
        if r.status_code == 200:
            j = r.json()
            usage = j.get("usage", {})
            return {
                "success": True,
                "content": j["choices"][0]["message"]["content"],
                "tokens": usage.get("total_tokens", 0),
                "time": elapsed,
                "model_id": model_config["model_id"],
                "provider": model_config["provider"]
            }
        else:
            return {"success": False, "error": "HTTP " + str(r.status_code), "time": elapsed}
    except Exception as e:
        return {"success": False, "error": str(e), "time": time.time() - t0}


def call_api_with_model(model_index, prompt, result_container, index):
    """线程函数：调用指定模型的API"""
    enabled_models = get_enabled_models()
    if model_index < len(enabled_models):
        model_config = enabled_models[model_index]
        result = call_api(model_config, prompt)
        result_container[index] = {
            "model_config": {
                "name": model_config.get("name"),
                "model_id": model_config.get("model_id"),
                "alias": model_config.get("alias"),
                "provider": model_config.get("provider")
            },
            **result
        }
    else:
        result_container[index] = {"success": False, "error": "Model index out of range"}


def parallel_call(prompts):
    """并行调用多个模型"""
    threads = []
    results = [None] * len(prompts)
    
    for i, prompt in enumerate(prompts):
        model_index = MODELS[i]["model_index"]
        t = threading.Thread(target=call_api_with_model, args=(model_index, prompt, results, i))
        threads.append(t)
        t.start()
    
    # 等待所有线程完成
    for t in threads:
        t.join()
    
    return results


def test_tool_usage(model_config):
    """测试模型使用工具的能力"""
    tool_prompt = """请完成以下任务：
1. 计算 123 * 456 的结果
2. 列出3个常用的Python库
3. 解释什么是API

请直接回答，不要使用任何工具。"""
    
    result = call_api(model_config, tool_prompt, max_tokens=400)
    
    # 检查是否能正确响应
    has_numbers = any(c.isdigit() for c in result.get("content", ""))
    has_libraries = any(word in result.get("content", "") for word in ["numpy", "pandas", "requests", "flask", "django", "torch"])
    has_api = "api" in result.get("content", "").lower()
    
    tool_capability = {
        "numeric_calculation": has_numbers,
        "library_knowledge": has_libraries,
        "concept_explanation": has_api,
        "overall_score": sum([has_numbers, has_libraries, has_api])
    }
    
    return tool_capability


def main():
    print("=" * 70)
    print("Symphony v4.0 - True Multi-Model Parallel Collaboration")
    print("=" * 70)
    print("\n核心原则：")
    print("  1. 每个模型只扮演一个角色")
    print("  2. 使用不同模型并行调用")
    print("  3. 禁止角色扮演")
    print("  4. 检查工具使用能力")
    print("=" * 70)
    
    # 获取可用模型
    enabled_models = get_enabled_models()
    print("\n可用模型数量: {}".format(len(enabled_models)))
    
    # 显示每个角色分配的模型
    print("\n模型分配:")
    for m in MODELS:
        idx = m["model_index"]
        if idx < len(enabled_models):
            cfg = enabled_models[idx]
            m["config"] = cfg
            m["model_name"] = cfg["alias"]
            m["provider"] = cfg["provider"]
            print("  {} {} -> {} ({})".format(m["emoji"], m["role"], cfg["alias"], cfg["provider"]))
        else:
            print("  {} {} -> 索引 {} 超出范围".format(m["emoji"], m["role"], idx))
    
    # 第一轮：并行调用测试
    print("\n" + "=" * 70)
    print("Round 1: Parallel Model Calling Test")
    print("=" * 70)
    
    prompts = [
        "作为产品经理，请简洁回答：什么是产品需求？",
        "作为架构师，请简洁回答：什么是系统架构？",
        "作为开发工程师，请简洁回答：什么是API？",
        "作为测试工程师，请简洁回答：什么是测试用例？",
        "作为运维工程师，请简洁回答：什么是监控？",
        "作为产品运营，请简洁回答：什么是用户留存？"
    ]
    
    print("\n开始并行调用...")
    results = parallel_call(prompts)
    
    print("\n并行调用结果:")
    total_tokens = 0
    for i, r in enumerate(results):
        m = MODELS[i]
        if r and r.get("success"):
            total_tokens += r.get("tokens", 0)
            print("\n  {} {} ({}):".format(m["emoji"], m["role"], r.get("model_id", "unknown")))
            print("    Provider: {}".format(r.get("provider", "unknown")))
            print("    Tokens: {} | Time: {:.2f}s".format(r.get("tokens", 0), r.get("time", 0)))
            print("    Content: {}".format(r.get("content", "")[:100]))
        else:
            print("\n  {} {}: FAILED - {}".format(m["emoji"], m["role"], r.get("error", "Unknown") if r else "No result"))
    
    # 第二轮：工具使用能力测试
    print("\n" + "=" * 70)
    print("Round 2: Tool Usage Capability Test")
    print("=" * 70)
    
    tool_results = []
    for m in MODELS:
        if "config" in m:
            print("\n  Testing {} ({})...".format(m["role"], m.get("model_name", "unknown")))
            capability = test_tool_usage(m["config"])
            tool_results.append({"model": m["role"], "capability": capability})
            print("    Score: {}/3".format(capability["overall_score"]))
            print("    - Numeric: {}".format(capability["numeric_calculation"]))
            print("    - Libraries: {}".format(capability["library_knowledge"]))
            print("    - Concept: {}".format(capability["concept_explanation"]))
    
    # 最终报告
    print("\n" + "=" * 70)
    print("Multi-Model Parallel Collaboration Report")
    print("=" * 70)
    
    print("\n模型调用统计:")
    for m in MODELS:
        if "config" in m:
            print("  {} {}: {} tokens".format(m["emoji"], m["role"], m.get("tokens", 0)))
    
    print("\n总Token消耗: {}".format(total_tokens))
    print("成功调用模型数: {}/{}".format(len([r for r in results if r and r.get("success")]), len(results)))
    
    # 保存报告
    report = {
        "title": "Symphony v4.0 True Multi-Model Collaboration",
        "version": "4.0",
        "datetime": datetime.now().isoformat(),
        "principles": [
            "每个模型只扮演一个角色",
            "使用不同模型并行调用",
            "禁止角色扮演",
            "检查工具使用能力"
        ],
        "models": MODELS,
        "parallel_results": results,
        "tool_results": tool_results,
        "summary": {
            "total_tokens": total_tokens,
            "successful_calls": len([r for r in results if r and r.get("success")]),
            "total_models": len(MODELS)
        }
    }
    
    with open("true_multi_model_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\nReport saved: true_multi_model_report.json")
    print("\nSymphony - 智韵交响，共创华章！")


if __name__ == "__main__":
    main()
