#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Real Model Call - ASCII Only Version
No emoji, no non-ASCII characters
"""

import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


def load_openclaw_config() -> Dict[str, Any]:
    """Load OpenClaw config"""
    config_path = Path(r"C:\Users\Administrator\.openclaw\openclaw.cherry.json")
    if not config_path.exists():
        return {}
    return json.loads(config_path.read_text(encoding='utf-8'))


def call_model_simple(provider: str, model_id: str, api_key: str, base_url: str, prompt: str) -> Dict[str, Any]:
    """Simple model call"""
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
    """Main function"""
    print("=" * 80)
    print("Simple Real Model Call")
    print("=" * 80)
    
    output_file = Path("simple_real_result.json")
    
    config = load_openclaw_config()
    
    if not config:
        result = {
            "success": False,
            "error": "OpenClaw config not found",
            "timestamp": datetime.now().isoformat()
        }
        output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        print("Config not found, result saved to:", output_file)
        return
    
    providers = config.get("models", {}).get("providers", {})
    
    if not providers:
        result = {
            "success": False,
            "error": "No model providers found",
            "timestamp": datetime.now().isoformat()
        }
        output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        print("No providers found, result saved to:", output_file)
        return
    
    if "cherry-doubao" in providers:
        provider_config = providers["cherry-doubao"]
        api_key = provider_config.get("apiKey", "")
        base_url = provider_config.get("baseUrl", "")
        models = provider_config.get("models", [])
        
        if models:
            model_id = models[0]["id"]
            print("\nTrying model: cherry-doubao/" + model_id)
            
            prompt = "Hello, please introduce yourself briefly"
            result = call_model_simple("cherry-doubao", model_id, api_key, base_url, prompt)
            
            output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
            
            if result["success"]:
                print("Success!")
                print(f"  Latency: {result['latency']:.2f}s")
                print(f"  Tokens: {result['prompt_tokens']}+{result['completion_tokens']}={result['total_tokens']}")
                if result["response"]:
                    print(f"  Response: {result['response'][:150]}...")
            else:
                print("Failed:", result["error"])
            
            print("\nResult saved to:", output_file)
            print("\n" + "=" * 80)
            return
    
    result = {
        "success": False,
        "error": "cherry-doubao provider not found",
        "timestamp": datetime.now().isoformat()
    }
    output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    print("No suitable model found, result saved to:", output_file)
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
