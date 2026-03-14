# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
序境系统 - 用户: 我饿了
"""
import sys, os, importlib.util, requests, time
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.chdir(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')

# Load kernel
spec = importlib.util.spec_from_file_location('kl', 'Kernel/kernel_loader.py')
kl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kl)
kernel = kl.get_kernel()

user_message = "我饿了"

print("=" * 50)
print("【序境系统】收到指令")
print(f"用户说: {user_message}")
print("=" * 50)
print()

# Call real model
url = "https://integrate.api.nvidia.com/v1/chat/completions"
api_key = "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"
model = "mistralai/mixtral-8x7b-instruct-v0.1"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": model,
    "messages": [
        {"role": "system", "content": "你是中国古代唐朝的官员，品级较高，语气温和关心百姓。用文言文简洁回复。"},
        {"role": "user", "content": user_message}
    ],
    "max_tokens": 80
}

print("正在调用真实模型...")
start = time.time()
try:
    resp = requests.post(url, headers=headers, json=data, timeout=60)
    elapsed = time.time() - start
    print(f"响应时间: {elapsed:.1f}秒\n")
    
    if resp.status_code == 200:
        result = resp.json()
        reply = result['choices'][0]['message']['content']
        print("【回复】")
        print(reply)
    else:
        print(f"错误: {resp.status_code}")
except Exception as e:
    print(f"错误: {e}")

print()
print("=" * 50)
