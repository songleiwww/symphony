#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v0.7.0 Phase 4: 文档编写 - 刘心怡（glm-4.7）
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
print("🎯 交响 v0.7.0 Phase 4: 文档编写")
print("👤 专家: 刘心怡（内容策划师）")
print("🤖 模型: cherry-doubao/glm-4.7")
print("=" * 80)

print("\n📋 任务:")
print("  1. 编写 v0.7.0 使用文档")
print("  2. 编写教程和快速入门")
print("  3. 编写 API 文档")
print("  4. 设计文档信息架构")

print("\n🔄 正在调用刘心怡（glm-4.7）...")

# 调用真实模型
prompt = """你好，我是刘心怡，内容策划师，技术作家与信息架构师。请基于之前的Phase 1-3成果，设计并编写v0.7.0的完整文档体系。

已有成果：
- Phase 1: 三层架构（决策层/协作层/执行层），Conductor代号
- Phase 2: 多模型协作调度器、MultiModelOrchestrator、Model Mesh
- Phase 3: CLI用户界面、4种协作模式、颜色编码系统

请设计并编写：
1. 文档信息架构（哪些文档文件）
2. 快速入门指南（5分钟上手）
3. 完整教程（多模型协作示例）
4. API文档（核心类和方法）
5. 文档大纲和内容结构

请给出详细的文档体系设计。"""

try:
    start = time.time()
    response = requests.post(
        "https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions",
        headers={
            "Authorization": "Bearer 3b922877-3fbe-45d1-a298-53f2231c5224",
            "Content-Type": "application/json"
        },
        json={
            "model": "glm-4.7",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 800
        },
        timeout=120
    )
    latency = time.time() - start
    result = response.json()
    
    print(f"✅ 刘心怡调用成功！")
    print(f"⏱️ 延迟: {latency:.2f}秒")
    print(f"🔢 Token: {result['usage']['total_tokens']}")
    
    print("\n" + "=" * 80)
    print("📝 刘心怡的文档体系:")
    print("=" * 80)
    print(result['choices'][0]['message']['content'])
    
    # 保存结果
    output = {
        "expert": "刘心怡",
        "role": "内容策划师",
        "model": "glm-4.7",
        "response": result['choices'][0]['message']['content'],
        "prompt_tokens": result['usage']['prompt_tokens'],
        "completion_tokens": result['usage']['completion_tokens'],
        "total_tokens": result['usage']['total_tokens'],
        "latency_seconds": latency
    }
    
    with open("v070_phase4_docs.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 80)
    print("💾 结果已保存: v070_phase4_docs.json")
    print("=" * 80)
    
except Exception as e:
    print(f"❌ 失败: {e}")
    import traceback
    traceback.print_exc()
