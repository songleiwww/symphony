#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Retry: Rate Limit Tracker Design
"""
from brainstorm_panel_v2 import BrainstormPanel

panel = BrainstormPanel()

print("=" * 60)
print("Retry: Rate Limit Tracker Design")
print("=" * 60)

result = panel.call_model(
    prompt="""Design a rate limit tracking system for multi-model API management.

Requirements:
1. Track rate limits for each provider (volcengine, zhipu, modelscope)
2. Store: provider, model, limit_type (hourly/weekly/monthly), limit_value, reset_time, current_usage
3. Auto-detect 429 errors and mark model as unavailable
4. Calculate recovery time based on reset timestamp
5. Provide status check API

Design the data structures and core functions in Python. Use dataclasses and typing.""",
    model_id="deepseek-ai/DeepSeek-R1-0528",
    max_tokens=1500
)

print(f"\nSuccess: {result.success}")
print(f"Tokens: {result.tokens}")

if result.success:
    print("\n" + "=" * 60)
    print("Rate Limit Tracker Design")
    print("=" * 60)
    print(result.response[:3000])
    if len(result.response) > 3000:
        print("... [truncated]")
    
    # Save to file
    with open("rate_limit_tracker_design.py", "w", encoding="utf-8") as f:
        f.write(result.response)
    print("\nSaved to rate_limit_tracker_design.py")
else:
    print(f"Error: {result.error}")
