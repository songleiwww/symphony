#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3个真实模型探讨：如何让模型调用交响技能调用真实模型不自己模拟
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

# 加载配置
config_path = Path(r"C:\Users\Administrator\.openclaw\openclaw.cherry.json")
config = json.loads(config_path.read_text(encoding='utf-8'))

# 讨论主题
TOPIC = "如何设计一个系统，让AI模型能够自动调用交响技能来调用真实模型，而不是自己模拟？"

# 3个专家配置
PANELISTS = [
    {
        "name": "系统架构师",
        "provider": "cherry-doubao",
        "model_id": "deepseek-v3.2",
        "persona": "精通系统架构设计，善于从技术可行性角度分析问题"
    },
    {
        "name": "工具链专家",
        "provider": "cherry-doubao",
        "model_id": "kimi-k2.5",
        "persona": "擅长工具链和自动化流程设计，关注实际可操作性"
    },
    {
        "name": "安全工程师",
        "provider": "cherry-doubao",
        "model_id": "glm-4.7",
        "persona": "关注安全性和风险控制，提出预防措施"
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
    
    prompt = f"""你是{panelist['name']}。{panelist['persona']}

讨论主题：{TOPIC}

背景：
- 我们有一个Symphony交响技能，能够调用多个真实模型进行讨论
- 但目前是人类手动运行脚本来实现的
- 我们希望让AI模型能够自动触发这个流程

问题：如何设计一个系统，让AI模型能够自动调用交响技能来调用真实模型，而不是自己模拟？

请从你的专业角度，给出具体的设计方案和技术实现建议，150-400字，用中文回复。"""
    
    data = {
        "model": panelist["model_id"],
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
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    print("=" * 100)
    print("3个真实模型探讨：如何让模型调用交响技能调用真实模型")
    print("=" * 100)
    print()
    print(f"讨论主题：{TOPIC}")
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
                "model": f"{panelist['provider']}/{panelist['model_id']}",
                "response": result['response']
            })
        else:
            print(f"  失败：{result.get('error')}")
            print()
        
        if i < len(PANELISTS):
            time.sleep(2)
    
    # 保存结果
    output = {
        "topic": TOPIC,
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    
    outfile = Path(r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\outputs") / f"howto_discussion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    outfile.parent.mkdir(exist_ok=True)
    outfile.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
    
    print()
    print("=" * 100)
    print("✅ 讨论完成！")
    print(f"💾 结果已保存到：{outfile}")
    print("=" * 100)

if __name__ == "__main__":
    main()
