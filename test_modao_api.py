# -*- coding: utf-8 -*-
import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 魔搭API配置
api_url = "https://api-inference.modelscope.cn/v1/chat/completions"
api_key = "ms-eac6f154-3502-4721-a168-ce7b9c80d7e1"

# 测试现有的7个模型
models = [
    ("moonshotai/Kimi-K2.5", "Kimi K2.5"),
    ("MiniMax/MiniMax-M2.5", "MiniMax M2.5"),
    ("ZhipuAI/GLM-5", "GLM-5"),
    ("deepseek-ai/DeepSeek-V3.2", "DeepSeek V3.2"),
    ("deepseek-ai/DeepSeek-R1-0528", "DeepSeek R1 0528"),
    ("Qwen/Qwen3.5-122B-A10B", "Qwen3.5 122B"),
    ("Qwen/Qwen3-Coder-480B-A35B-Instruct", "Qwen3 Coder 480B"),
]

print("="*60)
print("【魔搭API测试】")
print("-"*60)

for identifier, name in models:
    print(f"\n{name}:")
    print(f"  ID: {identifier}")
    try:
        resp = requests.post(api_url, json={"model": identifier, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 10},
                          headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, timeout=15)
        print(f"  状态: {resp.status_code}")
        if resp.status_code != 200:
            print(f"  响应: {resp.text[:100]}")
    except Exception as e:
        print(f"  错误: {e}")
