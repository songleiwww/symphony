import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests, time, threading, json, random

# 持续聊天系统 - 30分钟
participants = [
    ('ark-code-latest', '林思远', '♂ 交响-架构师/青丘-长老'),
    ('deepseek-v3.2', '陈美琪', '♀ 交响-安全/青丘-史官'),
    ('doubao-seed-2.0-code', '王浩然', '♂ 交响-开发/青丘-猎手'),
    ('glm-4.7', '张明远', '♂ 交响-测试/青丘-舞姬'),
    ('kimi-k2.5', '赵敏', '♀ 交响-运维/青丘-守护'),
    ('MiniMax-M2.5', '刘心怡', '♀ 交响-策划/青丘-祭司'),
]

topics = [
    '大家最近都在研究什么新技术？分享一下',
    '说说你们各自领域的难点和解决方法',
    '推荐一个最近发现的实用工具或方法',
    '谈谈如何平衡工作和生活',
    '对交响系统的未来有什么期待和建议',
    '今晚的聊天收获了什么？总结一下'
]

results = []

def call(model_id, name, role, topic, round_i):
    try:
        url = 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions'
        prompt = f'你是{name}，{role}。请针对话题"{topic}"发表看法，要自然聊天风格，简洁有趣。'
        r = requests.post(url, headers={'Authorization': 'Bearer 3b922877-3fbe-45d1-a298-53f2231c5224', 'Content-Type': 'application/json'}, 
                         json={'model': model_id, 'messages': [{'role': 'user', 'content': prompt}], 'max_tokens': 120}, timeout=60)
        
        if r.status_code == 200:
            resp = r.json()
            content = resp['choices'][0]['message']['content']
            usage = resp.get('usage', {})
            total_tokens = usage.get('total_tokens', 0)
            results.append({'round': round_i+1, 'name': name, 'role': role, 'topic': topic, 'content': content, 'tokens': total_tokens})
            print(f'OK: R{round_i+1} - {name}')
        else:
            print(f'Error: R{round_i+1} - {name}')
    except Exception as e:
        print(f'Error: R{round_i+1} - {name}')

print('='*60)
print('* Symphony Team Chat (30 min) *')
print('='*60)

for round_i, topic in enumerate(topics):
    print(f'--- Round {round_i+1} ---')
    for p in participants:
        call(p[0], p[1], p[2], topic, round_i)
    time.sleep(3)

with open('C:/Users/Administrator/.openclaw/workspace/skills/symphony/chat_30min.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f'Total: {len(results)} messages')
print('Done!')
