#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v1.8.0 - 客服能力增强会议
加强和用户交互，直接执行会议决议
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


VERSION = "1.8.0"


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_index: int, prompt: str, max_tokens=400):
    """真实API调用"""
    enabled = get_enabled_models()
    if model_index >= len(enabled):
        return None
    
    model = enabled[model_index]
    url = model["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model["api_key"], "Content-Type": "application/json"}
    data = {"model": model["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=40)
        if r.status_code == 200:
            j = r.json()
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": j.get("usage", {}).get("total_tokens", 0)}
    except Exception as e:
        return {"success": False, "error": str(e)}
    return None


def customer_service_meeting():
    """客服能力增强会议"""
    
    print("\n")
    print("=" * 80)
    print(f"🎼 Symphony v{VERSION} - 客服能力增强会议")
    print("=" * 80)
    print()
    print("📢 会议主题: 加强交响系统的客服能力和用户交互体验")
    print("📢 参会人员: 5位专家")
    print("📢 会议目标: 制定客服能力增强方案并直接执行")
    print()
    
    total_tokens = 0
    meeting_results = {}
    lock = threading.Lock()
    
    # 参会成员
    participants = [
        {
            "id": 0,
            "name": "林思远",
            "nickname": "思远",
            "model": "智谱GLM-4-Flash",
            "role": "客服架构师",
            "avatar": "🎯",
            "task": "设计客服能力框架"
        },
        {
            "id": 8,
            "name": "王明远",
            "nickname": "明远",
            "model": "DeepSeek-V3.2",
            "role": "交互设计师",
            "avatar": "💬",
            "task": "设计用户交互流程"
        },
        {
            "id": 10,
            "name": "张晓明",
            "nickname": "晓明",
            "model": "Qwen3-235B",
            "role": "响应优化师",
            "avatar": "⚡",
            "task": "优化响应速度和质量"
        },
        {
            "id": 12,
            "name": "赵心怡",
            "nickname": "心怡",
            "model": "MiniMax-M2.5",
            "role": "用户体验师",
            "avatar": "💝",
            "task": "设计友好交互语言"
        },
        {
            "id": 13,
            "name": "陈浩然",
            "nickname": "浩然",
            "model": "Kimi-K2.5",
            "role": "质量控制师",
            "avatar": "✅",
            "task": "制定服务质量标准"
        }
    ]
    
    # ============ 会议环节 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 28 + "🎤 会议发言环节" + " " * 32 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    def meeting_speech(member):
        nonlocal total_tokens
        
        print(f"┌─ {member['avatar']} {member['name']}（{member['nickname']}）- {member['role']}")
        print(f"│  📌 发言主题: {member['task']}")
        print(f"│  🤖 使用模型: {member['model']}")
        print("│")
        print(f"│  🎤 正在发言...")
        
        prompt = f"""你是Symphony系统的{member['role']}，参加客服能力增强会议。

【会议主题】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
加强交响系统的客服能力和用户交互体验

【你的任务】
{member['task']}

【发言要求】
1. 提出具体可行的改进方案
2. 说明方案的实施步骤
3. 预估需要的资源和工作量
4. 说明对用户体验的改善效果

【决议执行】
会议结束后，方案将直接执行，请确保方案可实施。

请用清晰的格式输出你的发言内容。
"""
        
        result = call_api(member["id"], prompt, 600)
        
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
                
                print("├" + "─" * 78 + "┤")
                print(f"│  ✅ 发言完成！")
                print(f"│  📊 Token用量: {result['tokens']}")
                print(f"│  📋 核心观点: {result['content'][:100]}...")
                print("└" + "─" * 78 + "┘")
                print()
            else:
                meeting_results[member["name"]] = {"success": False}
                print("├" + "─" * 78 + "┤")
                print(f"│  ❌ 发言失败")
                print("└" + "─" * 78 + "┘")
                print()
    
    # 顺序发言
    for member in participants:
        meeting_speech(member)
    
    # ============ 会议决议 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 30 + "📋 会议决议" + " " * 34 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    decisions = []
    for name, data in meeting_results.items():
        if data.get("success"):
            decisions.append(f"• {data['task']}: 已制定方案")
    
    for d in decisions:
        print(f"  {d}")
    
    print()
    print("  🎯 决议: 直接执行客服能力增强方案")
    print()
    
    # ============ 拟人化工作报告 ============
    print("\n" + "=" * 80)
    print("📋 拟人化工作报告")
    print("=" * 80)
    
    success_count = sum(1 for r in meeting_results.values() if r.get("success"))
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              🎭 Symphony v{VERSION} 会议工作报告                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  📊 会议统计                                                                ║
║  ┌────────────────────────────────────────────────────────────────────────┐ ║
║  │  参会人数: {len(participants)}                                                          │ ║
║  │  发言人数: {success_count}                                                          │ ║
║  │  发言率: {success_count/len(participants)*100:.0f}%                                                          │ ║
║  │  总Token消耗: {total_tokens}                                               │ ║
║  └────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    print("┌──────────────────────────────────────────────────────────────────────────────┐")
    print("│                          📋 每位成员详细工作汇报                             │")
    print("└──────────────────────────────────────────────────────────────────────────────┘")
    print()
    
    for name, data in meeting_results.items():
        if data.get("success"):
            print(f"""
┌──────────────────────────────────────────────────────────────────────────────┐
│  🎭 {name}（{data['nickname']}）- {data['role']}                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  📌 基本信息                                                                │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  姓名: {name}  昵称: {data['nickname']}  职位: {data['role']}        │ │
│  │  使用模型: {data['model']}                                         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  📊 工作数据                                                                │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  任务: {data['task']}                                              │ │
│  │  Token用量: {data['tokens']}                                              │ │
│  │  工作状态: ✅ 已完成                                                  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
""")
    
    # ============ Token用量汇总表 ============
    print("┌──────────────────────────────────────────────────────────────────────────────┐")
    print("│                          📊 Token用量详细汇总表                              │")
    print("└──────────────────────────────────────────────────────────────────────────────┘")
    print()
    
    print("┌────────────┬────────────────────┬────────────────────┬──────────┬──────────┐")
    print("│   成员     │      使用模型       │       任务         │  Token   │   状态   │")
    print("├────────────┼────────────────────┼────────────────────┼──────────┼──────────┤")
    
    for name, data in meeting_results.items():
        if data.get("success"):
            model_short = data['model'][:16] if len(data['model']) > 16 else data['model']
            print(f"│ {name:<10} │ {model_short:<18} │ {data['task'][:14]:<14} │ {data['tokens']:>8} │ {'✅ 完成':^8} │")
    
    print("├────────────┼────────────────────┼────────────────────┼──────────┼──────────┤")
    print(f"│ {'合计':^10} │ {'-':^18} │ {'-':^18} │ {total_tokens:>8} │ {'100%':^8} │")
    print("└────────────┴────────────────────┴────────────────────┴──────────┴──────────┘")
    print()
    
    print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎵 智韵交响，共创华章！

""")
    
    return {
        "version": VERSION,
        "datetime": datetime.now().isoformat(),
        "participants": len(participants),
        "completed": success_count,
        "total_tokens": total_tokens,
        "meeting_results": meeting_results
    }


if __name__ == "__main__":
    report = customer_service_meeting()
    
    with open("customer_service_meeting_v180.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("✅ 会议报告已保存: customer_service_meeting_v180.json")
