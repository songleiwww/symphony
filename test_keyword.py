# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony')
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel')

from skills.takeover_skill import XujingTakeover
import io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

takeover = XujingTakeover()

# 测试关键词
test_keywords = ["序境", "陆念昭", "接管", "symphony", "调度"]

print("=== 关键词触发测试 ===")
for kw in test_keywords:
    result = takeover.should_takeover(kw)
    print(f"'{kw}': {result}")

# 测试序境触发
print("\n=== 序境触发测试 ===")
response = takeover.get_xujing_response("序境")
print(f"状态: {response.get('status')}")
print(f"类型: {response.get('metadata', {}).get('type')}")
if response.get('content'):
    print(f"\n内容:\n{response['content'][:300]}")
