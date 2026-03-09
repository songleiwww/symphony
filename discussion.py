# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests
import time
import threading
import json

# 使用火山引擎API
API_URL = 'https://ark.cn-beijing.volces.com/api/coding/v3'
API_KEY = '3b922877-3fbe-45d1-a298-53f2231c5224'

# 5位专家模型
models = [
    ('ark-code-latest', '林思远', '系统架构师'),
    ('doubao-seed-2.0-code', '王浩然', '算法工程师'),
    ('glm-4.7', '张明远', '产品经理'),
    ('kimi-k2.5', '赵敏', '测试工程师'),
    ('deepseek-v3.2', '陈美琪', '安全专家'),
]

topic = '''根据今天学习的AI自动进化知识，为交响(Symphony)系统制定开发计划：

背景：
1. EvoAgentX框架 - 自动构建、评估、演化LLM代理
2. 四阶段演进：静态→动态→自主学习→自进化
3. 进化算法：TextGrad、MIPRO、AFlow、EvoPrompt

请制定：
1. 短期功能（1-2周）
2. 中期目标（1个月）
3. 长期愿景（3个月+）
4. 交响特有优势
5. 风险预警

简洁有力，150字以内！'''

def call_model(model_id, prompt):
    url = f'{API_URL}/chat/completions'
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    data = {
        'model': model_id,
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 300
    }
    try:
        r = requests.post(url, headers=headers, json=data, timeout=60)
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content']
        else:
            return f'Error: {r.status_code}'
    except Exception as e:
        return f'Error: {str(e)}'

results = [None] * len(models)

def call(i, model_id, name, role):
    start = time.time()
    prompt = f'你是{name}，{role}。{topic}'
    results[i] = {'name': name, 'role': role, 'content': call_model(model_id, prompt), 'time': time.time()-start}
    print(f'OK: {name}')

threads = []
for i, (model_id, name, role) in enumerate(models):
    t = threading.Thread(target=call, args=(i, model_id, name, role))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# 保存结果到文件
with open('discussion_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print('Done!')
