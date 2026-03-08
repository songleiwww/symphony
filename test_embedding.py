import requests
import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_KEY = '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'

# 测试向量嵌入模型
models_to_test = [
    'baai/bge-m3',
    'nvidia/nv-embed-v1',
    'nvidia/llama-nemotron-embed-1b-v2'
]

test_text = "你好，我是交交，青丘女狐"

print("="*60)
print("测试英伟达向量嵌入API")
print("="*60)

for model_id in models_to_test:
    print(f"\n测试模型: {model_id}")
    print("-"*40)
    
    try:
        # 不同的模型可能使用不同的端点
        if 'bge' in model_id:
            url = f"https://integrate.api.nvidia.com/v1/embeddings"
            data = {
                'model': model_id,
                'input': test_text,
                'encoding_format': 'float'
            }
        elif 'nv-embed' in model_id:
            url = f"https://integrate.api.nvidia.com/v1/embeddings"
            data = {
                'model': model_id,
                'input': test_text
            }
        else:
            url = f"https://integrate.api.nvidia.com/v1/embeddings"
            data = {
                'model': model_id,
                'input': [test_text]
            }
        
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }
        
        r = requests.post(url, headers=headers, json=data, timeout=30)
        
        if r.status_code == 200:
            result = r.json()
            embedding = result.get('data', [{}])[0].get('embedding', [])
            dimension = len(embedding)
            print(f"✅ 成功! 维度: {dimension}")
        else:
            print(f"❌ 失败: {r.status_code}")
            print(f"   {r.text[:100]}")
            
    except Exception as e:
        print(f"❌ 异常: {str(e)[:50]}")

print("\n" + "="*60)
print("测试完成")
print("="*60)
