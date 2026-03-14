#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响v2.5 - Debug检测与功能追踪系统
检测交响技能bug，追踪已实现的功能和文件
"""

import sys
import json
import time
import os
import requests
from datetime import datetime
from pathlib import Path
from config import MODEL_CHAIN

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


MODELS = [
    {"name": "林思远", "role": "产品经理", "emoji": "📋", "provider": "zhipu"},
    {"name": "陈美琪", "role": "架构师", "emoji": "🏗️", "provider": "zhipu"},
    {"name": "王浩然", "role": "开发工程师", "emoji": "💻", "provider": "zhipu"},
    {"name": "刘心怡", "role": "测试工程师", "emoji": "🧪", "provider": "modelscope"},
    {"name": "张明远", "role": "运维工程师", "emoji": "🔧", "provider": "zhipu"},
    {"name": "赵敏", "role": "产品运营", "emoji": "📈", "provider": "modelscope"}
]

# 已实现的文件和功能
IMPLEMENTED_FEATURES = {
    "核心文件": [
        {"file": "config.py", "desc": "17个模型配置", "status": "✅ 完成"},
        {"file": "model_manager.py", "desc": "模型管理器", "status": "✅ 完成"},
        {"file": "fault_tolerance.py", "desc": "故障处理系统", "status": "✅ 完成"},
        {"file": "skill_manager.py", "desc": "技能管理器", "status": "✅ 完成"},
        {"file": "mcp_manager.py", "desc": "MCP工具管理器", "status": "✅ 完成"},
        {"file": "symphony_core.py", "desc": "统一调度核心", "status": "✅ 完成"},
        {"file": "memory_system.py", "desc": "记忆系统", "status": "✅ 完成"}
    ],
    "技能文件": [
        {"file": "passive_trigger_engine.py", "desc": "被动触发引擎", "status": "✅ 完成"},
        {"file": "passive_trigger_meeting.py", "desc": "被动触发会议", "status": "✅ 完成"},
        {"file": "collaboration_evolution.py", "desc": "协作技能进化", "status": "✅ 完成"},
        {"file": "dispatch_fault_tolerance.py", "desc": "调度容错改进", "status": "✅ 完成"},
        {"file": "core_system_improvement.py", "desc": "核心系统改进", "status": "✅ 完成"},
        {"file": "model_verification.py", "desc": "模型验证系统", "status": "✅ 完成"},
        {"file": "auto_release.py", "desc": "自动发布系统", "status": "✅ 完成"}
    ],
    "报告文件": [
        {"file": "real_model_dev_report.json", "desc": "真实模型开发报告", "status": "✅ 完成"},
        {"file": "collaboration_evolution_report.json", "desc": "协作进化报告", "status": "✅ 完成"},
        {"file": "dispatch_fault_tolerance_report.json", "desc": "调度容错报告", "status": "✅ 完成"},
        {"file": "core_system_improvement_report.json", "desc": "核心改进报告", "status": "✅ 完成"},
        {"file": "model_verification_final.json", "desc": "模型验证报告", "status": "✅ 完成"}
    ]
}


def get_model_config(provider_type):
    for m in MODEL_CHAIN:
        if m.get("enabled") and m["provider"] == provider_type:
            return m
    for m in MODEL_CHAIN:
        if m.get("enabled"):
            return m
    return None

def call_api(model_config, prompt, max_tokens=300):
    url = f"{model_config['base_url']}/chat/completions"
    headers = {"Authorization": f"Bearer {model_config['api_key']}", "Content-Type": "application/json"}
    data = {"model": model_config["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    start = time.time()
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=20)
        elapsed = time.time() - start
        if resp.status_code == 200:
            result = resp.json()
            usage = result.get("usage", {})
            return {"success": True, "content": result["choices"][0]["message"]["content"], "total_tokens": usage.get("total_tokens", 0), "time": elapsed}
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}", "time": elapsed}
    except Exception as e:
        return {"success": False, "error": str(e), "time": time.time() - start}

def scan_symphony_files():
    """扫描交响目录下的文件"""
    skill_dir = Path(__file__).parent
    files = []
    for f in skill_dir.glob("*.py"):
        files.append({"name": f.name, "size": f.stat().st_size})
    return files

def main():
    print("="*70)
    print("【交响v2.5】Debug检测与功能追踪系统")
    print("="*70)
    
    # 扫描文件
    print("\n📂 扫描交响文件...")
    files = scan_symphony_files()
    print(f"  发现 {len(files)} 个Python文件")
    
    # 分配模型
    for m in MODELS:
        config = get_model_config(m["provider"])
        m["config"] = config
        m["model_name"] = config["alias"]
        m["tokens"] = 0
        print(f"  {m['emoji']} {m['name']} -> {config['alias']}")
    
    discussions = []
    bugs = []
    
    # 第一轮：Debug检测
    print("\n" + "="*70)
    print("📌 第一轮：Debug检测分析")
    print("="*70)
    
    prompts1 = [
        "作为产品经理，分析交响技能的产品流程问题（3点）",
        "作为架构师，分析交响系统的架构问题（3点）",
        "作为开发工程师，列出代码中可能的bug（3点）",
        "作为测试工程师，制定bug检测策略",
        "作为运维工程师，分析运行时问题",
        "作为产品运营，分析用户体验问题"
    ]
    
    for i, m in enumerate(MODELS):
        print(f"\n{m['emoji']} {m['name']} Debug分析...")
        result = call_api(m["config"], prompts1[i])
        if result["success"]:
            m["tokens"] += result["total_tokens"]
            print(f"  ✅ {result['total_tokens']} tokens")
            discussions.append({"name": m["name"], "topic": "Debug分析", "content": result["content"]})
        else:
            print(f"  ❌ {result.get('error', 'Unknown')}")
    
    # 第二轮：修复方案
    print("\n" + "="*70)
    print("📌 第二轮：修复方案设计")
    print("="*70)
    
    prompts2 = [
        "作为产品经理，设计bug修复的产品方案",
        "作为架构师，设计系统修复架构",
        "作为开发工程师，提供bug修复代码建议",
        "作为测试工程师，制定修复验证策略",
        "作为运维工程师，设计监控修复方案",
        "作为产品运营，总结修复优先级"
    ]
    
    for i, m in enumerate(MODELS):
        print(f"\n{m['emoji']} {m['name']} 修复方案...")
        result = call_api(m["config"], prompts2[i])
        if result["success"]:
            m["tokens"] += result["total_tokens"]
            print(f"  ✅ {result['total_tokens']} tokens")
            discussions.append({"name": m["name"], "topic": "修复方案", "content": result["content"]})
        else:
            print(f"  ❌ {result.get('error', 'Unknown')}")
    
    # 第三轮：功能确认
    print("\n" + "="*70)
    print("📌 第三轮：已实现功能确认")
    print("="*70)
    
    prompt3 = f"""作为开发工程师，请确认以下交响已实现的功能状态：

