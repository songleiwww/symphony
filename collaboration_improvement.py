#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v3.2 - Model Collaboration Capability Improvement
Theme: Inter-model collaboration improvement and reporting
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
    {"name": "林思远", "role": "PM", "emoji": "PE", "provider": "zhipu"},
    {"name": "陈美琪", "role": "ARCH", "emoji": "AR", "provider": "zhipu"},
    {"name": "王浩然", "role": "DEV", "emoji": "DEV", "provider": "zhipu"},
    {"name": "刘心怡", "role": "TEST", "emoji": "TEST", "provider": "modelscope"},
    {"name": "张明远", "role": "OPS", "emoji": "OPS", "provider": "zhipu"},
    {"name": "赵敏", "role": "PO", "emoji": "PO", "provider": "modelscope"}
]

def get_model_config(ptype):
    for m in MODEL_CHAIN:
        if m.get("enabled") and m["provider"] == ptype:
            return m
    for m in MODEL_CHAIN:
        if m.get("enabled"):
            return m
    return None

def call_api(cfg, prompt, max_t=350):
    url = cfg["base_url"] + "/chat/completions"
    hdrs = {"Authorization": "Bearer " + cfg["api_key"], "Content-Type": "application/json"}
    data = {"model": cfg["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_t, "temperature": 0.7}
    t0 = time.time()
    try:
        r = requests.post(url, headers=hdrs, json=data, timeout=20)
        elapsed = time.time() - t0
        if r.status_code == 200:
            j = r.json()
            usage = j.get("usage", {})
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": usage.get("total_tokens", 0), "time": elapsed}
        else:
            return {"success": False, "error": "HTTP " + str(r.status_code), "time": elapsed}
    except Exception as e:
        return {"success": False, "error": str(e), "time": time.time() - t0}

def main():
    print("=" * 70)
    print("Symphony v3.2 - Model Collaboration Capability Improvement")
    print("=" * 70)
    
    for m in MODELS:
        cfg = get_model_config(m["provider"])
        m["config"] = cfg
        m["model_name"] = cfg["alias"]
        m["tokens"] = 0
        print("  {} {} -> {}".format(m["emoji"], m["name"], cfg["alias"]))
    
    discussions = []
    
    # Round 1: Current Collaboration Analysis
    print("\n" + "=" * 70)
    print("Round 1: Current Collaboration Analysis")
    print("=" * 70)
    
    prompts1 = [
        "As PM, analyze current model collaboration workflow issues",
        "As Architect, analyze technical collaboration architecture problems",
        "As DEV, identify code-level collaboration barriers",
        "As TEST, identify testing collaboration gaps",
        "As OPS, identify operational collaboration issues",
        "As PO, analyze user-facing collaboration problems"
    ]
    
    for i, m in enumerate(MODELS):
        print("\n{} {} analyzing...".format(m["emoji"], m["name"]))
        result = call_api(m["config"], prompts1[i])
        if result["success"]:
            m["tokens"] += result["tokens"]
            print("  OK: {} tokens".format(result["tokens"]))
            discussions.append({"name": m["name"], "round": 1, "topic": "Current Analysis", "content": result["content"]})
        else:
            print("  FAIL: {}".format(result.get("error", "Unknown")))
    
    # Round 2: Improvement Solutions
    print("\n" + "=" * 70)
    print("Round 2: Improvement Solutions")
    print("=" * 70)
    
    prompts2 = [
        "As PM, propose collaboration improvement solutions",
        "As ARCH, propose architectural improvements for collaboration",
        "As DEV, propose code-level collaboration improvements",
        "As TEST, propose testing collaboration improvements",
        "As OPS, propose operational collaboration improvements",
        "As PO, propose user experience collaboration improvements"
    ]
    
    for i, m in enumerate(MODELS):
        print("\n{} {} proposing solutions...".format(m["emoji"], m["name"]))
        result = call_api(m["config"], prompts2[i])
        if result["success"]:
            m["tokens"] += result["tokens"]
            print("  OK: {} tokens".format(result["tokens"]))
            discussions.append({"name": m["name"], "round": 2, "topic": "Solutions", "content": result["content"]})
        else:
            print("  FAIL: {}".format(result.get("error", "Unknown")))
    
    # Round 3: Implementation Plan
    print("\n" + "=" * 70)
    print("Round 3: Implementation Plan")
    print("=" * 70)
    
    prompts3 = [
        "As PM, define collaboration improvement roadmap",
        "As ARCH, define technical implementation plan",
        "As DEV, define development implementation steps",
        "As TEST, define testing implementation plan",
        "As OPS, define operational implementation plan",
        "As PO, define rollout and communication plan"
    ]
    
    for i, m in enumerate(MODELS):
        print("\n{} {} defining plan...".format(m["emoji"], m["name"]))
        result = call_api(m["config"], prompts3[i])
        if result["success"]:
            m["tokens"] += result["tokens"]
            print("  OK: {} tokens".format(result["tokens"]))
            discussions.append({"name": m["name"], "round": 3, "topic": "Implementation", "content": result["content"]})
        else:
            print("  FAIL: {}".format(result.get("error", "Unknown")))
    
    # Round 4: Final Report
    print("\n" + "=" * 70)
    print("Round 4: Final Report Generation")
    print("=" * 70)
    
    total_tokens = sum(m["tokens"] for m in MODELS)
    
    print("\n" + "=" * 70)
    print("Collaboration Improvement Report")
    print("=" * 70)
    
    print("\nExperts: {}".format(len(MODELS)))
    print("Rounds: 3")
    print("Total Tokens: {}".format(total_tokens))
    
    print("\nContributors:")
    for m in sorted(MODELS, key=lambda x: x["tokens"], reverse=True):
        print("  {} {}: {} tokens".format(m["emoji"], m["name"], m["tokens"]))
    
    # Improvement Summary
    print("\nImprovement Areas:")
    print("  1. Workflow Optimization")
    print("  2. Technical Architecture")
    print("  3. Code-level Collaboration")
    print("  4. Testing Integration")
    print("  5. Operations Coordination")
    print("  6. User Experience")
    
    # Save report
    report = {
        "title": "Symphony v3.2 Model Collaboration Improvement",
        "version": "3.2",
        "datetime": datetime.now().isoformat(),
        "theme": "Inter-model Collaboration Improvement",
        "models": MODELS,
        "discussions": discussions,
        "improvements": [
            "Workflow Optimization",
            "Technical Architecture Improvement",
            "Code-level Collaboration",
            "Testing Integration",
            "Operations Coordination",
            "User Experience Enhancement"
        ],
        "summary": {"total_tokens": total_tokens, "experts": len(MODELS), "rounds": 3}
    }
    
    with open("collaboration_improvement_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\nReport saved: collaboration_improvement_report.json")
    print("\nSymphony - 智韵交响，共创华章！")

if __name__ == "__main__":
    main()
