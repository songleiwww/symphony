#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青丘多人研讨会 - 交响系统进化方向
使用meta模型获取更直接的答案
"""

import sys
import io

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

import time
import requests

# =============================================================================
# 配置
# =============================================================================

CONFIG = {
    "api_key": "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",
    "base_url": "https://integrate.api.nvidia.com/v1",
}


def call_model(model_id: str, prompt: str) -> dict:
    """调用模型"""
    url = f"{CONFIG['base_url']}/chat/completions"
    headers = {
        "Authorization": f"Bearer {CONFIG['api_key']}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 150,
        "temperature": 0.7
    }
    
    start = time.time()
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=120)
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            result = resp.json()
            msg = result["choices"][0]["message"]
            content = msg.get("content") or msg.get("reasoning_content") or ""
            return {"success": True, "model": model_id, "response": content.strip()[:200], "elapsed": elapsed}
        else:
            return {"success": False, "model": model_id, "error": f"Status {resp.status_code}"}
    except Exception as e:
        return {"success": False, "model": model_id, "error": str(e)}


def main():
    print("\n" + "="*70)
    print("青丘研讨会 - 交响系统进化方向")
    print("="*70)
    
    # 使用meta模型
    participants = [
        ("林思远", "银白九尾狐", "青丘长老", "架构师思维", 
         "交响系统下一步最需要什么功能？为什么？用20字以内回答。"),
        ("王明远", "火红九尾狐", "青丘猎手", "工程师思维",
         "交响系统下一步最需要什么功能？为什么？用20字以内回答。"),
        ("张晓明", "墨黑九尾狐", "青丘史官", "产品思维",
         "交响系统下一步最需要什么功能？为什么？用20字以内回答。"),
    ]
    
    for name, fox, role, thinking, question in participants:
        print(f"\n【{name}】{fox} - {role}")
        print(f"  思考角度: {thinking}")
        
        # 使用meta模型
        prompt = f"你是{name}，{fox}，{role}。{thinking}。直接回答：{question}"
        result = call_model("meta/llama-3.1-405b-instruct", prompt)
        
        if result.get("success"):
            print(f"  → {result.get('response', '')}")
        else:
            print(f"  ✗ {result.get('error', 'error')}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
