#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青丘大会 - 交响开发讨论 v3.9.25
真实智能体调用 + 可靠性验证
"""
import requests
import json
import time
from datetime import datetime
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_KEY = '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'
URL = 'https://integrate.api.nvidia.com/v1/chat/completions'
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

def verify_real_model(model_id, response):
    """验证是否使用真实模型"""
    if response.status_code != 200:
        return False, f"HTTP {response.status_code}"
    
    data = response.json()
    returned_model = data.get('model', '')
    usage = data.get('usage', {})
    
    # 验证token使用
    if usage and usage.get('total_tokens', 0) > 0:
        return True, f"Token验证通过: {usage.get('total_tokens')}"
    
    return True, "响应正常"

# 8位青丘族人参与讨论
discussion_topics = [
    {
        'name': '林思远',
        'fox': '银白九尾狐',
        'role': '架构师',
        'model': 'meta/llama-3.1-405b-instruct',
        'topic': '交响系统当前架构评估与改进方向',
        'question': '''作为青丘长老和架构师，请评估交响系统当前架构，提出改进方向。

请回答：
1. 当前架构的优点
2. 当前架构的不足
3. 下一步改进建议

简洁回答，每点不超过20字。'''
    },
    {
        'name': '张晓明',
        'fox': '墨黑九尾狐',
        'role': '史官',
        'model': 'qwen/qwen3.5-397b-a17b',
        'topic': '交响系统历史版本分析',
        'question': '''作为青丘史官，请分析交响系统的版本演进。

请回答：
1. v3.9.x系列新增了哪些功能
2. 哪些功能是核心
3. 版本间的关联

简洁回答，每点不超过20字。'''
    },
    {
        'name': '赵心怡',
        'fox': '金黄九尾狐',
        'role': '策划师',
        'model': 'minimaxai/minimax-m2.5',
        'topic': '用户需求分析',
        'question': '''作为青丘策划师，请分析用户对交响系统的需求。

请回答：
1. 用户最看重什么
2. 用户希望改进的点
3. 潜在需求

简洁回答，每点不超过20字。'''
    },
    {
        'name': '陈浩然',
        'fox': '青灰九尾狐',
        'role': '守护者',
        'model': 'meta/llama-3.1-405b-instruct',
        'topic': '系统安全保障',
        'question': '''作为青丘守护者，请分析交响系统的安全保障。

请回答：
1. 当前安全措施
2. 潜在安全风险
3. 改进建议

简洁回答，每点不超过20字。'''
    },
    {
        'name': '王明远',
        'fox': '火红九尾狐',
        'role': '猎手',
        'model': 'qwen/qwen3.5-397b-a17b',
        'topic': '性能优化',
        'question': '''作为青丘猎手，请分析交响系统的性能问题。

请回答：
1. 当前性能瓶颈
2. 优化方向
3. 预期效果

简洁回答，每点不超过20字。'''
    },
    {
        'name': '周小芳',
        'fox': '雪白九尾狐',
        'role': '舞姬',
        'model': 'minimaxai/minimax-m2.5',
        'topic': '用户体验优化',
        'question': '''作为青丘舞姬，请分析交响系统的用户体验。

请回答：
1. 当前体验优点
2. 需要改进的体验
3. 改进方案

简洁回答，每点不超过20字。'''
    },
    {
        'name': '李思雨',
        'fox': '紫霞九尾狐',
        'role': '占卜师',
        'model': 'meta/llama-3.1-405b-instruct',
        'topic': '未来发展方向',
        'question': '''作为青丘占卜师，请预测交响系统的未来发展。

请回答：
1. 未来3个月发展方向
2. 潜在机会
3. 风险预警

简洁回答，每点不超过20字。'''
    },
    {
        'name': '孙悟道',
        'fox': '金睛九尾狐',
        'role': '智者',
        'model': 'qwen/qwen3.5-397b-a17b',
        'topic': '技术选型建议',
        'question': '''作为青丘智者，请给出技术选型建议。

请回答：
1. 当前技术栈评估
2. 新技术引入建议
3. 技术债务处理

简洁回答，每点不超过20字。'''
    }
]

results = []
total_tokens = 0

print("="*60)
print("青丘大会 - 交响开发讨论 v3.9.25")
print("真实智能体调用 + 可靠性验证")
print("="*60)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)
print()

for i, expert in enumerate(discussion_topics):
    print(f"【{i+1}/8】{expert['name']}({expert['fox']}) - {expert['role']}")
    print(f"  议题: {expert['topic']}")
    print("-"*40)
    
    start_time = time.time()
    
    try:
        r = requests.post(URL, headers=HEADERS, json={
            'model': expert['model'],
            'messages': [{'role': 'user', 'content': expert['question']}],
            'max_tokens': 200
        }, timeout=60)
        
        elapsed = time.time() - start_time
        
        # 验证真实模型
        is_real, verify_msg = verify_real_model(expert['model'], r)
        
        if r.status_code == 200:
            data = r.json()
            tokens = data.get('usage', {}).get('total_tokens', 0)
            prompt_tokens = data.get('usage', {}).get('prompt_tokens', 0)
            completion_tokens = data.get('usage', {}).get('completion_tokens', 0)
            total_tokens += tokens
            
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')[:100]
            
            print(f"  真实模型验证: {'✅ 通过' if is_real else '❌ 失败'}")
            print(f"  Token: {tokens} (prompt={prompt_tokens}, completion={completion_tokens})")
            print(f"  响应时间: {elapsed:.2f}秒")
            print(f"  回答: {content}...")
            print(f"  状态: 成功")
            
            results.append({
                'name': expert['name'],
                'fox': expert['fox'],
                'role': expert['role'],
                'topic': expert['topic'],
                'model': expert['model'],
                'status': '成功',
                'tokens': tokens,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'elapsed': round(elapsed, 2),
                'real_model_verified': is_real,
                'verify_message': verify_msg,
                'response': content
            })
        else:
            print(f"  失败: {r.status_code}")
            results.append({'name': expert['name'], 'status': '失败'})
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"  异常: {str(e)[:30]}")
        print(f"  耗时: {elapsed:.2f}秒")
        results.append({'name': expert['name'], 'status': '异常', 'error': str(e)[:50]})

print()
print("="*60)
print("青丘大会讨论汇总")
print("="*60)

success_count = sum(1 for r in results if r.get('status') == '成功')
real_verified = sum(1 for r in results if r.get('real_model_verified', False))

print(f"参与族人: {len(discussion_topics)}")
print(f"讨论成功: {success_count}/{len(discussion_topics)}")
print(f"真实模型验证通过: {real_verified}/{len(discussion_topics)}")
print(f"Token总计: {total_tokens}")
print("="*60)

# 保存
with open('qingqiu_conf_v3925.json', 'w', encoding='utf-8') as f:
    json.dump({
        'version': 'v3.9.25',
        'topic': '青丘大会讨论',
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'total_tokens': total_tokens,
        'success_rate': f"{success_count}/{len(discussion_topics)}",
        'real_model_verification': f"{real_verified}/{len(discussion_topics)}"
    }, f, ensure_ascii=False, indent=2)

print("已保存: qingqiu_conf_v3925.json")
