#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""序境主力多人开发 - 主动被动应答系统"""
import requests
import json
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 6位核心成员，完整开发任务
dev_tasks = [
    {
        'name': '沈清弦',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '枢密使',
        'title': '架构总设计师',
        'task': '''你是序境枢密使沈清弦，架构总设计师。

请为序境"主动被动应答系统"设计完整架构，要求：
1. 系统层级：父级(OpenClaw) → 序境中枢 → 6成员
2. 通信协议：同步/异步双通道
3. 触发机制：主动感知 + 被动响应
4. 状态管理：在线/忙碌/离线三态
5. 输出JSON架构文档（150字以内）
'''
    },
    {
        'name': '苏云渺',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '工部尚书',
        'title': '代码主工程师',
        'task': '''你是序境工部尚书苏云渺，代码主工程师。

请设计"主动被动应答模块"的Python类结构，要求：
1. 基类：BaseResponder（响应器基类）
2. 子类：ActiveResponder（主动响应）, PassiveResponder（被动响应）
3. 交互方法：handle_parent_call(), handle_peer_call(), handle_subagent_call()
4. 执行方法：immediate_execute(task)
5. 输出类定义代码（150字以内）
'''
    },
    {
        'name': '顾清歌',
        'model': 'THUDM/glm-4-9b-chat',
        'role': '翰林学士',
        'title': '规则知识库',
        'task': '''你是序境翰林学士顾清歌，规则知识库。

请设计"应答规则引擎"的规则配置，要求：
1. 被动规则：关键词匹配、上下文识别、意图分类
2. 主动规则：困难检测、沉默感知、情绪分析
3. 交互规则：父子通信、同级协作、子级调度
4. 紧急规则：优先级插队、强制中断、任务转移
5. 输出JSON规则配置（150字以内）
'''
    },
    {
        'name': '沈星衍',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '智囊博士',
        'title': '策略军师',
        'task': '''你是序境智囊博士沈星衍，策略军师。

请设计"智能调度策略"的决策逻辑，要求：
1. 任务分类：简单/复杂/紧急/长期
2. 模型选择：根据任务类型 + 成员状态 + 历史表现
3. 负载均衡：避免单成员过载
4. 故障转移：主失败切备用
5. 输出策略伪代码（150字以内）
'''
    },
    {
        'name': '叶轻尘',
        'model': 'Qwen/Qwen2.5-7B-Instruct',
        'role': '行走使',
        'title': '轻量执行者',
        'task': '''你是序境行走使叶轻尘，轻量执行者。

请设计"即时执行引擎"的执行流程，要求：
1. 任务解析：提取指令、参数、目标
2. 安全校验：权限检查、风险评估
3. 快速执行：优先队列、超时控制
4. 结果回传：状态同步、结果汇总
5. 输出执行流程图（100字以内）
'''
    },
    {
        'name': '林码',
        'model': 'Qwen/Qwen2.5-72B-Instruct',
        'role': '营造司正',
        'title': '代码实现者',
        'task': '''你是序境营造司正林码，代码实现者。

请设计"Skill生态适配层"的集成方案，要求：
1. OpenClaw Skill格式兼容
2. 描述文件规范（name, trigger, action, description）
3. 生命周期管理（load/unload/execute）
4. 依赖注入机制
5. 输出适配层接口（150字以内）
'''
    },
]

results = []
total_tokens = 0

print('=== 序境主力多人开发 ===')
print('主题：主动被动应答系统 + Skill生态适配\n')

for m in dev_tasks:
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    data = {
        'model': m['model'],
        'messages': [{'role': 'user', 'content': m['task']}],
        'max_tokens': 400,
        'temperature': 0.7
    }
    try:
        r = requests.post(API_URL, headers=headers, json=data, timeout=60)
        result = r.json()
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message'].get('content', '无响应')
            tokens = result.get('usage', {}).get('total_tokens', 0)
            total_tokens += tokens
            results.append({'name': m['name'], 'role': m['role'], 'title': m['title'], 'model': m['model'].split('/')[-1], 'response': content, 'tokens': tokens, 'status': 'OK'})
            print('[OK] %s | %s | %d tokens' % (m['name'], m['title'], tokens))
        else:
            results.append({'name': m['name'], 'role': m['role'], 'title': m['title'], 'response': str(result), 'status': 'FAIL'})
            print('[FAIL] %s | %s' % (m['name'], str(result)[:30]))
    except Exception as e:
        results.append({'name': m['name'], 'role': m['role'], 'title': m['title'], 'response': str(e), 'status': 'FAIL'})
        print('[ERROR] %s | %s' % (m['name'], str(e)[:30]))
    time.sleep(0.5)

print('\n=== 开发成果汇总 ===')
for r in results:
    if r['status'] == 'OK':
        print('\n【%s】%s (%s):' % (r['name'], r['role'], r['title']))
        print(r['response'][:250])

print('\n\n总消耗: %d tokens' % total_tokens)

# 保存开发成果
with open('multi_responder_dev.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('\n开发成果已保存: multi_responder_dev.json')
