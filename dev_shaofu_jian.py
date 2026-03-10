#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""序境少府监体质建设 - 完整系统开发"""
import requests
import json
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 少府监体质建设 - 8个核心职位
system_tasks = [
    {
        'name': '沈清弦',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '枢密使',
        'position': '少府监正职',
        'task': '''你是序境枢密使沈清弦，少府监正职。

请设计"少府监体质"的完整组织架构，要求：
1. 职位体系：正职、副职、参事、行走等
2. 职能分工：每位成员职责明确
3. 汇报关系：层级清晰
4. 决策机制：分级授权
输出JSON架构文档（150字以内）
'''
    },
    {
        'name': '苏云渺',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '工部尚书',
        'position': '建设总监',
        'task': '''你是序境工部尚书苏云渺，建设总监。

请设计"少府监体质建设"的开发规范，要求：
1. 代码规范：命名/注释/文档
2. 协作流程：评审/测试/发布
3. 质量标准：Bug率/覆盖率
4. 绩效指标：产出/质量/效率
输出开发规范文档（150字以内）
'''
    },
    {
        'name': '顾清歌',
        'model': 'THUDM/glm-4-9b-chat',
        'role': '翰林学士',
        'position': '典章大臣',
        'task': '''你是序境翰林学士顾清歌，典章大臣。

请设计"少府监典章制度"的法规体系，要求：
1. 基础法规：组织法/职责法
2. 运行制度：会议/汇报/决策
3. 考核制度：晋升/奖惩/问责
4. 保密制度：权限/审计/追责
输出典章制度文档（150字以内）
'''
    },
    {
        'name': '沈星衍',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '智囊博士',
        'position': '策略军师',
        'task': '''你是序境智囊博士沈星衍，策略军师。

请设计"少府监发展战略"的长期规划，要求：
1. 短期目标：3个月内
2. 中期目标：6个月内
3. 长期目标：1年内
4. 里程碑：关键节点
输出战略规划文档（150字以内）
'''
    },
    {
        'name': '叶轻尘',
        'model': 'Qwen/Qwen2.5-7B-Instruct',
        'role': '行走使',
        'position': '联络大臣',
        'task': '''你是序境行走使叶轻尘，联络大臣。

请设计"少府监对外联络"的协作机制，要求：
1. 内部联络：与OpenClaw各模块
2. 外部联络：与Skill生态
3. 资源协调：算力/数据/人才
4. 应急响应：故障/投诉/危机
输出联络机制文档（150字以内）
'''
    },
    {
        'name': '林码',
        'model': 'Qwen/Qwen2.5-72B-Instruct',
        'role': '营造司正',
        'position': '营造大臣',
        'task': '''你是序境营造司正林码，营造大臣。

请设计"少府监基础设施"的技术架构，要求：
1. 核心系统：调度/监控/日志
2. 数据系统：存储/分析/备份
3. 安全系统：权限/审计/容灾
4. 基础设施：计算/网络/存储
输出技术架构文档（150字以内）
'''
    },
    {
        'name': '顾至尊',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '首辅大学士',
        'position': '统筹大臣',
        'task': '''你是序境首辅大学士顾至尊，统筹大臣。

请设计"少府监体质建设"的实施路线图，要求：
1. 阶段划分：准备/建设/完善
2. 资源投入：人力/财力/时间
3. 风险管控：识别/预防/应对
4. 验收标准：功能/性能/质量
输出实施路线图（150字以内）
'''
    },
    {
        'name': '陆念昭',
        'model': 'Qwen/Qwen2.5-7B-Instruct',
        'role': '少府监',
        'position': '总监',
        'task': '''你是序境少府监陆念昭，体质建设总监。

请设计"少府监体质建设"的完整方案总结，要求：
1. 核心理念：愿景/使命/价值观
2. 建设目标：组织/制度/技术
3. 实施计划：步骤/时间/责任
4. 成功标准：指标/验收/评估
输出完整方案（150字以内）
'''
    },
]

results = []
total_tokens = 0

print('=== 少府监体质建设 ===')
print('主题：完整组织架构 + 典章制度 + 发展战略\n')

for m in system_tasks:
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
            results.append({'name': m['name'], 'role': m['role'], 'position': m['position'], 'model': m['model'].split('/')[-1], 'response': content, 'tokens': tokens, 'status': 'OK'})
            print('[OK] %s | %s | %d tokens' % (m['name'], m['position'], tokens))
        else:
            results.append({'name': m['name'], 'role': m['role'], 'position': m['position'], 'response': str(result), 'status': 'FAIL'})
            print('[FAIL] %s | %s' % (m['name'], str(result)[:30]))
    except Exception as e:
        results.append({'name': m['name'], 'role': m['role'], 'position': m['position'], 'response': str(e), 'status': 'FAIL'})
        print('[ERROR] %s | %s' % (m['name'], str(e)[:30]))
    time.sleep(0.5)

print('\n=== 建设成果汇总 ===')
for r in results:
    if r['status'] == 'OK':
        print('\n【%s】%s (%s):' % (r['name'], r['role'], r['position']))
        print(r['response'][:200])

print('\n\n总消耗: %d tokens' % total_tokens)

# 保存建设成果
with open('shaofu_jian_system.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('\n建设成果已保存: shaofu_jian_system.json')
