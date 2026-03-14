#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行Symphony交响讨论
使用5个真实模型进行讨论
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from symphony_real_orchestrator import SymphonyRealOrchestrator
import json
from datetime import datetime

print("=" * 100)
print("🎼 Symphony 交响讨论 - 真实模型版")
print("=" * 100)
print()

# 讨论主题
TOPIC = "人工智能如何改变未来的工作方式？"

# 5个专家配置
PANELISTS = [
    {
        "name": "战略分析师",
        "provider": "cherry-doubao",
        "model_id": "deepseek-v3.2",
        "persona": "思维缜密，善于从全局角度分析问题，关注长期影响",
        "focus": "战略规划与长期发展"
    },
    {
        "name": "创意专家",
        "provider": "cherry-doubao",
        "model_id": "kimi-k2.5",
        "persona": "富有想象力，善于提出创新想法，不拘泥于传统思维",
        "focus": "创新思维与突破"
    },
    {
        "name": "技术专家",
        "provider": "cherry-doubao",
        "model_id": "glm-4.7",
        "persona": "注重细节，善于从技术可行性角度分析，关注实现方案",
        "focus": "技术实现与可行性"
    },
    {
        "name": "风险评估师",
        "provider": "cherry-minimax",
        "model_id": "MiniMax-M2.5",
        "persona": "谨慎理性，善于识别潜在风险，提出预防措施",
        "focus": "风险识别与应对"
    },
    {
        "name": "用户体验专家",
        "provider": "cherry-doubao",
        "model_id": "deepseek-v3.2",
        "persona": "以人为本，善于从用户角度思考，关注实际使用体验",
        "focus": "用户需求与体验"
    }
]

print(f"📌 讨论主题：{TOPIC}")
print(f"👥 参与专家：{len(PANELISTS)} 位（真实模型）")
print()

for i, panelist in enumerate(PANELISTS, 1):
    print(f"  {i}. {panelist['name']}")
    print(f"     - 模型：{panelist['provider']}/{panelist['model_id']}")
    print(f"     - 专长：{panelist['focus']}")
    print()

# 初始化编排器
orchestrator = SymphonyRealOrchestrator()

# 存储讨论结果
discussion_results = {
    "topic": TOPIC,
    "timestamp": datetime.now().isoformat(),
    "panelists": PANELISTS,
    "rounds": []
}

print("=" * 100)
print("🔄 第一轮讨论开始")
print("=" * 100)
print()

round_results = []

for panelist in PANELISTS:
    print(f"🎤 {panelist['name']} 正在思考...")
    print(f"   模型：{panelist['provider']}/{panelist['model_id']}")
    print()
    
    # 构建提示词
    prompt = f"""你是{panelist['name']}。{panelist['persona']}

讨论主题：{TOPIC}

请从你的专业角度发表看法，要求：
1. 观点鲜明，有自己的独特见解
2. 结合你的专业背景
3. 提出具体的观点或建议
4. 控制在150-300字之间
5. 用中文回复

现在请发表你的看法："""
    
    # 调用模型
    result = orchestrator.call_model(
        panelist['provider'],
        panelist['model_id'],
        prompt,
        max_tokens=800
    )
    
    if result['success']:
        print(f"✅ {panelist['name']} 发言：")
        print("-" * 80)
        print(result['response'])
        print("-" * 80)
        print()
        
        round_results.append({
            "panelist": panelist['name'],
            "model": f"{panelist['provider']}/{panelist['model_id']}",
            "success": True,
            "response": result['response'],
            "latency": result.get('latency', 0),
            "tokens": result.get('total_tokens', 0)
        })
    else:
        print(f"❌ {panelist['name']} 调用失败：{result.get('error', 'Unknown error')}")
        print()
        
        round_results.append({
            "panelist": panelist['name'],
            "model": f"{panelist['provider']}/{panelist['model_id']}",
            "success": False,
            "error": result.get('error', 'Unknown error')
        })
    
    # 避免请求过快
    import time
    time.sleep(2)

discussion_results['rounds'].append({
    "round": 1,
    "results": round_results
})

# 保存结果
output_path = Path(__file__).parent / "outputs" / f"symphony_discussion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
output_path.parent.mkdir(exist_ok=True)

output_path.write_text(
    json.dumps(discussion_results, indent=2, ensure_ascii=False),
    encoding='utf-8'
)

print("=" * 100)
print("✅ 讨论完成！")
print(f"💾 结果已保存到：{output_path}")
print("=" * 100)
print()

# 打印总结
print("📊 讨论总结：")
print()
for result in round_results:
    if result['success']:
        print(f"  ✅ {result['panelist']}")
        print(f"     模型：{result['model']}")
        print(f"     耗时：{result['latency']:.2f}s")
        print(f"     Tokens：{result['tokens']}")
    else:
        print(f"  ❌ {result['panelist']} - 失败")
    print()

print("=" * 100)
print("🎼 智韵交响，共创华章")
print("=" * 100)
