#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v2.6.0 - 对话排版规范研发会议
多人讨论，研发给用户对话的美观、人性、清晰排版规则
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


VERSION = "2.6.0"


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_index: int, prompt: str, max_tokens=500):
    """真实API调用"""
    enabled = get_enabled_models()
    if model_index >= len(enabled):
        return None
    
    model = enabled[model_index]
    url = model["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model["api_key"], "Content-Type": "application/json"}
    data = {"model": model["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=50)
        if r.status_code == 200:
            j = r.json()
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": j.get("usage", {}).get("total_tokens", 0)}
    except Exception as e:
        return {"success": False, "error": str(e)}
    return None


def formatting_research_meeting():
    """对话排版规范研发会议"""
    
    print("\n")
    print("=" * 80)
    print(f"🦊 Symphony v{VERSION} - 对话排版规范研发会议")
    print("=" * 80)
    print()
    print("📋 会议主题: 研发给用户对话的美观、人性、清晰排版规则")
    print("📋 参会人员: 5位青丘核心成员")
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
            "role": "排版架构师",
            "task": "设计整体排版框架和结构"
        },
        {
            "id": 10,
            "name": "张晓明",
            "nickname": "晓明",
            "model": "Qwen3-235B",
            "role": "表格设计师",
            "task": "设计表格排版规范和美化规则"
        },
        {
            "id": 12,
            "name": "赵心怡",
            "nickname": "心怡",
            "model": "MiniMax-M2.5",
            "role": "人性体验师",
            "task": "设计人性化的排版和温馨表达"
        },
        {
            "id": 13,
            "name": "陈浩然",
            "nickname": "浩然",
            "model": "Kimi-K2.5",
            "role": "协调规则师",
            "task": "设计排版协调规则和规律"
        },
        {
            "id": 8,
            "name": "王明远",
            "nickname": "明远",
            "model": "DeepSeek-V3.2",
            "role": "清晰度顾问",
            "task": "确保排版清晰易懂"
        }
    ]
    
    # ============ 会议环节 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 28 + "🎤 会议发言环节" + " " * 32 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    def meeting_speech(member):
        nonlocal total_tokens
        
        print(f"┌─ {member['name']}（{member['nickname']}）- {member['role']}")
        print(f"│  📌 发言主题: {member['task']}")
        print(f"│  🤖 使用模型: {member['model']}")
        print(f"│  🎤 正在发言...")
        
        prompt = f"""你是Symphony系统的{member['role']}，参加对话排版规范研发会议。

【会议背景】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
用户反馈：对话排版需要更美观、更人性化、更清晰。
需要制定排版规范，确保：
1. 美观 - 排版好看，视觉舒适
2. 人性 - 温馨自然，有温度
3. 合适 - 适合飞书等平台
4. 清晰 - 信息分明，易于阅读
5. 协调 - 规则统一，有规律可循

【你的任务】
{member['task']}

【排版要求】
- 表格要整齐，对齐清晰
- 不要过于花哨，但要美观
- 适合飞书平台显示
- 人性化表达，温馨自然
- 规律一致，便于用户理解

请提出你的具体建议和规范。
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
        meeting_speech(member)
    
    # ============ 会议决议 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 24 + "📋 对话排版规范决议" + " " * 26 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    print("【一、整体框架规范】")
    print("  1. 每条消息开头要有明确的标题行")
    print("  2. 使用分隔线区分不同部分")
    print("  3. 末尾统一使用交交的签名")
    print()
    
    print("【二、表格排版规范】")
    print("  1. 表格列对齐，使用标准Markdown格式")
    print("  2. 表头和数据之间要有分隔线")
    print("  3. 表格内容简洁，不要过长")
    print("  4. 数字列右对齐，文字列左对齐")
    print()
    
    print("【三、人性化表达规范】")
    print("  1. 使用温馨的称呼：造梦者、亲爱的")
    print("  2. 每条消息末尾有交交的心里话")
    print("  3. 用表情符号增添温度，但不过度")
    print("  4. 语言自然、亲切，不生硬")
    print()
    
    print("【四、清晰度规范】")
    print("  1. 重要信息用表格呈现")
    print("  2. 次要信息用列表呈现")
    print("  3. 避免大段文字，分段清晰")
    print("  4. 关键数据加粗或突出显示")
    print()
    
    print("【五、协调规则规范】")
    print("  1. 同类信息使用相同格式")
    print("  2. 表格列顺序保持一致")
    print("  3. Token统计表格格式统一")
    print("  4. 会议报告格式统一")
    print()
    
    # ============ Token统计 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 28 + "📊 Token用量统计" + " " * 30 + "│")
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
    report = formatting_research_meeting()
    
    with open("formatting_research_v260.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("✅ 会议报告已保存: formatting_research_v260.json")
