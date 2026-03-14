# -*- coding: utf-8 -*-
"""
使用真实模型进行学习总结 - 第二轮
"""
import requests
import json
import time

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
API_KEY = "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"
MODEL = "mistralai/mixtral-8x7b-instruct-v0.1"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

learning_content = """
2025年AI Agent协议标准化的关键进展：

1. MCP (Model Context Protocol) - Anthropic
- 2024年11月推出，被称为AI界的"USB Type-C"
- 解决AI与外部工具/数据的连接问题
- 一次编写，多次集成，无需为每个新集成重写定制代码
- 支持本地运行，未来将引入企业级远程认证

2. A2A (Agent-to-Agent Protocol) - Google
- 2025年推出，专注于智能体之间的协作
- 基于Web标准：HTTP(S)、JSON-RPC 2.0、SSE
- 解决不同系统和平台中智能体的标准化交互问题
- OpenAI、Google、阿里、腾讯已纷纷支持

3. 市场预测
- 2025年AI智能体市场规模：78.4亿美元
- 2030年预计：526.2亿美元
- 复合年增长率：46.3%

4. 核心区别
- MCP：解决"AI如何访问外部工具和数据"
- A2A：解决"AI如何与另一台AI直接对话与配合"
"""

# 调用模型
data = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "你是一个AI技术顾问，请用简洁专业的方式总结以下AI Agent协议的核心要点。"},
        {"role": "user", "content": f"请总结以下2025年AI Agent协议标准化的核心信息：\n\n{learning_content}"}
    ],
    "max_tokens": 400
}

print("调用真实模型分析...")
start = time.time()
try:
    resp = requests.post(API_URL, headers=headers, json=data, timeout=90)
    elapsed = time.time() - start
    print(f"响应时间: {elapsed:.1f}秒")
    
    if resp.status_code == 200:
        result = resp.json()
        content = result["choices"][0]["message"]["content"]
        print("\n=== 模型分析结果 ===")
        print(content)
    else:
        print(f"Error: {resp.status_code}")
except Exception as e:
    print(f"Exception: {e}")
