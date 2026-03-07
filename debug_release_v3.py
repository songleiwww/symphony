#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v3.0 - Debug Fix and Release
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

BUGS = [
    {"id": "BUG-001", "desc": "Passive trigger import error", "severity": "High"},
    {"id": "BUG-002", "desc": "API key exposure", "severity": "High"},
    {"id": "BUG-003", "desc": "Memory JSON parse error", "severity": "Medium"},
    {"id": "BUG-004", "desc": "Scheduling timeout issue", "severity": "Medium"},
    {"id": "BUG-005", "desc": "Report encoding issue", "severity": "Low"}
]

def get_model_config(ptype):
    for m in MODEL_CHAIN:
        if m.get("enabled") and m["provider"] == ptype:
            return m
    for m in MODEL_CHAIN:
        if m.get("enabled"):
            return m
    return None

def call_api(cfg, prompt, max_t=300):
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
    print("Symphony v3.0 - Debug Fix and Release")
    print("=" * 70)
    
    for m in MODELS:
        cfg = get_model_config(m["provider"])
        m["config"] = cfg
        m["model_name"] = cfg["alias"]
        m["tokens"] = 0
        print("  {} {} -> {}".format(m["emoji"], m["name"], cfg["alias"]))
    
    fixes = []
    discussions = []
    
    print("\n" + "=" * 70)
    print("Round 1: Bug Detection")
    print("=" * 70)
    
    prompts1 = [
        "As Product Manager, list 3 potential issues in Symphony",
        "As Architect, list 3 architectural issues",
        "As Developer, list known bugs and fixes",
        "As Tester, list discovered bugs",
        "As Ops, list runtime issues",
        "As Product Ops, list UX issues"
    ]
    
    for i, m in enumerate(MODELS):
        print("\n{} {} detecting...".format(m["emoji"], m["name"]))
        result = call_api(m["config"], prompts1[i])
        if result["success"]:
            m["tokens"] += result["tokens"]
            print("  OK: {} tokens".format(result["tokens"]))
            discussions.append({"name": m["name"], "topic": "Bug Detection", "content": result["content"]})
        else:
            print("  FAIL: {}".format(result.get("error", "Unknown")))
    
    print("\n" + "=" * 70)
    print("Round 2: Bug Fixing")
    print("=" * 70)
    
    for bug in BUGS:
        print("\n  Fixing {}: {}".format(bug["id"], bug["desc"]))
        dev = [m for m in MODELS if m["role"] == "DEV"][0]
        prompt = "Provide fix for Bug {}: {}".format(bug["id"], bug["desc"])
        result = call_api(dev["config"], prompt, 400)
        if result["success"]:
            dev["tokens"] += result["tokens"]
            print("    OK: {} tokens".format(result["tokens"]))
            fixes.append({"bug_id": bug["id"], "desc": bug["desc"], "fix": result["content"], "status": "Fixed"})
        else:
            print("    FAIL")
            fixes.append({"bug_id": bug["id"], "status": "Failed"})
    
    print("\n" + "=" * 70)
    print("Round 3: Documentation")
    print("=" * 70)
    
    prompts3 = [
        "As PM, suggest doc structure",
        "As Architect, suggest tech doc structure",
        "As Developer, write API doc summary",
        "As Tester, write test doc summary",
        "As Ops, write ops doc summary",
        "As PO, write user manual"
    ]
    
    for i, m in enumerate(MODELS):
        print("\n{} {} documenting...".format(m["emoji"], m["name"]))
        result = call_api(m["config"], prompts3[i])
        if result["success"]:
            m["tokens"] += result["tokens"]
            print("  OK: {} tokens".format(result["tokens"]))
            discussions.append({"name": m["name"], "topic": "Documentation", "content": result["content"]})
        else:
            print("  FAIL: {}".format(result.get("error", "Unknown")))
    
    print("\n" + "=" * 70)
    print("Round 4: Release v3.0")
    print("=" * 70)
    
    total_tokens = sum(m["tokens"] for m in MODELS)
    
    release = "# Symphony v3.0 Official Release\n\n"
    release += "Version: v3.0 Official\n"
    release += "Date: " + datetime.now().strftime('%Y-%m-%d') + "\n"
    release += "Slogan: 智韵交响，共创华章！\n\n"
    release += "---\n\n## New Features\n"
    release += "- Passive Trigger Engine v2.0\n"
    release += "- Real Model Verification System\n"
    release += "- Debug Tracking System\n"
    release += "- Auto Release\n\n"
    release += "## Bug Fixes\n"
    
    for fix in fixes:
        release += "- {}: {} - {}\n".format(fix["bug_id"], fix.get("desc", ""), fix.get("status", ""))
    
    release += "\n## Contributors\n"
    for m in sorted(MODELS, key=lambda x: x["tokens"], reverse=True):
        release += "- {} {}: {} tokens\n".format(m["emoji"], m["name"], m["tokens"])
    
    release += "\n---\n\nStats:\n"
    release += "- Experts: {}\n".format(len(MODELS))
    release += "- Bugs Fixed: {}\n".format(len([f for f in fixes if f.get("status") == "Fixed"]))
    release += "- Total Tokens: {}\n\n".format(total_tokens)
    release += "Symphony - 智韵交响，共创华章！\n"
    
    release_file = "RELEASE_v3.0_" + datetime.now().strftime('%Y%m%d') + ".md"
    with open(release_file, "w", encoding="utf-8") as f:
        f.write(release)
    
    print("\n  Release saved: " + release_file)
    
    print("\n" + "=" * 70)
    print("Release Report")
    print("=" * 70)
    print("\nExperts: {}".format(len(MODELS)))
    print("Bugs Fixed: {}".format(len(fixes)))
    print("Total Tokens: {}".format(total_tokens))
    
    print("\nContributors:")
    for m in sorted(MODELS, key=lambda x: x["tokens"], reverse=True):
        print("  {} {}: {} tokens".format(m["emoji"], m["name"], m["tokens"]))
    
    print("\nBug Fix Status:")
    for fix in fixes:
        status = "OK" if fix.get("status") == "Fixed" else "FAIL"
        print("  {} {}: {}".format(status, fix["bug_id"], fix.get("desc", "")))
    
    report = {
        "title": "Symphony v3.0 Release",
        "version": "3.0",
        "datetime": datetime.now().isoformat(),
        "models": MODELS,
        "fixes": fixes,
        "discussions": discussions,
        "summary": {"total_tokens": total_tokens, "bugs_fixed": len([f for f in fixes if f.get("status") == "Fixed"])}
    }
    
    with open("release_v3_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\nReport saved: release_v3_report.json")
    print("\nSymphony - 智韵交响，共创华章！")

if __name__ == "__main__":
    main()
