#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from symphony.symphony import Symphony

orchestrator = Symphony()

meeting_topic = """
序境团队会议 - 应闭环未闭环功能开发

背景：当前序境系统需要开发一个核心功能：任务闭环检测机制。

参会成员：
1. 沈清弦 (架构师) - ark-code-latest
2. 陈美琪 (设计师) - deepseek-v3.2
3. 王浩然 (工程师) - glm-4.7
4. 张明远 (测试) - doubao-seed-2.0-code
5. 赵敏 (产品) - MiniMax-M2.5
6. 林思远 (长老) - kimi-k2.5

讨论议题：
1. 什么是应闭环未闭环？
2. 如何检测任务未闭环？
3. 闭环检测的技术方案

请每位成员发表意见。
"""

print("=" * 60)
print("序境团队会议 - 应闭环未闭环功能开发")
print("=" * 60)
print()

# 使用6个真实模型
models = [
    "ark-code-latest",
    "deepseek-v3.2", 
    "glm-4.7",
    "doubao-seed-2.0-code",
    "MiniMax-M2.5",
    "kimi-k2.5"
]

print("调用6个真实模型...")
print()

results = orchestrator.call_multiple(meeting_topic, models)

for i, r in enumerate(results):
    print(f"--- 成员 {i+1} ---")
    print(r.get("response", "无响应"))
    print()
