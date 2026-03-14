# -*- coding: utf-8 -*-
"""
第五轮学习 - 调度多人搜索+模型分析
"""
import requests, time, json
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_CONFIGS = {
    '火山引擎': {
        'url': 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions',
        'key': '3b922877-3fbe-45d1-a298-53f2231c5224',
    },
    'NVIDIA': {
        'url': 'https://integrate.api.nvidia.com/v1/chat/completions',
        'key': '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',
    }
}

# 搜索内容总结
SEARCH_RESULTS = """
1. Claude 3.7 Agent能力 (2026年2月)
- 2025年2月发布，全球首个混合推理模型
- 支持近乎实时回答+深入推理
- Claude Code命令行工具发布
- 2026年2月曾出现大规模服务中断

2. OpenAI o3/o4-mini (2025-2026)
- 2025年推出推理模型系列
- 2026年2月推出Frontier企业级AI平台
- 目标：2026年9月达到实习生级别研究助理
- 2028年3月完成独立科研项目

3. 字节跳动豆包2.0 (2026年2月)
- Pro/Lite/Mini三款通用Agent模型
- Code版深度适配编程环境
- 对标GPT-5.2和Gemini 3 Pro

4. 2026年AI Agent融资
- Q1全球超50亿美元
- 国内超100亿元人民币
"""

OFFICIALS = [
    {'name': '沈星衍', 'title': '智囊博士', 'topic': '分析AI Agent技术趋势', 'model': 'glm-4.7'},
    {'name': '苏云渺', 'title': '工部尚书', 'topic': '分析工程实现方案', 'model': 'glm-4.7'},
    {'name': '林码', 'title': '营造司正', 'topic': '分析性能优化方向', 'model': 'glm-4.7'},
]

def call_model(provider, model, messages):
    config = API_CONFIGS[provider]
    url, api_key = config['url'], config['key']
    model_map = {'glm-4.7': 'glm-4.7', 'glm-4-flash': 'glm-4-flash'}
    actual = model_map.get(model, model)
    
    start = time.time()
    try:
        resp = requests.post(url, headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}, json={'model': actual, 'messages': messages, 'max_tokens': 120}, timeout=90)
        elapsed = time.time() - start
        if resp.status_code == 200:
            r = resp.json()
            u = r.get('usage', {})
            return {'success': True, 'reply': r['choices'][0]['message']['content'], 'provider': provider, 'model': actual, 'elapsed': elapsed, 'tokens': u.get('total_tokens', 0)}
    except: pass
    return {'success': False}

def run():
    print("=" * 60)
    print("【第五轮学习】AI Agent技术进展")
    print("=" * 60)
    print()
    
    results = []
    total = 0
    
    for off in OFFICIALS:
        print(f"【{off['name']}】{off['title']} → {off['topic']}")
        
        result = call_model('火山引擎', off['model'], [
            {'role': 'system', 'content': f'你是唐朝官员{off["title"]}，用文言文简洁回复。'},
            {'role': 'user', 'content': f'根据以下AI技术动态，总结核心要点（限40字）：\n{SEARCH_RESULTS}'}
        ])
        
        if result['success']:
            print(f"  ✓ {result['provider']}/{result['model']} | {result['elapsed']:.1f}s | {result['tokens']}tokens")
            print(f"  → {result['reply']}")
            results.append({'official': off, 'result': result})
            total += result['tokens']
        print()
    
    print("=" * 60)
    print(f"【汇总】{len(results)}人 | 总Token: {total}")
    print("=" * 60)

run()
