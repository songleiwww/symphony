#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
官署角色组合技能 - 真实API调用
"""
import requests
import json

# 角色配置
ROLES = {
    '陆念昭': {
        'api': 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions',
        'model': 'doubao-seed-2.0-pro',
        'key': '3b922877-3fbe-45d1-a298-53f2231c5224'
    },
    '徐浩': {
        'api': 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions',
        'model': 'deepseek-v3-2-250121',
        'key': '3b922877-3fbe-45d1-a298-53f2231c5224'
    },
    '高益': {
        'api': 'https://integrate.api.nvidia.com/v1/chat/completions',
        'model': 'deepseek-ai/deepseek-r1',
        'key': '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'
    }
}

def call_model(name, prompt):
    """调用单个模型"""
    cfg = ROLES[name]
    headers = {
        'Authorization': f'Bearer {cfg["key"]}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': cfg['model'],
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 200
    }
    
    print(f"\n【{name}】调用模型: {cfg['model']}")
    try:
        r = requests.post(cfg['api'], headers=headers, json=data, timeout=30)
        if r.status_code == 200:
            result = r.json()
            content = result['choices'][0]['message']['content']
            tokens = result.get('usage', {}).get('total_tokens', 0)
            print(f"  状态: {r.status_code}")
            print(f"  Tokens: {tokens}")
            print(f"  响应: {content[:100]}...")
            return {'status': 200, 'content': content, 'tokens': tokens}
        else:
            print(f"  错误: {r.status_code} - {r.text[:100]}")
            return {'status': r.status_code, 'error': r.text[:100]}
    except Exception as e:
        print(f"  异常: {e}")
        return {'status': 500, 'error': str(e)}

def skill_1_dialogue():
    """组合技能1: 协作对话 - 三人讨论AI未来"""
    print("\n" + "="*60)
    print("组合技能1: 协作对话 - 三人讨论AI未来")
    print("="*60)
    
    prompt = "用一句话回答：你认为2026年AI最重要的趋势是什么？"
    
    results = []
    for name in ['陆念昭', '徐浩', '高益']:
        result = call_model(name, prompt)
        results.append({'name': name, 'result': result})
    
    # 汇总
    total_tokens = sum(r['result'].get('tokens', 0) for r in results)
    success = sum(1 for r in results if r['result']['status'] == 200)
    
    print(f"\n【汇总】")
    print(f"  成功: {success}/3")
    print(f"  总Tokens: {total_tokens}")
    
    return {'skill': '协作对话', 'success': success, 'total_tokens': total_tokens, 'results': results}

def skill_2_coding():
    """组合技能2: 协作编程 - 三人完成一个简单任务"""
    print("\n" + "="*60)
    print("组合技能2: 协作编程 - 三人完成Python任务")
    print("="*60)
    
    # 陆念昭: 写函数
    r1 = call_model('陆念昭', '用Python写一个计算斐波那契数列的函数，代码简洁')
    
    # 徐浩: 代码审查
    code = "def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)"
    r2 = call_model('徐浩', f'审查这段Python代码并指出优缺点: {code}')
    
    # 高益: 优化建议
    r3 = call_model('高益', '给出Python计算斐波那契的优化建议')
    
    results = [
        {'name': '陆念昭', 'result': r1},
        {'name': '徐浩', 'result': r2},
        {'name': '高益', 'result': r3}
    ]
    
    total_tokens = sum(r['result'].get('tokens', 0) for r in results)
    success = sum(1 for r in results if r['result']['status'] == 200)
    
    print(f"\n【汇总】")
    print(f"  成功: {success}/3")
    print(f"  总Tokens: {total_tokens}")
    
    return {'skill': '协作编程', 'success': success, 'total_tokens': total_tokens, 'results': results}

def main():
    print("="*60)
    print("官署角色组合技能开发")
    print("="*60)
    
    # 执行两个组合技能
    s1 = skill_1_dialogue()
    s2 = skill_2_coding()
    
    # 总体验证
    print("\n" + "="*60)
    print("组合技能验证报告")
    print("="*60)
    print(f"技能1 ({s1['skill']}): 成功{s1['success']}/3, Tokens={s1['total_tokens']}")
    print(f"技能2 ({s2['skill']}): 成功{s2['success']}/3, Tokens={s2['total_tokens']}")
    
    total_success = s1['success'] + s2['success']
    total_tokens = s1['total_tokens'] + s2['total_tokens']
    print(f"\n总计: 成功{total_success}/6, 总Tokens={total_tokens}")
    print("="*60)

if __name__ == "__main__":
    main()
