# -*- coding: utf-8 -*-
"""
序境系统 - 少府监全员开会
序境系统内核完善优化研发计划
使用序境调度系统进行
"""
import requests
import time
import json
import sys
import io
import sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API配置
API_CONFIGS = {
    '火山引擎': {
        'url': 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions',
        'key': '3b922877-3fbe-45d1-a298-53f2231c5224',
    },
    'NVIDIA': {
        'url': 'https://integrate.api.nvidia.com/v1/chat/completions',
        'key': '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',
    },
    '硅基流动': {
        'url': 'https://api.siliconflow.cn/v1/chat/completions',
        'key': 'sk-dtjmdjzmxwqqgkcwhkkkvhhhfdlgfgypnnctvhykfvtlgxlu',
    }
}

# 模型映射
MODEL_MAP = {
    'glm-4.7': {'火山引擎': 'glm-4.7', 'NVIDIA': 'mistralai/mixtral-8x7b-instruct-v0.1'},
    'glm-4-flash': {'火山引擎': 'glm-4-flash', 'NVIDIA': 'mistralai/mixtral-8x7b-instruct-v0.1'},
    'Qwen2.5-14B': {'火山引擎': 'glm-4.7', 'NVIDIA': 'Qwen/Qwen2.5-14B-Instruct', '硅基流动': 'Qwen/Qwen2.5-14B-Instruct'}
}

def get_all_officials():
    """从数据库获取所有官属"""
    db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, 姓名, 官职, 职务, 模型名称, 模型服务商 FROM 官属角色表 WHERE 状态='正常' OR 状态 IS NULL OR 状态=''")
    rows = cursor.fetchall()
    conn.close()
    return [{'id': r[0], 'name': r[1], 'title': r[2], 'duty': r[3], 'model': r[4], 'provider': r[5]} for r in rows]

def call_model(provider, model, messages, max_tokens=150):
    """调用模型API"""
    if provider not in API_CONFIGS:
        return {'success': False, 'error': f'Unknown provider: {provider}'}
    
    config = API_CONFIGS[provider]
    url = config['url']
    api_key = config['key']
    
    # 获取实际模型名
    actual_model = MODEL_MAP.get(model, {}).get(provider, model)
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": actual_model, "messages": messages, "max_tokens": max_tokens}
    
    start = time.time()
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=120)
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            result = resp.json()
            usage = result.get('usage', {})
            return {
                'success': True,
                'reply': result['choices'][0]['message']['content'],
                'provider': provider,
                'model': actual_model,
                'elapsed': elapsed,
                'tokens': {
                    'prompt': usage.get('prompt_tokens', 0),
                    'completion': usage.get('completion_tokens', 0),
                    'total': usage.get('total_tokens', 0)
                }
            }
        else:
            return {'success': False, 'error': f"HTTP {resp.status_code}", 'provider': provider}
    except Exception as e:
        return {'success': False, 'error': str(e), 'provider': provider}

def run_meeting():
    print("=" * 80)
    print("【少府监全员会议】序境系统内核完善优化研发计划")
    print("调度系统：序境调度引擎 | 会议主题：提升序境系统内核")
    print("=" * 80)
    print()
    
    # 获取所有官员
    officials = get_all_officials()
    print(f"应到官员: {len(officials)}人\n")
    
    results = []
    total_tokens = 0
    total_prompt = 0
    total_completion = 0
    success_count = 0
    fail_count = 0
    
    # 会议主题 - 根据官员职责分配
    topic_template = "你是{title}，职责{duty}。请为序境系统内核优化提出1-2个具体建议，限20字内。"
    
    for i, official in enumerate(officials):
        print(f"[{i+1}/{len(officials)}] 【{official['name']}】({official['title']}) → {official['provider']}/{official['model']}")
        
        system_prompt = f"你是唐朝官员{official['title']}，用文言文简洁回复。"
        user_prompt = topic_template.format(title=official['title'], duty=official['duty'])
        
        # 优先使用指定的provider
        result = call_model(official['provider'], official['model'], [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        # 失败则尝试其他provider
        if not result['success']:
            print(f"  {official['provider']} 失败 → 尝试其他...")
            for alt_provider in ['火山引擎', 'NVIDIA', '硅基流动']:
                if alt_provider != official['provider']:
                    result = call_model(alt_provider, official['model'], [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ])
                    if result['success']:
                        print(f"  ✓ 切换到 {alt_provider}")
                        break
        
        if result['success']:
            print(f"  ✓ {result['provider']}/{result['model']} | {result['elapsed']:.1f}秒 | tokens: {result['tokens']['total']}")
            print(f"  → {result['reply'][:50]}...")
            results.append({
                'official': official,
                'result': result
            })
            total_tokens += result['tokens']['total']
            total_prompt += result['tokens']['prompt']
            total_completion += result['tokens']['completion']
            success_count += 1
        else:
            print(f"  ✗ {result.get('error', 'Unknown error')}")
            fail_count += 1
        print()
    
    # 汇总报告
    print("=" * 80)
    print("【会议汇总 - 序境系统内核完善优化研发计划】")
    print("=" * 80)
    print(f"参会: {success_count}/{len(officials)}人 | 成功: {success_count} | 失败: {fail_count}")
    print(f"总Token: {total_tokens} (prompt: {total_prompt}, completion: {total_completion})")
    print()
    
    # 详细表格
    print("| # | 官员 | 官职 | 模型 | 服务商 | Tokens | 耗时 |")
    print("|---|------|------|------|--------|--------|------|")
    for i, r in enumerate(results):
        o = r['official']
        res = r['result']
        print(f"| {i+1} | {o['name']} | {o['title']} | {o['model']} | {o['provider']} | {res['tokens']['total']} | {res['elapsed']:.1f}s |")
    
    # 按模型统计
    print()
    print("【模型使用统计】")
    model_stats = {}
    for r in results:
        m = r['official']['model']
        p = r['official']['provider']
        key = f"{m}({p})"
        if key not in model_stats:
            model_stats[key] = {'count': 0, 'tokens': 0}
        model_stats[key]['count'] += 1
        model_stats[key]['tokens'] += r['result']['tokens']['total']
    
    for k, v in sorted(model_stats.items(), key=lambda x: x[1]['tokens'], reverse=True):
        print(f"  {k}: {v['count']}次, {v['tokens']}tokens")
    
    print()
    print("=" * 80)
    print("【研发建议汇总】")
    print("=" * 80)
    for r in results:
        o = r['official']
        reply = r['result']['reply']
        print(f"• {o['name']}({o['title']}): {reply}")
    
    return results

if __name__ == "__main__":
    run_meeting()
