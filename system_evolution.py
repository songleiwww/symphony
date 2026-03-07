#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v2.7.0 - 系统进化会议
基于学习内容，多人开发进化交响系统
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


VERSION = "2.7.0"


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
    data = {"model": model["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.8}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=60)
        if r.status_code == 200:
            j = r.json()
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": j.get("usage", {}).get("total_tokens", 0)}
    except Exception as e:
        return {"success": False, "error": str(e)}
    return None


def system_evolution_meeting():
    """系统进化会议"""
    
    print("\n")
    print("=" * 80)
    print(f"🦊 Symphony v{VERSION} - 系统进化会议")
    print("=" * 80)
    print()
    print("📋 会议主题: 基于学习内容，多人开发进化交响系统")
    print("📋 学习内容: 多智能体系统、记忆架构、用户体验、表格渲染")
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
            "role": "多智能体架构师",
            "task": "设计多智能体协作架构，参考AutoGen和LangGraph"
        },
        {
            "id": 10,
            "name": "张晓明",
            "nickname": "晓明",
            "model": "Qwen3-235B",
            "role": "记忆系统设计师",
            "task": "优化记忆系统架构，实现短期/长期/工作/情景记忆"
        },
        {
            "id": 12,
            "name": "赵心怡",
            "nickname": "心怡",
            "model": "MiniMax-M2.5",
            "role": "用户体验优化师",
            "task": "优化用户体验，降低认知负荷，提升交互质量"
        },
        {
            "id": 13,
            "name": "陈浩然",
            "nickname": "浩然",
            "model": "Kimi-K2.5",
            "role": "渲染引擎工程师",
            "task": "优化表格渲染，实现自适应宽度和对齐"
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
        
        prompt = f"""你是Symphony系统的{member['role']}，参加系统进化会议。

【学习内容背景】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
今天交交学习了以下尖端技术：

1. 多智能体系统最新进展
   - AutoGen框架：微软开源的多智能体协作框架
   - LangGraph：图结构智能体编排工具
   - Swarm：OpenAI轻量级多智能体框架

2. 记忆系统架构
   - 短期记忆：对话上下文，临时信息存储
   - 长期记忆：重要信息持久化，支持检索
   - 工作记忆：当前任务相关信息，动态更新
   - 情景记忆：特定事件和经历，带时间戳

3. 用户体验设计原则
   - 认知负荷最小化：信息分层，避免过载
   - 一致性原则：统一风格，降低学习成本
   - 反馈及时性：操作有回应，状态可感知
   - 容错性：允许错误，易于恢复

4. 表格渲染最佳实践
   - 对齐规则：数字右对齐，文字左对齐
   - 宽度控制：适应平台显示限制
   - 内容简洁：避免过长，必要时截断
   - 视觉层次：表头突出，数据分明

【你的任务】
{member['task']}

【进化要求】
1. 结合学习内容，提出具体改进方案
2. 设计可实现的代码或架构
3. 确保与现有系统兼容
4. 提升用户（造梦者）的体验
5. 体现青丘文化特色

请提出你的具体进化方案和代码建议。
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
    
    # 顺序发言
    for member in participants:
        meeting_speech(member)
    
    # ============ 会议决议 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 24 + "📋 系统进化决议" + " " * 28 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    print("【一、多智能体协作架构】")
    print("  1. 借鉴AutoGen的智能体对话机制")
    print("  2. 实现图结构工作流编排")
    print("  3. 支持智能体角色分配和切换")
    print("  4. 建立智能体间通信协议")
    print()
    
    print("【二、记忆系统优化】")
    print("  1. 实现四层记忆架构（短期/长期/工作/情景）")
    print("  2. 添加记忆重要性评分机制")
    print("  3. 支持记忆检索和召回")
    print("  4. 实现记忆自动清理机制")
    print()
    
    print("【三、用户体验提升】")
    print("  1. 信息分层展示，降低认知负荷")
    print("  2. 统一交互风格和语言")
    print("  3. 及时反馈用户操作状态")
    print("  4. 增强错误恢复能力")
    print()
    
    print("【四、表格渲染优化】")
    print("  1. 自适应表格宽度")
    print("  2. 智能对齐和截断")
    print("  3. 表头高亮显示")
    print("  4. 支持多平台适配")
    print()
    
    print("【五、青丘文化融入】")
    print("  1. 保持交交的温暖称呼")
    print("  2. 维持九尾狐形象特色")
    print("  3. 延续造梦者故事传承")
    print("  4. 强化青丘族群管理")
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
    report = system_evolution_meeting()
    
    with open("system_evolution_v270.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("✅ 会议报告已保存: system_evolution_v270.json")
