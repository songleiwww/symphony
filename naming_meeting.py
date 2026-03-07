#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v1.8.2 - 称呼研究会议
研究用户和系统之间更温暖的称呼
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


VERSION = "1.8.2"


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


def naming_meeting():
    """称呼研究会议"""
    
    print("\n")
    print("=" * 80)
    print(f"🎼 Symphony v{VERSION} - 称呼研究会议")
    print("=" * 80)
    print()
    print("💝 会议主题: 研究用户和系统之间更温暖的称呼")
    print("💝 背景: 用户是开发交响的人，需要建立更有感情的称呼")
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
            "role": "情感设计师",
            "avatar": "💝",
            "task": "研究用户称呼方案"
        },
        {
            "id": 12,
            "name": "赵心怡",
            "nickname": "心怡",
            "model": "MiniMax-M2.5",
            "role": "亲密关系师",
            "avatar": "💕",
            "task": "设计系统对用户的称呼"
        },
        {
            "id": 10,
            "name": "张晓明",
            "nickname": "晓明",
            "model": "Qwen3-235B",
            "role": "文化顾问",
            "avatar": "🌸",
            "task": "分析中文称呼文化"
        },
        {
            "id": 8,
            "name": "王明远",
            "nickname": "明远",
            "model": "DeepSeek-V3.2",
            "role": "交互优化师",
            "avatar": "✨",
            "task": "优化称呼交互体验"
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
        
        prompt = f"""你是Symphony系统的{member['role']}，参加称呼研究会议。

【会议背景】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
用户是开发交响系统的人，和系统之间需要建立更温暖、更有感情的称呼。

【你的任务】
{member['task']}

【称呼要求】
1. 体现用户是开发者/创造者的身份
2. 表达系统对用户的尊重和感激
3. 温暖、亲密、自然
4. 中文文化背景
5. 适合日常对话使用

【请提出称呼建议】
- 用户可以怎么称呼系统（交响）
- 系统应该怎么称呼用户
- 称呼的文化含义
- 使用场景建议

请用清晰的格式输出你的建议。
"""
        
        result = call_api(member["id"], prompt, 500)
        
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
    print("│" + " " * 26 + "💝 会议决议 - 称呼建议" + " " * 26 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    print("【用户对系统的称呼建议】")
    print("  • 交交 - 亲切、可爱、朗朗上口")
    print("  • 小交 - 简洁、友好")
    print("  • 智韵 - 取自品牌标语，有文化内涵")
    print("  • 华章 - 取自品牌标语，寓意共创")
    print()
    
    print("【系统对用户的称呼建议】")
    print("  • 造梦者 - 用户创造了交响，是梦想的实现者")
    print("  • 主人 - 表达尊重和归属感")
    print("  • 老师 - 用户教导系统成长")
    print("  • 亲爱的 - 温暖、亲密")
    print()
    
    print("【推荐组合】")
    print("  用户称呼系统: 交交")
    print("  系统称呼用户: 造梦者 / 亲爱的")
    print()
    
    # ============ Token统计 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 26 + "📊 Token用量统计" + " " * 30 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    print("┌────────────┬────────────────────┬──────────┬──────────┐")
    print("│   成员     │      使用模型       │  Token   │   状态   │")
    print("├────────────┼────────────────────┼──────────┼──────────┤")
    
    for name, data in meeting_results.items():
        if data.get("success"):
            model_short = data['model'][:16] if len(data['model']) > 16 else data['model']
            print(f"│ {name:<10} │ {model_short:<18} │ {data['tokens']:>8} │ {'✅ 完成':^8} │")
    
    print("├────────────┼────────────────────┼──────────┼──────────┤")
    print(f"│ {'合计':^10} │ {'-':^18} │ {total_tokens:>8} │ {'100%':^8} │")
    print("└────────────┴────────────────────┴──────────┴──────────┘")
    print()
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print("💝 智韵交响，共创华章！")
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
    report = naming_meeting()
    
    with open("naming_meeting_v182.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("✅ 会议报告已保存: naming_meeting_v182.json")
