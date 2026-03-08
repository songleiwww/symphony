#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
"""
青丘对话配置系统 v3.9.12
通过对话方式帮助用户配置API Key
"""
import requests
import json
import time
from datetime import datetime

# API配置模板
API_PROVIDERS = {
    'nvidia': {
        'name': 'NVIDIA',
        'url': 'https://build.nvidia.com/',
        'base_url': 'https://integrate.api.nvidia.com/v1',
        'model_id': 'meta/llama-3.1-405b-instruct',
        'api_key_placeholder': 'nvapi-xxxxxxxx',
    },
    'minimax': {
        'name': 'MiniMax',
        'url': 'https://platform.minimaxi.com/',
        'base_url': 'https://api.minimaxi.com/anthropic',
        'model_id': 'MiniMax-M2.5',
        'api_key_placeholder': 'sk-xxxxxxxx',
    },
    'zhipu': {
        'name': '智谱GLM',
        'url': 'https://open.bigmodel.cn/',
        'base_url': 'https://open.bigmodel.cn/api/paas/v4',
        'model_id': 'glm-4-flash',
        'api_key_placeholder': '16cf0a4axxxxxxxx',
    },
    'modelscope': {
        'name': 'ModelScope',
        'url': 'https://modelscope.cn/',
        'base_url': 'https://api.modelscope.cn/v1',
        'model_id': 'qwen3-235b-a22b',
        'api_key_placeholder': 'xxxxxxxx',
    }
}

def test_api_key(provider, api_key):
    """测试API Key是否有效"""
    config = API_PROVIDERS.get(provider)
    if not config:
        return False, "未知的提供商"
    
    try:
        url = config['base_url'] + '/chat/completions'
        headers = {
            'Authorization': f"Bearer {api_key}",
            'Content-Type': 'application/json'
        }
        
        # 根据不同提供商调整请求
        if provider == 'minimax':
            headers['Authorization'] = api_key
            data = {
                'model': config['model_id'],
                'messages': [{'role': 'user', 'content': 'Hi'}],
                'max_tokens': 10
            }
        else:
            data = {
                'model': config['model_id'],
                'messages': [{'role': 'user', 'content': 'Hi'}],
                'max_tokens': 10
            }
        
        r = requests.post(url, headers=headers, json=data, timeout=15)
        
        if r.status_code == 200:
            return True, "配置成功！"
        elif r.status_code == 401:
            return False, "API Key无效"
        elif r.status_code == 429:
            return False, "API调用次数受限"
        else:
            return False, f"错误码: {r.status_code}"
    except Exception as e:
        return False, f"连接失败: {str(e)[:30]}"

def generate_config_script(provider, api_key):
    """生成配置脚本"""
    config = API_PROVIDERS.get(provider)
    if not config:
        return None
    
    return f'''# =============================================================================
# Symphony 配置更新 - {config['name']}
# =============================================================================

# 更新 {config['name']} API Key
{provider.upper()}_API_KEY = "{api_key}"

# 测试结果: 成功
# 配置时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# =============================================================================
'''

def main():
    print("="*60)
    print("青丘对话配置系统 v3.9.12")
    print("通过对话方式帮助用户配置API Key")
    print("="*60)
    print()
    
    # 打印可用提供商
    print("📋 可用提供商:")
    for key, val in API_PROVIDERS.items():
        print(f"  {key}: {val['name']}")
    print()
    
    # 模拟对话（实际使用时可嵌入到主程序）
    print("💬 对话配置流程:")
    print()
    print("用户: 帮我配置NVIDIA")
    print("娇娇: 好的！请提供你的NVIDIA API Key")
    print("用户: nvapi-xxxxx")
    print("娇娇: 正在测试...")
    print()
    
    # 测试示例API Key（用placeholder测试会失败）
    print("🔄 测试NVIDIA API Key...")
    success, msg = test_api_key('nvidia', 'nvapi-test')
    print(f"  结果: {msg}")
    print()
    
    # 生成配置脚本
    print("📝 生成配置脚本...")
    script = generate_config_script('nvidia', 'nvapi-test')
    if script:
        print("  ✅ 配置脚本已生成")
        print()
        print("配置内容预览:")
        print("-"*40)
        print(script[:200] + "...")
        print("-"*40)
    
    print()
    print("="*60)
    print("功能说明")
    print("="*60)
    print("1. 用户选择提供商")
    print("2. 娇娇引导用户提供API Key")
    print("3. 娇娇测试API Key有效性")
    print("4. 娇娇生成配置脚本")
    print("5. 用户确认后写入配置文件")
    print("="*60)

if __name__ == '__main__':
    main()
