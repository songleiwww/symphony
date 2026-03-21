# -*- coding: utf-8 -*-
"""
序境系统 - 正确接管流程测试
"""
import sys
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony')
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel')

from skills.takeover_skill import XujingTakeover
import json
import io
import sys

# 修复编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

# 初始化接管器
takeover = XujingTakeover(db_path)

# 测试 - 直接触发接管
msg = "陆念昭"

print(f"【用户消息】: {msg}")
print(f"【是否接管】: {takeover.should_takeover(msg)}")

# 获取接管回复
response = takeover.get_xujing_response(msg)
print(f"【回复状态】: {response.get('status')}")
print(f"【回复类型】: {response.get('metadata', {}).get('type')}")

if response.get('content'):
    print(f"\n【回复内容】:\n{response['content'][:500]}")
