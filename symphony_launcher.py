#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响独立运行启动器 - 修复API调用问题
"""

import sys
import os
import json
import requests
from pathlib import Path

# 加载独立配置
from symphony_config import *

# 尝试从OpenClaw模型配置读取API Key
try:
    models_json = Path(os.path.expanduser("~")) / ".openclaw" / "agents" / "main" / "agent" / "models.json"
    with open(models_json, 'r', encoding='utf-8') as f:
        models_config = json.load(f)
    
    # 获取豆包API Key
    DOUBao_API_KEY = models_config.get("cherry-doubao", {}).get("apiKey", "")
    print(f"加载API Key成功: {DOUBao_API_KEY[:8]}...")
except Exception as e:
    print(f"读取API Key失败: {e}")
    DOUBao_API_KEY = input("请输入豆包API Key: ")

# API配置
BASE_URL = PROVIDERS["cherry-doubao"]["base_url"]
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {DOUBao_API_KEY}"
}

def send_message(message):
    """发送消息到模型 - 用requests直接调用"""
    try:
        data = {
            "model": PRIMARY_MODEL,
            "messages": [
                {"role": "user", "content": message}
            ],
            "max_tokens": 1024,
            "temperature": 0.7,
            "top_p": 0.95
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=HEADERS,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"调用失败 (状态码: {response.status_code}): {response.text}"
            
    except Exception as e:
        return f"调用失败: {str(e)}"

def main():
    print("\n" + "="*60)
    print("交响 Symphony 独立运行版")
    print("="*60)
    print(f"主模型: {PRIMARY_MODEL}")
    print(f"提供商: {PROVIDERS['cherry-doubao']['name']}")
    print(f"模式: 完全独立运行，不依赖OpenClaw")
    print("="*60)
    print("\n输入消息开始对话 (输入 quit 退出)")
    print("-"*60)
    
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() in ["quit", "exit", "退出"]:
                print("\n再见！")
                break
            if not user_input.strip():
                continue
            
            print("思考中...")
            response = send_message(user_input)
            print(f"\n交交: {response}")
            
        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"\n错误: {e}")

if __name__ == "__main__":
    main()
