import requests
import json
import time
import threading

# API configs - 换成不同的模型
apis = [
    ('qwen/qwen3.5-397b-a17b', 'https://integrate.api.nvidia.com/v1/chat/completions', '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'),
    ('glm-z1-flash', 'https://open.bigmodel.cn/api/paas/v4/chat/completions', '16cf0a4a775c46cfa1684abcf4b802d0.rtb4oMgpFocBy87y'),
    ('Doubao-Seed-2.0-Code', 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions', '3b922877-3fbe-45d1-a298-53f2231c5224'),
]

results = []
lock = threading.Lock()

def call_api(name, url, key):
    headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
    data = {'model': name, 'messages': [{'role':'user','content':'hello'}], 'max_tokens': 20}
    start = time.time()
    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        elapsed = time.time() - start
        with lock:
            results.append({'model': name, 'success': r.status_code==200, 'elapsed': elapsed})
            print(f"OK: {name} ({elapsed:.2f}s)")
    except Exception as e:
        with lock:
            results.append({'model': name, 'success': False, 'error': str(e)})
            print(f"FAIL: {name}")

print("并发调用 3 个不同模型...")
threads = []
for name, url, key in apis:
    t = threading.Thread(target=call_api, args=(name, url, key))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(f"\n成功: {sum(1 for r in results if r.get('success'))}/{len(results)}")

# Update monitor
total = len(results)
success = sum(1 for r in results if r.get('success'))
monitor_file = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\monitor_data.json"
with open(monitor_file, 'w', encoding='utf-8') as f:
    json.dump({
        'uptime': time.time(),
        'total_calls': total,
        'success_rate': success/total*100,
        'active_calls': 0,
        'model_stats': {r['model']: {'success':1 if r.get('success')else 0,'fail':0 if r.get('success')else 1,'total_time':r.get('elapsed',0),'calls':1} for r in results},
        'recent_calls': [{'model':r['model'],'success':r.get('success'),'elapsed':r.get('elapsed',0),'prompt':'hello','timestamp':time.strftime('%Y-%m-%dT%H:%M:%S')} for r in results],
        'last_update': time.strftime('%Y-%m-%dT%H:%M:%S')
    }, f, ensure_ascii=False, indent=2)

print("监控已更新!")
