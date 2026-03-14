#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版Symphony交响讨论
"""

import json
import time
import requests
from datetime import datetime
from pathlib import Path
import sys
import io

# 设置输出编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 加载配置
config_path = Path(r"C:\Users\Administrator\.openclaw\openclaw.cherry.json")
config = json.loads(config_path.read_text(encoding='utf-8'))

# 讨论主题
TOPIC = "人工智能如何改变未来的工作方式？"

# 5个专家配置
PANELISTS = [
    {
        "name": "战略分析师",
        "provider": "cherry-doubao",
        "model_id": "deepseek-v3.2",
        "persona": "思维缜密，善于从全局角度分析问题，关注长期影响"
    },
    {
        "name": "创意专家",
        "provider": "cherry-doubao",
        "model_id": "kimi-k2.5",
        "persona": "富有想象力，善于提出创新想法，不拘泥于传统思维"
    },
    {
        "name": "技术专家",
        "provider": "cherry-doubao",
        "model_id": "glm-4.7",
        "persona": "注重细节，善于从技术可行性角度分析，关注实现方案"
    },
    {
        "name": "风险评估师",
        "provider": "cherry-minimax",
        "model_id": "MiniMax-M2.5",
        "persona": "谨慎理性，善于识别潜在风险，提出预防措施"
    },
    {
        "name": "用户体验专家",
        "provider": "cherry-doubao",
        "model_id": "deepseek-v3.2",
        "persona": "以人为本，善于从用户角度思考，关注实际使用体验"
    }
]

def call_openai(provider, model_id, prompt, max_tokens=800):
    """调用OpenAI兼容API"""
    providers = config.get("models", {}).get("providers", {})
    provider_config = providers.get(provider, {})
    
    api_key = provider_config.get("apiKey", "")
    base_url = provider_config.get("baseUrl", "")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens
    }
    
    url = f"{base_url}/chat/completions"
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
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

def call_anthropic(provider, model_id, prompt, max_tokens=800):
    """调用Anthropic兼容API"""
    providers = config.get("models", {}).get("providers", {})
    provider_config = providers.get(provider, {})
    
    api_key = provider_config.get("apiKey", "")
    base_url = provider_config.get("baseUrl", "")
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    data = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens
    }
    
    url = f"{base_url}/v1/messages"
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "response": result['content'][0]['text']
            }
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    print("=" * 100)
    print("Symphony 交响讨论 - 真实模型版")
    print("=" * 100)
    print()
    print(f"讨论主题：{TOPIC}")
    print(f"参与专家：{len(PANELISTS)} 位")
    print()
    
    results = []
    
    for panelist in PANELISTS:
        print(f"{panelist['name']} 正在思考...")
        print(f"  模型：{panelist['provider']}/{panelist['model_id']}")
        
        prompt = f"""你是{panelist['name']}。{panelist['persona']}

讨论主题：{TOPIC}

请从你的专业角度发表看法，150-300字，用中文回复。"""
        
        if panelist['provider'] == 'cherry-minimax':
            result = call_anthropic(
                panelist['provider'],
                panelist['model_id'],
                prompt
            )
        else:
            result = call_openai(
                panelist['provider'],
                panelist['model_id'],
                prompt
            )
        
        if result['success']:
            print()
            print(f"{panelist['name']} 发言：")
            print("-" * 80)
            print(result['response'])
            print("-" * 80)
            print()
            
            results.append({
                "panelist": panelist['name'],
                "model": f"{panelist['provider']}/{panelist['model_id']}",
                "response": result['response']
            })
        else:
            print(f"  失败：{result.get('error')}")
            print()
        
        time.sleep(2)
    
    # 保存结果
    output = {
        "topic": TOPIC,
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    
    outfile = Path(r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\outputs") / f"discussion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    outfile.parent.mkdir(exist_ok=True)
    outfile.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
    
    print("=" * 100)
    print(f"讨论完成！结果已保存到：{outfile}")
    print("=" * 100)

if __name__ == "__main__":
    main()
