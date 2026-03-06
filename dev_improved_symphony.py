#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3个真实模型开发：改进版交响工具
按照之前3个模型的建议进行优化
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

# 开发任务
TOPIC = "根据之前3个模型的建议，开发改进版的symphony交响工具"

# 3个专家配置
PANELISTS = [
    {
        "name": "核心开发工程师",
        "provider": "cherry-doubao",
        "model": "deepseek-v3.2",
        "role": "实现工具命名优化、参数精简"
    },
    {
        "name": "文档与示例专家",
        "provider": "cherry-doubao",
        "model": "kimi-k2.5",
        "role": "编写结构化描述、提供调用模板"
    },
    {
        "name": "系统架构师",
        "provider": "cherry-doubao",
        "model": "glm-4.7",
        "role": "设计触发场景、强调价值主张"
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
我们之前让3个模型研究如何让AI模型更容易理解和使用symphony交响工具。

3个模型的总结建议：
1. 提示词工程师建议：
   - 工具描述结构化，类比为"交响乐指挥"
   - 参数解释具体化，给每个参数补充示例和约束
   - 提供调用模板
   - 强化错误预防提示
   - 关联输出预期

2. 用户体验专家建议：
   - 将工具名改为"MultiModelCollaboration"或"BrainstormPanel"（更直观）
   - 移除require_real_api（固定为true无需暴露）
   - 为mode设置明确的枚举值：debate（辩论）、brainstorm（头脑风暴）、evaluate（评估）
   - 在工具说明中加入示例调用

3. 工具设计专家建议：
   - 明确触发场景，强化特定意图关键词
   - 简化参数结构，移除冗余的require_real_api
   - 注入少样本示例
   - 强调价值主张："超越单一模型的综合分析质量"

开发任务：{TOPIC}

请从你的专业角度，给出具体的实现方案和代码示例。
要求：
1. 给出具体的Python代码实现
2. 代码要完整、可运行
3. 包含详细的注释
4. 200-500字，用中文回复。"""
    
    data = {
        "model": panelist["model"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1500
    }
    
    url = f"{base_url}/chat/completions"
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=120)
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
    print("3个真实模型开发：改进版交响工具")
    print("=" * 100)
    print()
    print(f"开发任务：{TOPIC}")
    print()
    
    results = []
    
    for i, panelist in enumerate(PANELISTS, 1):
        print(f"[{i}/{len(PANELISTS)}] {panelist['name']} 正在开发...")
        
        result = call_model(panelist)
        
        if result['success']:
            print()
            print("=" * 100)
            print(f"{panelist['name']} 的方案：")
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
    
    outfile = Path(r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\outputs") / f"dev_improved_symphony_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    outfile.parent.mkdir(exist_ok=True)
    outfile.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
    
    print()
    print("=" * 100)
    print("✅ 开发完成！")
    print(f"💾 结果已保存到：{outfile}")
    print("=" * 100)

if __name__ == "__main__":
    main()
