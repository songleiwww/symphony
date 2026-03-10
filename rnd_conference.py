#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境智能Skills研发会议 - 被动进化+主动智能体开发
多轮讨论，由最有智慧者决策
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
import json
import time

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 少府监精英
ELITES = [
    {"name": "沈清弦", "title": "枢密使", "model": "Qwen/Qwen2.5-14B-Instruct", "specialty": "架构设计", "wisdom": 95},
    {"name": "顾至尊", "title": "首辅大学士", "model": "Qwen/Qwen2.5-14B-Instruct", "specialty": "统筹协调", "wisdom": 93},
    {"name": "沈星衍", "title": "智囊博士", "model": "Qwen/Qwen2.5-14B-Instruct", "specialty": "策略规划", "wisdom": 98},
    {"name": "顾清歌", "title": "翰林学士", "model": "THUDM/glm-4-9b-chat", "specialty": "知识规则", "wisdom": 92},
    {"name": "苏云渺", "title": "工部尚书", "model": "Qwen/Qwen2.5-14B-Instruct", "specialty": "代码工程", "wisdom": 90},
    {"name": "陆念昭", "title": "少府监", "model": "Qwen/Qwen2.5-7B-Instruct", "specialty": "调度管理", "wisdom": 88},
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

def run_rnd_conference():
    results = []
    total_tokens = 0
    
    print("=" * 60)
    print("🧠 序境智能Skills研发会议 🧠")
    print("=" * 60)
    print("\n主题：开发被动进化AI智能体 + 主动AI智能体")
    print("目标：进化序境，实现智能Skills\n")
    
    # 第一轮：问题分析
    print("【第一轮：问题分析】\n")
    
    analysis_prompt = """你是序境{title}{name}。

请分析以下研发项目：
项目：开发交响作为智能Skills，成为被动进化的AI智能体和主动的AI智能体

请从你的专业角度分析：
1. 核心挑战是什么？
2. 需要哪些技术能力？
3. 如何实现被动进化+主动智能？

输出JSON格式，60字以内。"""

    for member in ELITES[:4]:
        print(f"📢 {member['name']}（{member['title']}）分析中...")
        prompt = analysis_prompt.format(title=member['title'], name=member['name'])
        response, tokens = call_model(member, prompt)
        total_tokens += tokens
        results.append({"round": 1, "member": member, "response": response, "tokens": tokens})
        print(f"   ✅ 完成，消耗 {tokens} tokens")
        time.sleep(0.5)
    
    # 第二轮：方案设计
    print("\n【第二轮：方案设计】\n")
    
    design_prompt = """你是序境{title}{name}。

基于以下分析，请设计具体方案：
项目：开发交响作为智能Skills，成为被动进化+主动AI智能体

请给出：
1. 系统架构设计
2. 核心功能模块
3. 进化机制设计

输出JSON格式，80字以内。"""

    for member in ELITES[:4]:
        print(f"📢 {member['name']}（{member['title']}）设计中...")
        prompt = design_prompt.format(title=member['title'], name=member['name'])
        response, tokens = call_model(member, prompt)
        total_tokens += tokens
        results.append({"round": 2, "member": member, "response": response, "tokens": tokens})
        print(f"   ✅ 完成，消耗 {tokens} tokens")
        time.sleep(0.5)
    
    # 第三轮：最有智慧者决策
    print("\n【第三轮：最终决策】\n")
    
    # 找出智慧最高者
    wisest = max(ELITES, key=lambda x: x['wisdom'])
    print(f"🎯 最终决策者：{wisest['name']}（智慧指数:{wisest['wisdom']}）\n")
    
    decision_prompt = """你是序境{wisest_title}{wisest_name}，智慧指数最高，负责最终决策。

请综合以下方案，整合为最终研发计划：
项目：开发交响作为智能Skills，被动进化+主动AI智能体

方案要点来自：
- 沈清弦（枢密使）- 架构设计
- 顾至尊（首辅大学士）- 统筹协调
- 沈星衍（智囊博士）- 策略规划
- 顾清歌（翰林学士）- 知识规则

请输出最终研发计划，包含：
1. 项目名称
2. 核心架构
3. 进化机制
4. 实现步骤
5. 预期成果

输出JSON格式，150字以内。
"""
    
    print(f"📢 {wisest['name']}（{wisest['title']}）决策中...")
    prompt = decision_prompt.format(wisest_title=wisest['title'], wisest_name=wisest['name'])
    response, tokens = call_model(wisest, prompt, max_tokens=500)
    total_tokens += tokens
    results.append({"round": 3, "member": wisest, "response": response, "tokens": tokens})
    print(f"   ✅ 完成，消耗 {tokens} tokens\n")
    
    # 输出结果
    print("=" * 60)
    print("📜 研发会议成果")
    print("=" * 60)
    
    for r in results:
        if r['round'] == 3:
            print(f"\n🏆 最终决策（{r['member']['name']}）:")
            print(f"   {r['response'][:300]}")
    
    print(f"\n总消耗: {total_tokens} tokens")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    run_rnd_conference()
