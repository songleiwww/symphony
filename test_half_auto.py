# -*- coding: utf-8 -*-
"""
测试半自动接管模式
"""
import sys
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony')
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel')

from skills.takeover_skill import XujingTakeover
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

takeover = XujingTakeover()

# 测试
test_messages = [
    ("你好", "普通消息"),
    ("陆念昭", "触发接管"),
    ("序境", "触发接管"),
    ("调度", "普通消息"),
    ("帮我", "普通消息"),
]

print("=== 半自动模式测试 ===\n")
for msg, desc in test_messages:
    should = takeover.should_takeover(msg)
    print(f"【{desc}】'{msg}': 接管={should}")

print("\n=== 触发接管测试 ===")
response = takeover.get_xujing_response("你好，我是测试用户")
print(f"状态: {response.get('status')}")
print(f"类型: {response.get('metadata', {}).get('type')}")
if response.get('content'):
    print(f"\n回复:\n{response['content']}")
