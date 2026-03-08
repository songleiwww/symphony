import requests
import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_KEY = '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'

# 尝试调用reranking模型
test_models = [
    'nvidia/nemoretriever-parse',
    'nvidia/llama-3.2-nemoretriever-1b-vlm-embed-v1'
]

print("Test reranking capability:")
print("="*50)

for model_id in test_models:
    print(f"\nTest: {model_id}")
    try:
        # 尝试使用chat接口测试
        url = 'https://integrate.api.nvidia.com/v1/chat/completions'
        headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
        
        # 模拟reranking任务
        data = {
            'model': model_id,
            'messages': [
                {'role': 'user', 'content': '请根据相关性排序以下文档：1.天气 2.股票 3.天气晴朗 4.股市下跌'}
            ],
            'max_tokens': 200
        }
        
        r = requests.post(url, headers=headers, json=data, timeout=30)
        if r.status_code == 200:
            result = r.json()
            content = result['choices'][0]['message']['content'][:100]
            print(f"OK: {content}")
        else:
            print(f"Failed: {r.status_code}")
    except Exception as e:
        print(f"Error: {str(e)[:50]}")

print("\n" + "="*50)
print("Note: NVIDIA没有专门的reranking API")
print("需要使用embedding+相似度计算来实现排序")
