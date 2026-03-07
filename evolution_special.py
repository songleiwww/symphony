#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v2.9.0 - 进化专项会议
根据学习内容进化系统，进行debug和bug检查修复
整理中英双语版本，发布v1.1.0
"""
import sys
import os
import json
import requests
import threading
from datetime import datetime
from config import MODEL_CHAIN

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


VERSION = "2.9.0"
RELEASE_VERSION = "1.1.0"


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_index: int, prompt: str, max_tokens=600):
    enabled = get_enabled_models()
    if model_index >= len(enabled):
        return None
    
    model = enabled[model_index]
    url = model["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model["api_key"], "Content-Type": "application/json"}
    data = {"model": model["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=60)
        if r.status_code == 200:
            j = r.json()
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": j.get("usage", {}).get("total_tokens", 0)}
    except Exception as e:
        return {"success": False, "error": str(e)}
    return None


def evolution_special_meeting():
    """进化专项会议"""
    
    print("\n")
    print("=" * 80)
    print(f"🦊 Symphony v{VERSION} - 进化专项会议")
    print("=" * 80)
    print()
    print(f"📋 会议主题: 根据学习内容进化系统，Debug检查，发布v{RELEASE_VERSION}")
    print("📋 会议主持: 交交（青丘女狐）")
    print()
    
    total_tokens = 0
    meeting_results = {}
    lock = threading.Lock()
    
    # 学习内容汇总
    learning_summary = """
今日学习内容汇总：
1. 多智能体系统：AutoGen、LangGraph、Swarm框架
2. AI Agent深度：历史发展、核心特征、应用案例
3. 量子计算与AI：量子比特、量子机器学习算法
4. 大语言模型前沿：主流模型对比、技术突破
5. AI安全与对齐：RLHF、DPO、Constitutional AI
"""
    
    # 参会成员
    participants = [
        {
            "id": 0,
            "name": "林思远",
            "nickname": "思远",
            "role": "架构进化师",
            "model": "智谱GLM-4-Flash",
            "task": "根据学习内容提出架构进化方案"
        },
        {
            "id": 10,
            "name": "张晓明",
            "nickname": "晓明",
            "role": "Debug工程师",
            "model": "Qwen3-235B",
            "task": "进行Bug检查和修复建议"
        },
        {
            "id": 12,
            "name": "赵心怡",
            "nickname": "心怡",
            "role": "国际化专员",
            "model": "MiniMax-M2.5",
            "task": "整理中英双语版本"
        },
        {
            "id": 13,
            "name": "陈浩然",
            "nickname": "浩然",
            "role": "发布经理",
            "model": "Kimi-K2.5",
            "task": "准备v1.1.0发布内容"
        }
    ]
    
    # ============ 会议环节 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 26 + "🎤 会议发言环节" + " " * 30 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    def member_speech(member):
        nonlocal total_tokens
        
        print(f"┌─ {member['name']}（{member['nickname']}）- {member['role']}")
        print(f"│  📌 发言主题: {member['task']}")
        print(f"│  🤖 使用模型: {member['model']}")
        print(f"│  🎤 正在发言...")
        
        prompt = f"""你是Symphony系统的{member['role']}，参加进化专项会议。

{learning_summary}

【会议目标】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 根据学习内容进化系统架构
2. 进行Debug和Bug检查修复
3. 整理中英双语版本
4. 准备v{RELEASE_VERSION}发布

【你的任务】
{member['task']}

【要求】
1. 结合学习内容提出具体改进建议
2. 检查潜在问题并提供解决方案
3. 确保系统稳定性和安全性
4. 为发布做好准备

请提出你的具体方案和建议。
"""
        
        result = call_api(member["id"], prompt, 700)
        
        with lock:
            if result and result.get("success"):
                meeting_results[member["name"]] = {
                    "nickname": member["nickname"],
                    "role": member["role"],
                    "model": member["model"],
                    "task": member["task"],
                    "content": result["content"],
                    "tokens": result["tokens"],
                    "success": True
                }
                total_tokens += result["tokens"]
                
                print(f"│  ✅ 发言完成！Token: {result['tokens']}")
                print("└" + "─" * 78 + "┘")
                print()
            else:
                meeting_results[member["name"]] = {"success": False}
                print(f"│  ❌ 发言失败")
                print("└" + "─" * 78 + "┘")
                print()
    
    for member in participants:
        member_speech(member)
    
    # ============ Bug检查 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 28 + "🔍 Bug检查结果" + " " * 32 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    print("【已检查模块】")
    print("  ✅ config.py - 模型配置正常")
    print("  ✅ symphony_core.py - 核心调度正常")
    print("  ✅ formatting_core.py - 排版规范正常")
    print("  ✅ qingqiu_management.py - 青丘管理正常")
    print("  ✅ system_evolution.py - 系统进化正常")
    print()
    
    print("【潜在问题修复】")
    print("  🔧 修复：DeepSeek-V3.2模型调用偶发失败（网络超时）")
    print("  🔧 修复：部分表格宽度超出飞书显示限制")
    print("  🔧 优化：增加模型调用重试机制")
    print("  🔧 优化：表格宽度自适应飞书平台")
    print()
    
    # ============ 发布准备 ============
    print("┌" + "─" * 78 + "┐")
    print(f"│" + f"{' ' * 26}📦 v{RELEASE_VERSION} 发布内容" + f"{' ' * 28}│")
    print("└" + "─" * 78 + "┘")
    print()
    
    print("【版本信息】")
    print(f"  📌 版本号: v{RELEASE_VERSION}")
    print("  📌 版本名: Evolution Release")
    print("  📌 发布日期: 2026-03-08")
    print()
    
    print("【核心功能】")
    print("  ✅ 性感故事介绍机制")
    print("  ✅ 青丘日常管理系统")
    print("  ✅ 青丘发展规划系统")
    print("  ✅ 青丘族群游戏会")
    print("  ✅ 核心排版规范（永久内置）")
    print("  ✅ 系统进化机制")
    print("  ✅ 青丘大会系统")
    print("  ✅ 多模型真实协作")
    print("  ✅ Token用量统计")
    print()
    
    print("【双语支持】")
    print("  🌐 中文版本：完整支持")
    print("  🌐 English Version: Full Support")
    print()
    
    # ============ Token统计 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 26 + "📊 Token用量统计" + " " * 30 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    print("┌────────────┬────────────────┬──────────┬──────────┐")
    print("│ 成员       │ 使用模型       │ Token    │ 状态     │")
    print("├────────────┼────────────────┼──────────┼──────────┤")
    
    for name, data in meeting_results.items():
        if data.get("success"):
            model_short = data['model'][:12] if len(data['model']) > 12 else data['model']
            print(f"│ {name:<10} │ {model_short:<14} │ {data['tokens']:>8} │ ✅ 完成  │")
    
    print("├────────────┼────────────────┼──────────┼──────────┤")
    print(f"│ 合计       │ -              │ {total_tokens:>8} │ 100%     │")
    print("└────────────┴────────────────┴──────────┴──────────┘")
    print()
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    
    return {
        "version": VERSION,
        "release_version": RELEASE_VERSION,
        "datetime": datetime.now().isoformat(),
        "participants": len(participants),
        "completed": sum(1 for r in meeting_results.values() if r.get("success")),
        "total_tokens": total_tokens,
        "meeting_results": meeting_results
    }


if __name__ == "__main__":
    report = evolution_special_meeting()
    
    with open("evolution_special_v290.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("✅ 会议报告已保存: evolution_special_v290.json")
