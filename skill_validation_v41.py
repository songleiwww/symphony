#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v4.1 - Skill Effectiveness Validation & Trigger Optimization
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


# 当前已实现的技能列表
SKILLS = [
    {"name": "被动触发引擎", "file": "passive_trigger_engine.py", "status": "已实现", "priority": "高"},
    {"name": "协作技能进化", "file": "collaboration_evolution.py", "status": "已实现", "priority": "高"},
    {"name": "调度容错改进", "file": "dispatch_fault_tolerance.py", "status": "已实现", "priority": "高"},
    {"name": "核心系统改进", "file": "core_system_improvement.py", "status": "已实现", "priority": "中"},
    {"name": "模型验证系统", "file": "model_verification.py", "status": "已实现", "priority": "高"},
    {"name": "自动发布系统", "file": "auto_release.py", "status": "已实现", "priority": "中"},
    {"name": "Debug追踪", "file": "debug_feature_tracker.py", "status": "已实现", "priority": "中"},
    {"name": "真正多模型", "file": "true_multi_model_v4.py", "status": "已实现", "priority": "高"},
]

# 触发词配置
TRIGGER_WORDS = {
    "P0_核心": ["交响", "symphony"],
    "P1_开发": ["开发", "研发", "实现", "构建"],
    "P2_优化": ["优化", "改进", "改善", "提升"],
    "P3_验证": ["验证", "测试", "检查", "分析"],
    "P4_发布": ["发布", "上线", " Release"],
}

