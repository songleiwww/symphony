# -*- coding: utf-8 -*-
"""
序境系统 - 完整响应测试
"""
import sys, os, importlib.util, requests, time

os.chdir(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')

# Load kernel
spec = importlib.util.spec_from_file_location('kl', 'Kernel/kernel_loader.py')
kl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kl)
kernel = kl.get_kernel()

# User said "序境" - just greeting, assign a high-level official
user_message = "序境"

print("=" * 50)
print("【序境系统】收到指令")
print("=" * 50)
print()

# Find an available high-level official
for role in kernel.roles:
    if role.get('角色等级', 5) <= 2:
        model = role.get('模型名称')
        provider = role.get('模型服务商')
        
        print(f"【调度官属】{role.get('官名', '未知')} ({role.get('职位', '未知')})")
        print(f"  模型: {model}")
        print(f"  服务商: {provider}")
        print()
        
        # Try to call the real model
        API_KEYS = {
            '火山引擎': '3b922877-3fbe-45d1-a298-53f2231c5224',
            '智谱': '',
            '硅基流动': ''
        }
        
        api_key = API_KEYS.get(provider, '')
        
        if provider == '火山引擎' and api_key:
            print("正在调用真实模型...")
            url = f"https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "你是中国古代唐朝的官员，请用文言文风格回复。"},
                    {"role": "user", "content": "请用一句话介绍自己"}
                ],
                "max_tokens": 100
            }
            try:
                resp = requests.post(url, headers=headers, json=data, timeout=30)
                if resp.status_code == 200:
                    result = resp.json()
                    reply = result['choices'][0]['message']['content']
                    print(f"【回复】{reply}")
                else:
                    print(f"【回复】(API限流中，状态码: {resp.status_code})")
            except Exception as e:
                print(f"【回复】(调用失败: {str(e)[:50]})")
        else:
            print("【回复】本官已就绪，听候差遣！")
        break

print()
print("=" * 50)
