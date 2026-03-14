#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""序境运行时监控系统整合 - 第二阶段"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 读取开发成果
with open('monitor_system_dev.json', 'r', encoding='utf-8') as f:
    dev_results = json.load(f)

# 整合任务
integration_task = {
    'name': '林码',
    'model': 'Qwen/Qwen2.5-72B-Instruct',
    'task': '''你是序境营造司正林码，负责代码整合。

请根据以下6位成员的成果，生成完整的"symphony.py"独立入口文件，包含运行时监控功能。

### 成员成果：

1. 沈清弦(枢密使) - 架构设计：
%s

2. 苏云渺(工部尚书) - 数据采集：
%s

3. 顾清歌(翰林学士) - 告警规则：
%s

4. 沈星衍(智囊博士) - 状态展示：
%s

5. 叶轻尘(行走使) - 监控探针：
%s

6. 林码(营造司正) - 入口集成：
%s

### 要求：
1. 生成完整的Python模块"symphony.py"
2. 包含：Symphony类、MonitorCollector类、AlertEngine类、get_status()函数
3. 支持：run_symphony(task)作为独立入口
4. 监控：模型调用、响应时间、Token消耗、成员状态
5. 代码可直接运行，包含完整注释
6. 输出Python代码即可。
''' % (
        dev_results[0]['response'][:400],
        dev_results[1]['response'][:400],
        dev_results[2]['response'][:400],
        dev_results[3]['response'][:300],
        dev_results[4]['response'][:300],
        dev_results[5]['response'][:400],
    )
}

headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
data = {
    'model': integration_task['model'],
    'messages': [{'role': 'user', 'content': integration_task['task']}],
    'max_tokens': 3000,
    'temperature': 0.7
}

print('=== 序境运行时监控系统整合 - 第二阶段 ===\n')
print('任务：整合6位成员成果，生成symphony.py\n')

try:
    r = requests.post(API_URL, headers=headers, json=data, timeout=180)
    result = r.json()
    if 'choices' in result and len(result['choices']) > 0:
        content = result['choices'][0]['message'].get('content', '')
        tokens = result.get('usage', {}).get('total_tokens', 0)
        
        print('[OK] 代码生成成功 | %d tokens\n' % tokens)
        
        # 提取Python代码
        code_start = content.find('```python')
        if code_start == -1:
            code_start = content.find('```')
        code_end = content.rfind('```')
        
        if code_start != -1 and code_end != -1:
            code = content[code_start:code_end+3]
        else:
            code = content
        
        # 保存代码
        with open('symphony.py', 'w', encoding='utf-8') as f:
            f.write(code)
        print('代码已保存: symphony.py')
        
        # 显示预览
        print('\n=== 代码预览（前60行）===')
        lines = code.split('\n')[:60]
        for line in lines:
            print(line)
        
    else:
        print('[FAIL] %s' % str(result))
except Exception as e:
    print('[ERROR] %s' % str(e))
