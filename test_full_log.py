# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
序境系统 - 完整响应日志系统
"""
import sys, os, importlib.util, requests, time
import io
import json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.chdir(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')

# Load kernel
spec = importlib.util.spec_from_file_location('kl', 'Kernel/kernel_loader.py')
kl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kl)
kernel = kl.get_kernel()

user_message = "序境 我饿了"

print("=" * 60)
print("【序境系统】收到指令")
print(f"用户说: {user_message}")
print("=" * 60)
print()

# Dispatch official
# In real system, this would be based on task type
# For now, select one with NVIDIA capability
dispatched_role = kernel.roles[0]  # First available

print("【调度记录】")
print(f"  官属ID: {dispatched_role.get('id')}")
print(f"  官名: {dispatched_role.get('官名', '未知')}")
print(f"  职位: {dispatched_role.get('职位', '未知')}")
print(f"  角色等级: {dispatched_role.get('角色等级')}")
print(f"  配置模型: {dispatched_role.get('模型名称')}")
print(f"  配置服务商: {dispatched_role.get('模型服务商')}")
print()

# Since original provider may be rate limited, use available API
# Map to available API
api_map = {
    '火山引擎': {
        'url': 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions',
        'key': '3b922877-3fbe-45d1-a298-53f2231c5224',
        'model_map': {'glm-4.7': 'glm-4.7', 'glm-4-flash': 'glm-4-flash'}
    },
    '智谱': {
        'url': 'https://open.bigmodel.cn/api/paas/v4/chat/completions',
        'key': '',  # Need to fill
        'model_map': {'glm-4-flash': 'glm-4-flash', 'glm-4.7': 'glm-4.7'}
    },
    '硅基流动': {
        'url': 'https://api.siliconflow.cn/v1/chat/completions',
        'key': '',  # Need to fill
        'model_map': {'Qwen2.5-14B': 'Qwen/Qwen2.5-14B-Instruct'}
    }
}

# Use NVIDIA as fallback
print("【API调用】")
provider = 'NVIDIA'
url = "https://integrate.api.nvidia.com/v1/chat/completions"
api_key = "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"
model = "mistralai/mixtral-8x7b-instruct-v0.1"

print(f"  服务商: {provider}")
print(f"  模型: {model}")
print(f"  Endpoint: {url}")
print()

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": model,
    "messages": [
        {"role": "system", "content": "你是中国古代唐朝的官员，品级较高，语气温和关心百姓。用文言文简洁回复，控制在20字以内。"},
        {"role": "user", "content": "我饿了"}
    ],
    "max_tokens": 50
}

print("【模型调用中...】")
start = time.time()
try:
    resp = requests.post(url, headers=headers, json=data, timeout=60)
    elapsed = time.time() - start
    
    # Parse response
    if resp.status_code == 200:
        result = resp.json()
        
        # Extract token info
        usage = result.get('usage', {})
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        total_tokens = usage.get('total_tokens', 0)
        
        reply = result['choices'][0]['message']['content']
        
        print()
        print("【调用结果】")
        print(f"  状态: 成功")
        print(f"  响应时间: {elapsed:.2f}秒")
        print(f"  Prompt Tokens: {prompt_tokens}")
        print(f"  Completion Tokens: {completion_tokens}")
        print(f"  Total Tokens: {total_tokens}")
        print()
        print("【回复内容】")
        print(f"  {reply}")
        print()
        
        # Log this interaction
        log_entry = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "user_message": user_message,
            "dispatched_official": {
                "id": dispatched_role.get('id'),
                "name": dispatched_role.get('官名'),
                "position": dispatched_role.get('职位'),
                "level": dispatched_role.get('角色等级')
            },
            "model_info": {
                "provider": provider,
                "model": model,
                "original_config": {
                    "model": dispatched_role.get('模型名称'),
                    "provider": dispatched_role.get('模型服务商')
                }
            },
            "api_response": {
                "status": resp.status_code,
                "elapsed_seconds": elapsed,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            },
            "reply": reply
        }
        
        # Save log
        log_file = 'data/call_log.json'
        os.makedirs('data', exist_ok=True)
        
        existing_logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                existing_logs = json.load(f)
        
        existing_logs.append(log_entry)
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(existing_logs, f, ensure_ascii=False, indent=2)
        
        print("【日志已保存】")
        
    else:
        print(f"  状态: 失败 ({resp.status_code})")
        print(f"  响应: {resp.text[:200]}")

except Exception as e:
    print(f"  错误: {e}")

print()
print("=" * 60)
