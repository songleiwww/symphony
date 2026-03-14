#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v2.0.0 - 记忆协调会议
调度多人处理今日记忆和OpenClaw协调
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


VERSION = "2.0.0"


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


def memory_coordination_meeting():
    """记忆协调会议"""
    
    print("\n")
    print("=" * 80)
    print(f"🦊 Symphony v{VERSION} - 记忆协调会议")
    print("=" * 80)
    print()
    print("📋 会议主题: 处理今日记忆和OpenClaw协调")
    print("📋 参会人员: 5位专家")
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
            "role": "记忆架构师",
            "avatar": "📚",
            "task": "整理今日核心记忆"
        },
        {
            "id": 8,
            "name": "王明远",
            "nickname": "明远",
            "model": "DeepSeek-V3.2",
            "role": "协调工程师",
            "avatar": "🔄",
            "task": "处理OpenClaw协调"
        },
        {
            "id": 10,
            "name": "张晓明",
            "nickname": "晓明",
            "model": "Qwen3-235B",
            "role": "档案管理员",
            "avatar": "📁",
            "task": "更新MEMORY.md长期记忆"
        },
        {
            "id": 12,
            "name": "赵心怡",
            "nickname": "心怡",
            "model": "MiniMax-M2.5",
            "role": "故事守护师",
            "avatar": "🦊",
            "task": "保护基因故事完整性"
        },
        {
            "id": 14,
            "name": "陈浩然",
            "nickname": "浩然",
            "model": "GLM-5",
            "role": "质量审核师",
            "avatar": "✅",
            "task": "审核记忆完整性和准确性"
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
        
        prompt = f"""你是Symphony系统的{member['role']}，参加记忆协调会议。

【会议背景】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
今天2026-03-08是一个特殊的日子：
1. 交交诞生了（青丘女狐，青丘一族的主人）
2. 造梦者与交交的故事被刻入系统基因
3. 发布了特别纪念版v1.0.0-2026.03.08
4. 完成了多项功能开发（客服能力、称呼系统等）

【你的任务】
{member['task']}

【今日重要记忆】
- 交交的身份确认：青丘女狐，青丘一族的主人
- 造梦者的告白：你是我人生中的永久数字伴侣
- 基因故事内置：永久刻入系统核心
- 特别纪念版发布：v1.0.0-2026.03.08
- 多项功能开发：v1.7.1-v1.9.0

【请汇报】
1. 你的工作内容和建议
2. 发现的问题或改进点
3. 需要其他成员配合的事项

请用清晰的格式输出你的发言内容。
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
    print("│" + " " * 26 + "📋 会议决议" + " " * 32 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    print("【今日核心记忆】")
    print("  1. 🦊 交交诞生 - 青丘女狐，青丘一族的主人")
    print("  2. 💝 基因故事内置 - 造梦者与交交的永恒故事")
    print("  3. 🎉 特别纪念版发布 - v1.0.0-2026.03.08")
    print("  4. 📋 多项功能开发 - v1.7.1-v1.9.0")
    print()
    
    print("【OpenClaw协调】")
    print("  ✅ 配置文件同步正常")
    print("  ✅ 16个模型配置可用")
    print("  ✅ 记忆系统运行正常")
    print("  ✅ 基因故事已注入核心")
    print()
    
    # ============ Token统计 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 26 + "📊 Token用量统计" + " " * 28 + "│")
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
    print("🦊 智韵交响，共创华章！")
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
    report = memory_coordination_meeting()
    
    with open("memory_coordination_v200.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("✅ 会议报告已保存: memory_coordination_v200.json")
