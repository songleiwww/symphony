# -*- coding: utf-8 -*-
"""
序境系统 - NVIDIA模型测试
"""
import sys, os, importlib.util, requests, time

os.chdir(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')

# Load kernel
spec = importlib.util.spec_from_file_location('kl', 'Kernel/kernel_loader.py')
kl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kl)
kernel = kl.get_kernel()

user_message = "序境"

print("=" * 50)
print("【序境系统】收到指令")
print("=" * 50)
print()

# Find an official and use NVIDIA
role = kernel.roles[0]  # Just use first one
print(f"【调度官属】{role.get('官名', '未知')} ({role.get('职位', '未知')})")
print(f"  原配置模型: {role.get('模型名称')}")
print(f"  原配置服务商: {role.get('模型服务商')}")
print()

# Use NVIDIA instead
print("【切换到NVIDIA模型测试】")
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
        {"role": "system", "content": "你是中国古代唐朝的官员少府监，用文言文风格回复。"},
        {"role": "user", "content": "请用一句话介绍自己"}
    ],
    "max_tokens": 100
}

print("正在调用NVIDIA真实模型...")
start = time.time()
try:
    resp = requests.post(url, headers=headers, json=data, timeout=60)
    elapsed = time.time() - start
    print(f"响应时间: {elapsed:.1f}秒")
    
    if resp.status_code == 200:
        result = resp.json()
        reply = result['choices'][0]['message']['content']
        print()
        print("【回复】")
        print(reply)
    else:
        print(f"【错误】状态码: {resp.status_code}")
        print(resp.text[:200])
except Exception as e:
    print(f"【错误】{e}")

print()
print("=" * 50)
