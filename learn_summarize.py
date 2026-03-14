# -*- coding: utf-8 -*-
"""
使用真实模型进行学习总结
"""
import requests
import json

# 使用NVIDIA的模型
API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
API_KEY = "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"
MODEL = "mistralai/mixtral-8x7b-instruct-v0.1"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# 学习内容总结
learning_content = """
AI Agent 自进化 2025年核心技术趋势：

1. 代理型AI (Agentic AI) 成为主流
- Gartner预测：到2028年，约33%的企业软件应用将内嵌代理型AI
- 2025年被公认为"AI Agent元年"

2. 三大突破：
- 基座大模型持续进化
- 多智能体系统成为主流 (从单体转向协同)
- 开放协议落地 (MCP和A2A)

3. MCP (Model Context Protocol)
- 由Anthropic推出，已成事实标准
- 2025年捐赠给Linux基金会
- OpenAI也宣布支持MCP

4. 多智能体系统 (MAS)
- 三层控制框架：底层控制层、中间管理层、顶层协调通信层
- 2025年MAS-GPT发表在ICML 2025
- 构建MAS变得"像与ChatGPT聊天一样简单"

5. 核心发展趋势：
- 多模态融合
- 自适应学习
- 绿色低碳
"""

# 发送请求让模型总结
data = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "你是一个AI助手，请用简洁的方式总结以下AI Agent自进化技术的核心要点。"},
        {"role": "user", "content": f"请总结以下2025年AI Agent核心技术趋势，用中文回复：\n\n{learning_content}"}
    ],
    "max_tokens": 500
}

print("正在调用真实模型进行分析...")
try:
    resp = requests.post(API_URL, headers=headers, json=data, timeout=60)
    if resp.status_code == 200:
        result = resp.json()
        content = result["choices"][0]["message"]["content"]
        print("\n模型分析结果:")
        print("=" * 60)
        print(content)
        print("=" * 60)
    else:
        print(f"Error: {resp.status_code} - {resp.text[:200]}")
except Exception as e:
    print(f"Exception: {e}")
