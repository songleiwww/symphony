#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v2.3.0 - 拟人化工作汇报系统
每个人物对应哪个公司的模型，干的什么活，贡献度
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


VERSION = "2.3.0"


# 团队成员配置 - 每个成员对应真实模型
TEAM = [
    {"id": 0, "name": "林思远", "role": "产品经理", "company": "智谱AI", "model_name": "GLM-4-Flash", "provider": "zhipu", "tasks": [], "tokens": 0},
    {"id": 1, "name": "陈美琪", "role": "架构师", "company": "智谱AI", "model_name": "GLM-Z1-Flash", "provider": "zhipu", "tasks": [], "tokens": 0},
    {"id": 2, "name": "王浩然", "role": "开发工程师", "company": "智谱AI", "model_name": "GLM-4.1V-Thinking", "provider": "zhipu", "tasks": [], "tokens": 0},
    {"id": 3, "name": "刘心怡", "role": "测试工程师", "company": "智谱AI", "model_name": "GLM-4V-Flash", "provider": "zhipu", "tasks": [], "tokens": 0},
    {"id": 10, "name": "张明远", "role": "运维工程师", "company": "ModelScope", "model_name": "Qwen3-235B", "provider": "modelscope", "tasks": [], "tokens": 0},
    {"id": 12, "name": "赵敏", "role": "产品运营", "company": "ModelScope", "model_name": "MiniMax-M2.5", "provider": "modelscope", "tasks": [], "tokens": 0},
    {"id": 13, "name": "周建", "role": "数据分析师", "company": "ModelScope", "model_name": "Kimi-K2.5", "provider": "modelscope", "tasks": [], "tokens": 0},
    {"id": 15, "name": "吴铭", "role": "安全工程师", "company": "ModelScope", "model_name": "DeepSeek R1", "provider": "modelscope", "tasks": [], "tokens": 0},
]


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_index: int, prompt: str, max_tokens=150):
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


def humanized_report():
    """拟人化工作汇报"""
    
    print("=" * 80)
    print(f"🎼 Symphony v{VERSION} - 拟人化工作汇报")
    print("=" * 80)
    
    # 任务分配 - 每个角色做不同工作
    task_assignments = [
        (0, "作为产品经理，今天完成的工作：1.梳理产品需求 2.编写PRD文档 3.跟进开发进度。请用一句话总结（30字）"),
        (1, "作为架构师，今天完成的工作：1.设计系统架构 2.评审技术方案 3.优化代码结构。请用一句话总结（30字）"),
        (2, "作为开发工程师，今天完成的工作：1.编写核心代码 2.修复Bug 3.优化性能。请用一句话总结（30字）"),
        (3, "作为测试工程师，今天完成的工作：1.编写测试用例 2.执行测试 3.提交缺陷报告。请用一句话总结（30字）"),
        (10, "作为运维工程师，今天完成的工作：1.部署上线 2.监控告警 3.日志分析。请用一句话总结（30字）"),
        (12, "作为产品运营，今天完成的工作：1.数据分析 2.用户反馈 3.运营报告。请用一句话总结（30字）"),
        (13, "作为数据分析师，今天完成的工作：1.数据采集 2.统计分析 3.报告输出。请用一句话总结（30字）"),
        (15, "作为安全工程师，今天完成的工作：1.安全扫描 2.漏洞修复 3.安全审计。请用一句话总结（30字）"),
    ]
    
    # 并行调用
    results = []
    threads = []
    
    def do_task(member_id, prompt):
        result = call_api(member_id, prompt)
        results.append({"id": member_id, "result": result})
    
    for member_id, prompt in task_assignments:
        t = threading.Thread(target=do_task, args=(member_id, prompt))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # 统计
    total_tokens = 0
    successful_members = []
    
    print("\n" + "=" * 80)
    print("👥 团队成员工作情况详情")
    print("=" * 80)
    
    for r in results:
        member = next((m for m in TEAM if m["id"] == r["id"]), None)
        if not member:
            continue
            
        result = r["result"]
        
        if result and result.get("success"):
            tokens = result.get("tokens", 0)
            member["tokens"] = tokens
            member["tasks"].append(result.get("content", ""))
            total_tokens += tokens
            successful_members.append(member)
            
            print(f"\n{'─' * 60}")
            print(f"👤 姓名: {member['name']}")
            print(f"🎭 角色: {member['role']}")
            print(f"🏢 公司: {member['company']}")
            print(f"🖥️ 模型: {member['model_name']}")
            print(f"🔢 Token消耗: {tokens}")
            print(f"📝 工作内容:")
            print(f"   {result.get('content', '无')[:80]}")
        else:
            print(f"\n{'─' * 60}")
            print(f"👤 {member['name']} ({member['company']} {member['model_name']}) - ❌ 调用失败")
    
    # 计算贡献度
    print("\n" + "=" * 80)
    print("📊 贡献度排名")
    print("=" * 80)
    
    if total_tokens > 0:
        # 按Token排序
        sorted_members = sorted(TEAM, key=lambda x: x.get("tokens", 0), reverse=True)
        
        print(f"\n总Token消耗: {total_tokens}")
        print(f"\n| 排名 | 姓名 | 角色 | 公司 | 模型 | Token | 贡献度 |")
        print(f"|------|------|------|------|------|-------|--------|")
        
        medals = ["🥇", "🥈", "🥉", "  ", "  ", "  ", "  ", "  "]
        
        for i, m in enumerate(sorted_members):
            token = m.get("tokens", 0)
            if token > 0:
                contribution = (token / total_tokens) * 100
                print(f"| {medals[i]} | {m['name']} | {m['role']} | {m['company'][:4]} | {m['model_name'][:12]} | {token} | {contribution:.1f}% |")
            else:
                print(f"| {medals[i]} | {m['name']} | {m['role']} | {m['company'][:4]} | {m['model_name'][:12]} | 0 | 0.0% |")
    
    # 公司统计
    print("\n" + "=" * 80)
    print("🏢 公司贡献统计")
    print("=" * 80)
    
    company_stats = {}
    for m in TEAM:
        token = m.get("tokens", 0)
        company = m["company"]
        if company not in company_stats:
            company_stats[company] = {"tokens": 0, "members": 0}
        company_stats[company]["tokens"] += token
        company_stats[company]["members"] += 1
    
    print(f"\n| 公司 | 成员数 | Token消耗 | 占比 |")
    print(f"|------|--------|-----------|------|")
    
    for company, stats in company_stats.items():
        pct = (stats["tokens"] / total_tokens * 100) if total_tokens > 0 else 0
        print(f"| {company} | {stats['members']} | {stats['tokens']} | {pct:.1f}% |")
    
    # 总结
    print("\n" + "=" * 80)
    print("📋 拟人化汇报总结")
    print("=" * 80)
    
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎵 Symphony 拟人化汇报 v{VERSION}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  👥 在岗人数: {len(successful_members)}/{len(TEAM)}
  🏢 参与公司: {len(company_stats)}
  💰 总Token消耗: {total_tokens}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    return {
        "version": VERSION,
        "datetime": datetime.now().isoformat(),
        "team": TEAM,
        "total_tokens": total_tokens,
        "company_stats": company_stats
    }


if __name__ == "__main__":
    report = humanized_report()
    
    with open("humanized_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 报告已保存: humanized_report.json")
    print("\nSymphony - 智韵交响，共创华章！")
