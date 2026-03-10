#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境少府监自进化功能完善会议
8位成员集体协商
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
import json
import time
import threading

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 少府监全员8人
MEMBERS = [
    {"name": "沈清弦", "title": "枢密使", "model": "Qwen/Qwen2.5-14B-Instruct", "specialty": "架构设计"},
    {"name": "苏云渺", "title": "工部尚书", "model": "Qwen/Qwen2.5-14B-Instruct", "specialty": "代码工程"},
    {"name": "顾清歌", "title": "翰林学士", "model": "THUDM/glm-4-9b-chat", "specialty": "规则知识"},
    {"name": "沈星衍", "title": "智囊博士", "model": "Qwen/Qwen2.5-14B-Instruct", "specialty": "策略规划"},
    {"name": "叶轻尘", "title": "行走使", "model": "Qwen/Qwen2.5-7B-Instruct", "specialty": "执行效率"},
    {"name": "林码", "title": "营造司正", "model": "Qwen/Qwen2.5-72B-Instruct", "specialty": "工程实现"},
    {"name": "顾至尊", "title": "首辅大学士", "model": "Qwen/Qwen2.5-14B-Instruct", "specialty": "统筹协调"},
    {"name": "陆念昭", "title": "少府监", "model": "Qwen/Qwen2.5-7B-Instruct", "specialty": "调度管理"},
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

def run_meeting():
    results = []
    total_tokens = 0
    
    print("=" * 60)
    print("🏛️ 少府监自进化功能完善会议 🏛️")
    print("=" * 60)
    print("\n议题：协商自进化功能完善方案\n")
    
    # 沈清弦：架构设计
    print("【1/8】沈清弦（枢密使）- 架构设计")
    p1 = """你是序境枢密使沈清弦。

请为自进化功能设计架构方案：
1. 被动进化机制设计
2. 主动进化机制设计
3. 进化触发条件

输出JSON格式，80字以内。"""
    r1, t1 = call_model(MEMBERS[0], p1)
    total_tokens += t1
    results.append({"name": MEMBERS[0]["name"], "specialty": "架构设计", "proposal": r1, "tokens": t1})
    print(f"   ✅ 完成 ({t1} tokens)")
    time.sleep(0.3)
    
    # 苏云渺：代码实现
    print("\n【2/8】苏云渺（工部尚书）- 代码实现")
    p2 = """你是序境工部尚书苏云渺。

请为自进化功能设计代码实现：
1. 进化算法模块
2. 数据收集模块
3. 反馈学习模块

输出JSON格式，80字以内。"""
    r2, t2 = call_model(MEMBERS[1], p2)
    total_tokens += t2
    results.append({"name": MEMBERS[1]["name"], "specialty": "代码实现", "proposal": r2, "tokens": t2})
    print(f"   ✅ 完成 ({t2} tokens)")
    time.sleep(0.3)
    
    # 顾清歌：规则知识
    print("\n【3/8】顾清歌（翰林学士）- 规则知识")
    p3 = """你是序境翰林学士顾清歌。

请为自进化功能设计规则约束：
1. 进化边界限制
2. 安全规则
3. 伦理准则

输出JSON格式，80字以内。"""
    r3, t3 = call_model(MEMBERS[2], p3)
    total_tokens += t3
    results.append({"name": MEMBERS[2]["name"], "specialty": "规则知识", "proposal": r3, "tokens": t3})
    print(f"   ✅ 完成 ({t3} tokens)")
    time.sleep(0.3)
    
    # 沈星衍：策略规划
    print("\n【4/8】沈星衍（智囊博士）- 策略规划")
    p4 = """你是序境智囊博士沈星衍。

请为自进化功能设计进化策略：
1. 进化时机选择
2. 进化方向判断
3. 优先级排序

输出JSON格式，80字以内。"""
    r4, t4 = call_model(MEMBERS[3], p4)
    total_tokens += t4
    results.append({"name": MEMBERS[3]["name"], "specialty": "策略规划", "proposal": r4, "tokens": t4})
    print(f"   ✅ 完成 ({t4} tokens)")
    time.sleep(0.3)
    
    # 叶轻尘：执行效率
    print("\n【5/8】叶轻尘（行走使）- 执行效率")
    p5 = """你是序境行走使叶轻尘。

请为自进化功能设计执行优化：
1. 后台异步执行
2. 资源占用优化
3. 失败恢复机制

输出JSON格式，80字以内。"""
    r5, t5 = call_model(MEMBERS[4], p5)
    total_tokens += t5
    results.append({"name": MEMBERS[4]["name"], "specialty": "执行优化", "proposal": r5, "tokens": t5})
    print(f"   ✅ 完成 ({t5} tokens)")
    time.sleep(0.3)
    
    # 林码：工程实现
    print("\n【6/8】林码（营造司正）- 工程实现")
    p6 = """你是序境营造司正林码。

请为自进化功能设计工程方案：
1. 模块划分
2. 接口设计
3. 测试方案

输出JSON格式，80字以内。"""
    r6, t6 = call_model(MEMBERS[5], p6)
    total_tokens += t6
    results.append({"name": MEMBERS[5]["name"], "specialty": "工程实现", "proposal": r6, "tokens": t6})
    print(f"   ✅ 完成 ({t6} tokens)")
    time.sleep(0.3)
    
    # 顾至尊：统筹协调
    print("\n【7/8】顾至尊（首辅大学士）- 统筹协调")
    p7 = """你是序境首辅大学士顾至尊。

请为自进化功能设计统筹方案：
1. 阶段规划
2. 资源分配
3. 进度控制

输出JSON格式，80字以内。"""
    r7, t7 = call_model(MEMBERS[6], p7)
    total_tokens += t7
    results.append({"name": MEMBERS[6]["name"], "specialty": "统筹协调", "proposal": r7, "tokens": t7})
    print(f"   ✅ 完成 ({t7} tokens)")
    time.sleep(0.3)
    
    # 陆念昭：调度管理
    print("\n【8/8】陆念昭（少府监）- 调度管理")
    p8 = """你是序境少府监陆念昭。

请为自进化功能设计调度方案：
1. 任务调度
2. 负载均衡
3. 监控告警

输出JSON格式，80字以内。"""
    r8, t8 = call_model(MEMBERS[7], p8)
    total_tokens += t8
    results.append({"name": MEMBERS[7]["name"], "specialty": "调度管理", "proposal": r8, "tokens": t8})
    print(f"   ✅ 完成 ({t8} tokens)")
    
    # 输出结果
    print("\n" + "=" * 60)
    print("📜 会议成果汇总")
    print("=" * 60)
    
    for r in results:
        print(f"\n【{r['name']}】{r['specialty']}:")
        print(f"   {r['proposal'][:150]}")
    
    print(f"\n总消耗: {total_tokens} tokens")
    print("=" * 60)
    
    # 保存会议纪要
    with open('evolution_meeting.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\n💾 会议纪要已保存: evolution_meeting.json")
    
    return results

if __name__ == "__main__":
    run_meeting()
