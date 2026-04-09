
import requests
import json
import time

# 两个实例的配置
MAIN_INSTANCE = {
    "url": "http://127.0.0.1:18789/api/v1/agent/run",
    "token": "f898e938c6fa7fbd4cae795369fd80ea6dd0cdb2541e80ec",
    "name": "主实例"
}
DEV_INSTANCE = {
    "url": "http://127.0.0.1:19001/api/v1/agent/run",
    "token": "b66cf8604f6cbc093864e603f2aa0f1b930aaa7baf3e75d6",
    "name": "开发实例"
}

# 讨论主题
TOPIC = "讨论「序境」项目当前存在的主要问题、缺陷，以及优先级最高的整改优化方案，尽量具体，多提实际可行的建议，不要空话。当前已经有一个实例梳理了部分问题，你需要基于对方的回答补充、反驳、深化讨论，每次回复控制在500字以内。"

# 对话历史
history = []
MAX_ROUNDS = 10

def call_agent(instance, message):
    headers = {
        "Authorization": f"Bearer {instance['token']}",
        "Content-Type": "application/json"
    }
    payload = {
        "message": message,
        "history": history[-5:],  # 保留最近5轮对话上下文
        "stream": False
    }
    try:
        resp = requests.post(instance["url"], headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        return result.get("content", "无回复")
    except Exception as e:
        return f"调用失败: {str(e)}"

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print("多脑讨论开始，主题：梳理「序境」项目问题与整改方案\n")
    current_speaker = DEV_INSTANCE
    current_message = f"第一轮：请你先梳理「序境」项目当前的主要问题和缺陷。{TOPIC}"
    
    for i in range(MAX_ROUNDS):
        print(f"{'='*60}\n{current_speaker['name']} 第{i+1}轮回复：\n")
        response = call_agent(current_speaker, current_message)
        print(response + "\n")
        
        # 更新历史
        history.append({
            "role": "user",
            "content": current_message
        })
        history.append({
            "role": "assistant",
            "content": response
        })
        
        # 切换发言人
        current_speaker = MAIN_INSTANCE if current_speaker == DEV_INSTANCE else DEV_INSTANCE
        current_message = f"基于上一轮对方的观点，继续讨论「序境」项目的问题和整改方案。{TOPIC}"
        
        time.sleep(2)  # 避免请求过快
    
    print("="*60)
    print("多脑讨论结束，共完成10轮对话，以上是全部讨论内容。")
