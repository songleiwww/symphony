#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v0.7.0 Phase 3: 用户体验设计 - 陈美琪（deepseek-v3.2）
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
print("🎯 交响 v0.7.0 Phase 3: 用户体验设计")
print("👤 专家: 陈美琪（用户体验设计师）")
print("🤖 模型: cherry-doubao/deepseek-v3.2")
print("=" * 80)

print("\n📋 任务:")
print("  1. 设计 CLI 用户界面")
print("  2. 优化用户交互流程")
print("  3. 添加进度显示和反馈")
print("  4. 设计多模型协作的用户体验")

print("\n🔄 正在调用陈美琪（deepseek-v3.2）...")

# 调用真实模型
prompt = """你好，我是陈美琪，用户体验设计师，获奖UI/UX设计师。请基于Phase 1和Phase 2的成果，设计v0.7.0的用户体验。

已有成果：
- Phase 1: 三层架构（决策层/协作层/执行层）
- Phase 2: 多模型协作调度器、MultiModelOrchestrator

请设计：
1. CLI用户界面（命令行交互）
2. 多模型协作的用户体验流程
3. 进度显示和实时反馈
4. 错误处理和用户引导
5. 完整的CLI界面设计和交互流程

请给出详细的UX设计方案。"""

try:
    start = time.time()
    response = requests.post(
        "https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions",
        headers={
            "Authorization": "Bearer 3b922877-3fbe-45d1-a298-53f2231c5224",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek-v3.2",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 800
        },
        timeout=90
    )
    latency = time.time() - start
    result = response.json()
    
    print(f"✅ 陈美琪调用成功！")
    print(f"⏱️ 延迟: {latency:.2f}秒")
    print(f"🔢 Token: {result['usage']['total_tokens']}")
    
    print("\n" + "=" * 80)
    print("🎨 陈美琪的UX设计:")
    print("=" * 80)
    print(result['choices'][0]['message']['content'])
    
    # 保存结果
    output = {
        "expert": "陈美琪",
        "role": "用户体验设计师",
        "model": "deepseek-v3.2",
        "response": result['choices'][0]['message']['content'],
        "prompt_tokens": result['usage']['prompt_tokens'],
        "completion_tokens": result['usage']['completion_tokens'],
        "total_tokens": result['usage']['total_tokens'],
        "latency_seconds": latency
    }
    
    with open("v070_phase3_ux.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 80)
    print("💾 结果已保存: v070_phase3_ux.json")
    print("=" * 80)
    
except Exception as e:
    print(f"❌ 失败: {e}")
    import traceback
    traceback.print_exc()
