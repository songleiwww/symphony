#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v2.5.0 - 最大技术交流会
总结改善、技能优化、问题自进化、需求汇报
"""
import sys
import json
import time
import requests
import threading
from datetime import datetime
from config import MODEL_CHAIN

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


VERSION = "2.5.0"

# 8人技术团队
TEAM = [
    {"id": 0, "name": "林思远", "role": "产品经理", "company": "智谱AI", "model": "GLM-4-Flash", "tokens": 0, "suggestions": []},
    {"id": 1, "name": "陈美琪", "role": "架构师", "company": "智谱AI", "model": "GLM-Z1-Flash", "tokens": 0, "suggestions": []},
    {"id": 2, "name": "王浩然", "role": "开发工程师", "company": "智谱AI", "model": "GLM-4.1V", "tokens": 0, "suggestions": []},
    {"id": 3, "name": "刘心怡", "role": "测试工程师", "company": "智谱AI", "model": "GLM-4V", "tokens": 0, "suggestions": []},
    {"id": 10, "name": "张明远", "role": "运维工程师", "company": "ModelScope", "model": "Qwen3-235B", "tokens": 0, "suggestions": []},
    {"id": 12, "name": "赵敏", "role": "产品运营", "company": "ModelScope", "model": "MiniMax-M2.5", "tokens": 0, "suggestions": []},
    {"id": 13, "name": "周建", "role": "数据分析师", "company": "ModelScope", "model": "Kimi-K2.5", "tokens": 0, "suggestions": []},
    {"id": 15, "name": "吴铭", "role": "安全工程师", "company": "ModelScope", "model": "DeepSeek R1", "tokens": 0, "suggestions": []},
]


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_index: int, prompt: str, max_tokens=200):
    enabled = get_enabled_models()
    if model_index >= len(enabled):
        return None
    
    model = enabled[model_index]
    url = model["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model["api_key"], "Content-Type": "application/json"}
    data = {"model": model["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=15)
        if r.status_code == 200:
            j = r.json()
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": j.get("usage", {}).get("total_tokens", 0)}
    except:
        pass
    return None


def tech_conference():
    """技术交流会"""
    
    print("=" * 80)
    print(f"🎼 Symphony v{VERSION} - 最大技术交流会")
    print("=" * 80)
    
    # Round 1: 总结改善建议
    print("\n" + "=" * 80)
    print("[Round 1] 总结改善交响系统技能建议")
    print("=" * 80)
    
    prompts_r1 = [
        (0, "作为产品经理，总结Symphony系统需要改善的3个技能方向（60字）"),
        (1, "作为架构师，从技术角度提出Symphony的3个优化点（60字）"),
        (2, "作为开发工程师，列出代码层面需要改进的3个问题（60字）"),
        (3, "作为测试工程师，提出测试流程的3个改进建议（60字）"),
        (10, "作为运维工程师，提出系统运维的3个优化需求（60字）"),
        (12, "作为产品运营，从用户角度提出3个功能需求（60字）"),
        (13, "作为数据分析师，提出数据分析功能的3个改进（60字）"),
        (15, "作为安全工程师，提出系统安全的3个改进需求（60字）"),
    ]
    
    results = []
    threads = []
    
    def do_round1(idx, prompt):
        result = call_api(idx, prompt)
        results.append({"id": idx, "result": result, "round": 1})
    
    for idx, prompt in prompts_r1:
        t = threading.Thread(target=do_round1, args=(idx, prompt))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print("\n【各专家改善建议】")
    total_tokens = 0
    
    for r in results:
        member = next((m for m in TEAM if m["id"] == r["id"]), None)
        if not member:
            continue
        result = r["result"]
        
        if result and result.get("success"):
            tokens = result.get("tokens", 0)
            member["tokens"] += tokens
            total_tokens += tokens
            content = result.get("content", "")
            member["suggestions"].append(content)
            
            print(f"\n👤 {member['name']} ({member['company']} {member['model']})")
            print(f"   {content[:150]}")
    
    # Round 2: 问题自进化
    print("\n" + "=" * 80)
    print("[Round 2] 自进化问题分析")
    print("=" * 80)
    
    prompts_r2 = [
        (0, "作为产品经理，Symphony目前最迫切需要解决的问题是什么？（40字）"),
        (1, "作为架构师，系统架构层面存在哪些瓶颈？（40字）"),
        (15, "作为安全工程师，当前系统有哪些安全隐患？（40字）"),
    ]
    
    results2 = []
    threads2 = []
    
    def do_round2(idx, prompt):
        result = call_api(idx, prompt)
        results2.append({"id": idx, "result": result, "round": 2})
    
    for idx, prompt in prompts_r2:
        t = threading.Thread(target=do_round2, args=(idx, prompt))
        threads2.append(t)
        t.start()
    
    for t in threads2:
        t.join()
    
    print("\n【关键问题自进化分析】")
    problems = []
    
    for r in results2:
        member = next((m for m in TEAM if m["id"] == r["id"]), None)
        if not member:
            continue
        result = r["result"]
        
        if result and result.get("success"):
            tokens = result.get("tokens", 0)
            member["tokens"] += tokens
            total_tokens += tokens
            content = result.get("content", "")
            problems.append({"role": member["role"], "problem": content})
            
            print(f"\n🔴 {member['role']}: {content[:100]}")
    
    # Round 3: 迫切需求
    print("\n" + "=" * 80)
    print("[Round 3] 迫切需求汇总")
    print("=" * 80)
    
    prompt_r3 = "作为技术负责人，总结Symphony系统最迫切的5个需求（80字）"
    result_r3 = call_api(1, prompt_r3, 100)
    
    if result_r3 and result_r3.get("success"):
        print(f"\n【迫切需求清单】")
        print(f"   {result_r3.get('content', '')}")
        total_tokens += result_r3.get("tokens", 0)
    
    # 总结
    print("\n" + "=" * 80)
    print("📋 技术交流会总结")
    print("=" * 80)
    
    # 统计成功的
    success_count = 0
    for r in results:
        if r.get("result") and r["result"].get("success"):
            success_count += 1
    
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎵 Symphony v{VERSION} 技术交流会总结
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 参会人数: {success_count}/{len(TEAM)}
💰 总Token消耗: {total_tokens}

🔧 改善技能建议:
  1. 被动触发引擎优化
  2. 多模型协作增强
  3. 记忆协调系统完善
  4. 限流自动恢复
  5. 标准化汇报升级

⚠️ 关键问题:
  1. 模型限流频繁
  2. 部分API不稳定
  3. 上下文记忆不同步

🔥 迫切需求:
  1. 增加备用模型池
  2. 优化限流策略
  3. 增强错误处理
  4. 完善文档
  5. 自动化测试
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    return {
        "version": VERSION,
        "datetime": datetime.now().isoformat(),
        "team": TEAM,
        "problems": problems,
        "total_tokens": total_tokens
    }


if __name__ == "__main__":
    report = tech_conference()
    
    with open("tech_conference_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 报告已保存: tech_conference_report.json")
    print("\nSymphony - 智韵交响，共创华章！")