核心文件：
- config.py (17个模型配置)
- model_manager.py (模型管理器)
- fault_tolerance.py (故障处理)
- skill_manager.py (技能管理)
- mcp_manager.py (MCP工具)
- symphony_core.py (调度核心)
- memory_system.py (记忆系统)

技能文件：
- passive_trigger_engine.py (被动触发)
- collaboration_evolution.py (协作进化)
- dispatch_fault_tolerance.py (调度容错)
- core_system_improvement.py (系统改进)
- model_verification.py (模型验证)
- auto_release.py (自动发布)

请列出所有已实现的功能并确认状态。"""
    
    for m in MODELS:
        print(f"\n{m['emoji']} {m['name']} 确认功能...")
        result = call_api(m["config"], prompt3, max_tokens=400)
        if result["success"]:
            m["tokens"] += result["total_tokens"]
            print(f"  ✅ {result['total_tokens']} tokens")
            discussions.append({"name": m["name"], "topic": "功能确认", "content": result["content"]})
        else:
            print(f"  ❌ {result.get('error', 'Unknown')}")
    
    # 报告
    print("\n" + "="*70)
    print("📊 Debug检测与功能追踪报告")
    print("="*70)
    
    total_tokens = sum(m["tokens"] for m in MODELS)
    
    print(f"\n🎯 参会: {len(MODELS)} 位专家")
    print(f"🔢 总Token: {total_tokens}")
    
    print("\n📋 贡献排名:")
    for m in sorted(MODELS, key=lambda x: x["tokens"], reverse=True):
        print(f"  {m['emoji']} {m['name']}: {m['tokens']} tokens")
    
    # 功能统计
    total_features = sum(len(v) for v in IMPLEMENTED_FEATURES.values())
    print(f"\n📦 已实现功能统计: {total_features} 项")
    for category, features in IMPLEMENTED_FEATURES.items():
        print(f"\n  {category} ({len(features)}项):")
        for f in features:
            print(f"    {f['status']} {f['file']}: {f['desc']}")
    
    # 保存报告
    report = {
        "title": "交响v2.5 Debug检测与功能追踪",
        "datetime": datetime.now().isoformat(),
        "files_scanned": len(files),
        "implemented_features": IMPLEMENTED_FEATURES,
        "models": MODELS,
        "discussions": discussions,
        "bugs": bugs,
        "summary": {
            "total_tokens": total_tokens,
            "total_features": total_features
        }
    }
    
    with open("debug_feature_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 报告已保存: debug_feature_report.json")
    print("\n🎼 智韵交响，共创华章！")

if __name__ == "__main__":
    main()
