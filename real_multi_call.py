#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实多模型调用 - 使用NVIDIA模型
Real Multi-Model Call - Using NVIDIA Models
"""

import json
import time
import requests
from datetime import datetime
from typing import Dict, Any


# =============================================================================
# 修复Windows编码
# =============================================================================

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# =============================================================================
# 从OpenClaw配置读取的真实API Key
# =============================================================================

MODELS = [
    {
        "name": "Llama-3.1-405B",
        "provider": "cherry-nvidia",
        "model_id": "meta/llama-3.1-405b-instruct",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "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",
        "enabled": True
    },
    {
        "name": "DeepSeek-V3.2",
        "provider": "cherry-nvidia",
        "model_id": "deepseek-ai/deepseek-v3.2",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "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",
        "enabled": True
    }
]


def call_openai_model(model_config: Dict, prompt: str) -> Dict[str, Any]:
    """调用OpenAI格式的模型"""
    url = f"{model_config['base_url']}/chat/completions"
    headers = {
        "Authorization": f"Bearer {model_config['api_key']}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_config["model_id"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "temperature": 0.7
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            return {
                "success": True,
                "model": model_config["name"],
                "provider": model_config["provider"],
                "response": content,
                "elapsed": elapsed,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "model": model_config["name"],
                "provider": model_config["provider"],
                "error": f"HTTP {response.status_code}: {response.text[:200]}",
                "elapsed": elapsed,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "success": False,
            "model": model_config["name"],
            "provider": model_config["provider"],
            "error": str(e),
            "elapsed": time.time() - start_time,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """主程序"""
    print("=" * 80)
    print("Real Multi-Model Call - Using NVIDIA API")
    print("=" * 80)
    
    prompt = "请用一句话介绍你自己，并说明你擅长什么"
    
    print(f"\nPrompt: {prompt}")
    print(f"Models to call: {len(MODELS)}")
    
    results = []
    
    for i, model in enumerate(MODELS, 1):
        print(f"\n{'='*60}")
        print(f"Calling Model {i}: {model['name']} ({model['provider']})")
        print(f"{'='*60}")
        
        result = call_openai_model(model, prompt)
        results.append(result)
        
        if result["success"]:
            print(f"Success!")
            print(f"Response: {result['response'][:300]}...")
            print(f"Time: {result['elapsed']:.2f}s")
        else:
            print(f"Failed!")
            print(f"Error: {result['error'][:300]}")
    
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    
    success_count = 0
    for r in results:
        status = "OK" if r["success"] else "FAIL"
        if r["success"]:
            success_count += 1
        print(f"{r['model']}: {status}")
    
    print(f"\nSuccess: {success_count}/{len(results)}")


if __name__ == "__main__":
    main()
