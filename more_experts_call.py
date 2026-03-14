#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
继续调用更多专家模型 - 完整6人团队
"""

import sys
import io
import json
import time
import requests

# 修复Windows编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("=" * 80)
print("🎯 继续调用更多专家模型 - 完整6人团队")
print("=" * 80)

# 定义剩余的4位专家
more_experts = [
    {
        "name": "王浩然",
        "role": "交互工程师",
        "model_id": "doubao-seed-2.0-code",
        "prompt": "你好，我是王浩然，交互工程师，全栈开发。请从技术实现角度，对Symphony v0.7.0的发展方向给出建议。"
    },
    {
        "name": "刘心怡",
        "role": "内容策划师",
        "model_id": "glm-4.7",
        "prompt": "你好，我是刘心怡，内容策划师，技术作家与信息架构师。请从内容和文档角度，对Symphony v0.7.0的发展方向给出建议。"
    },
    {
        "name": "张明远",
        "role": "质量保证主管",
        "model_id": "kimi-k2.5",
        "prompt": "你好，我是张明远，质量保证主管，注重细节的QA专家。请从质量保证和测试角度，对Symphony v0.7.0的发展方向给出建议。"
    },
    {
        "name": "赵敏",
        "role": "项目协调员",
        "model_id": "MiniMax-M2.5",
        "prompt": "你好，我是赵敏，项目协调员，敏捷项目经理。请从项目管理和协作角度，对Symphony v0.7.0的发展方向给出建议。"
    }
]

print(f"\n📋 剩余专家: {len(more_experts)} 位")

# 调用每个专家
all_results = []

for i, expert in enumerate(more_experts, 3):
    print(f"\n[{i}] 调用 {expert['name']} ({expert['model_id']})...")
    try:
        start = time.time()
        
        # 判断提供商
        if expert['model_id'] == "MiniMax-M2.5":
            # cherry-minimax (anthropic-messages)
            response = requests.post(
                "https://api.minimaxi.com/anthropic/v1/messages",
                headers={
                    "x-api-key": "sk-cp-c_GUV0dBahIRIeYgEvbXK8YAPlZBTNwN_6FcETIELPo_zrGAXtwscyVLNs_FKh9aQZECdOwdm2UqsKy85D8KlmkR7EGro-tiTADoYapVwiA7xu9NYcnidak",
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "MiniMax-M2.5",
                    "messages": [{"role": "user", "content": expert['prompt']}],
                    "max_tokens": 500
                },
                timeout=60
            )
            result = response.json()
            response_text = result['content'][0]['text']
            usage = result.get('usage', {})
            prompt_tokens = usage.get('input_tokens', 0)
            completion_tokens = usage.get('output_tokens', 0)
        else:
            # cherry-doubao (openai-completions)
            response = requests.post(
                "https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions",
                headers={
                    "Authorization": "Bearer 3b922877-3fbe-45d1-a298-53f2231c5224",
                    "Content-Type": "application/json"
                },
                json={
                    "model": expert['model_id'],
                    "messages": [{"role": "user", "content": expert['prompt']}],
                    "max_tokens": 500
                },
                timeout=60
            )
            result = response.json()
            response_text = result['choices'][0]['message']['content']
            usage = result.get('usage', {})
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
        
        latency = time.time() - start
        total_tokens = prompt_tokens + completion_tokens
        
        print(f"   ✅ 成功！")
        print(f"   延迟: {latency:.2f}秒")
        print(f"   Token: {total_tokens} (prompt:{prompt_tokens} + completion:{completion_tokens})")
        print(f"\n   建议:")
        print(f"   {response_text[:300]}...")
        
        all_results.append({
            "name": expert['name'],
            "role": expert['role'],
            "model_id": expert['model_id'],
            "response": response_text,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "latency_seconds": latency
        })
        
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        import traceback
        traceback.print_exc()

# 保存完整报告
report_path = Path(__file__).parent / "REAL_6_EXPERTS_MEETING.json"
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump({
        "meeting_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "experts": all_results
    }, f, ensure_ascii=False, indent=2)

print(f"\n💾 完整报告已保存: {report_path}")

print("\n" + "=" * 80)
print("✅ 6位专家全部完成！")
print("=" * 80)
