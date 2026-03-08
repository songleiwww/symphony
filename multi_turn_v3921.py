#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青丘多轮对话能力 v3.9.21
开发多轮对话系统
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

# 4位专家开发多轮对话系统
experts = [
    {
        'name': '林思远',
        'role': '对话历史管理',
        'assign_reason': '需要管理对话历史，林思远擅长数据结构设计',
        'model': 'meta/llama-3.1-405b-instruct',
        'task': '''请作为对话历史管理专家，设计多轮对话的历史管理系统：

需求：
1. ConversationHistory类 - 对话历史管理器
   - 存储多轮对话记录
   - 支持上下文窗口
   - 自动摘要压缩

2. MessageFormatter类 - 消息格式化器
   - 格式化用户/助手消息
   - 添加元数据
   - 支持多种格式

请给出Python代码（约80行）。'''
    },
    {
        'name': '张晓明',
        'role': '对话状态追踪',
        'assign_reason': '需要追踪对话状态，张晓明擅长状态管理',
        'model': 'qwen/qwen3.5-397b-a17b',
        'task': '''请作为对话状态追踪专家，设计多轮对话的状态追踪系统：

需求：
1. ConversationState类 - 对话状态
   - 追踪当前话题
   - 记录用户意图变化
   - 管理对话阶段

2. StateManager类 - 状态管理器
   - 保存/恢复状态
   - 状态序列化
   - 状态过期处理

请给出Python代码（约80行）。'''
    },
    {
        'name': '赵心怡',
        'role': '上下文理解',
        'assign_reason': '需要理解上下文，赵心怡擅长语义理解',
        'model': 'minimaxai/minimax-m2.5',
        'task': '''请作为上下文理解专家，设计多轮对话的上下文理解系统：

需求：
1. ContextTracker类 - 上下文追踪器
   - 追踪指代词（他/她/它）
   - 理解省略信息
   - 关联历史上下文

2. ReferenceResolver类 - 指代消解器
   - 消解人称代词
   - 消解指示代词
   - 消解名词省略

请给出Python代码（约80行）。'''
    },
    {
        'name': '陈浩然',
        'role': '对话流程控制',
        'assign_reason': '需要控制对话流程，陈浩然擅长流程设计',
        'model': 'meta/llama-3.1-405b-instruct',
        'task': '''请作为对话流程控制专家，设计多轮对话的流程控制系统：

需求：
1. DialogFlowController类 - 对话流程控制器
   - 管理对话阶段
   - 处理对话跳转
   - 支持对话分支

2. TurnManager类 - 轮次管理器
   - 跟踪当前轮次
   - 管理轮次超时
   - 处理对话中断

请给出Python代码（约80行）。'''
    }
]

results = []
total_tokens = 0

print("="*60)
print("青丘多轮对话能力 v3.9.21")
print("="*60)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)
print()

for i, expert in enumerate(experts):
    print(f"【{expert['name']}】{expert['role']}")
    print(f"  分配理由: {expert['assign_reason']}")
    print("-"*40)
    
    try:
        r = requests.post(URL, headers=HEADERS, json={
            'model': expert['model'],
            'messages': [{'role': 'user', 'content': expert['task']}],
            'max_tokens': 400
        }, timeout=60)
        
        if r.status_code == 200:
            data = r.json()
            tokens = data.get('usage', {}).get('total_tokens', 0)
            total_tokens += tokens
            print(f"  Token: {tokens}, 状态: 成功")
            results.append({
                'name': expert['name'],
                'role': expert['role'],
                'assign_reason': expert['assign_reason'],
                'status': '成功',
                'tokens': tokens
            })
        else:
            print(f"  失败: {r.status_code}")
            results.append({'name': expert['name'], 'status': '失败'})
    except Exception as e:
        print(f"  异常: {str(e)[:20]}")
        results.append({'name': expert['name'], 'status': '异常'})

print()
print("="*60)
print(f"研发完成 Token: {total_tokens}")
print("="*60)

# 保存
with open('multi_turn_v3921.json', 'w', encoding='utf-8') as f:
    json.dump({
        'version': 'v3.9.21',
        'topic': '多轮对话能力',
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'total_tokens': total_tokens
    }, f, ensure_ascii=False, indent=2)

print("已保存: multi_turn_v3921.json")
