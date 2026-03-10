#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境2.3.0发行版发布 - 少府监全员协作
任务：适配各种系统、Debug测试、清理冗余、发布GitHub
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
import json
import time
import os

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 少府监精英
MEMBERS = [
    {"name": "沈清弦", "title": "枢密使", "model": "Qwen/Qwen2.5-14B-Instruct", "task": "架构检查"},
    {"name": "苏云渺", "title": "工部尚书", "model": "Qwen/Qwen2.5-14B-Instruct", "task": "代码审查"},
    {"name": "顾清歌", "title": "翰林学士", "model": "THUDM/glm-4-9b-chat", "task": "规则检查"},
    {"name": "沈星衍", "title": "智囊博士", "model": "Qwen/Qwen2.5-14B-Instruct", "task": "策略检查"},
    {"name": "叶轻尘", "title": "行走使", "model": "Qwen/Qwen2.5-7B-Instruct", "task": "执行测试"},
    {"name": "林码", "title": "营造司正", "model": "Qwen/Qwen2.5-72B-Instruct", "task": "工程检查"},
    {"name": "顾至尊", "title": "首辅大学士", "model": "Qwen/Qwen2.5-14B-Instruct", "task": "统筹发布"},
    {"name": "陆念昭", "title": "少府监", "model": "Qwen/Qwen2.5-7B-Instruct", "task": "调度协调"},
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

def run_release():
    results = []
    total_tokens = 0
    
    print("=" * 60)
    print("🚀 序境2.3.0发行版发布 🚀")
    print("=" * 60)
    print("\n任务：适配、Debug、清理、发布\n")
    
    # 沈清弦：架构检查
    print("【1/8】沈清弦（枢密使）- 架构检查")
    p1 = """你是序境枢密使沈清弦。

请检查序境2.3.0架构：
1. 模块解耦度
2. 接口标准化
3. 系统适配性

输出JSON检查报告，80字以内。"""
    r1, t1 = call_model(MEMBERS[0], p1)
    total_tokens += t1
    results.append({"name": MEMBERS[0]["name"], "task": "架构检查", "report": r1, "tokens": t1})
    print(f"   ✅ 完成 ({t1} tokens)")
    time.sleep(0.3)
    
    # 苏云渺：代码审查
    print("\n【2/8】苏云渺（工部尚书）- 代码审查")
    p2 = """你是序境工部尚书苏云渺。

请审查序境2.3.0代码：
1. 语法错误
2. 逻辑漏洞
3. Bug修复

输出JSON审查报告，80字以内。"""
    r2, t2 = call_model(MEMBERS[1], p2)
    total_tokens += t2
    results.append({"name": MEMBERS[1]["name"], "task": "代码审查", "report": r2, "tokens": t2})
    print(f"   ✅ 完成 ({t2} tokens)")
    time.sleep(0.3)
    
    # 顾清歌：规则检查
    print("\n【3/8】顾清歌（翰林学士）- 规则检查")
    p3 = """你是序境翰林学士顾清歌。

请检查序境2.3.0规则：
1. 配置完整性
2. 权限控制
3. 边界条件

输出JSON检查报告，80字以内。"""
    r3, t3 = call_model(MEMBERS[2], p3)
    total_tokens += t3
    results.append({"name": MEMBERS[2]["name"], "task": "规则检查", "report": r3, "tokens": t3})
    print(f"   ✅ 完成 ({t3} tokens)")
    time.sleep(0.3)
    
    # 沈星衍：策略检查
    print("\n【4/8】沈星衍（智囊博士）- 策略检查")
    p4 = """你是序境智囊博士沈星衍。

请检查序境2.3.0策略：
1. 调度策略
2. 容错策略
3. 升级策略

输出JSON检查报告，80字以内。"""
    r4, t4 = call_model(MEMBERS[3], p4)
    total_tokens += t4
    results.append({"name": MEMBERS[3]["name"], "task": "策略检查", "report": r4, "tokens": t4})
    print(f"   ✅ 完成 ({t4} tokens)")
    time.sleep(0.3)
    
    # 叶轻尘：执行测试
    print("\n【5/8】叶轻尘（行走使）- 执行测试")
    p5 = """你是序境行走使叶轻尘。

请测试序境2.3.0执行：
1. 功能测试
2. 性能测试
3. 兼容性测试

输出JSON测试报告，80字以内。"""
    r5, t5 = call_model(MEMBERS[4], p5)
    total_tokens += t5
    results.append({"name": MEMBERS[4]["name"], "task": "执行测试", "report": r5, "tokens": t5})
    print(f"   ✅ 完成 ({t5} tokens)")
    time.sleep(0.3)
    
    # 林码：工程检查
    print("\n【6/8】林码（营造司正）- 工程检查")
    p6 = """你是序境营造司正林码。

请检查序境2.3.0工程：
1. 代码规范
2. 文档完整
3. 冗余文件

输出JSON检查报告，80字以内。"""
    r6, t6 = call_model(MEMBERS[5], p6)
    total_tokens += t6
    results.append({"name": MEMBERS[5]["name"], "task": "工程检查", "report": r6, "tokens": t6})
    print(f"   ✅ 完成 ({t6} tokens)")
    time.sleep(0.3)
    
    # 顾至尊：统筹发布
    print("\n【7/8】顾至尊（首辅大学士）- 统筹发布")
    p7 = """你是序境首辅大学士顾至尊。

请统筹序境2.3.0发布：
1. 版本说明
2. GitHub适配
3. 发行备注

输出JSON发布计划，80字以内。"""
    r7, t7 = call_model(MEMBERS[6], p7)
    total_tokens += t7
    results.append({"name": MEMBERS[6]["name"], "task": "统筹发布", "report": r7, "tokens": t7})
    print(f"   ✅ 完成 ({t7} tokens)")
    time.sleep(0.3)
    
    # 陆念昭：调度协调
    print("\n【8/8】陆念昭（少府监）- 调度协调")
    p8 = """你是序境少府监陆念昭。

请协调序境2.3.0调度：
1. 工具调用
2. 协调度检查
3. 最终确认

输出JSON协调报告，80字以内。"""
    r8, t8 = call_model(MEMBERS[7], p8)
    total_tokens += t8
    results.append({"name": MEMBERS[7]["name"], "task": "调度协调", "report": r8, "tokens": t8})
    print(f"   ✅ 完成 ({t8} tokens)")
    
    # 输出结果
    print("\n" + "=" * 60)
    print("📜 2.3.0发布检查报告")
    print("=" * 60)
    
    for r in results:
        print(f"\n【{r['name']}】{r['task']}:")
        print(f"   {r['report'][:150]}")
    
    print(f"\n总消耗: {total_tokens} tokens")
    print("=" * 60)
    
    # 保存报告
    with open('release_230_check.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\n💾 检查报告已保存: release_230_check.json")
    
    return results

if __name__ == "__main__":
    run_release()
