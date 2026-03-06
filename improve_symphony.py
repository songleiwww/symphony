#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3个真实模型研究：如何让模型更容易理解和使用交响工具
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 加载配置
config_path = Path(r"C:\Users\Administrator\.openclaw\openclaw.cherry.json")
config = json.loads(config_path.read_text(encoding='utf-8'))

# 讨论主题
TOPIC = "如何让AI模型更容易理解和使用symphony交响工具？"

# 3个专家配置
PANELISTS = [
    {
        "name": "提示词工程师",
        "provider": "cherry-doubao",
        "model": "deepseek-v3.2",
        "role": "提示词优化、指令清晰性"
    },
    {
        "name": "用户体验专家",
        "provider": "cherry-doubao",
        "model": "kimi-k2.5",
        "role": "交互设计、易用性优化"
    },
    {
        "name": "工具设计专家",
        "provider": "cherry-doubao",
        "model": "glm-4.7",
        "role": "API设计、工具定义优化"
    }
]

def call_model(panelist):
    """调用单个模型"""
    provider_config = config["models"]["providers"][panelist["provider"]]
    api_key = provider_config["apiKey"]
    base_url = provider_config["baseUrl"]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""你是{panelist['name']}。{panelist['role']}

背景：
我们开发了一个symphony交响工具，用于让AI模型调用多个真实模型进行讨论。
工具定义如下：
- 工具名称：symphony_orchestrator
- 参数：topic（主题）、mode（模式）、num_models（模型数量）、require_real_api（必须true）
- 功能：调用多个真实模型进行讨论、头脑风暴等

问题：{TOPIC}

请从你的专业角度，给出具体的改进建议，让AI模型更容易理解和使用这个工具。
200-400字，用中文回复。"""
    
    data = {
        "model": panelist["model"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1200
    }
    
    url = f"{base_url}/chat/completions"
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=90)
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "response": result['choices'][0]['message']['content']
            }
        else:
            return {
                "success": False,
                "response": f"HTTP {response.status_code}: {response.text}"
            }
    except Exception as e:
        return {
            "success": False,
            "response": f"调用异常：{str(e)}"
        }

def main():
    print("=" * 100)
    print("3个真实模型研究：如何让模型更容易理解和使用交响工具")
    print("=" * 100)
    print()
    print(f"研究主题：{TOPIC}")
    print()
    
    results = []
    
    for i, panelist in enumerate(PANELISTS, 1):
        print(f"[{i}/{len(PANELISTS)}] {panelist['name']} 正在思考...")
        
        result = call_model(panelist)
        
        if result['success']:
            print()
            print("=" * 100)
            print(f"{panelist['name']} 发言：")
            print("=" * 100)
            print(result['response'])
            print("=" * 100)
            print()
            
            results.append({
                "panelist": panelist['name'],
                "model": f"{panelist['provider']}/{panelist['model']}",
                "response": result['response']
            })
        else:
            print(f"  失败：{result.get('response')}")
            print()
        
        if i < len(PANELISTS):
            time.sleep(2)
    
    # 保存结果
    output = {
        "topic": TOPIC,
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    
    outfile = Path(r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\outputs") / f"improve_symphony_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    outfile.parent.mkdir(exist_ok=True)
    outfile.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
    
    print()
    print("=" * 100)
    print("✅ 研究完成！")
    print(f"💾 结果已保存到：{outfile}")
    print("=" * 100)

if __name__ == "__main__":
    main()
