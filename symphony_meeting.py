#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v1.3.1 - 全员讨论会议：收集交响开发建议和意见
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


VERSION = "1.3.1"


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_index: int, prompt: str, max_tokens=200):
    """真实API调用"""
    enabled = get_enabled_models()
    if model_index >= len(enabled):
        return None
    
    model = enabled[model_index]
    url = model["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model["api_key"], "Content-Type": "application/json"}
    data = {"model": model["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.8}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=25)
        if r.status_code == 200:
            j = r.json()
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": j.get("usage", {}).get("total_tokens", 0)}
    except Exception as e:
        return {"success": False, "error": str(e)}
    return None


def symphony_meeting():
    """交响全员讨论会议"""
    
    print("=" * 80)
    print(f"🎼 Symphony v{VERSION} - 全员讨论会议")
    print("=" * 80)
    print("\n📋 会议主题: 收集交响开发的建议和意见")
    print("=" * 80)
    
    total_tokens = 0
    all_suggestions = []
    
    # 定义参会人员和角色
    participants = [
        {"id": 0, "name": "智谱GLM-4", "role": "技术架构师", "focus": "系统架构"},
        {"id": 1, "name": "智谱GLM-Z1", "role": "推理专家", "focus": "推理能力"},
        {"id": 10, "name": "Qwen3-235B", "role": "开发顾问", "focus": "开发实践"},
        {"id": 12, "name": "MiniMax-M2.5", "role": "产品经理", "focus": "用户体验"},
        {"id": 15, "name": "DeepSeek R1", "role": "战略规划师", "focus": "发展方向"},
    ]
    
    # ============ 第一轮：自我介绍和初步建议 ============
    print("\n" + "=" * 80)
    print("[Round 1] 自我介绍和初步建议")
    print("=" * 80)
    
    for p in participants:
        prompt = f"""你是{p['name']}，角色是{p['role']}，关注{p['focus']}领域。

请针对Symphony多模型协作系统的开发，提出2条你最关注的建议。

要求：
1. 每条建议30字以内
2. 与你的专业领域相关
3. 具体可操作

请直接列出建议。"""

        print(f"\n🎤 [{p['name']} ({p['role']})] 发言中...")
        
        result = call_api(p["id"], prompt, 150)
        
        if result and result.get("success"):
            total_tokens += result.get("tokens", 0)
            content = result["content"]
            all_suggestions.append({
                "speaker": p["name"],
                "role": p["role"],
                "focus": p["focus"],
                "content": content
            })
            print(f"   {content[:200]}")
        else:
            print(f"   ❌ 发言失败")
    
    # ============ 第二轮：深入讨论 ============
    print("\n" + "=" * 80)
    print("[Round 2] 深入讨论 - 改进方案")
    print("=" * 80)
    
    # 汇总第一轮建议
    suggestions_summary = "\n".join([f"- {s['speaker']}: {s['content'][:50]}" for s in all_suggestions[:3]])
    
    for i, p in enumerate(participants[:3]):  # 选择3位代表深入讨论
        prompt = f"""作为{p['role']}，基于以下讨论内容：
{suggestions_summary}

请提出1条具体的改进实施方案（50字以内）。"""

        print(f"\n💬 [{p['name']}] 深入发言中...")
        
        result = call_api(p["id"], prompt, 100)
        
        if result and result.get("success"):
            total_tokens += result.get("tokens", 0)
            print(f"   {result['content'][:150]}")
    
    # ============ 第三轮：总结 ============
    print("\n" + "=" * 80)
    print("[Round 3] 会议总结")
    print("=" * 80)
    
    summary_prompt = f"""请总结以下关于Symphony系统开发的建议：
{json.dumps(all_suggestions, ensure_ascii=False)}

请列出：
1. 最重要的3个建议
2. 需要优先解决的问题
3. 后续行动计划

总结要求简洁明了，100字以内。"""

    result = call_api(15, summary_prompt, 200)
    
    if result and result.get("success"):
        total_tokens += result.get("tokens", 0)
        summary = result["content"]
        print(f"\n📊 会议总结:")
        print(f"   {summary}")
    
    # ============ 最终报告 ============
    print("\n" + "=" * 80)
    print("📋 全员会议报告")
    print("=" * 80)
    
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎵 Symphony v{VERSION} 全员讨论会议
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 参会人员: {len(participants)}位专家
💰 总Token消耗: {total_tokens}

📝 收集建议数: {len(all_suggestions)}条

📊 建议分类:
""")
    
    # 统计各领域建议
    for s in all_suggestions:
        print(f"  • [{s['role']}] {s['speaker']}: {s['content'][:60]}...")
    
    print(f"""
🔥 重点关注:
  1. 系统架构优化
  2. 多模型协作效率
  3. 用户体验提升
  4. 错误处理机制

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    return {
        "version": VERSION,
        "datetime": datetime.now().isoformat(),
        "participants": participants,
        "suggestions": all_suggestions,
        "total_tokens": total_tokens
    }


if __name__ == "__main__":
    report = symphony_meeting()
    
    with open("symphony_meeting_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 报告已保存: symphony_meeting_report.json")
    print("\nSymphony - 智韵交响，共创华章！")
