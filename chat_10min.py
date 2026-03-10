import requests, time, json

# 简化持续聊天 - 10分钟版本
participants = [
    ('ark-code-latest', '林思远', '架构师'),
    ('deepseek-v3.2', '陈美琪', '安全'),
    ('doubao-seed-2.0-code', '王浩然', '开发'),
    ('glm-4.7', '张明远', '测试'),
    ('kimi-k2.5', '赵敏', '运维'),
]

topics = [
    '大家最近在研究什么新技术？',
    '工作上遇到的最大挑战是什么？',
    '有什么好的学习方法推荐？',
    '对交响系统有什么建议？',
    '今晚聊天感觉如何？'
]

print('='*50)
print('Symphony Chat 10 min')
print('='*50)

all_results = []

for round_i, topic in enumerate(topics):
    print(f'\n--- Round {round_i+1}/5 ---')
    round_results = []
    
    for model_id, name, role in participants:
        try:
            url = 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions'
            r = requests.post(url, 
                headers={'Authorization': 'Bearer 3b922877-3fbe-45d1-a298-53f2231c5224', 'Content-Type': 'application/json'}, 
                json={'model': model_id, 'messages': [{'role': 'user', 'content': f'你是{name}，{role}。话题: {topic} 请简短回复'}], 'max_tokens': 100}, 
                timeout=30)
            
            if r.status_code == 200:
                content = r.json()['choices'][0]['message']['content']
                tokens = r.json().get('usage', {}).get('total_tokens', 0)
                round_results.append({'name': name, 'content': content, 'tokens': tokens})
                print(f'OK: {name}')
            else:
                print(f'Error: {name}')
        except Exception as e:
            print(f'Error: {name}')
    
    all_results.append({'round': round_i+1, 'topic': topic, 'messages': round_results})
    time.sleep(2)

# 保存
with open('C:/Users/Administrator/.openclaw/workspace/skills/symphony/chat_10min.json', 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print(f'\nTotal: {len(all_results)} rounds')
print('Done!')
