#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""序境运行时监控系统开发 - 6人并行"""
import requests
import json
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 运行时监控系统开发任务
dev_tasks = [
    {
        'name': '沈清弦',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '枢密使',
        'task': '''你是序境枢密使沈清弦，架构总设计师。

请设计"序境运行时监控系统"的系统架构，要求：
1. 模块结构：监控面板、数据采集、告警模块
2. 数据流：采集→存储→分析→展示
3. 实时性：秒级数据刷新
4. 扩展性：支持插件化监控项
输出架构设计JSON（100字以内）
'''
    },
    {
        'name': '苏云渺',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '工部尚书',
        'task': '''你是序境工部尚书苏云渺，代码主工程师。

请设计"监控数据采集模块"的Python代码结构：
1. 采集项：模型调用、响应时间、Token消耗、错误率
2. 采集方式：定时采集、事件触发
3. 存储：内存缓存、文件持久化
4. 接口：RESTful API
输出类定义代码（100字以内）
'''
    },
    {
        'name': '顾清歌',
        'model': 'THUDM/glm-4-9b-chat',
        'role': '翰林学士',
        'task': '''你是序境翰林学士顾清歌，规则知识库。

请设计"告警规则引擎"的配置规则：
1. 告警级别：INFO/WARNING/ERROR/CRITICAL
2. 触发条件：响应超时、错误率高、资源耗尽
3. 告警动作：日志、消息、邮件
4. 阈值配置：可自定义阈值
输出告警规则JSON（100字以内）
'''
    },
    {
        'name': '沈星衍',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '智囊博士',
        'task': '''你是序境智囊博士沈星衍，策略军师。

请设计"状态展示面板"的数据展示方案：
1. 仪表盘：核心指标一目了然
2. 实时图表：模型响应时间趋势
3. 成员状态：在线/忙碌/离线
4. 历史记录：最近N次调用详情
输出展示方案（80字以内）
'''
    },
    {
        'name': '叶轻尘',
        'model': 'Qwen/Qwen2.5-7B-Instruct',
        'role': '行走使',
        'task': '''你是序境行走使叶轻尘，轻量执行者。

请设计"轻量监控探针"的实现方案：
1. 侵入性：最小化性能影响
2. 资源占用：CPU<1%, 内存<10MB
3. 采集频率：可配置
4. 异常检测：自动识别异常模式
输出探针设计（80字以内）
'''
    },
    {
        'name': '林码',
        'model': 'Qwen/Qwen2.5-72B-Instruct',
        'role': '营造司正',
        'task': '''你是序境营造司正林码，代码实现者。

请设计"symphony.py独立入口"的集成方案：
1. 入口函数：run_symphony(task, mode='auto')
2. 监控钩子：任务开始/结束/错误回调
3. 状态导出：get_status()返回实时状态
4. 插件接口：register_monitor(plugin)
输出集成代码框架（100字以内）
'''
    },
]

results = []
total_tokens = 0

print('=== 序境运行时监控系统开发 ===')
print('主题：symphony.py独立入口 + 实时监控\n')

for m in dev_tasks:
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    data = {
        'model': m['model'],
        'messages': [{'role': 'user', 'content': m['task']}],
        'max_tokens': 300,
        'temperature': 0.7
    }
    try:
        r = requests.post(API_URL, headers=headers, json=data, timeout=60)
        result = r.json()
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message'].get('content', '无响应')
            tokens = result.get('usage', {}).get('total_tokens', 0)
            total_tokens += tokens
            results.append({'name': m['name'], 'role': m['role'], 'model': m['model'].split('/')[-1], 'response': content, 'tokens': tokens, 'status': 'OK'})
            print('[OK] %s | %s | %d tokens' % (m['name'], m['role'], tokens))
        else:
            results.append({'name': m['name'], 'role': m['role'], 'response': str(result), 'status': 'FAIL'})
            print('[FAIL] %s' % m['name'])
    except Exception as e:
        results.append({'name': m['name'], 'role': m['role'], 'response': str(e), 'status': 'FAIL'})
        print('[ERROR] %s' % m['name'])
    time.sleep(0.5)

print('\n=== 开发成果汇总 ===')
for r in results:
    if r['status'] == 'OK':
        print('\n【%s】%s:' % (r['name'], r['role']))
        print(r['response'][:200])

print('\n\n总消耗: %d tokens' % total_tokens)

# 保存开发成果
with open('monitor_system_dev.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('\n开发成果已保存: monitor_system_dev.json')
