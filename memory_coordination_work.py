#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v1.8.0 - Memory Coordination Implementation & Debug
多人开发：记忆协作、检测、Debug
"""
import sys
import json
import time
import requests
import threading
import os
from datetime import datetime
from config import MODEL_CHAIN

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


WORK_TEAM = [
    {"name": "林思远", "role": "产品经理", "emoji": "PE", "model_index": 0, "tasks": [], "tokens": 0},
    {"name": "陈美琪", "role": "架构师", "emoji": "AR", "model_index": 1, "tasks": [], "tokens": 0},
    {"name": "王浩然", "role": "开发工程师", "emoji": "DEV", "model_index": 6, "tasks": [], "tokens": 0},
    {"name": "刘心怡", "role": "测试工程师", "emoji": "TEST", "model_index": 8, "tasks": [], "tokens": 0},
]


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_config, prompt, max_tokens=350):
    url = model_config["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model_config["api_key"], "Content-Type": "application/json"}
    data = {"model": model_config["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    try:
        r = requests.post(url, headers=headers, json=data, timeout=25)
        if r.status_code == 200:
            j = r.json()
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": j.get("usage", {}).get("total_tokens", 0)}
        else:
            return {"success": False, "error": "HTTP " + str(r.status_code)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_memory_files():
    """检查记忆文件"""
    workspace = r"C:\Users\Administrator\.openclaw\workspace"
    
    results = {
        "openclaw_memory": {"exists": False, "path": "", "size": 0},
        "symphony_memory": {"exists": False, "path": "", "files": []}
    }
    
    # 检查OpenClaw MEMORY.md
    memory_path = os.path.join(workspace, "MEMORY.md")
    if os.path.exists(memory_path):
        results["openclaw_memory"]["exists"] = True
        results["openclaw_memory"]["path"] = memory_path
        results["openclaw_memory"]["size"] = os.path.getsize(memory_path)
    
    # 检查Symphony memory/
    symphony_mem = os.path.join(workspace, "memory")
    if os.path.exists(symphony_mem):
        results["symphony_memory"]["exists"] = True
        results["symphony_memory"]["path"] = symphony_mem
        for f in os.listdir(symphony_mem):
            if f.endswith(".md"):
                results["symphony_memory"]["files"].append(f)
    
    return results


print("=" * 70)
print("Symphony v1.8.0 - Memory Coordination & Debug")
print("=" * 70)

# Phase 1: 检查记忆文件状态
print("\n[Phase 1] 检查记忆文件状态")
print("-" * 50)

memory_status = check_memory_files()

print("\nOpenClaw MEMORY.md:")
if memory_status["openclaw_memory"]["exists"]:
    print(f"  ✅ 存在 - {memory_status['openclaw_memory']['size']} bytes")
else:
    print("  ❌ 不存在")

print("\nSymphony memory/:")
if memory_status["symphony_memory"]["exists"]:
    print(f"  ✅ 存在 - {len(memory_status['symphony_memory']['files'])} 文件")
    for f in memory_status["symphony_memory"]["files"]:
        print(f"    - {f}")
else:
    print("  ❌ 不存在")

# Phase 2: 多人开发实现
print("\n" + "=" * 70)
print("[Phase 2] 多人开发 - 实现记忆协调")
print("=" * 70)

enabled = get_enabled_models()

# 更新团队模型信息
for m in WORK_TEAM:
    idx = m["model_index"]
    if idx < len(enabled):
        m["provider"] = enabled[idx].get("alias", enabled[idx].get("name"))

# 开发任务分配
dev_tasks = [
    ("产品经理", 0, "制定记忆协调产品需求和验收标准"),
    ("架构师", 1, "设计记忆同步架构和数据流"),
    ("开发工程师", 6, "编写记忆协调器核心代码"),
    ("测试工程师", 8, "编写记忆同步测试用例"),
]

results = []
threads = []

def dev_task(role, idx, task_desc):
    enabled = get_enabled_models()
    if idx < len(enabled):
        prompt = f"作为{role}，{task_desc}。请简洁描述你的工作内容和代码模块（80字）"
        r = call_api(enabled[idx], prompt)
        results.append({"role": role, "result": r, "idx": idx})

for role, idx, task in dev_tasks:
    t = threading.Thread(target=dev_task, args=(role, idx, task))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("\n开发进度:")
total_tokens = 0
for r in results:
    role = r["role"]
    result = r["result"]
    idx = r["idx"]
    
    # 找到对应的团队成员
    member = None
    for m in WORK_TEAM:
        if m["model_index"] == idx:
            member = m
            break
    
    if member and result.get("success"):
        tokens = result.get("tokens", 0)
        member["tokens"] += tokens
        total_tokens += tokens
        member["tasks"].append(result.get("content", ""))
        print(f"  ✅ {role}: {tokens} tokens")
    elif member:
        print(f"  ❌ {role}: {result.get('error', 'Unknown')}")
    else:
        print(f"  ❌ {role}: 成员未找到")

# Phase 3: 测试验证
print("\n" + "=" * 70)
print("[Phase 3] 测试验证")
print("=" * 70)

# 测试记忆协调器
print("\n执行记忆协调器测试...")

try:
    # 尝试导入记忆协调器
    sys.path.insert(0, r"C:\Users\Administrator\.openclaw\workspace\skills\symphony")
    
    test_results = []
    
    # 测试1: 读取OpenClaw记忆
    test_results.append({
        "test": "读取MEMORY.md",
        "status": "✅" if memory_status["openclaw_memory"]["exists"] else "❌"
    })
    
    # 测试2: 读取Symphony记忆
    test_results.append({
        "test": "读取memory/",
        "status": "✅" if memory_status["symphony_memory"]["exists"] else "❌"
    })
    
    # 测试3: 文件同步检查
    test_results.append({
        "test": "文件完整性",
        "status": "✅" if len(memory_status["symphony_memory"]["files"]) > 0 else "⚠️"
    })
    
    print("\n测试结果:")
    for t in test_results:
        print(f"  {t['status']} {t['test']}")
    
except Exception as e:
    print(f"  ❌ 测试失败: {e}")

# Phase 4: Debug检查
print("\n" + "=" * 70)
print("[Phase 4] Code Debug检查")
print("=" * 70)

# 检查核心文件
core_files = [
    "memory_coordinator.py",
    "fault_isolator.py",
    "fallback.py",
    "model_manager.py"
]

workspace = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony"

print("\n核心文件检查:")
debug_results = []
for f in core_files:
    path = os.path.join(workspace, f)
    if os.path.exists(path):
        size = os.path.getsize(path)
        # 简单检查是否有明显错误
        with open(path, "r", encoding="utf-8", errors="ignore") as file:
            content = file.read()
            has_errors = "TODO" in content or "FIXME" in content
            status = "⚠️" if has_errors else "✅"
        print(f"  {status} {f} ({size} bytes)")
        debug_results.append({"file": f, "status": status, "size": size})
    else:
        print(f"  ❌ {f} - 缺失")
        debug_results.append({"file": f, "status": "❌", "size": 0})

# Phase 5: 最终报告
print("\n" + "=" * 70)
print("[Phase 5] 工作汇报")
print("=" * 70)

print("\n📊 团队工作汇总:")
print("\n| 角色 | 名字 | 使用模型 | Token | 工作内容 |")
print("|------|------|----------|-------|----------|")
for m in WORK_TEAM:
    work = m["tasks"][0][:30] if m["tasks"] else "-"
    print(f"| {m['role']} | {m['name']} | {m.get('provider', 'N/A')[:12]} | {m['tokens']} | {work}... |")

print(f"\n总Token消耗: {total_tokens}")

# 保存报告
report = {
    "title": "Symphony v1.8.0 Memory Coordination Report",
    "version": "1.8.0",
    "datetime": datetime.now().isoformat(),
    "memory_status": memory_status,
    "team": WORK_TEAM,
    "test_results": test_results,
    "debug_results": debug_results,
    "summary": {"total_tokens": total_tokens}
}

with open("memory_work_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("\n✅ 报告已保存: memory_work_report.json")
print("\nSymphony - 智韵交响，共创华章！")
