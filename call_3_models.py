#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Call 3 Models - ASCII Only
Test calling 3 real models
"""

import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


def load_openclaw_config() -> Dict[str, Any]:
    """Load OpenClaw config"""
    config_path = Path(r"C:\Users\Administrator\.openclaw\openclaw.cherry.json")
    if not config_path.exists():
        return {}
    return json.loads(config_path.read_text(encoding='utf-8'))


def call_model_single(provider: str, model_id: str, api_key: str, base_url: str, prompt: str) -> Dict[str, Any]:
    """Call a single model"""
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
            "max_tokens": 300
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
    print("Call 3 Models - Test")
    print("=" * 80)
    
    output_file = Path("call_3_models_result.json")
    
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
    
    models_to_call = []
    
    if "cherry-doubao" in providers:
        p = providers["cherry-doubao"]
        ms = p.get("models", [])
        if len(ms) >= 3:
            models_to_call = [
                {"provider": "cherry-doubao", "model": ms[0], "api_key": p["apiKey"], "base_url": p["baseUrl"]},
                {"provider": "cherry-doubao", "model": ms[1], "api_key": p["apiKey"], "base_url": p["baseUrl"]},
                {"provider": "cherry-doubao", "model": ms[2], "api_key": p["apiKey"], "base_url": p["baseUrl"]}
            ]
    
    if not models_to_call and "cherry-doubao" in providers:
        p = providers["cherry-doubao"]
        ms = p.get("models", [])
        if len(ms) >= 1:
            models_to_call = [
                {"provider": "cherry-doubao", "model": ms[0], "api_key": p["apiKey"], "base_url": p["baseUrl"]},
                {"provider": "cherry-doubao", "model": ms[0], "api_key": p["apiKey"], "base_url": p["baseUrl"]},
                {"provider": "cherry-doubao", "model": ms[0], "api_key": p["apiKey"], "base_url": p["baseUrl"]}
            ]
    
    if not models_to_call:
        result = {
            "success": False,
            "error": "Not enough models found",
            "timestamp": datetime.now().isoformat()
        }
        output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        print("Not enough models, result saved to:", output_file)
        return
    
    print(f"\nCalling {len(models_to_call)} models...")
    
    prompt = "Hello, please introduce yourself briefly in one sentence"
    
    results = []
    total_start = time.time()
    
    for i, spec in enumerate(models_to_call, 1):
        print(f"\n[{i}/{len(models_to_call)}] Calling: {spec['provider']}/{spec['model']['id']}")
        
        result = call_model_single(
            spec["provider"],
            spec["model"]["id"],
            spec["api_key"],
            spec["base_url"],
            prompt
        )
        
        results.append(result)
        
        if result["success"]:
            print(f"  Success! Latency: {result['latency']:.2f}s")
            print(f"  Tokens: {result['prompt_tokens']}+{result['completion_tokens']}={result['total_tokens']}")
            if result["response"]:
                print(f"  Response: {result['response'][:100]}...")
        else:
            print(f"  Failed: {result['error']}")
    
    total_time = time.time() - total_start
    
    output_data = {
        "success": True,
        "total_models": len(results),
        "total_time": total_time,
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    
    output_file.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    print("\n" + "=" * 80)
    print(f"Complete! Total time: {total_time:.2f}s")
    print(f"Result saved to: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
