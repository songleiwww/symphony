# -*- coding: utf-8 -*-
"""
测试序境调度器 - 使用陆念昭模型
"""
import sys
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony')

from dynamic_dispatcher import DynamicDispatcher
import json

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

# 初始化调度器
dispatcher = DynamicDispatcher(db_path)

# 查找陆念昭的模型
lunianzhao_model = None
for m in dispatcher.models:
    if 'ark-code-latest' in m.get('name', '').lower() or 'ark' in m.get('name', '').lower():
        print(f"找到模型: {m['name']} - {m['provider']} - {m['url']}")
        lunianzhao_model = m
        break

# 也查看火山引擎的模型
print("\n火山引擎模型:")
huoshan_models = [m for m in dispatcher.models if '火山' in m.get('provider', '')]
for m in huoshan_models[:5]:
    print(f"  {m['name']} - {m['url']}")

if lunianzhao_model:
    # 使用陆念昭模型测试
    result = dispatcher.execute("你好，请回复一句问候语", model=lunianzhao_model)
    print("\n调度结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
else:
    print("\n未找到陆念昭模型")
