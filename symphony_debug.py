#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境debug交响 - 少府监精英全员Debug
真实模型调用，找出并修复所有问题
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
import json
import time

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 少府监精英
MEMBERS = [
    {"name": "沈清弦", "title": "枢密使", "model": "Qwen/Qwen2.5-14B-Instruct", "specialty": "架构分析"},
    {"name": "苏云渺", "title": "工部尚书", "model": "Qwen/Qwen2.5-14B-Instruct", "specialty": "代码审查"},
    {"name": "顾清歌", "title": "翰林学士", "model": "THUDM/glm-4-9b-chat", "specialty": "规则检查"},
    {"name": "沈星衍", "title": "智囊博士", "model": "Qwen/Qwen2.5-14B-Instruct", "specialty": "逻辑分析"},
    {"name": "叶轻尘", "title": "行走使", "model": "Qwen/Qwen2.5-7B-Instruct", "specialty": "性能分析"},
    {"name": "林码", "title": "营造司正", "model": "Qwen/Qwen2.5-72B-Instruct", "specialty": "工程审查"},
    {"name": "顾至尊", "title": "首辅大学士", "model": "Qwen/Qwen2.5-14B-Instruct", "specialty": "统筹检查"},
    {"name": "陆念昭", "title": "少府监", "model": "Qwen/Qwen2.5-7B-Instruct", "specialty": "调度检查"},
]

def call_model(member, prompt, max_tokens=400):
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    data = {
        'model': member['model'],
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': max_tokens,
        'temperature': 0.7
    }
    try:
        r = requests.post(API_URL, headers=headers, json=data, timeout=90)
        result = r.json()
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message'].get('content', '')
            tokens = result.get('usage', {}).get('total_tokens', 0)
            return content, tokens
    except Exception as e:
        return f"失败: {str(e)}", 0
    return "无响应", 0

def run_debug():
    issues = []
    total_tokens = 0
    
    print("=" * 60)
    print("🔧 少府监精英Debug交响 🔧")
    print("=" * 60)
    print("\n任务：找出并修复交响所有问题\n")
    
    # 8位精英各自检查一个方向
    checks = [
        ("沈清弦", "架构", "请检查symphony核心架构问题：模块耦合、接口设计、层次结构。输出JSON格式，列出发现的问题。"),
        ("苏云渺", "代码", "请检查symphony代码问题：语法错误、逻辑漏洞、异常处理。输出JSON格式，列出发现的问题。"),
        ("顾清歌", "规则", "请检查symphony规则问题：配置错误、权限控制、边界条件。输出JSON格式，列出发现的问题。"),
        ("沈星衍", "逻辑", "请检查symphony逻辑问题：流程错误、状态管理、任务调度。输出JSON格式，列出发现的问题。"),
        ("叶轻尘", "性能", "请检查symphony性能问题：内存泄漏、阻塞操作、并发处理。输出JSON格式，列出发现的问题。"),
        ("林码", "工程", "请检查symphony工程问题：代码规范、测试覆盖、文档完整。输出JSON格式，列出发现的问题。"),
        ("顾至尊", "统筹", "请检查symphony统筹问题：资源管理、负载均衡、容错机制。输出JSON格式，列出发现的问题。"),
        ("陆念昭", "调度", "请检查symphony调度问题：任务分配、优先级、超时处理。输出JSON格式，列出发现的问题。"),
    ]
    
    for name, specialty, prompt in checks:
        member = next(m for m in MEMBERS if m['name'] == name)
        print(f"🔍 {name}（{specialty}）检查中...")
        
        full_prompt = f"""你是序境{name}，负责{specialty}检查。

请检查symphony.py和相关模块，找出所有问题：

{prompt}

输出JSON格式，100字以内。"""
        
        response, tokens = call_model(member, full_prompt)
        total_tokens += tokens
        
        issues.append({
            "name": name,
            "specialty": specialty,
            "issues": response,
            "tokens": tokens
        })
        print(f"   ✅ 完成 ({tokens} tokens)")
        time.sleep(0.5)
    
    # 输出问题汇总
    print("\n" + "=" * 60)
    print("📋 问题汇总")
    print("=" * 60)
    
    for i in issues:
        print(f"\n【{i['name']}】{i['specialty']}:")
        print(f"   {i['issues'][:200]}")
    
    print(f"\n总消耗: {total_tokens} tokens")
    
    # 保存问题
    with open('debug_issues.json', 'w', encoding='utf-8') as f:
        json.dump(issues, f, ensure_ascii=False, indent=2)
    print("\n💾 问题已保存: debug_issues.json")
    
    return issues

if __name__ == "__main__":
    run_debug()
