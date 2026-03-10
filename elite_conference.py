#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境整体调度协调系统设计 - 少府监精英会议
使用真实模型进行多轮讨论，设计OpenClaw技能调度协调方案
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
import json
import time

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 少府监精英成员
ELITES = [
    {"name": "沈清弦", "title": "枢密使", "model": "Qwen/Qwen2.5-14B-Instruct", "specialty": "架构设计", "role": "方案统筹"},
    {"name": "顾至尊", "title": "首辅大学士", "model": "Qwen/Qwen2.5-14B-Instruct", "specialty": "统筹协调", "role": "资源整合"},
    {"name": "沈星衍", "title": "智囊博士", "model": "Qwen/Qwen2.5-14B-Instruct", "specialty": "策略规划", "role": "调度策略"},
    {"name": "陆念昭", "title": "少府监", "model": "Qwen/Qwen2.5-7B-Instruct", "specialty": "调度管理", "role": "执行协调"},
]

def call_model(member, prompt, max_tokens=300):
    """调用真实模型"""
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
        return f"调用失败: {str(e)}", 0
    return "无响应", 0

def run_elite_conference():
    """运行精英会议"""
    results = []
    total_tokens = 0
    
    print("=" * 60)
    print("🏛️ 序境整体调度协调系统设计会议 🏛️")
    print("=" * 60)
    print("\n议题：设计OpenClaw Skills整体调度协调工作方案")
    print("要求：人性化适配、智能化调度、协作优化\n")
    
    # 第一轮：各精英提出方案
    print("【第一轮：方案提出】\n")
    
    prompts = {
        "沈清弦": """你是序境枢密使沈清弦，负责方案统筹。

请为序境整体调度协调系统设计架构方案，包括：
1. 技能调用流程
2. 模块解耦设计
3. 接口标准化

输出JSON格式，80字以内。""",
        
        "顾至尊": """你是序境首辅大学士顾至尊，负责资源整合。

请为序境整体调度协调系统设计资源管理方案，包括：
1. 技能优先级
2. 负载均衡
3. 容错机制

输出JSON格式，80字以内。""",
        
        "沈星衍": """你是序境智囊博士沈星衍，负责调度策略。

请为序境整体调度协调系统设计智能调度方案，包括：
1. 任务分类
2. 模型匹配
3. 自适应选择

输出JSON格式，80字以内。""",
        
        "陆念昭": """你是序境少府监陆念昭，负责执行协调。

请为序境整体调度协调系统设计人性化适配方案，包括：
1. 用户体验优化
2. 交互流程简化
3. 反馈机制

输出JSON格式，80字以内。"""
    }
    
    for member in ELITES:
        print(f"📢 {member['name']}（{member['title']}）发言中...")
        response, tokens = call_model(member, prompts[member['name']])
        total_tokens += tokens
        results.append({
            "member": member,
            "response": response,
            "tokens": tokens
        })
        print(f"   ✅ 完成，消耗 {tokens} tokens")
        time.sleep(0.5)
    
    # 第二轮：整合方案
    print("\n【第二轮：方案整合】\n")
    
    integration_prompt = """你是序境首辅大学士顾至尊，负责整合各精英方案。

请整合以下方案，设计完整的序境整体调度协调系统：

1. 沈清弦（枢密使）- 架构设计
2. 顾至尊（首辅大学士）- 资源整合  
3. 沈星衍（智囊博士）- 调度策略
4. 陆念昭（少府监）- 人性化适配

请输出完整的系统设计方案，JSON格式，150字以内。
"""
    
    print("📢 顾至尊整合方案中...")
    integration, int_tokens = call_model(ELITES[1], integration_prompt, max_tokens=400)
    total_tokens += int_tokens
    print(f"   ✅ 完成，消耗 {int_tokens} tokens\n")
    
    # 输出结果
    print("=" * 60)
    print("📜 会议成果汇总")
    print("=" * 60)
    
    for r in results:
        print(f"\n【{r['member']['name']}】{r['member']['title']}（{r['member']['specialty']}）:")
        print(f"   {r['response'][:150]}")
    
    print(f"\n【方案整合】:")
    print(f"   {integration[:200]}")
    
    print(f"\n总消耗: {total_tokens} tokens")
    print("=" * 60)
    
    return {
        "results": results,
        "integration": integration,
        "total_tokens": total_tokens
    }

if __name__ == "__main__":
    run_elite_conference()
