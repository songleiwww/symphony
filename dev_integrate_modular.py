#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""序境模块化改进整合 - 第二阶段"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 读取开发成果
with open('modular_improvement.json', 'r', encoding='utf-8') as f:
    dev_results = json.load(f)

# 整合任务
integration_task = {
    'name': '陆念昭',
    'model': 'Qwen/Qwen2.5-14B-Instruct',
    'task': '''你是序境少府监陆念昭，负责整合所有改进方案到symphony.py。

请根据以下8位成员的成果，整合生成全新的"symphony.py"。

### 成员成果：

1. 沈清弦(枢密使) - 模块化改进：
%s

2. 苏云渺(工部尚书) - 可维护性：
%s

3. 顾清歌(翰林学士) - 个性化服务：
%s

4. 沈星衍(智囊博士) - 意图理解：
%s

5. 叶轻尘(行走使) - 响应速度：
%s

6. 林码(营造司正) - 并发处理：
%s

7. 顾至尊(首辅大学士) - 扩展性：
%s

8. 陆念昭(少府监) - 开发效率：
%s

### 要求：
1. 生成完整的"symphony.py"文件
2. 包含所有8个改进模块
3. 可直接运行测试
4. 输出Python代码。
''' % (
        dev_results[0]['response'][:400],
        dev_results[1]['response'][:400],
        dev_results[2]['response'][:400],
        dev_results[3]['response'][:400],
        dev_results[4]['response'][:400],
        dev_results[5]['response'][:400],
        dev_results[6]['response'][:400],
        dev_results[7]['response'][:400],
    )
}

headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
data = {
    'model': integration_task['model'],
    'messages': [{'role': 'user', 'content': integration_task['task']}],
    'max_tokens': 4000,
    'temperature': 0.7
}

print('=== 序境模块化改进整合 - 第二阶段 ===\n')
print('任务：整合8位成员成果到symphony.py\n')

try:
    r = requests.post(API_URL, headers=headers, json=data, timeout=240)
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
        
        # 清理代码
        code = code.replace('```python', '').replace('```', '').strip()
        
        # 保存代码
        with open('symphony.py', 'w', encoding='utf-8') as f:
            f.write(code)
        print('代码已保存: symphony.py')
        
        # 显示预览
        print('\n=== 代码预览（前40行）===')
        lines = code.split('\n')[:40]
        for line in lines:
            print(line)
        
    else:
        print('[FAIL] %s' % str(result))
except Exception as e:
    print('[ERROR] %s' % str(e))
