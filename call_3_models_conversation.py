#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Call 3 Models - Conversation
3 models have a conversation
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
            "max_tokens": 200
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
    print("3 Models Conversation")
    print("=" * 80)
    
    output_file = Path("call_3_models_conversation.json")
    
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
    
    model_a = None
    model_b = None
    model_c = None
    
    if "cherry-doubao" in providers:
        p = providers["cherry-doubao"]
        ms = p.get("models", [])
        if len(ms) >= 3:
            model_a = {"provider": "cherry-doubao", "model": ms[0], "api_key": p["apiKey"], "base_url": p["baseUrl"], "name": "Doubao Ark"}
            model_b = {"provider": "cherry-doubao", "model": ms[1], "api_key": p["apiKey"], "base_url": p["baseUrl"], "name": "DeepSeek"}
            model_c = {"provider": "cherry-doubao", "model": ms[2], "api_key": p["apiKey"], "base_url": p["baseUrl"], "name": "Doubao Seed"}
    
    if not model_a:
        result = {
            "success": False,
            "error": "Not enough models found",
            "timestamp": datetime.now().isoformat()
        }
        output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        print("Not enough models, result saved to:", output_file)
        return
    
    conversation = []
    total_start = time.time()
    
    print(f"\nModels: {model_a['name']}, {model_b['name']}, {model_c['name']}")
    
    # Round 1: Model A starts
    print(f"\n[Round 1] {model_a['name']} speaks...")
    prompt_a = "Hello! Let's have a friendly conversation. What do you think about AI collaboration?"
    result_a1 = call_model_single(
        model_a["provider"],
        model_a["model"]["id"],
        model_a["api_key"],
        model_a["base_url"],
        prompt_a
    )
    conversation.append({"speaker": model_a["name"], "prompt": prompt_a, "result": result_a1})
    
    if result_a1["success"]:
        print(f"  Response: {result_a1['response'][:80]}...")
    
    # Round 2: Model B responds to A
    print(f"\n[Round 2] {model_b['name']} responds...")
    context_b = f"Model A said: '{result_a1['response'] if result_a1['success'] else 'Hello'}'. Now please respond in a friendly way."
    result_b1 = call_model_single(
        model_b["provider"],
        model_b["model"]["id"],
        model_b["api_key"],
        model_b["base_url"],
        context_b
    )
    conversation.append({"speaker": model_b["name"], "prompt": context_b, "result": result_b1})
    
    if result_b1["success"]:
        print(f"  Response: {result_b1['response'][:80]}...")
    
    # Round 3: Model C responds
    print(f"\n[Round 3] {model_c['name']} joins...")
    context_c = f"Model A: '{result_a1['response'][:100] if result_a1['success'] else 'Hi'}', Model B: '{result_b1['response'][:100] if result_b1['success'] else 'Hello'}'. Now please add your thoughts!"
    result_c1 = call_model_single(
        model_c["provider"],
        model_c["model"]["id"],
        model_c["api_key"],
        model_c["base_url"],
        context_c
    )
    conversation.append({"speaker": model_c["name"], "prompt": context_c, "result": result_c1})
    
    if result_c1["success"]:
        print(f"  Response: {result_c1['response'][:80]}...")
    
    total_time = time.time() - total_start
    
    output_data = {
        "success": True,
        "title": "3 Models Conversation",
        "total_models": 3,
        "total_rounds": 3,
        "total_time": total_time,
        "timestamp": datetime.now().isoformat(),
        "conversation": conversation
    }
    
    output_file.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    print("\n" + "=" * 80)
    print(f"Complete! Total time: {total_time:.2f}s")
    print(f"Result saved to: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
