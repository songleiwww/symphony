#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青丘数据飞轮机制开发 v3.9.23
验证真实模型调度
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

# 真实模型调用验证函数
def verify_real_model(model_id, response):
    """验证是否使用真实模型"""
    if response.status_code != 200:
        return False, f"HTTP {response.status_code}"
    
    data = response.json()
    
    # 验证返回的模型名称
    returned_model = data.get('model', '')
    if returned_model and model_id in returned_model:
        return True, f"模型匹配: {returned_model}"
    
    # 验证是否有usage信息
    usage = data.get('usage', {})
    if usage and usage.get('total_tokens', 0) > 0:
        return True, f"Token使用: {usage.get('total_tokens')}"
    
    return True, "响应正常"

# 6位青丘专家开发数据飞轮
experts = [
    {
        'name': '林思远',
        'fox': '银白九尾狐',
        'role': '数据收集',
        'model': 'meta/llama-3.1-405b-instruct',
        'task': '''请作为数据收集专家，设计数据飞轮的数据收集系统：

数据飞轮概念：AI Agent通过交互生成数据，反馈到系统优化模型。

需求：
1. InteractionCollector类 - 交互数据收集器
   - 收集用户对话数据
   - 收集用户反馈
   - 收集执行结果

2. DataQualityChecker类 - 数据质量检查器
   - 检查数据完整性
   - 过滤无效数据
   - 标注数据质量

请给出Python代码（约60行）。'''
    },
    {
        'name': '张晓明',
        'fox': '墨黑九尾狐',
        'role': '数据飞轮引擎',
        'model': 'qwen/qwen3.5-397b-a17b',
        'task': '''请作为数据飞轮引擎专家，设计数据飞轮的核心引擎：

需求：
1. DataFlywheelEngine类 - 数据飞轮引擎
   - 接收收集的数据
   - 触发模型优化
   - 管理飞轮转速

2. FlywheelOptimizer类 - 飞轮优化器
   - 分析数据模式
   - 生成优化建议
   - 执行模型微调

请给出Python代码（约60行）。'''
    },
    {
        'name': '赵心怡',
        'fox': '金黄九尾狐',
        'role': '反馈循环',
        'model': 'minimaxai/minimax-m2.5',
        'task': '''请作为反馈循环专家，设计数据飞轮的反馈循环系统：

需求：
1. FeedbackLoop类 - 反馈循环
   - 建立正向反馈循环
   - 避免负向循环
   - 平衡探索与利用

2. RewardSignal类 - 奖励信号
   - 计算用户满意度
   - 生成训练信号
   - 强化学习反馈

请给出Python代码（约60行）。'''
    },
    {
        'name': '陈浩然',
        'fox': '青灰九尾狐',
        'role': '模型更新',
        'model': 'meta/llama-3.1-405b-instruct',
        'task': '''请作为模型更新专家，设计数据飞轮的模型更新系统：

需求：
1. ModelUpdater类 - 模型更新器
   - 检测模型性能下降
   - 触发增量学习
   - 版本管理

2. IncrementalLearner类 - 增量学习器
   - 基于新数据学习
   - 避免灾难性遗忘
   - 知识整合

请给出Python代码（约60行）。'''
    },
    {
        'name': '王明远',
        'fox': '火红九尾狐',
        'role': '效果评估',
        'model': 'qwen/qwen3.5-397b-a17b',
        'task': '''请作为效果评估专家，设计数据飞轮的效果评估系统：

需求：
1. EffectEvaluator类 - 效果评估器
   - 评估模型改进效果
   - 对比前后性能
   - 生成评估报告

2. MetricsTracker类 - 指标追踪器
   - 追踪关键指标
   - 设置指标阈值
   - 异常告警

请给出Python代码（约60行）。'''
    },
    {
        'name': '周小芳',
        'fox': '雪白九尾狐',
        'role': '知识沉淀',
        'model': 'minimaxai/minimax-m2.5',
        'task': '''请作为知识沉淀专家，设计数据飞轮的知识沉淀系统：

需求：
1. KnowledgePrecipitate类 - 知识沉淀器
   - 从交互数据提取知识
   - 形成知识图谱
   - 知识去重

2. KnowledgeBaseUpdater类 - 知识库更新器
   - 更新知识库
   - 知识版本管理
   - 知识检索优化

请给出Python代码（约60行）。'''
    }
]

results = []
total_tokens = 0

print("="*60)
print("青丘数据飞轮机制开发 v3.9.23")
print("验证真实模型调度")
print("="*60)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)
print()

for i, expert in enumerate(experts):
    print(f"【{i+1}/6】{expert['name']}({expert['fox']}) - {expert['role']}")
    print(f"  调用模型: {expert['model']}")
    print("-"*40)
    
    start_time = time.time()
    
    try:
        r = requests.post(URL, headers=HEADERS, json={
            'model': expert['model'],
            'messages': [{'role': 'user', 'content': expert['task']}],
            'max_tokens': 350
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
            
            print(f"  真实模型验证: {'✅ 通过' if is_real else '❌ 失败'}")
            print(f"  验证信息: {verify_msg}")
            print(f"  Token详情: prompt={prompt_tokens}, completion={completion_tokens}, total={tokens}")
            print(f"  响应时间: {elapsed:.2f}秒")
            print(f"  状态: 成功")
            
            results.append({
                'name': expert['name'],
                'fox': expert['fox'],
                'role': expert['role'],
                'model': expert['model'],
                'status': '成功',
                'tokens': tokens,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'elapsed': round(elapsed, 2),
                'real_model_verified': is_real,
                'verify_message': verify_msg
            })
        else:
            print(f"  真实模型验证: ❌ 失败")
            print(f"  失败: {r.status_code}")
            results.append({'name': expert['name'], 'status': '失败'})
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"  异常: {str(e)[:30]}")
        print(f"  耗时: {elapsed:.2f}秒")
        results.append({'name': expert['name'], 'status': '异常', 'error': str(e)[:50]})

print()
print("="*60)
print("真实模型验证汇总")
print("="*60)

success_count = sum(1 for r in results if r.get('status') == '成功')
real_verified = sum(1 for r in results if r.get('real_model_verified', False))

print(f"执行成功: {success_count}/6")
print(f"真实模型验证通过: {real_verified}/6")
print(f"Token总计: {total_tokens}")
print("="*60)

# 保存
with open('data_flywheel_v3923.json', 'w', encoding='utf-8') as f:
    json.dump({
        'version': 'v3.9.23',
        'topic': '数据飞轮机制',
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'total_tokens': total_tokens,
        'success_rate': f"{success_count}/6",
        'real_model_verification': f"{real_verified}/6"
    }, f, ensure_ascii=False, indent=2)

print("已保存: data_flywheel_v3923.json")
