#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型限流替补调度器 - 调试版本
"""

import time
import json
import requests
from pathlib import Path
from typing import Optional, List, Dict


def main():
    print("=" * 60)
    print("调试：测试各模型")
    print("=" * 60)
    
    # 加载配置
    config_path = r"C:\Users\Administrator\.openclaw\openclaw.cherry.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    providers = config["models"]["providers"]
    
    # 测试各模型
    test_models = [
        {"provider": "cherry-doubao", "model": "deepseek-v3.2"},
        {"provider": "cherry-doubao", "model": "glm-4.7"},
        {"provider": "cherry-doubao", "model": "kimi-k2.5"},
        {"provider": "cherry-minimax", "model": "MiniMax-M2.5"},
    ]
    
    for model_cfg in test_models:
        provider = providers.get(model_cfg["provider"])
        if not provider:
            print(f"\n[ERROR] 找不到提供商: {model_cfg['provider']}")
            continue
        
        api_key = provider.get("apiKey", "")
        base_url = provider.get("baseUrl", "")
        
        url = f"{base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model_cfg["model"],
            "messages": [{"role": "user", "content": "你好"}],
            "max_tokens": 50
        }
        
        print(f"\n测试 {model_cfg['provider']}/{model_cfg['model']}...")
        print(f"  URL: {url}")
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            print(f"  HTTP: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print(f"  成功: {content[:50]}")
            else:
                print(f"  失败: {response.text[:100]}")
        except Exception as e:
            print(f"  异常: {e}")


if __name__ == "__main__":
    main()
