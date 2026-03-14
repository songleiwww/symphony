#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v1.3.0 - Self-Evolution & Maintenance Discussion
多模型讨论：交响项目的自进化和维修处理方案
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


# 讨论团队
DISCUSSION_TEAM = [
    {"name": "林思远", "role": "产品经理", "emoji": "PE", "model_index": 0},
    {"name": "陈美琪", "role": "架构师", "emoji": "AR", "model_index": 1},
    {"name": "王浩然", "role": "开发工程师", "emoji": "DEV", "model_index": 6},
    {"name": "刘心怡", "role": "测试工程师", "emoji": "TEST", "model_index": 8},
    {"name": "张明远", "role": "运维工程师", "emoji": "OPS", "model_index": 9},
    {"name": "赵敏", "role": "产品运营", "emoji": "PO", "model_index": 10},
]

TOPIC = "交响项目的自进化和维修处理方案"


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_config, prompt, max_tokens=400):
    url = model_config["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model_config["api_key"], "Content-Type": "application/json"}
    data = {"model": model_config["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    t0 = time.time()
    try:
        r = requests.post(url, headers=headers, json=data, timeout=25)
        elapsed = time.time() - t0
        if r.status_code == 200:
            j = r.json()
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": j.get("usage", {}).get("total_tokens", 0), "time": elapsed}
        else:
            return {"success": False, "error": "HTTP " + str(r.status_code)}
    except Exception as e:
        return {"success": False, "error": str(e)}


print("=" * 70)
print("Symphony v1.3.0 - Self-Evolution & Maintenance Discussion")
print("=" * 70)

enabled = get_enabled_models()
for m in DISCUSSION_TEAM:
    idx = m["model_index"]
    if idx < len(enabled):
        cfg = enabled[idx]
        m["model_name"] = cfg["alias"]
        print("  {} {} -> {}".format(m["emoji"], m["name"], cfg["alias"]))

# Round 1: 问题诊断
print("\n" + "=" * 70)
print("Round 1: Problem Diagnosis")
print("=" * 70)

diagnosis_prompts = [
    "作为产品经理，诊断交响项目当前存在的问题和挑战",
    "作为架构师，分析交响系统架构的不足和风险",
    "作为开发工程师，列出代码层面的技术债务",
    "作为测试工程师，指出质量保障方面隐患",
    "作为运维工程师，指出运维和监控薄弱环节",
    "作为产品运营，收集用户反馈问题"
]

results1 = []
threads = []

def call_diagnosis(i, prompt):
    idx = DISCUSSION_TEAM[i]["model_index"]
    enabled = get_enabled_models()
    if idx < len(enabled):
        r = call_api(enabled[idx], prompt)
        results1.append({"index": i, "result": r})

for i, prompt in enumerate(diagnosis_prompts):
    t = threading.Thread(target=call_diagnosis, args=(i, prompt))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("\n问题诊断结果:")
total_tokens = 0
for r in sorted(results1, key=lambda x: x["index"]):
    i = r["index"]
    m = DISCUSSION_TEAM[i]
    result = r["result"]
    if result.get("success"):
        total_tokens += result.get("tokens", 0)
        print("\n  【{}】: OK ({} tokens)".format(m["name"], result.get("tokens", 0)))
        print("    {}".format(result.get("content", "")[:200]))
    else:
        print("\n  【{}】: FAILED".format(m["name"]))

# Round 2: 自进化方案
print("\n" + "=" * 70)
print("Round 2: Self-Evolution Solutions")
print("=" * 70)

evolution_prompts = [
    "作为产品经理，提出交响项目的自进化路线图",
    "作为架构师，设计交响系统的自我优化机制",
    "作为开发工程师，规划代码自修复和自优化功能",
    "作为测试工程师，设计自动化测试和自验证系统",
    "作为运维工程师，构建自我监控和自愈系统",
    "作为产品运营，规划用户驱动的进化机制"
]

results2 = []
threads2 = []

def call_evolution(i, prompt):
    idx = DISCUSSION_TEAM[i]["model_index"]
    enabled = get_enabled_models()
    if idx < len(enabled):
        r = call_api(enabled[idx], prompt)
        results2.append({"index": i, "result": r})

for i, prompt in enumerate(evolution_prompts):
    t = threading.Thread(target=call_evolution, args=(i, prompt))
    threads2.append(t)
    t.start()

for t in threads2:
    t.join()

print("\n自进化方案:")
for r in sorted(results2, key=lambda x: x["index"]):
    i = r["index"]
    m = DISCUSSION_TEAM[i]
    result = r["result"]
    if result.get("success"):
        total_tokens += result.get("tokens", 0)
        print("\n  【{}】: OK ({} tokens)".format(m["name"], result.get("tokens", 0)))
        print("    {}".format(result.get("content", "")[:200]))
    else:
        print("\n  【{}】: FAILED".format(m["name"]))

# Round 3: 维修处理方案
print("\n" + "=" * 70)
print("Round 3: Maintenance Solutions")
print("=" * 70)

maintenance_prompts = [
    "作为产品经理，制定交响项目的维护计划",
    "作为架构师，设计故障隔离和降级机制",
    "作为开发工程师，编写错误处理和恢复代码",
    "作为测试工程师，建立回归测试和监控体系",
    "作为运维工程师，制定告警响应和故障恢复流程",
    "作为产品运营，规划用户问题反馈处理机制"
]

results3 = []
threads3 = []

def call_maintenance(i, prompt):
    idx = DISCUSSION_TEAM[i]["model_index"]
    enabled = get_enabled_models()
    if idx < len(enabled):
        r = call_api(enabled[idx], prompt)
        results3.append({"index": i, "result": r})

for i, prompt in enumerate(maintenance_prompts):
    t = threading.Thread(target=call_maintenance, args=(i, prompt))
    threads3.append(t)
    t.start()

for t in threads3:
    t.join()

print("\n维修处理方案:")
for r in sorted(results3, key=lambda x: x["index"]):
    i = r["index"]
    m = DISCUSSION_TEAM[i]
    result = r["result"]
    if result.get("success"):
        total_tokens += result.get("tokens", 0)
        print("\n  【{}】: OK ({} tokens)".format(m["name"], result.get("tokens", 0)))
        print("    {}".format(result.get("content", "")[:200]))
    else:
        print("\n  【{}】: FAILED".format(m["name"]))

# 总结
print("\n" + "=" * 70)
print("Discussion Summary")
print("=" * 70)

print("\n  讨论主题: {}".format(TOPIC))
print("  参会专家: {} 位".format(len(DISCUSSION_TEAM)))
print("  讨论轮次: 3 轮")
print("  总Token消耗: {}".format(total_tokens))

# 保存报告
report = {
    "title": "Symphony v1.3.0 Self-Evolution & Maintenance",
    "version": "1.3.0",
    "datetime": datetime.now().isoformat(),
    "topic": TOPIC,
    "team": DISCUSSION_TEAM,
    "rounds": {
        "diagnosis": results1,
        "evolution": results2,
        "maintenance": results3
    },
    "summary": {"total_tokens": total_tokens}
}

with open("evolution_maintenance_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("\nReport saved: evolution_maintenance_report.json")
print("\nSymphony - 智韵交响，共创华章！")
