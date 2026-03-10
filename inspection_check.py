#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境少府监真实模型使用情况大检查
由检查官员进行全面彻查
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
import json
import time

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 检查官员
INSPECTORS = [
    {"name": "顾清歌", "title": "翰林学士", "model": "THUDM/glm-4-9b-chat", "task": "规则检查"},
    {"name": "沈星衍", "title": "智囊博士", "model": "Qwen/Qwen2.5-14B-Instruct", "task": "逻辑验证"},
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

def run_inspection():
    results = []
    total_tokens = 0
    
    print("=" * 60)
    print("🔍 少府监真实模型使用情况大检查 🔍")
    print("=" * 60)
    print("\n任务：检查所有序境少府人员是否使用真实模型\n")
    
    # 第一轮：检查近期活动记录
    print("【第一轮：活动记录检查】\n")
    
    for inspector in INSPECTORS:
        print(f"🔎 {inspector['name']}（{inspector['title']}）检查中...")
        
        prompt = f"""你是序境{inspector['title']}{inspector['name']}，担任检查官员。

请检查近期少府监成员的所有活动记录，验证：
1. 每次模型调用是否使用真实API
2. 是否有模拟或幻觉的迹象
3. Token消耗是否合理
4. 返回结果是否真实有效

请以检查官员的身份，输出检查报告。JSON格式，100字以内。"""
        
        response, tokens = call_model(inspector, prompt)
        total_tokens += tokens
        results.append({"round": 1, "inspector": inspector, "report": response, "tokens": tokens})
        print(f"   ✅ 完成 ({tokens} tokens)")
        time.sleep(0.5)
    
    # 第二轮：综合评估
    print("\n【第二轮：综合评估】\n")
    
    # 顾清歌做最终评估
    final_prompt = """你是序境翰林学士顾清歌，检查官员最高负责人。

请对少府监近期所有活动进行综合评估：
1. 真实模型使用率
2. 是否存在幻觉/模拟
3. 整体协作质量评分

输出JSON格式评估报告，80字以内。"""
    
    response, tokens = call_model(INSPECTORS[0], final_prompt)
    total_tokens += tokens
    results.append({"round": 2, "inspector": INSPECTORS[0], "report": response, "tokens": tokens})
    print(f"   ✅ 完成 ({tokens} tokens)")
    
    # 输出结果
    print("\n" + "=" * 60)
    print("📜 检查报告汇总")
    print("=" * 60)
    
    for r in results:
        print(f"\n【{r['inspector']['name']}】{r['inspector']['title']}:")
        print(f"   {r['report'][:200]}")
    
    print(f"\n总消耗: {total_tokens} tokens")
    print("=" * 60)
    
    # 保存报告
    with open('inspection_report.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\n💾 检查报告已保存: inspection_report.json")
    
    return results

if __name__ == "__main__":
    run_inspection()
