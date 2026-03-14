import requests, json, time, sys

# 3人聊天 - 5轮 = 15条消息
names = [
    ('ark-code-latest', '林思远', '架构师'),
    ('deepseek-v3.2', '陈美琪', '安全'),
    ('glm-4.7', '王浩然', '开发'),
]

topics = [
    '最近在研究什么新技术？',
    '工作上遇到的最大挑战是什么？',
    '有什么好的学习方法推荐？',
    '对交响系统有什么建议？',
    '今晚聊天收获是什么？'
]

results = []
print('Chat Start', flush=True)

for ri, topic in enumerate(topics):
    print(f'Round {ri+1}/5', flush=True)
    for mid, name, role in names:
        try:
            r = requests.post(
                'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions', 
                headers={
                    'Authorization': 'Bearer 3b922877-3fbe-45d1-a298-53f2231c5224', 
                    'Content-Type': 'application/json'
                }, 
                json={
                    'model': mid, 
                    'messages': [{
                        'role': 'user', 
                        'content': f'你是{name}，{role}。话题: {topic} 请简短回复'
                    }], 
                    'max_tokens': 80
                }, 
                timeout=25
            )
            if r.status_code == 200:
                data = r.json()
                c = data['choices'][0]['message']['content']
                t = data.get('usage', {}).get('total_tokens', 0)
                results.append({
                    'round': ri+1,
                    'name': name,
                    'role': role,
                    'topic': topic,
                    'content': c,
                    'tokens': t
                })
                print(f'OK: {name}', flush=True)
            else:
                print(f'Error: {name} ({r.status_code})', flush=True)
        except Exception as e:
            print(f'Error: {name} - {str(e)[:30]}', flush=True)
    
    time.sleep(1)

# 保存结果
output_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/chat_30min.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f'Done! {len(results)} messages saved', flush=True)
