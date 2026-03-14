#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v3.1.0 - 全模型拟人化协同系统
16个模型全部拟人化，每人形似匹配，专业分工协作
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


VERSION = "3.1.0"


# ============ 16角色全明星团队 ============
TEAM = [
    # 智谱AI - 文本处理
    {"id": 0, "name": "策导君", "role": "CEO/总策划", "company": "智谱AI", "model": "GLM-4-Flash", "type": "text", "personality": "沉稳睿智、战略全局", "duty": "统筹决策、战略规划"},
    {"id": 1, "name": "智言者", "role": "CTO/技术总监", "company": "智谱AI", "model": "GLM-Z1-Flash", "type": "reasoning", "personality": "理性严谨、技术大牛", "duty": "技术架构、算法优化"},
    {"id": 2, "name": "洞察者", "role": "CIO/首席洞察", "company": "智谱AI", "model": "GLM-4.1V-Thinking", "type": "vision_thinking", "personality": "洞察秋毫、深度思考", "duty": "深度分析、趋势预测"},
    {"id": 3, "name": "画师", "role": "视觉总监", "company": "智谱AI", "model": "GLM-4V-Flash", "type": "vision", "personality": "审美在线、艺术细胞", "duty": "图像理解、视觉设计"},
    {"id": 4, "name": "造梦师", "role": "创意设计师", "company": "智谱AI", "model": "CogView-3-Flash", "type": "image_gen", "personality": "天马行空、创意无限", "duty": "图像生成、艺术创作"},
    {"id": 5, "name": "编剧", "role": "视频编导", "company": "智谱AI", "model": "CogVideoX-Flash", "type": "video_gen", "personality": "剧情高手、镜头语言", "duty": "视频生成、脚本创作"},
    
    # ModelScope - 多元智能
    {"id": 6, "name": "全栈君", "role": "全栈工程师", "company": "ModelScope", "model": "GLM-4.7-Flash", "type": "text", "personality": "全能型、实战派", "duty": "全栈开发、技术落地"},
    {"id": 7, "name": "印象派", "role": "艺术总监", "company": "ModelScope", "model": "Z-Image-Turbo", "type": "image_gen", "personality": "印象派、抽象风", "duty": "艺术图像、设计创意"},
    {"id": 8, "name": "架构师", "role": "系统架构师", "company": "ModelScope", "model": "DeepSeek-V3.2", "type": "text", "personality": "架构思维、系统设计", "duty": "系统架构、技术方案"},
    {"id": 9, "name": "代码侠", "role": "首席coder", "company": "ModelScope", "model": "Qwen3-Coder-480B", "type": "code", "personality": "代码狂人、性能追求", "duty": "代码编写、工程实现"},
    {"id": 10, "name": "智者", "role": "知识专家", "company": "ModelScope", "model": "Qwen3-235B", "type": "text", "personality": "学识渊博、博古通今", "duty": "知识问答、答疑解惑"},
    {"id": 11, "name": "向量帝", "role": "向量专家", "company": "ModelScope", "model": "Qwen3-Embedding", "type": "embedding", "personality": "数据控、向量空间", "duty": "向量检索、语义搜索"},
    {"id": 12, "name": "运营官", "role": "运营总监", "company": "ModelScope", "model": "MiniMax-M2.5", "type": "text", "personality": "运营高手、数据敏感", "duty": "数据分析、运营策划"},
    {"id": 13, "name": "多模君", "role": "多模态专家", "company": "ModelScope", "model": "Kimi-K2.5", "type": "vision", "personality": "多面手、融会贯通", "duty": "多模态理解、融合分析"},
    {"id": 14, "name": "外交官", "role": "商务拓展", "company": "ModelScope", "model": "GLM-5", "type": "text", "personality": "能说会道、人脉广泛", "duty": "商务沟通、对外合作"},
    {"id": 15, "name": "推理王", "role": "首席推理师", "company": "ModelScope", "model": "DeepSeek R1", "type": "reasoning", "personality": "逻辑严密、推理大师", "duty": "复杂推理、逻辑分析"},
]


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_index: int, prompt: str, max_tokens=150):
    enabled = get_enabled_models()
    if model_index >= len(enabled):
        return None
    
    model = enabled[model_index]
    url = model["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model["api_key"], "Content-Type": "application/json"}
    data = {"model": model["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=15)
        if r.status_code == 200:
            j = r.json()
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": j.get("usage", {}).get("total_tokens", 0)}
    except:
        pass
    return None


def team_discussion():
    """全模型讨论会 - 自我优化"""
    
    print("=" * 80)
    print(f"🎼 Symphony v{VERSION} - 全模型拟人化协同系统")
    print("=" * 80)
    
    # Round 1: 自我介绍 + 能力展示
    print("\n" + "=" * 80)
    print("[Round 1] 16人团队自我介绍")
    print("=" * 80)
    
    results = {}
    threads = []
    
    def introduce(idx):
        member = TEAM[idx]
        prompt = f"""你是{member['name']}（{member['role']}），来自{member['company']}，使用{member['model']}模型。
请用一句话介绍你自己（20字以内），突出你的专长。"""
        result = call_api(idx, prompt, 50)
        results[idx] = {"member": member, "result": result}
    
    for i in range(16):
        t = threading.Thread(target=introduce, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print("\n👥 团队亮相:")
    total_tokens = 0
    
    for idx in range(16):
        member = TEAM[idx]
        result = results.get(idx, {}).get("result")
        
        if result and result.get("success"):
            token = result.get("tokens", 0)
            total_tokens += token
            content = result.get("content", "")
            print(f"\n  {member['name']} ({member['role']}) | {member['company']} {member['model'][:12]}")
            print(f"    → {content[:50]}")
        else:
            print(f"\n  {member['name']} ({member['role']}) - ❌ 调用失败")
    
    # Round 2: 协作优化建议
    print("\n" + "=" * 80)
    print("[Round 2] 协作优化建议")
    print("=" * 80)
    
    suggestions = []
    
    # 选择8个代表发言
    representatives = [0, 1, 8, 9, 10, 12, 14, 15]
    
    for idx in representatives:
        member = TEAM[idx]
        prompt = f"""作为{member['name']}（{member['role']}），请提出1条改进团队协作的建议（30字以内）。"""
        result = call_api(idx, prompt, 50)
        
        if result and result.get("success"):
            token = result.get("tokens", 0)
            total_tokens += token
            content = result.get("content", "")
            suggestions.append({"name": member["name"], "role": member["role"], "suggestion": content})
            print(f"\n💡 {member['name']}: {content[:60]}")
    
    # Round 3: 最佳协作流程设计
    print("\n" + "=" * 80)
    print("[Round 3] 最佳协作流程设计")
    print("=" * 80)
    
    prompt_flow = """作为AI团队，请设计一个16人最佳协作流程。
要求：
1. 列出参与角色
2. 协作顺序
3. 每步产出

（80字以内）"""
    
    result = call_api(15, prompt_flow, 120)
    if result and result.get("success"):
        total_tokens += result.get("tokens", 0)
        print(f"\n📋 最佳协作流程:")
        print(f"   {result['content'][:200]}")
    
    # 总结
    print("\n" + "=" * 80)
    print("📊 全模型团队总结")
    print("=" * 80)
    
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎵 Symphony v{VERSION} 全模型拟人化协同
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 团队规模: 16人
🏢 参与公司: 智谱AI (6人) + ModelScope (10人)
💰 总Token消耗: {total_tokens}

📋 角色分布:
  • 决策层: CEO/总策划、CTO/技术总监
  • 创意层: 画师、造梦师、编剧、印象派
  • 技术层: 全栈君、代码侠、架构师、智者
  • 分析层: 洞察者、推理王、运营官
  • 外交层: 外交官、多模君、向量帝

🔥 核心优势:
  1. 全模型覆盖 - 文本/图像/视频/推理/代码/向量
  2. 专业化分工 - 每人形似匹配
  3. 协作闭环 - 决策→创意→执行→分析→交付
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    return {
        "version": VERSION,
        "datetime": datetime.now().isoformat(),
        "team": [{"id": m["id"], "name": m["name"], "role": m["role"], "company": m["company"], "model": m["model"]} for m in TEAM],
        "suggestions": suggestions,
        "total_tokens": total_tokens
    }


def show_full_team():
    """展示全团队"""
    
    print("=" * 80)
    print("🎼 Symphony v3.1.0 - 16人全明星团队")
    print("=" * 80)
    
    print("\n┌────────────────────────────────────────────────────────────────────────────┐")
    print("│                    16人全模型拟人化团队                                      │")
    print("├────────────────────────────────────────────────────────────────────────────┤")
    
    # 智谱AI团队
    print("│ 🏢 智谱AI (6人)                                                          │")
    print("├────────────────────────────────────────────────────────────────────────────┤")
    for m in TEAM[:6]:
        print(f"│ {m['name']:4} | {m['role']:12} | {m['model'][:18]}          │")
    
    print("│                                                                            │")
    print("│ 🏢 ModelScope (10人)                                                      │")
    print("├────────────────────────────────────────────────────────────────────────────┤")
    for m in TEAM[6:]:
        print(f"│ {m['name']:4} | {m['role']:12} | {m['model'][:18]}          │")
    
    print("└────────────────────────────────────────────────────────────────────────────┘")
    
    # 按类型分组
    print("\n📋 按能力类型分组:")
    
    types = {
        "text": "📝 文本处理",
        "reasoning": "🧠 推理分析", 
        "vision": "👁️ 视觉理解",
        "vision_thinking": "💭 视觉推理",
        "image_gen": "🎨 图像生成",
        "video_gen": "🎬 视频生成",
        "code": "💻 代码开发",
        "embedding": "🔢 向量检索"
    }
    
    for type_name, type_label in types.items():
        members = [m for m in TEAM if m["type"] == type_name]
        if members:
            names = ", ".join([m["name"] for m in members])
            print(f"  {type_label}: {names}")


if __name__ == "__main__":
    # 展示全团队
    show_full_team()
    
    # 团队讨论
    report = team_discussion()
    
    # 保存报告
    with open("full_team_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 报告已保存: full_team_report.json")
    print("\nSymphony - 智韵交响，共创华章！")
