#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""序境应答系统整合 - 第二阶段"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 读取开发成果
with open('multi_responder_dev.json', 'r', encoding='utf-8') as f:
    dev_results = json.load(f)

# 整合任务
integration_task = {
    'name': '顾至尊',
    'model': 'Qwen/Qwen2.5-14B-Instruct',
    'role': '首辅大学士',
    'task': '''你是序境首辅大学士顾至尊，负责代码整合。

请根据以下6位成员的开发成果，生成一个完整的"序境主动被动应答系统"Python模块。

### 成员成果：

1. 沈清弦(枢密使) - 架构设计：
%s

2. 苏云渺(工部尚书) - 类结构：
%s

3. 顾清歌(翰林学士) - 规则引擎：
%s

4. 沈星衍(智囊博士) - 调度策略：
%s

5. 叶轻尘(行走使) - 执行流程：
%s

6. 林码(营造司正) - Skill适配：
%s

### 要求：
1. 生成完整的Python模块"xuyuan_responder.py"
2. 包含：系统架构类、响应器基类、规则引擎、调度器、执行器、Skill适配层
3. 每个类需要完整实现，可直接运行
4. 支持OpenClaw Skill生态
5. 输出代码即可，不需要解释。
''' % (
        dev_results[0]['response'][:400],
        dev_results[1]['response'][:400],
        dev_results[2]['response'][:400],
        dev_results[3]['response'][:400],
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

print('=== 序境应答系统整合 - 第二阶段 ===\n')
print('任务：整合6位成员成果，生成完整系统代码\n')

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
        with open('xuyuan_responder.py', 'w', encoding='utf-8') as f:
            f.write(code)
        print('代码已保存: xuyuan_responder.py')
        
        # 显示代码预览
        print('\n=== 代码预览（前50行）===')
        lines = code.split('\n')[:50]
        for line in lines:
            print(line)
        
    else:
        print('[FAIL] %s' % str(result))
except Exception as e:
    print('[ERROR] %s' % str(e))
