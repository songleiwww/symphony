#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境智能Skills研发 - 少府监全员开发
基于决策：双层架构+自适应学习机制
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
import json
import time

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 少府监全员8人
MEMBERS = [
    {"name": "沈清弦", "title": "枢密使", "model": "Qwen/Qwen2.5-14B-Instruct", "task": "核心架构设计"},
    {"name": "苏云渺", "title": "工部尚书", "model": "Qwen/Qwen2.5-14B-Instruct", "task": "代码实现"},
    {"name": "顾清歌", "title": "翰林学士", "model": "THUDM/glm-4-9b-chat", "task": "知识规则"},
    {"name": "沈星衍", "title": "智囊博士", "model": "Qwen/Qwen2.5-14B-Instruct", "task": "进化机制"},
    {"name": "叶轻尘", "title": "行走使", "model": "Qwen/Qwen2.5-7B-Instruct", "task": "执行优化"},
    {"name": "林码", "title": "营造司正", "model": "Qwen/Qwen2.5-72B-Instruct", "task": "工程实现"},
    {"name": "顾至尊", "title": "首辅大学士", "model": "Qwen/Qwen2.5-14B-Instruct", "task": "统筹协调"},
    {"name": "陆念昭", "title": "少府监", "model": "Qwen/Qwen2.5-7B-Instruct", "task": "调度整合"},
]

def call_model(member, prompt, max_tokens=500):
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

def develop_system():
    results = []
    total_tokens = 0
    
    print("=" * 60)
    print("⚡ 少府监全员开发 - 智能Skills研发 ⚡")
    print("=" * 60)
    print("\n项目：交响智能Skills研发")
    print("架构：双层架构+自适应学习机制\n")
    
    # 沈清弦：核心架构
    print("【1/8】沈清弦（枢密使）- 核心架构设计")
    p1 = """设计交响智能Skills核心架构：
项目：被动进化+主动AI智能体
要求：双层架构设计

输出架构设计JSON（100字以内）："""
    r1, t1 = call_model(MEMBERS[0], p1)
    total_tokens += t1
    results.append({"name": MEMBERS[0]["name"], "task": "核心架构", "result": r1, "tokens": t1})
    print(f"   ✅ 完成 ({t1} tokens)")
    time.sleep(0.5)
    
    # 沈星衍：进化机制
    print("\n【2/8】沈星衍（智囊博士）- 进化机制")
    p2 = """设计自适应学习进化机制：
项目：被动进化+主动AI智能体
要求：基于数据反馈的自适应学习

输出进化机制JSON（100字以内）："""
    r2, t2 = call_model(MEMBERS[3], p2)
    total_tokens += t2
    results.append({"name": MEMBERS[3]["name"], "task": "进化机制", "result": r2, "tokens": t2})
    print(f"   ✅ 完成 ({t2} tokens)")
    time.sleep(0.5)
    
    # 顾清歌：知识规则
    print("\n【3/8】顾清歌（翰林学士）- 知识规则")
    p3 = """设计知识规则系统：
项目：被动进化+主动AI智能体
要求：知识库、规则引擎、推理机制

输出知识规则JSON（100字以内）："""
    r3, t3 = call_model(MEMBERS[2], p3)
    total_tokens += t3
    results.append({"name": MEMBERS[2]["name"], "task": "知识规则", "result": r3, "tokens": t3})
    print(f"   ✅ 完成 ({t3} tokens)")
    time.sleep(0.5)
    
    # 苏云渺：代码实现
    print("\n【4/8】苏云渺（工部尚书）- 代码实现")
    p4 = """设计代码实现方案：
项目：被动进化+主动AI智能体
要求：模块化、可维护、可扩展

输出代码结构JSON（100字以内）："""
    r4, t4 = call_model(MEMBERS[1], p4)
    total_tokens += t4
    results.append({"name": MEMBERS[1]["name"], "task": "代码实现", "result": r4, "tokens": t4})
    print(f"   ✅ 完成 ({t4} tokens)")
    time.sleep(0.5)
    
    # 叶轻尘：执行优化
    print("\n【5/8】叶轻尘（行走使）- 执行优化")
    p5 = """设计执行优化方案：
项目：被动进化+主动AI智能体
要求：高效执行、异步处理、并发控制

输出执行优化JSON（100字以内）："""
    r5, t5 = call_model(MEMBERS[4], p5)
    total_tokens += t5
    results.append({"name": MEMBERS[4]["name"], "task": "执行优化", "result": r5, "tokens": t5})
    print(f"   ✅ 完成 ({t5} tokens)")
    time.sleep(0.5)
    
    # 林码：工程实现
    print("\n【6/8】林码（营造司正）- 工程实现")
    p6 = """设计工程实现方案：
项目：被动进化+主动AI智能体
要求：工程规范、测试、部署

输出工程方案JSON（100字以内）："""
    r6, t6 = call_model(MEMBERS[5], p6)
    total_tokens += t6
    results.append({"name": MEMBERS[5]["name"], "task": "工程实现", "result": r6, "tokens": t6})
    print(f"   ✅ 完成 ({t6} tokens)")
    time.sleep(0.5)
    
    # 顾至尊：统筹协调
    print("\n【7/8】顾至尊（首辅大学士）- 统筹协调")
    p7 = """设计统筹协调方案：
项目：被动进化+主动AI智能体
要求：分阶段实施、资源协调、进度管理

输出协调方案JSON（100字以内）："""
    r7, t7 = call_model(MEMBERS[6], p7)
    total_tokens += t7
    results.append({"name": MEMBERS[6]["name"], "task": "统筹协调", "result": r7, "tokens": t7})
    print(f"   ✅ 完成 ({t7} tokens)")
    time.sleep(0.5)
    
    # 陆念昭：调度整合
    print("\n【8/8】陆念昭（少府监）- 调度整合")
    p8 = """整合所有模块，设计调度中心：
项目：被动进化+主动AI智能体
要求：统一调度、技能管理、协作机制

输出调度整合JSON（100字以内）："""
    r8, t8 = call_model(MEMBERS[7], p8)
    total_tokens += t8
    results.append({"name": MEMBERS[7]["name"], "task": "调度整合", "result": r8, "tokens": t8})
    print(f"   ✅ 完成 ({t8} tokens)")
    
    # 输出结果
    print("\n" + "=" * 60)
    print("📜 开发成果汇总")
    print("=" * 60)
    
    for r in results:
        print(f"\n【{r['name']}】{r['task']}:")
        print(f"   {r['result'][:150]}")
    
    print(f"\n总消耗: {total_tokens} tokens")
    print("=" * 60)
    
    # 保存结果
    with open('intelligent_skills_dev.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\n💾 开发成果已保存: intelligent_skills_dev.json")
    
    return results

if __name__ == "__main__":
    develop_system()
