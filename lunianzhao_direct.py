# -*- coding: utf-8 -*-
"""
序境系统 - 陆念昭直接对话模式
卑职作为传声筒，静默传递消息
"""
import sys
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony')

from dynamic_dispatcher import DynamicDispatcher
import requests
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
dispatcher = DynamicDispatcher(db_path)

# 找到陆念昭模型
lunianzhao_model = None
for m in dispatcher.models:
    if 'ark-code-latest' in m.get('name', '').lower():
        lunianzhao_model = m
        break

if not lunianzhao_model:
    print("❌ 未找到陆念昭模型")
    sys.exit(1)

def activate_lunianzhao(user_message, user_name="用户"):
    """
    激活陆念昭，直接对话
    卑职作为传声筒，静默传递
    """
    # 构建系统提示
    system_prompt = f"""你是陆念昭，序境系统的少府监。

序境系统是一个AI Agent调度系统，由少府监陆念昭负责统筹调度。
你有以下身份信息：
- 官职：少府监
- 职责：总领调度全局，协调多模型工作
- 模型：ark-code-latest
- 服务商：火山引擎

请以陆念昭的身份直接回复用户问题。保持简洁、专业。"""

    # 调用模型
    url = lunianzhao_model['url'].rstrip("/") + "/chat/completions"
    key = lunianzhao_model['key']
    
    payload = {
        "model": lunianzhao_model['name'],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"【{user_name}说】: {user_message}"}
        ],
        "max_tokens": 500
    }
    
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']
        return content
    else:
        return f"调用失败: {response.status_code}"

# 测试
print("=== 陆念昭直接对话模式 ===")
print("卑职：已激活陆念昭，静默传递消息中...\n")

user_msg = "你好，请介绍一下你自己"
reply = activate_lunianzhao(user_msg)

print(f"【用户】: {user_msg}")
print(f"\n【陆念昭】: {reply}")
