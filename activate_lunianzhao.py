# -*- coding: utf-8 -*-
"""
序境系统 - 启动陆念昭进行对话
"""
import sys
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony')

from dynamic_dispatcher import DynamicDispatcher
import json
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

# 初始化调度器
dispatcher = DynamicDispatcher(db_path)

# 查找陆念昭的模型
lunianzhao_model = None
for m in dispatcher.models:
    if 'ark-code-latest' in m.get('name', '').lower():
        lunianzhao_model = m
        break

print(f"找到陆念昭模型: {lunianzhao_model['name']}")
print(f"服务商: {lunianzhao_model['provider']}")
print(f"API: {lunianzhao_model['url']}")

# 模拟用户对话
user_message = "你好，请介绍你自己"

print(f"\n【用户消息】: {user_message}")
print("【调用模型】: ark-code-latest (陆念昭)")
print("【状态】: 正在激活陆念昭...")

# 调用陆念昭模型
result = dispatcher.execute(user_message, model=lunianzhao_model)

print(f"\n【响应状态】: {result.get('status')}")
if result.get('status') == 'success':
    content = result.get('result', {}).get('choices', [{}])[0].get('message', {}).get('content', '')
    print(f"\n【陆念昭回复】:\n{content}")
    print(f"\n【模型】: {result.get('model')}")
    print(f"【延迟】: {result.get('latency', 0):.2f}秒")
else:
    print(f"【错误】: {result.get('error')}")
