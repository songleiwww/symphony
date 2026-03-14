import requests
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_KEY = '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'
URL = 'https://integrate.api.nvidia.com/v1/models'
HEADERS = {'Authorization': f'Bearer {API_KEY}'}

r = requests.get(URL, headers=HEADERS, timeout=30)
if r.status_code == 200:
    models = r.json().get('data', [])
    print('Search for reranking models:')
    print('='*50)
    
    keywords = ['rank', 'rerank', 'retrieval', 'search', 'recall', 'sort']
    found = []
    
    for m in models:
        name = m.get('id', '').lower()
        for k in keywords:
            if k in name:
                found.append(m.get('id'))
                break
    
    if found:
        for name in found:
            print(f'Found: {name}')
    else:
        print('No rerank model found.')
        print('Related models:')
        for m in models:
            name = m.get('id')
            if 'nemo' in name or 'qa' in name or 'embed' in name:
                print(f'  - {name}')
