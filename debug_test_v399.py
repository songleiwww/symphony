#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青丘Debug测试 v3.9.9
对v3.9.8生成的代码进行Bug检测和修复
"""
import requests
import json
import time
from datetime import datetime

API_KEY = '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'
URL = 'https://integrate.api.nvidia.com/v1/chat/completions'
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

# Debug测试 - 3位专家（陈浩然之前失败，用林思远替代测试）
experts = [
    {
        'name': '林思远',
        'fox': '银白九尾狐 - 青丘长老',
        'role': '代码审查专家',
        'model': 'meta/llama-3.1-405b-instruct',
        'task': '''请作为代码审查专家，对以下代码进行Debug测试。

代码内容：
```python
# 函数调用核心模块
class ToolRegistry:
    def __init__(self):
        self.tools = {}
    def register_tool(self, tool_name, tool_func):
        self.tools[tool_name] = tool_func
    def get_tool(self, tool_name):
        return self.tools.get(tool_name)

class FunctionCaller:
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry
    def call_function(self, tool_name, params):
        tool_func = self.tool_registry.get_tool(tool_name)
        if tool_func:
            return tool_func(**params)
        else:
            raise ValueError(f"工具'{tool_name}'未注册")
```

请检查：
1. 潜在Bug和错误
2. 边界情况处理
3. 安全漏洞
4. 性能优化建议

给出修复后的代码。'''
    },
    {
        'name': '张晓明',
        'fox': '墨黑九尾狐 - 青丘史官',
        'role': '单元测试专家',
        'model': 'qwen/qwen3.5-397b-a17b',
        'task': '''请作为单元测试专家，为以下代码编写测试用例。

代码内容：
```python
# 反思机制核心模块
class ReflectionTrigger:
    def should_trigger(self, context):
        if context.metrics.get("score", 1.0) < 0.8:
            return True
        result_str = str(context.current_result).lower()
        if any(kw in result_str for kw in ["error", "fail"]):
            return True
        return False
```

请编写：
1. 正常情况测试
2. 边界情况测试
3. 异常情况测试
4. 覆盖率分析

给出完整的测试代码。'''
    },
    {
        'name': '赵心怡',
        'fox': '金黄九尾狐 - 青丘舞姬',
        'role': '安全测试专家',
        'model': 'minimaxai/minimax-m2.5',
        'task': '''请作为安全测试专家，对以下代码进行安全测试。

代码内容：
```python
# 工具扩展核心模块
class PermissionManager:
    def __init__(self):
        self.permissions = {}
    def check_permission(self, user, tool, action):
        key = f"{user}:{tool}:{action}"
        return self.permissions.get(key, False)
    def grant_permission(self, user, tool, action):
        key = f"{user}:{tool}:{action}"
        self.permissions[key] = True
```

请检查：
1. 权限绕过风险
2. 注入攻击风险
3. 数据泄露风险
4. 安全加固建议

给出安全修复方案。'''
    }
]

results = []
total_tokens = 0
success_count = 0

print("="*60)
print("青丘Debug测试会议 v3.9.9")
print("代码Bug检测和安全测试")
print("="*60)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)
print()

for i, expert in enumerate(experts):
    print(f"【专家{i+1}】{expert['name']} - {expert['role']}")
    
    data = {
        'model': expert['model'],
        'messages': [{'role': 'user', 'content': expert['task']}],
        'temperature': 0.7
    }
    
    start_time = time.time()
    
    try:
        r = requests.post(URL, headers=HEADERS, json=data, timeout=300)
        elapsed = time.time() - start_time
        
        if r.status_code == 200:
            result = r.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            prompt_tokens = result.get('usage', {}).get('prompt_tokens', 0)
            completion_tokens = result.get('usage', {}).get('completion_tokens', 0)
            tokens = result.get('usage', {}).get('total_tokens', 0)
            total_tokens += tokens
            success_count += 1
            
            results.append({
                'name': expert['name'],
                'role': expert['role'],
                'model': expert['model'],
                'status': '成功',
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': tokens,
                'elapsed': round(elapsed, 2)
            })
            
            print(f"  Token: {tokens}, 时间: {elapsed:.2f}秒")
        else:
            results.append({
                'name': expert['name'],
                'role': expert['role'],
                'model': expert['model'],
                'status': '失败',
                'total_tokens': 0
            })
            print(f"  失败: {r.status_code}")
    except Exception as e:
        results.append({
            'name': expert['name'],
            'role': expert['role'],
            'model': expert['model'],
            'status': '异常',
            'total_tokens': 0
        })
        print(f"  异常: {str(e)[:30]}")
    
    print()

print("="*60)
print(f"Debug测试完成: 成功{success_count}/3, Token:{total_tokens}")
print("="*60)

# 保存报告
report = {
    'version': 'v3.9.9',
    'topic': 'Debug测试和安全检查',
    'timestamp': datetime.now().isoformat(),
    'total_experts': 3,
    'success_count': success_count,
    'total_tokens': total_tokens,
    'success_rate': f"{success_count/3*100:.1f}%",
    'results': results
}

with open('debug_test_v399.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("报告已保存: debug_test_v399.json")
