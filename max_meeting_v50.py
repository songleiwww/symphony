#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v5.0 - Maximum Discussion Meeting
Theme: Evolution Capability Selection & Work Reports
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


# 6位专家模型 - 分配不同模型
MODELS = [
    {"name": "林思远", "role": "产品经理", "emoji": "PE", "model_index": 0, "tasks": [], "tokens": 0},
    {"name": "陈美琪", "role": "架构师", "emoji": "AR", "model_index": 1, "tasks": [], "tokens": 0},
    {"name": "王浩然", "role": "开发工程师", "emoji": "DEV", "model_index": 6, "tasks": [], "tokens": 0},
    {"name": "刘心怡", "role": "测试工程师", "emoji": "TEST", "model_index": 8, "tasks": [], "tokens": 0},
    {"name": "张明远", "role": "运维工程师", "emoji": "OPS", "model_index": 9, "tasks": [], "tokens": 0},
    {"name": "赵敏", "role": "产品运营", "emoji": "PO", "model_index": 10, "tasks": [], "tokens": 0},
]

# 交响已完成的进化能力
EVOLUTION_CAPABILITIES = [
    {"id": "EV-001", "name": "被动触发引擎", "desc": "多模式智能触发", "priority": "高", "status": "完成"},
    {"id": "EV-002", "name": "真正多模型协作", "desc": "并行调用不同模型", "priority": "高", "status": "完成"},
    {"id": "EV-003", "name": "模型验证系统", "desc": "真实API调用验证", "priority": "高", "status": "完成"},
    {"id": "EV-004", "name": "技能有效性验证", "desc": "技能测试与优化", "priority": "中", "status": "完成"},
    {"id": "EV-005", "name": "多模型类型正确使用", "desc": "图像/向量/排序模型", "priority": "高", "status": "完成"},
    {"id": "EV-006", "name": "Debug追踪系统", "desc": "Bug检测与修复", "priority": "中", "status": "完成"},
    {"id": "EV-007", "name": "自动发布系统", "desc": "GitHub自动发布", "priority": "中", "status": "完成"},
    {"id": "EV-008", "name": "调度容错改进", "desc": "错误处理与降级", "priority": "高", "status": "完成"},
]


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
print("Symphony v5.0 - Maximum Discussion Meeting")
print("Theme: Evolution Capability Selection & Work Reports")
print("=" * 70)

# 初始化模型配置
enabled = get_enabled_models()
for m in MODELS:
    idx = m["model_index"]
    if idx < len(enabled):
        cfg = enabled[idx]
        m["model_name"] = cfg["alias"]
        m["provider"] = cfg["provider"]
        print("  {} {} -> {} ({})".format(m["emoji"], m["name"], cfg["alias"], cfg["provider"]))

# Round 1: 进化能力评估
print("\n" + "=" * 70)
print("Round 1: Evolution Capability Assessment")
print("=" * 70)

evolve_prompts = [
    "作为产品经理，评估交响进化能力，列出最优秀的3项并说明理由",
    "作为架构师，从技术角度评估交响架构进化，选出最重要的3项",
    "作为开发工程师，评估代码实现进化能力，选出最实用的3项",
    "作为测试工程师，评估质量保障进化能力，选出最关键的3项",
    "作为运维工程师，评估运维自动化进化能力，选出最有效的3项",
    "作为产品运营，评估用户价值进化能力，选出最有价值的3项"
]

results1 = []
threads = []

def call_model(i, prompt):
    idx = MODELS[i]["model_index"]
    enabled = get_enabled_models()
    if idx < len(enabled):
        r = call_api(enabled[idx], prompt)
        results1.append({"index": i, "result": r})

for i, prompt in enumerate(evolve_prompts):
    t = threading.Thread(target=call_model, args=(i, prompt))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("\n进化能力评估结果:")
total_tokens = 0
for r in sorted(results1, key=lambda x: x["index"]):
    i = r["index"]
    m = MODELS[i]
    result = r["result"]
    if result.get("success"):
        MODELS[i]["tokens"] += result.get("tokens", 0)
        total_tokens += result.get("tokens", 0)
        print("\n  {} {}: OK ({} tokens)".format(m["emoji"], m["name"], result.get("tokens", 0)))
        print("    {}".format(result.get("content", "")[:200]))
    else:
        print("\n  {} {}: FAILED".format(m["emoji"], m["name"]))

