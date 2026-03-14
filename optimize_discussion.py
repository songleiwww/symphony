#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony Project Optimization - 3 Models Discussion
"""
from brainstorm_panel_v2 import BrainstormPanel

panel = BrainstormPanel()

print("=" * 60)
print("Symphony Project Optimization - 3 Models Discussion")
print("=" * 60)

topic = """
Please analyze and optimize the Symphony project. Provide improvement suggestions in:

1. **Multi-model Collaboration**: How to make different models work better together
2. **Task Scheduling**: How to intelligently assign tasks to suitable models
3. **Error Handling**: How to improve system stability
4. **User Experience**: How to make the tool more user-friendly
5. **Scalability**: How to support more models and scenarios

Based on the current project code, propose specific implementation plans.
"""

results = []

# Model 1: DeepSeek-R1 for architecture
print("\n[1/3] Calling DeepSeek-R1 for system architecture analysis...")
r1 = panel.call_model(
    prompt=f"You are a system architecture expert. Analyze the Symphony project architecture issues and propose optimizations. Focus on: module decoupling, interface design, scalability.\n\n{topic}",
    model_id="deepseek-ai/DeepSeek-R1-0528",
    max_tokens=1500
)
results.append(("System Architecture Expert (DeepSeek-R1)", r1))
print(f"  Success: {r1.success}, Tokens: {r1.tokens}, Latency: {r1.latency:.1f}s")

# Model 2: GLM-4.7 for UX
print("\n[2/3] Calling GLM-4.7 for user experience optimization...")
r2 = panel.call_model(
    prompt=f"You are a user experience expert. Analyze the Symphony project UX issues and propose optimizations. Focus on: usability, interaction design, documentation.\n\n{topic}",
    model_id="ZhipuAI/GLM-4.7-Flash",
    max_tokens=1500
)
results.append(("User Experience Expert (GLM-4.7)", r2))
print(f"  Success: {r2.success}, Tokens: {r2.tokens}, Latency: {r2.latency:.1f}s")

# Model 3: DeepSeek-V3.2 for code quality
print("\n[3/3] Calling DeepSeek-V3.2 for code quality analysis...")
r3 = panel.call_model(
    prompt=f"You are a code quality expert. Analyze the Symphony project code quality issues and propose optimizations. Focus on: code standards, performance optimization, test coverage.\n\n{topic}",
    model_id="deepseek-ai/DeepSeek-V3.2",
    max_tokens=1500
)
results.append(("Code Quality Expert (DeepSeek-V3.2)", r3))
print(f"  Success: {r3.success}, Tokens: {r3.tokens}, Latency: {r3.latency:.1f}s")

# Summary
print("\n" + "=" * 60)
print("Discussion Results Summary")
print("=" * 60)

total_tokens = sum(r.tokens for _, r in results)
total_latency = sum(r.latency for _, r in results)

print(f"\nTotal: {total_tokens} tokens, {total_latency:.1f}s")

for name, r in results:
    print(f"\n### {name}")
    print("-" * 40)
    print(r.response[:1000] if len(r.response) > 1000 else r.response)
    if len(r.response) > 1000:
        print("... [truncated]")
