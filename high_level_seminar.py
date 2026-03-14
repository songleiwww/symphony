#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v3.1 - High-Level Development Seminar
Theme: Model Tool Usage Capability + Participant Selection Standards
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
    {"name": "刘心怡", "role": "TEST", "emoji": "TEST", "provider": "zhipu"},
    {"name": "张明远", "role": "OPS", "emoji": "OPS", "provider": "modelscope"},
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
    print("Symphony v3.1 - High-Level Development Seminar")
    print("Theme: Model Tool Usage + Participant Selection Standards")
    print("=" * 70)
    
    for m in MODELS:
        cfg = get_model_config(m["provider"])
        m["config"] = cfg
        m["model_name"] = cfg["alias"]
        m["tokens"] = 0
        print("  {} {} -> {}".format(m["emoji"], m["name"], cfg["alias"]))
    
    discussions = []
    
    # Round 1: Model Tool Usage Capability
    print("\n" + "=" * 70)
    print("Round 1: Model Tool Usage Capability Development")
    print("=" * 70)
    
    prompts1 = [
        "As PM, design the product requirements for model tool usage capability",
        "As Architect, design the architecture for model tool integration",
        "As Developer, explain how to implement tool calling in models (code framework)",
        "As Tester, design test cases for tool usage verification",
        "As Ops, design monitoring for tool execution",
        "As PO, analyze the value of tool-enabled models"
    ]
    
    for i, m in enumerate(MODELS):
        print("\n{} {} discussing tool usage...".format(m["emoji"], m["name"]))
        result = call_api(m["config"], prompts1[i])
        if result["success"]:
            m["tokens"] += result["tokens"]
            print("  OK: {} tokens".format(result["tokens"]))
            discussions.append({"name": m["name"], "topic": "Tool Usage", "content": result["content"]})
        else:
            print("  FAIL: {}".format(result.get("error", "Unknown")))
    
    # Round 2: Participant Selection Standards
    print("\n" + "=" * 70)
    print("Round 2: Participant Selection Standards")
    print("=" * 70)
    
    prompts2 = [
        "As PM, define criteria for selecting development participants",
        "As Architect, define technical capability assessment standards",
        "As Developer, define coding skill evaluation metrics",
        "As Tester, define quality assurance capability standards",
        "As Ops, define operational skill requirements",
        "As PO, define collaboration and communication standards"
    ]
    
    for i, m in enumerate(MODELS):
        print("\n{} {} defining selection standards...".format(m["emoji"], m["name"]))
        result = call_api(m["config"], prompts2[i])
        if result["success"]:
            m["tokens"] += result["tokens"]
            print("  OK: {} tokens".format(result["tokens"]))
            discussions.append({"name": m["name"], "topic": "Selection Standards", "content": result["content"]})
        else:
            print("  FAIL: {}".format(result.get("error", "Unknown")))
    
    # Round 3: Real Capability Assessment
    print("\n" + "=" * 70)
    print("Round 3: Real Capability Assessment")
    print("=" * 70)
    
    prompts3 = [
        "As PM, design real capability assessment method for participants",
        "As Architect, design technical capability verification process",
        "As Developer, design practical coding test framework",
        "As Tester, design skill verification test suite",
        "As Ops, design operational capability assessment",
        "As PO, design comprehensive evaluation system"
    ]
    
    for i, m in enumerate(MODELS):
        print("\n{} {} assessing capabilities...".format(m["emoji"], m["name"]))
        result = call_api(m["config"], prompts3[i])
        if result["success"]:
            m["tokens"] += result["tokens"]
            print("  OK: {} tokens".format(result["tokens"]))
            discussions.append({"name": m["name"], "topic": "Capability Assessment", "content": result["content"]})
        else:
            print("  FAIL: {}".format(result.get("error", "Unknown")))
    
    # Round 4: Implementation Plan
    print("\n" + "=" * 70)
    print("Round 4: Implementation Plan")
    print("=" * 70)
    
    total_tokens = sum(m["tokens"] for m in MODELS)
    
    print("\n" + "=" * 70)
    print("Seminar Report")
    print("=" * 70)
    
    print("\nExperts: {}".format(len(MODELS)))
    print("Total Tokens: {}".format(total_tokens))
    
    print("\nContributors:")
    for m in sorted(MODELS, key=lambda x: x["tokens"], reverse=True):
        print("  {} {}: {} tokens".format(m["emoji"], m["name"], m["tokens"]))
    
    # Key deliverables
    print("\nKey Deliverables:")
    print("  1. Model Tool Usage Capability Design")
    print("  2. Participant Selection Standards")
    print("  3. Real Capability Assessment System")
    
    # Save report
    report = {
        "title": "Symphony v3.1 High-Level Seminar",
        "version": "3.1",
        "datetime": datetime.now().isoformat(),
        "theme": "Tool Usage + Participant Selection",
        "models": MODELS,
        "discussions": discussions,
        "deliverables": [
            "Model Tool Usage Capability Design",
            "Participant Selection Standards", 
            "Real Capability Assessment System"
        ],
        "summary": {"total_tokens": total_tokens, "experts": len(MODELS)}
    }
    
    with open("seminar_v31_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\nReport saved: seminar_v31_report.json")
    print("\nSymphony - 智韵交响，共创华章！")

if __name__ == "__main__":
    main()
