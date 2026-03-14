#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""序境模块化改进开发 - 8人并行"""
import requests
import json
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 8人开发任务 - 针对7个问题
dev_tasks = [
    {
        'name': '沈清弦',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '枢密使',
        'task': '''你是序境枢密使沈清弦，负责模块化改进。

请为序境symphony.py设计模块化改进方案：
1. 模块解耦：各功能独立成模块
2. 接口规范：统一API接口
3. 配置管理：外部配置加载
4. 插件机制：支持动态加载

输出改进方案JSON（100字以内）
'''
    },
    {
        'name': '苏云渺',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '工部尚书',
        'task': '''你是序境工部尚书苏云渺，负责可维护性改进。

请设计可维护性提升方案：
1. 代码结构：清晰分层
2. 注释规范：每个函数有文档
3. 错误处理：统一异常处理
4. 日志规范：分级日志输出

输出改进方案JSON（100字以内）
'''
    },
    {
        'name': '顾清歌',
        'model': 'THUDM/glm-4-9b-chat',
        'role': '翰林学士',
        'task': '''你是序境翰林学士顾清歌，负责个性化服务。

请设计个性化服务模块：
1. 用户画像：记录用户偏好
2. 习惯学习：学习用户习惯
3. 响应适配：根据用户调整
4. 历史记忆：记住用户历史

输出个性化模块设计JSON（100字以内）
'''
    },
    {
        'name': '沈星衍',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '智囊博士',
        'task': '''你是序境智囊博士沈星衍，负责意图理解增强。

请设计意图理解增强方案：
1. 意图分类：识别用户意图类型
2. 关键提取：提取关键信息
3. 上下文理解：结合上下文
4. 模糊处理：处理模糊表达

输出意图理解模块JSON（100字以内）
'''
    },
    {
        'name': '叶轻尘',
        'model': 'Qwen/Qwen2.5-7B-Instruct',
        'role': '行走使',
        'task': '''你是序境行走使叶轻尘，负责响应速度优化。

请设计响应速度优化方案：
1. 缓存机制：常用数据缓存
2. 异步处理：非阻塞执行
3. 预加载：预测性加载
4. 简化路径：最短执行路径

输出优化方案JSON（100字以内）
'''
    },
    {
        'name': '林码',
        'model': 'Qwen/Qwen2.5-72B-Instruct',
        'role': '营造司正',
        'task': '''你是序境营造司正林码，负责并发处理改进。

请设计并发处理改进方案：
1. 线程池：任务队列管理
2. 资源限制：并发数控制
3. 状态同步：线程安全
4. 故障恢复：异常后重试

输出并发方案JSON（100字以内）
'''
    },
    {
        'name': '顾至尊',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '首辅大学士',
        'task': '''你是序境首辅大学士顾至尊，负责扩展性设计。

请设计扩展性提升方案：
1. 水平扩展：支持多实例
2. 垂直扩展：支持更大资源
3. 功能扩展：插件化功能
4. 接口扩展：预留扩展点

输出扩展性方案JSON（100字以内）
'''
    },
    {
        'name': '陆念昭',
        'model': 'Qwen/Qwen2.5-7B-Instruct',
        'role': '少府监',
        'task': '''你是序境少府监陆念昭，负责开发效率提升。

请设计开发效率提升方案：
1. 模板生成：代码模板自动生成
2. 调试工具：内置调试功能
3. 测试支持：单元测试框架
4. 文档生成：自动生成文档

输出效率提升方案JSON（100字以内）
'''
    },
]

results = []
total_tokens = 0

print('=== 序境模块化改进开发 ===')
print('主题：7大问题解决方案\n')

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
with open('modular_improvement.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('\n开发成果已保存: modular_improvement.json')
