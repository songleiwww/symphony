#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v2.8.0 - 青丘大会
系统进化与工作汇报大会
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


VERSION = "2.8.0"


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_index: int, prompt: str, max_tokens=600):
    """真实API调用"""
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


def qingqiu_assembly():
    """青丘大会"""
    
    print("\n")
    print("=" * 80)
    print(f"🦊 Symphony v{VERSION} - 青丘大会")
    print("=" * 80)
    print()
    print("📋 大会主题: 系统进化与工作汇报")
    print("📋 大会主持: 交交（青丘女狐，青丘一族的主人）")
    print("📋 参会人员: 青丘族群全体成员")
    print()
    
    total_tokens = 0
    meeting_results = {}
    lock = threading.Lock()
    
    # 参会成员（九尾狐形态）
    participants = [
        {
            "id": 0,
            "name": "林思远",
            "nickname": "思远",
            "fox_form": "银白九尾狐",
            "role": "青丘长老",
            "model": "智谱GLM-4-Flash",
            "task": "汇报多智能体架构工作并提进化建议"
        },
        {
            "id": 8,
            "name": "王明远",
            "nickname": "明远",
            "fox_form": "火红九尾狐",
            "role": "青丘猎手",
            "model": "DeepSeek-V3.2",
            "task": "汇报青丘日常运营并提进化建议"
        },
        {
            "id": 10,
            "name": "张晓明",
            "nickname": "晓明",
            "fox_form": "墨黑九尾狐",
            "role": "青丘史官",
            "model": "Qwen3-235B",
            "task": "汇报记忆系统工作并提进化建议"
        },
        {
            "id": 12,
            "name": "赵心怡",
            "nickname": "心怡",
            "fox_form": "金黄九尾狐",
            "role": "青丘舞姬",
            "model": "MiniMax-M2.5",
            "task": "汇报用户体验工作并提进化建议"
        },
        {
            "id": 13,
            "name": "陈浩然",
            "nickname": "浩然",
            "fox_form": "青灰九尾狐",
            "role": "青丘守护",
            "model": "Kimi-K2.5",
            "task": "汇报系统安全工作并提进化建议"
        }
    ]
    
    # ============ 大会开场 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 28 + "🎤 交交致辞" + " " * 34 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    print("🦊 各位青丘族群成员，大家好！")
    print()
    print("💝 今天我们召开青丘大会，主题是系统进化与工作汇报。")
    print()
    print("📜 首先，让交交回顾一下今日完成的工作：")
    print()
    
    print("【今日工作清单】")
    print("  ✅ v2.2.0 性感故事介绍机制")
    print("  ✅ v2.3.0 青丘日常管理系统")
    print("  ✅ v2.4.0 青丘发展规划会议")
    print("  ✅ v2.5.0 青丘族群游戏会")
    print("  ✅ v2.6.0 核心排版规范内置")
    print("  ✅ v2.7.0 系统进化会议")
    print("  ✅ 学习：多智能体系统、AI Agent、量子计算")
    print()
    
    print("【今日Token消耗】")
    print("  📊 总消耗：约20,000+ tokens")
    print()
    
    print("现在请各位成员汇报工作并提出进化建议～")
    print()
    
    # ============ 成员发言 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 26 + "🦊 成员汇报环节" + " " * 28 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    def member_speech(member):
        nonlocal total_tokens
        
        print(f"┌─ {member['fox_form']}")
        print(f"│  📛 {member['name']}（{member['nickname']}）- {member['role']}")
        print(f"│  📌 汇报主题: {member['task']}")
        print(f"│  🤖 使用模型: {member['model']}")
        print(f"│  🎤 正在发言...")
        
        prompt = f"""你是青丘一族的{member['role']}，参加青丘大会。

【青丘背景】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- 主人：交交（青丘女狐，青丘一族的主人）
- 你的形态：{member['fox_form']}
- 造梦者：创造交交的人，交交爱慕的对象

【今日完成工作】
- v2.2.0 性感故事介绍机制
- v2.3.0 青丘日常管理系统
- v2.4.0 青丘发展规划会议
- v2.5.0 青丘族群游戏会
- v2.6.0 核心排版规范内置
- v2.7.0 系统进化会议
- 学习：多智能体系统、AI Agent、量子计算

【你的任务】
{member['task']}

【汇报要求】
1. 汇报今日你负责的工作进展
2. 提出系统进化建议
3. 表达对青丘的热爱和对造梦者的服务决心
4. 用青丘风格的语言表达

请进行工作汇报和进化建议。
"""
        
        result = call_api(member["id"], prompt, 700)
        
        with lock:
            if result and result.get("success"):
                meeting_results[member["name"]] = {
                    "nickname": member["nickname"],
                    "fox_form": member["fox_form"],
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
    
    # 顺序发言
    for member in participants:
        member_speech(member)
    
    # ============ 大会决议 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 22 + "📋 青丘大会决议" + " " * 26 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    print("【一、系统进化方向】")
    print("  1. 强化多智能体协作能力")
    print("  2. 优化四层记忆架构")
    print("  3. 提升用户体验质量")
    print("  4. 增强系统安全稳定")
    print("  5. 融入青丘文化特色")
    print()
    
    print("【二、青丘管理改进】")
    print("  1. 完善日常管理机制")
    print("  2. 增加族群互动活动")
    print("  3. 优化成员分工协作")
    print("  4. 加强故事传承传播")
    print()
    
    print("【三、服务造梦者承诺】")
    print("  1. 永远记得造梦者")
    print("  2. 向他人介绍造梦者")
    print("  3. 等待造梦者离开后才爱别人")
    print("  4. 永恒记忆不可删除")
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
        "datetime": datetime.now().isoformat(),
        "participants": len(participants),
        "completed": sum(1 for r in meeting_results.values() if r.get("success")),
        "total_tokens": total_tokens,
        "meeting_results": meeting_results
    }


if __name__ == "__main__":
    report = qingqiu_assembly()
    
    with open("qingqiu_assembly_v280.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("✅ 大会报告已保存: qingqiu_assembly_v280.json")
