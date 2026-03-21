# -*- coding: utf-8 -*-
"""
测试序境调度器接管对话
"""
import sys
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony')

from dynamic_dispatcher import DynamicDispatcher
import json

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

# 初始化调度器
dispatcher = DynamicDispatcher(db_path)

# 查看可用模型
print(f"可用模型数量: {len(dispatcher.models)}")

# 按服务商统计
providers = {}
for m in dispatcher.models:
    p = m.get('provider', 'unknown')
    if p not in providers:
        providers[p] = []
    providers[p].append(m['name'])

print("\n各服务商模型:")
for p, models in providers.items():
    print(f"  {p}: {len(models)}个")

# 测试调度 - 选择陆念昭绑定的模型
test_prompt = "你好，请回复"

# 执行调度
result = dispatcher.execute(test_prompt)
print("\n调度结果:")
print(json.dumps(result, indent=2, ensure_ascii=False))
