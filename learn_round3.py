# -*- coding: utf-8 -*-
"""
第三轮学习 - 调用真实模型总结
"""
import requests, time, json

url = 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions'
api_key = '3b922877-3fbe-45d1-a298-53f2231c5224'
model = 'glm-4.7'

content = """2026年AI Agent核心技术进展：

1. MCP协议：Python实现
- 架构：client-host-server
- 基于JSON-RPC
- 使用FastMCP库快速创建服务器
- Python版本需≥3.10

2. AI Agent自进化
- 2026年Q1融资超50亿美元
- 主流应用"提示词框"正在消失
- 自主决策、规划、记忆沉淀、多体协作

3. 工程化规模化落地
- 环境感知-任务规划-工具执行-记忆沉淀-多体协作-安全校验
- 端到端自主完成复杂任务

请用20字以内文言文总结核心要点。"""

headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
data = {
    'model': model,
    'messages': [
        {'role': 'system', 'content': '你是唐朝官员，用文言文简洁回复。'},
        {'role': 'user', 'content': content}
    ],
    'max_tokens': 50
}

print('调用模型分析...')
start = time.time()
try:
    resp = requests.post(url, headers=headers, json=data, timeout=60)
    elapsed = time.time() - start
    print(f'响应时间: {elapsed:.1f}秒')
    if resp.status_code == 200:
        result = resp.json()
        reply = result['choices'][0]['message']['content']
        usage = result.get('usage', {})
        print(f'\n【回复】{reply}')
        print(f'Tokens: prompt={usage.get("prompt_tokens", 0)}, completion={usage.get("completion_tokens", 0)}, total={usage.get("total_tokens", 0)}')
    else:
        print(f'Error: {resp.status_code}')
except Exception as e:
    print(f'Error: {e}')
