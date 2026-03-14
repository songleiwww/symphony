#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整Symphony交响讨论 - 5个真实模型
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
        "provider": "cherry-doubao",
        "model_id": "deepseek-v3.2",
        "persona": "谨慎理性，善于识别潜在风险，提出预防措施"
    },
    {
        "name": "用户体验专家",
        "provider": "cherry-doubao",
        "model_id": "kimi-k2.5",
        "persona": "以人为本，善于从用户角度思考，关注实际使用体验"
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

请从你的专业角度发表看法，150-300字，用中文回复。"""
    
    data = {
        "model": panelist["model_id"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 800
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

def main():
    print("=" * 100)
    print("Symphony 交响讨论会 - 真实模型版")
    print("=" * 100)
    print()
    print(f"讨论主题：{TOPIC}")
    print(f"参与专家：{len(PANELISTS)} 位（真实模型调用）")
    print()
    
    results = []
    
    for i, panelist in enumerate(PANELISTS, 1):
        print(f"[{i}/{len(PANELISTS)}] {panelist['name']} 正在思考...")
        print(f"  模型：{panelist['provider']}/{panelist['model_id']}")
        
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
    
    outfile = Path(r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\outputs") / f"symphony_discussion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    outfile.parent.mkdir(exist_ok=True)
    outfile.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
    
    # 生成Markdown摘要
    md_file = Path(r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\outputs") / f"symphony_discussion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    md_content = f"# Symphony 交响讨论会记录\n\n"
    md_content += f"**主题：** {TOPIC}\n"
    md_content += f"**时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    md_content += f"**参与专家：** {len(results)} 位（真实模型调用）\n\n"
    
    md_content += "## 与会专家\n\n"
    for panelist in PANELISTS:
        md_content += f"- **{panelist['name']}** - {panelist['model_id']}\n"
    
    md_content += "\n## 讨论内容\n"
    
    for result in results:
        md_content += f"\n### {result['panelist']}\n\n"
        md_content += f"*模型：{result['model']}*\n\n"
        md_content += f"{result['response']}\n"
    
    md_content += "\n---\n\n"
    md_content += "*智韵交响，共创华章* 🎼\n"
    
    md_file.write_text(md_content, encoding='utf-8')
    
    print()
    print("=" * 100)
    print("✅ 交响讨论会圆满完成！")
    print(f"💾 JSON结果：{outfile}")
    print(f"📄 Markdown摘要：{md_file}")
    print("=" * 100)
    print()
    print("🎼 智韵交响，共创华章")

if __name__ == "__main__":
    main()
