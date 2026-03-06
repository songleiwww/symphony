#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v0.7.0 Phase 2: 核心实现 - 王浩然（doubao-seed-2.0-code）
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
print("🎯 交响 v0.7.0 Phase 2: 核心实现")
print("👤 专家: 王浩然（交互工程师）")
print("🤖 模型: cherry-doubao/doubao-seed-2.0-code")
print("=" * 80)

print("\n📋 任务:")
print("  1. 实现多模型协作调度器")
print("  2. 集成 real_model_caller 到 symphony_core")
print("  3. 实现并行/串行调用模式")
print("  4. 实现故障转移和重试")

print("\n🔄 正在调用王浩然（doubao-seed-2.0-code）...")

# 调用真实模型
prompt = """你好，我是王浩然，交互工程师，全栈开发。请基于Phase 1的架构设计，实现v0.7.0的核心功能。

Phase 1架构设计要点：
1. 三层架构：决策层、协作层、执行层
2. 适配器模式集成real_model_caller
3. Model Mesh模型网状协作
4. Symphony Core作为Planner和Router

请设计并实现：
1. 多模型协作调度器（MultiModelOrchestrator）
2. 集成real_model_caller的代码
3. 并行/串行调用模式
4. 故障转移和重试机制
5. 完整的实现代码示例

请给出详细的实现方案和代码。"""

try:
    start = time.time()
    response = requests.post(
        "https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions",
        headers={
            "Authorization": "Bearer 3b922877-3fbe-45d1-a298-53f2231c5224",
            "Content-Type": "application/json"
        },
        json={
            "model": "doubao-seed-2.0-code",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        },
        timeout=120
    )
    latency = time.time() - start
    result = response.json()
    
    print(f"✅ 王浩然调用成功！")
    print(f"⏱️ 延迟: {latency:.2f}秒")
    print(f"🔢 Token: {result['usage']['total_tokens']}")
    
    print("\n" + "=" * 80)
    print("💻 王浩然的核心实现:")
    print("=" * 80)
    print(result['choices'][0]['message']['content'])
    
    # 保存结果
    output = {
        "expert": "王浩然",
        "role": "交互工程师",
        "model": "doubao-seed-2.0-code",
        "response": result['choices'][0]['message']['content'],
        "prompt_tokens": result['usage']['prompt_tokens'],
        "completion_tokens": result['usage']['completion_tokens'],
        "total_tokens": result['usage']['total_tokens'],
        "latency_seconds": latency
    }
    
    with open("v070_phase2_core.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 80)
    print("💾 结果已保存: v070_phase2_core.json")
    print("=" * 80)
    
except Exception as e:
    print(f"❌ 失败: {e}")
    import traceback
    traceback.print_exc()