# Round 2: 述职报告 - 各自汇报工作
print("\n" + "=" * 70)
print("Round 2: Work Reports (述职报告)")
print("=" * 70)

work_reports = [
    "作为产品经理，提交你的述职报告：1.完成了哪些工作 2.解决了什么问题 3.下一步计划",
    "作为架构师，提交你的述职报告：1.完成了哪些工作 2.解决了什么问题 3.下一步计划",
    "作为开发工程师，提交你的述职报告：1.完成了哪些工作 2.解决了什么问题 3.下一步计划",
    "作为测试工程师，提交你的述职报告：1.完成了哪些工作 2.解决了什么问题 3.下一步计划",
    "作为运维工程师，提交你的述职报告：1.完成了哪些工作 2.解决了什么问题 3.下一步计划",
    "作为产品运营，提交你的述职报告：1.完成了哪些工作 2.解决了什么问题 3.下一步计划"
]

results2 = []
threads2 = []

def call_report(i, prompt):
    idx = MODELS[i]["model_index"]
    enabled = get_enabled_models()
    if idx < len(enabled):
        r = call_api(enabled[idx], prompt, 500)
        results2.append({"index": i, "result": r, "name": MODELS[i]["name"], "role": MODELS[i]["role"]})

for i, prompt in enumerate(work_reports):
    t = threading.Thread(target=call_report, args=(i, prompt))
    threads2.append(t)
    t.start()

for t in threads2:
    t.join()

print("\n述职报告:")
for r in sorted(results2, key=lambda x: x["index"]):
    i = r["index"]
    m = MODELS[i]
    result = r["result"]
    if result.get("success"):
        MODELS[i]["tokens"] += result.get("tokens", 0)
        total_tokens += result.get("tokens", 0)
        
        # 记录任务
        content = result.get("content", "")
        MODELS[i]["tasks"].append(content[:300])
        
        print("\n  {} {} 的述职报告:".format(m["emoji"], m["name"]))
        print("    {}".format(content[:300]))
    else:
        print("\n  {} {}: 述职失败".format(m["emoji"], m["name"]))

# Round 3: 最佳选择
print("\n" + "=" * 70)
print("Round 3: Best Selection")
print("=" * 70)

# 根据Token消耗选出最佳
best_model = max(MODELS, key=lambda x: x.get("tokens", 0))

print("\n  🏆 最佳贡献奖: {} {} ({} tokens)".format(
    best_model["emoji"], best_model["name"], best_model.get("tokens", 0)))

# 排名
print("\n  贡献排名:")
for i, m in enumerate(sorted(MODELS, key=lambda x: x.get("tokens", 0), reverse=True)):
    medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "  "
    print("    {} {} - {}: {} tokens".format(medal, m["name"], m["role"], m.get("tokens", 0)))

# 最终报告
print("\n" + "=" * 70)
print("Final Report")
print("=" * 70)

print("\n  参会专家: {} 位".format(len(MODELS)))
print("  进化能力: {} 项".format(len(EVOLUTION_CAPABILITIES)))
print("  总Token消耗: {}".format(total_tokens))
print("  最佳贡献: {} {}".format(best_model["emoji"], best_model["name"]))

print("\n  已完成的进化能力:")
for ev in EVOLUTION_CAPABILITIES:
    print("    [{}] {} - {}".format(ev["status"], ev["name"], ev["desc"]))

# 保存完整报告
report = {
    "title": "Symphony v5.0 Maximum Discussion Meeting",
    "version": "5.0",
    "datetime": datetime.now().isoformat(),
    "theme": "Evolution Capability & Work Reports",
    "evolution_capabilities": EVOLUTION_CAPABILITIES,
    "models": MODELS,
    "best_model": {"name": best_model["name"], "role": best_model["role"], "tokens": best_model.get("tokens", 0)},
    "summary": {
        "total_experts": len(MODELS),
        "total_evolution": len(EVOLUTION_CAPABILITIES),
        "total_tokens": total_tokens
    }
}

with open("max_meeting_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("\nReport saved: max_meeting_report.json")
print("\nSymphony - 智韵交响，共创华章！")
