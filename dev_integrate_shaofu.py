#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""少府监体质建设整合 - 第二阶段"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 读取建设成果
with open('shaofu_jian_system.json', 'r', encoding='utf-8') as f:
    dev_results = json.load(f)

# 整合任务
integration_task = {
    'name': '陆念昭',
    'model': 'Qwen/Qwen2.5-14B-Instruct',
    'task': '''你是序境少府监陆念昭，负责体质建设整合。

请根据以下8位成员的建设成果，生成一个完整的"少府监体质建设"实施文档。

### 成员成果：

1. 沈清弦(枢密使) - 组织架构：
%s

2. 苏云渺(工部尚书) - 开发规范：
%s

3. 顾清歌(翰林学士) - 典章制度：
%s

4. 沈星衍(智囊博士) - 发展战略：
%s

5. 叶轻尘(行走使) - 联络机制：
%s

6. 林码(营造司正) - 技术架构：
%s

7. 顾至尊(首辅大学士) - 实施路线图：
%s

8. 陆念昭(少府监) - 方案总结：
%s

### 要求：
1. 生成完整的Markdown实施文档"少府监体质建设方案.md"
2. 包含：愿景、架构、制度、技术、实施、验收
3. 格式规范，适合飞书阅读
4. 输出文档内容，不要代码。
''' % (
        dev_results[0]['response'][:500],
        dev_results[1]['response'][:400],
        dev_results[2]['response'][:500],
        dev_results[3]['response'][:400],
        dev_results[4]['response'][:400],
        dev_results[5]['response'][:500],
        dev_results[6]['response'][:400],
        dev_results[7]['response'][:400],
    )
}

headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
data = {
    'model': integration_task['model'],
    'messages': [{'role': 'user', 'content': integration_task['task']}],
    'max_tokens': 3000,
    'temperature': 0.7
}

print('=== 少府监体质建设整合 - 第二阶段 ===\n')
print('任务：整合8位成员成果，生成完整实施文档\n')

try:
    r = requests.post(API_URL, headers=headers, json=data, timeout=180)
    result = r.json()
    if 'choices' in result and len(result['choices']) > 0:
        content = result['choices'][0]['message'].get('content', '')
        tokens = result.get('usage', {}).get('total_tokens', 0)
        
        print('[OK] 文档生成成功 | %d tokens\n' % tokens)
        
        # 保存文档
        with open('少府监体质建设方案.md', 'w', encoding='utf-8') as f:
            f.write(content)
        print('文档已保存: 少府监体质建设方案.md')
        
        # 显示预览
        print('\n=== 文档预览（前100行）===')
        lines = content.split('\n')[:100]
        for line in lines:
            print(line)
        
    else:
        print('[FAIL] %s' % str(result))
except Exception as e:
    print('[ERROR] %s' % str(e))
