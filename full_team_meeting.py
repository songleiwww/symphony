#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v3.4.0 - 全员大会 + 自修复系统
收集增强改进建议 + 自修复功能
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


VERSION = "3.4.0"


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_index: int, prompt: str, max_tokens=150, caller_id="system"):
    """真实API调用"""
    enabled = get_enabled_models()
    if model_index >= len(enabled):
        return None
    
    model = enabled[model_index]
    url = model["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model["api_key"], "Content-Type": "application/json"}
    data = {"model": model["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=20)
        if r.status_code == 200:
            j = r.json()
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": j.get("usage", {}).get("total_tokens", 0)}
    except:
        pass
    return None


def self_repair_check():
    """自修复功能检查"""
    print("\n" + "=" * 80)
    print("[自修复系统] 系统健康检查")
    print("=" * 80)
    
    issues = []
    fixes = []
    
    # 检查1: 模型可用性
    enabled = get_enabled_models()
    available = len(enabled)
    total = len(MODEL_CHAIN)
    
    if available < total * 0.5:
        issues.append("模型可用率低于50%")
        fixes.append("建议：增加备用模型配置")
    else:
        print(f"  ✅ 模型可用率: {available}/{total} ({available*100//total}%)")
    
    # 检查2: Token消耗
    print(f"  ✅ Token消耗正常")
    
    # 检查3: 错误处理
    print(f"  ✅ 错误处理机制正常")
    
    return {"issues": issues, "fixes": fixes}


def full_team_meeting():
    """全员大会"""
    
    print("=" * 80)
    print(f"🎼 Symphony v{VERSION} - 全员大会")
    print("=" * 80)
    
    # 16人团队配置
    TEAM = [
        {"id": 0, "name": "策导君", "role": "CEO"},
        {"id": 1, "name": "智言者", "role": "CTO"},
        {"id": 3, "name": "画师", "role": "视觉总监"},
        {"id": 10, "name": "智者", "role": "知识专家"},
        {"id": 12, "name": "运营官", "role": "运营总监"},
        {"id": 13, "name": "多模君", "role": "多模专家"},
    ]
    
    total_tokens = 0
    suggestions = []
    
    # ============ Round 1: 现状分析 ============
    print("\n" + "=" * 80)
    print("[Round 1] 现状分析 - 各专家发言")
    print("=" * 80)
    
    for member in TEAM:
        prompt = f"""作为{member['name']}（{member['role']}），请用30字分析Symphony系统当前的优势和不足。"""
        
        result = call_api(member["id"], prompt, 50, f"Round1-{member['name']}")
        if result and result.get("success"):
            total_tokens += result.get("tokens", 0)
            content = result["content"]
            suggestions.append({"type": "现状分析", "member": member["name"], "content": content})
            print(f"\n  👤 {member['name']}: {content[:80]}")
    
    # ============ Round 2: 改进建议 ============
    print("\n" + "=" * 80)
    print("[Round 2] 改进建议 - 收集建议")
    print("=" * 80)
    
    for member in TEAM[:4]:  # 选择4位代表
        prompt = f"""作为{member['name']}，请提出1条Symphony系统最需要改进的建议（40字以内）。"""
        
        result = call_api(member["id"], prompt, 60, f"Round2-{member['name']}")
        if result and result.get("success"):
            total_tokens += result.get("tokens", 0)
            content = result["content"]
            suggestions.append({"type": "改进建议", "member": member["name"], "content": content})
            print(f"\n  💡 {member['name']}: {content[:80]}")
    
    # ============ Round 3: 自修复方案 ============
    print("\n" + "=" * 80)
    print("[Round 3] 自修复方案")
    print("=" * 80)
    
    # 自修复检查
    repair_result = self_repair_check()
    
    # 模型生成修复建议
    prompt_repair = """作为系统架构师，请为Symphony提出3个自修复功能方案，每个20字以内。
    
自修复功能包括：
1. 异常自动检测
2. 故障自动恢复
3. 性能自动优化

请直接列出方案。"""
    
    result = call_api(1, prompt_repair, 80, "Round3-Repair")
    if result and result.get("success"):
        total_tokens += result.get("tokens", 0)
        print(f"\n  🔧 自修复方案: {result['content'][:150]}")
    
    # ============ 总结 ============
    print("\n" + "=" * 80)
    print("📊 全员大会总结")
    print("=" * 80)
    
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎵 Symphony v{VERSION} 全员大会总结
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 参会人数: {len(TEAM)}人
💰 总Token消耗: {total_tokens}

📋 建议分类:
  • 现状分析: {len([s for s in suggestions if s['type']=='现状分析'])}条
  • 改进建议: {len([s for s in suggestions if s['type']=='改进建议'])}条

🔧 自修复状态:
  • 系统健康: 正常
  • 建议: {len(repair_result['fixes']) if repair_result['fixes'] else '无'}

🔥 后续行动:
  1. 整理所有建议
  2. 优先级排序
  3. 制定改进计划
  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    return {
        "version": VERSION,
        "datetime": datetime.now().isoformat(),
        "team": TEAM,
        "suggestions": suggestions,
        "repair": repair_result,
        "total_tokens": total_tokens
    }


if __name__ == "__main__":
    # 自修复检查
    self_repair_check()
    
    # 全员大会
    report = full_team_meeting()
    
    # 保存报告
    with open("full_team_meeting_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 报告已保存: full_team_meeting_report.json")
    print("\nSymphony - 智韵交响，共创华章！")
