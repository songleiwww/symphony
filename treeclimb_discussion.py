#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5个真实模型交响开发：上树问题
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
TOPIC = "上树问题（Tree Climbing Problem）的算法分析与实现方案"

# 5个专家配置
PANELISTS = [
    {
        "name": "算法专家",
        "provider": "cherry-doubao",
        "model_id": "deepseek-v3.2",
        "persona": "精通算法设计与分析，善于从时间复杂度、空间复杂度角度优化问题"
    },
    {
        "name": "架构设计师",
        "provider": "cherry-doubao",
        "model_id": "kimi-k2.5",
        "persona": "善于设计可扩展、可维护的软件架构，关注工程实践"
    },
    {
        "name": "代码实现专家",
        "provider": "cherry-doubao",
        "model_id": "glm-4.7",
        "persona": "注重代码质量、可读性和可测试性，擅长编写生产级代码"
    },
    {
        "name": "性能优化师",
        "provider": "cherry-doubao",
        "model_id": "deepseek-v3.2",
        "persona": "关注性能优化、内存管理、并行计算，追求极致效率"
    },
    {
        "name": "测试工程师",
        "provider": "cherry-doubao",
        "model_id": "kimi-k2.5",
        "persona": "注重测试覆盖、边界条件、异常处理，确保代码健壮性"
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

开发任务：上树问题（Tree Climbing Problem）

请先明确：
1. "上树问题"可能的几种理解（树数据结构遍历？物理爬树？其他？）
2. 从你的专业角度，给出具体的算法/架构/实现/优化/测试方案

请给出详细的设计方案和代码示例（如果适用），200-500字，用中文回复。"""
    
    data = {
        "model": panelist["model_id"],
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
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    print("=" * 100)
    print("5个真实模型交响开发：上树问题")
    print("=" * 100)
    print()
    print(f"开发主题：{TOPIC}")
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
    
    outfile = Path(r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\outputs") / f"treeclimb_discussion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    outfile.parent.mkdir(exist_ok=True)
    outfile.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
    
    print()
    print("=" * 100)
    print("✅ 交响开发完成！")
    print(f"💾 结果已保存到：{outfile}")
    print("=" * 100)

if __name__ == "__main__":
    main()