MODELS = [
    {"name": "Model-1", "role": "产品经理", "emoji": "PE", "model_index": 0},
    {"name": "Model-2", "role": "架构师", "emoji": "AR", "model_index": 1},
    {"name": "Model-3", "role": "开发工程师", "emoji": "DEV", "model_index": 6},
    {"name": "Model-4", "role": "测试工程师", "emoji": "TEST", "model_index": 8},
    {"name": "Model-5", "role": "运维工程师", "emoji": "OPS", "model_index": 9},
    {"name": "Model-6", "role": "产品运营", "emoji": "PO", "model_index": 10},
]


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_config, prompt, max_tokens=350):
    url = model_config["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model_config["api_key"], "Content-Type": "application/json"}
    data = {"model": model_config["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    t0 = time.time()
    try:
        r = requests.post(url, headers=headers, json=data, timeout=20)
        elapsed = time.time() - t0
        if r.status_code == 200:
            j = r.json()
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": j.get("usage", {}).get("total_tokens", 0), "time": elapsed}
        else:
            return {"success": False, "error": "HTTP " + str(r.status_code), "time": elapsed}
    except Exception as e:
        return {"success": False, "error": str(e), "time": time.time() - t0}


def parallel_call(prompts):
    results = [None] * len(prompts)
    threads = []
    
    for i, prompt in enumerate(prompts):
        idx = MODELS[i]["model_index"]
        enabled = get_enabled_models()
        
        def call(idx, i, prompt):
            if idx < len(enabled):
                r = call_api(enabled[idx], prompt)
                results[i] = r
        
        t = threading.Thread(target=call, args=(idx, i, prompt))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    return results


def main():
    print("=" * 70)
    print("Symphony v4.1 - Skill Effectiveness & Trigger Optimization")
    print("=" * 70)
    
    enabled = get_enabled_models()
    print("\n可用模型: {}".format(len(enabled)))
    
    for m in MODELS:
        idx = m["model_index"]
        if idx < len(enabled):
            cfg = enabled[idx]
            m["model_name"] = cfg["alias"]
            m["provider"] = cfg["provider"]
            print("  {} {} -> {} ({})".format(m["emoji"], m["role"], cfg["alias"], cfg["provider"]))
    
    # Round 1: 技能有效性验证
    print("\n" + "=" * 70)
    print("Round 1: Skill Effectiveness Validation")
    print("=" * 70)
    
    prompts1 = [
        "作为产品经理，验证交响技能的有效性，列出当前技能的问题",
        "作为架构师，分析交响系统架构的有效性",
        "作为开发工程师，验证每个技能文件的实现效果",
        "作为测试工程师，制定技能有效性测试用例",
        "作为运维工程师，评估技能运行稳定性",
        "作为产品运营，分析用户意图匹配度"
    ]
    
    results1 = parallel_call(prompts1)
    
    print("\n技能验证结果:")
    total_tokens = 0
    for i, r in enumerate(results1):
        m = MODELS[i]
        if r and r.get("success"):
            total_tokens += r.get("tokens", 0)
            print("\n  {} {}: OK ({} tokens)".format(m["emoji"], m["role"], r.get("tokens", 0)))
            print("    {}".format(r.get("content", "")[:150]))
        else:
            print("\n  {} {}: FAILED".format(m["emoji"], m["role"]))
    
    # Round 2: 改进方案
    print("\n" + "=" * 70)
    print("Round 2: Improvement Plan")
    print("=" * 70)
    
    prompts2 = [
        "作为产品经理，提出技能改进方案",
        "作为架构师，提出架构优化方案",
        "作为开发工程师，提出代码改进建议",
        "作为测试工程师，提出验证优化方案",
        "作为运维工程师，提出稳定性改进方案",
        "作为产品运营，提出用户意图匹配改进"
    ]
    
    results2 = parallel_call(prompts2)
    
    print("\n改进方案:")
    for i, r in enumerate(results2):
        m = MODELS[i]
        if r and r.get("success"):
            total_tokens += r.get("tokens", 0)
            print("\n  {} {}: OK".format(m["emoji"], m["role"]))
            print("    {}".format(r.get("content", "")[:150]))
    
    # Round 3: 被动/主动触发优化
    print("\n" + "=" * 70)
    print("Round 3: Passive/Active Trigger Optimization")
    print("=" * 70)
    
    prompts3 = [
        "作为产品经理，设计被动触发优化方案",
        "作为架构师，设计主动触发架构",
        "作为开发工程师，实现触发优化代码",
        "作为测试工程师，测试触发有效性",
        "作为运维工程师，配置触发监控",
        "作为产品运营，分析触发用户满意度"
    ]
    
    results3 = parallel_call(prompts3)
    
    print("\n触发优化:")
    for i, r in enumerate(results3):
        m = MODELS[i]
        if r and r.get("success"):
            total_tokens += r.get("tokens", 0)
            print("\n  {} {}: OK".format(m["emoji"], m["role"]))
            print("    {}".format(r.get("content", "")[:150]))
    
    # 技能状态总结
    print("\n" + "=" * 70)
    print("Skill Status Summary")
    print("=" * 70)
    
    print("\n已实现技能:")
    for s in SKILLS:
        print("  [{}] {} - {}".format(s["status"], s["name"], s["priority"]))
    
    print("\n触发词配置:")
    for level, words in TRIGGER_WORDS.items():
        print("  {}: {}".format(level, ", ".join(words)))
    
    # 报告
    print("\n" + "=" * 70)
    print("Report")
    print("=" * 70)
    print("\n总Token消耗: {}".format(total_tokens))
    print("成功调用: {}/{}".format(
        len([r for r in results1 + results2 + results3 if r and r.get("success")]),
        len(results1) + len(results2) + len(results3)
    ))
    
    report = {
        "title": "Symphony v4.1 Skill Effectiveness & Trigger Optimization",
        "version": "4.1",
        "datetime": datetime.now().isoformat(),
        "skills": SKILLS,
        "triggers": TRIGGER_WORDS,
        "summary": {"total_tokens": total_tokens},
        "results": {
            "validation": results1,
            "improvement": results2,
            "optimization": results3
        }
    }
    
    with open("skill_validation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\nReport saved: skill_validation_report.json")
    print("\nSymphony - 智韵交响，共创华章！")


if __name__ == "__main__":
    main()
