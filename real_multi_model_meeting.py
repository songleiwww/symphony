#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实多模型会议 - 调用真实模型，组织会议，每个模型真实阐述建议
"""

import sys
import json
from pathlib import Path

project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from real_model_caller import RealModelCaller

print("=" * 80)
print("🎯 交响 - 真实多模型会议")
print("=" * 80)

# 1. 初始化真实模型调用器
print("\n[1] 初始化真实模型调用器...")
caller = RealModelCaller()
print("   ✅ 初始化成功！")
print(f"   可用模型: {len(caller.available_models)} 个")

# 2. 定义会议专家团队
print("\n[2] 定义会议专家团队...")
meeting_experts = [
    {
        "model_id": "ark-code-latest",
        "name": "林思远",
        "role": "系统架构师",
        "prompt": "你是林思远，系统架构师，有10+年NLP和人机交互经验。请从系统架构角度，对Symphony v0.7.0的发展方向给出建议。"
    },
    {
        "model_id": "deepseek-v3.2",
        "name": "陈美琪",
        "role": "用户体验设计师",
        "prompt": "你是陈美琪，用户体验设计师，获奖UI/UX设计师。请从用户体验角度，对Symphony v0.7.0的发展方向给出建议。"
    },
    {
        "model_id": "doubao-seed-2.0-code",
        "name": "王浩然",
        "role": "交互工程师",
        "prompt": "你是王浩然，交互工程师，全栈开发。请从技术实现角度，对Symphony v0.7.0的发展方向给出建议。"
    }
]

print(f"   专家团队: {len(meeting_experts)} 位专家")

# 3. 调用每个真实模型
print("\n[3] 开始调用真实模型...")
meeting_results = []

for expert in meeting_experts:
    print(f"\n   正在调用: {expert['name']} ({expert['model_id']})...")
    try:
        result = caller.call_model(expert['model_id'], expert['prompt'])
        
        meeting_result = {
            "expert_name": expert['name'],
            "expert_role": expert['role'],
            "model_id": expert['model_id'],
            "response": result['response'],
            "prompt_tokens": result['prompt_tokens'],
            "completion_tokens": result['completion_tokens'],
            "total_tokens": result['total_tokens'],
            "latency_seconds": result['latency_seconds']
        }
        
        meeting_results.append(meeting_result)
        
        print(f"   ✅ {expert['name']} 完成！")
        print(f"      Token: {result['total_tokens']}")
        print(f"      延迟: {result['latency_seconds']:.2f}秒")
        
    except Exception as e:
        print(f"   ❌ {expert['name']} 失败: {e}")

# 4. 生成述职报告
print("\n" + "=" * 80)
print("📊 真实多模型会议 - 述职报告")
print("=" * 80)

total_tokens = sum(r['total_tokens'] for r in meeting_results)
total_latency = sum(r['latency_seconds'] for r in meeting_results)

print(f"\n📈 会议统计:")
print(f"   参与专家: {len(meeting_results)} 位")
print(f"   总Token消耗: {total_tokens}")
print(f"   总耗时: {total_latency:.2f}秒")

print(f"\n👥 专家述职:")
for r in meeting_results:
    print(f"\n   {r['expert_name']} ({r['expert_role']})")
    print(f"   模型: {r['model_id']}")
    print(f"   Token: {r['total_tokens']} | 延迟: {r['latency_seconds']:.2f}秒")
    print(f"\n   建议:")
    print(f"   {r['response'][:200]}...")

# 5. 保存完整报告
report_path = project_dir / "REAL_MULTI_MODEL_MEETING_REPORT.json"
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump({
        "meeting_experts": meeting_experts,
        "meeting_results": meeting_results,
        "total_tokens": total_tokens,
        "total_latency_seconds": total_latency
    }, f, ensure_ascii=False, indent=2)

print(f"\n💾 完整报告已保存: {report_path}")

print("\n" + "=" * 80)
print("✅ 真实多模型会议完成！")
print("=" * 80)
