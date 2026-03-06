#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单真实模型调用 - 独立版本
不依赖 real_model_caller.py 的编码修复
"""

import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


def load_openclaw_config() -> Dict[str, Any]:
    """加载OpenClaw配置"""
    config_path = Path(r"C:\Users\Administrator\.openclaw\openclaw.cherry.json")
    if not config_path.exists():
        return {}
    return json.loads(config_path.read_text(encoding='utf-8'))


def call_model_simple(provider: str, model_id: str, api_key: str, base_url: str, prompt: str) -> Dict[str, Any]:
    """简单的模型调用"""
    result = {
        "success": False,
        "model_name": model_id,
        "provider": provider,
        "prompt": prompt,
        "response": "",
        "error": "",
        "latency": 0.0,
        "timestamp": datetime.now().isoformat(),
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0
    }
    
    start_time = time.time()
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500
        }
        
        # 使用OpenAI兼容格式
        if "/v1" in base_url:
            url = f"{base_url}/chat/completions"
        else:
            url = f"{base_url}/chat/completions"
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        latency = time.time() - start_time
        result["latency"] = latency
        
        if response.status_code == 200:
            data = response.json()
            result["success"] = True
            result["response"] = data["choices"][0]["message"]["content"]
            
            if "usage" in data:
                result["prompt_tokens"] = data["usage"].get("prompt_tokens", 0)
                result["completion_tokens"] = data["usage"].get("completion_tokens", 0)
                result["total_tokens"] = data["usage"].get("total_tokens", 0)
        else:
            result["error"] = f"HTTP {response.status_code}: {response.text}"
    
    except Exception as e:
        latency = time.time() - start_time
        result["latency"] = latency
        result["error"] = str(e)
    
    return result


def main():
    """主程序"""
    print("=" * 80)
    print("🤖 简单真实模型调用")
    print("=" * 80)
    
    output_file = Path("simple_real_result.json")
    
    config = load_openclaw_config()
    
    if not config:
        result = {
            "success": False,
            "error": "OpenClaw配置文件未找到",
            "timestamp": datetime.now().isoformat()
        }
        output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"❌ 配置未找到，结果已保存到: {output_file}")
        return
    
    # 获取第一个可用的模型
    providers = config.get("models", {}).get("providers", {})
    
    if not providers:
        result = {
            "success": False,
            "error": "没有找到模型提供商",
            "timestamp": datetime.now().isoformat()
        }
        output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"❌ 没有提供商，结果已保存到: {output_file}")
        return
    
    # 尝试 cherry-doubao
    if "cherry-doubao" in providers:
        provider_config = providers["cherry-doubao"]
        api_key = provider_config.get("apiKey", "")
        base_url = provider_config.get("baseUrl", "")
        models = provider_config.get("models", [])
        
        if models:
            model_id = models[0]["id"]
            print(f"\n🎯 尝试模型: cherry-doubao/{model_id}")
            
            prompt = "你好，请简单介绍一下你自己"
            result = call_model_simple("cherry-doubao", model_id, api_key, base_url, prompt)
            
            output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
            
            if result["success"]:
                print(f"✅ 调用成功!")
                print(f"   延迟: {result['latency']:.2f}秒")
                print(f"   Token: {result['prompt_tokens']}+{result['completion_tokens']}={result['total_tokens']}")
                if result["response"]:
                    print(f"   响应: {result['response'][:150]}...")
            else:
                print(f"❌ 调用失败: {result['error']}")
            
            print(f"\n📝 结果已保存到: {output_file}")
            print("\n" + "=" * 80)
            return
    
    # 如果没有cherry-doubao，保存错误
    result = {
        "success": False,
        "error": "cherry-doubao 提供商未找到",
        "timestamp": datetime.now().isoformat()
    }
    output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"❌ 未找到合适的模型，结果已保存到: {output_file}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
