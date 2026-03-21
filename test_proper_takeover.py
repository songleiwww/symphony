# -*- coding: utf-8 -*-
"""
序境系统 - 正确接管流程测试
"""
import sys
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony')
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel')

from skills.takeover_skill import XujingTakeover
import json

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

# 初始化接管器
takeover = XujingTakeover(db_path)

# 测试用户消息
test_messages = [
    "你好",
    "陆念昭在吗",
    "序境系统状态",
    "调度一个模型来对话"
]

print("="*50)
print("序境系统接管流程测试")
print("="*50)

for msg in test_messages:
    print(f"\n【用户消息】: {msg}")
    
    # 1. 判断是否需要接管
    should = takeover.should_takeover(msg)
    print(f"【是否接管】: {should}")
    
    if should:
        # 2. 获取接管回复
        response = takeover.get_xujing_response(msg)
        print(f"【回复状态】: {response.get('status')}")
        print(f"【回复类型】: {response.get('metadata', {}).get('type')}")
        if response.get('content'):
            content = response['content'][:200]
            print(f"【回复内容】: {content}...")
