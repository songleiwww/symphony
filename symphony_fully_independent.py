#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响完全独立启动器 - 不依赖任何OpenClaw文件
"""

import sys
import os
import json
import requests

# 导入完全独立的配置
from symphony_independent_config import API_CONFIG, SYSTEM_CONFIG, SYSTEM_PROMPT

def send_message(message):
    """发送消息到模型 - 完全独立实现，无任何外部依赖"""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_CONFIG['api_key']}"
        }
        
        data = {
            "model": API_CONFIG["primary_model"],
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ],
            "max_tokens": SYSTEM_CONFIG["max_tokens"],
            "temperature": SYSTEM_CONFIG["temperature"]
        }
        
        response = requests.post(
            f"{API_CONFIG['base_url']}/chat/completions",
            headers=headers,
            json=data,
            timeout=SYSTEM_CONFIG["timeout"]
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
    print("交响 Symphony 完全独立运行版")
    print("="*60)
    print(f"主模型: {API_CONFIG['primary_model']}")
    print(f"模式: 完全独立，不依赖任何OpenClaw文件")
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
