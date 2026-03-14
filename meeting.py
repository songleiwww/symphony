# -*- coding: utf-8 -*-
"""
序境系统 - 少府监全员开会 (增强版)
"""
import requests, time, json
import io
import sys
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

MODEL_MAP = {
    'glm-4.7': {'火山引擎': 'glm-4.7', 'NVIDIA': 'mistralai/mixtral-8x7b-instruct-v0.1'},
    'glm-4-flash': {'火山引擎': 'glm-4-flash', 'NVIDIA': 'mistralai/mixtral-8x7b-instruct-v0.1'},
    'Qwen2.5-14B': {'火山引擎': 'glm-4.7', 'NVIDIA': 'Qwen/Qwen2.5-14B-Instruct'}
}

MEETING_ATTENDEES = [
    {'id': 'evolve_002', 'name': '陆念昭', 'title': '少府监', 'office': '少府监本部', 'topic': '总体统筹与调度优化', 'model': 'glm-4.7'},
    {'id': 'evolve_001', 'name': '沈清弦', 'title': '枢密使', 'office': '枢密院', 'topic': '架构设计与安全审查', 'model': 'glm-4.7'},
    {'id': 'evolve_003', 'name': '苏云渺', 'title': '工部尚书', 'office': '工部', 'topic': '并发处理与性能优化', 'model': 'Qwen2.5-14B'},
    {'id': 'evolve_006', 'name': '沈星衍', 'title': '智囊博士', 'office': '枢密院', 'topic': '策略规划与意图理解', 'model': 'Qwen2.5-14B'},
    {'id': 'evolve_004', 'name': '顾清歌', 'title': '翰林学士', 'office': '翰林院', 'topic': '规则制定与文化传承', 'model': 'glm-4-flash'},
    {'id': 'evolve_008', 'name': '林码', 'title': '营造司正', 'office': '工部', 'topic': 'GPU加速与工程实现', 'model': 'Qwen2.5-14B'},
]

def call_model(provider, model, messages):
    config = API_CONFIGS[provider]
    url = config['url']
    api_key = config['key']
    actual_model = MODEL_MAP.get(model, {}).get(provider, model)
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": actual_model, "messages": messages, "max_tokens": 150}
    
    start = time.time()
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=90)
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            result = resp.json()
            usage = result.get('usage', {})
            return {'success': True, 'reply': result['choices'][0]['message']['content'], 'provider': provider, 'model': actual_model, 'elapsed': elapsed, 'tokens': {'prompt': usage.get('prompt_tokens', 0), 'completion': usage.get('completion_tokens', 0), 'total': usage.get('total_tokens', 0)}}
        return {'success': False, 'error': f"HTTP {resp.status_code}", 'provider': provider}
    except Exception as e:
        return {'success': False, 'error': str(e), 'provider': provider}

def run_meeting():
    print("=" * 70)
    print("【少府监全员会议】序境系统内核完善优化研发计划")
    print("=" * 70)
    print()
    
    results = []
    total_tokens = 0
    
    for official in MEETING_ATTENDEES:
        print(f"【{official['name']}】({official['office']}) → {official['topic']}")
        
        system_prompt = f"你是唐朝官员{official['title']}，用文言文简洁回复。"
        user_prompt = f"主题：{official['topic']}。请提出具体改进建议，限30字。"
        
        # 尝试火山引擎
        result = call_model('火山引擎', official['model'], [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        # 失败则尝试NVIDIA
        if not result['success']:
            print(f"  火山引擎失败 → 尝试NVIDIA...")
            result = call_model('NVIDIA', official['model'], [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
        
        if result['success']:
            print(f"  ✓ {result['provider']}/{result['model']} | {result['elapsed']:.1f}秒 | {result['tokens']['total']}tokens")
            print(f"  → {result['reply']}")
            results.append({'official': official, 'result': result})
            total_tokens += result['tokens']['total']
        else:
            print(f"  ✗ {result.get('error')}")
        print()
    
    # 汇总
    print("=" * 70)
    print("【会议汇总】")
    print("=" * 70)
    print(f"参会: {len(results)}/{len(MEETING_ATTENDEES)}人 | 总Token: {total_tokens}")
    print()
    print("| 官员 | 官署 | 话题 | 模型 | Tokens |")
    print("|------|------|------|------|--------|")
    for r in results:
        o = r['official']
        res = r['result']
        print(f"| {o['name']} | {o['office']} | {o['topic']} | {res['model']} | {res['tokens']['total']} |")
    
    return results

run_meeting()
