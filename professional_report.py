#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v1.6.0 - Professional Work Report
人性化、职业化汇报：人员、模型、Token、工作内容
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


# 专业汇报团队
REPORT_TEAM = [
    {"name": "林思远", "role": "产品经理", "emoji": "PE", "model_index": 0, "provider": "智谱GLM-4-Flash", "tokens": 0, "works": [], "code": []},
    {"name": "陈美琪", "role": "架构师", "emoji": "AR", "model_index": 1, "provider": "智谱GLM-Z1-Flash", "tokens": 0, "works": [], "code": []},
    {"name": "王浩然", "role": "开发工程师", "emoji": "DEV", "model_index": 6, "provider": "ModelScope GLM-4.7", "tokens": 0, "works": [], "code": []},
    {"name": "刘心怡", "role": "测试工程师", "emoji": "TEST", "model_index": 8, "provider": "ModelScope DeepSeek-V3.2", "tokens": 0, "works": [], "code": []},
    {"name": "张明远", "role": "运维工程师", "emoji": "OPS", "model_index": 9, "provider": "ModelScope Qwen3-Coder", "tokens": 0, "works": [], "code": []},
    {"name": "赵敏", "role": "产品运营", "emoji": "PO", "model_index": 10, "provider": "ModelScope Qwen3-235B", "tokens": 0, "works": [], "code": []},
]


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_config, prompt, max_tokens=350):
    url = model_config["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model_config["api_key"], "Content-Type": "application/json"}
    data = {"model": model_config["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    t0 = time.time()
    try:
        r = requests.post(url, headers=headers, json=data, timeout=25)
        elapsed = time.time() - t0
        if r.status_code == 200:
            j = r.json()
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": j.get("usage", {}).get("total_tokens", 0), "time": elapsed}
        else:
            return {"success": False, "error": "HTTP " + str(r.status_code)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def professional_report():
    """生成职业化工作汇报"""
    
    print("=" * 80)
    print("🎼 Symphony v1.6.0 - 专业工作汇报")
    print("=" * 80)
    
    enabled = get_enabled_models()
    for m in REPORT_TEAM:
        idx = m["model_index"]
        if idx < len(enabled):
            m["provider"] = enabled[idx].get("alias", enabled[idx].get("name"))
    
    # Round 1: 每人汇报工作
    print("\n" + "=" * 80)
    print("📋 第一部分：各成员工作汇报")
    print("=" * 80)
    
    work_prompts = [
        "作为产品经理，汇报今天完成的工作任务和成果（简洁50字）",
        "作为架构师，汇报今天完成的工作任务和成果（简洁50字）",
        "作为开发工程师，汇报今天完成的工作任务和成果（简洁50字）",
        "作为测试工程师，汇报今天完成的工作任务和成果（简洁50字）",
        "作为运维工程师，汇报今天完成的工作任务和成果（简洁50字）",
        "作为产品运营，汇报今天完成的工作任务和成果（简洁50字）",
    ]
    
    results1 = []
    threads = []
    
    def call_work(i, prompt):
        idx = REPORT_TEAM[i]["model_index"]
        enabled = get_enabled_models()
        if idx < len(enabled):
            r = call_api(enabled[idx], prompt)
            results1.append({"index": i, "result": r})
    
    for i, prompt in enumerate(work_prompts):
        t = threading.Thread(target=call_work, args=(i, prompt))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    total_tokens = 0
    
    print("\n【团队成员工作详情】\n")
    
    for r in sorted(results1, key=lambda x: x["index"]):
        i = r["index"]
        m = REPORT_TEAM[i]
        result = r["result"]
        
        if result.get("success"):
            tokens = result.get("tokens", 0)
            m["tokens"] += tokens
            total_tokens += tokens
            content = result.get("content", "")
            m["works"].append(content)
            
            print("-" * 60)
            print(f"👤 {m['name']} | {m['role']}")
            print(f"🖥️  使用模型: {m['provider']}")
            print(f"🔢 消耗Token: {tokens}")
            print(f"📝 工作内容:")
            print(f"   {content[:200]}")
        else:
            print(f"\n👤 {m['name']} | {m['role']} - API调用失败")
    
    # Round 2: 代码处理汇报
    print("\n" + "=" * 80)
    print("💻 第二部分：代码处理汇报")
    print("=" * 80)
    
    code_prompts = [
        "作为产品经理，列出今天参与编写的代码文件或模块（简洁列出）",
        "作为架构师，列出今天参与设计的代码结构或架构（简洁列出）",
        "作为开发工程师，列出今天编写或修改的代码文件（简洁列出）",
        "作为测试工程师，列出今天编写或执行的测试用例（简洁列出）",
        "作为运维工程师，列出今天编写或修改的配置/脚本（简洁列出）",
        "作为产品运营，今天协助完成了哪些产品支持工作（简洁列出）",
    ]
    
    results2 = []
    threads2 = []
    
    def call_code(i, prompt):
        idx = REPORT_TEAM[i]["model_index"]
        enabled = get_enabled_models()
        if idx < len(enabled):
            r = call_api(enabled[idx], prompt)
            results2.append({"index": i, "result": r})
    
    for i, prompt in enumerate(code_prompts):
        t = threading.Thread(target=call_code, args=(i, prompt))
        threads2.append(t)
        t.start()
    
    for t in threads2:
        t.join()
    
    print("\n【代码/文件处理详情】\n")
    
    for r in sorted(results2, key=lambda x: x["index"]):
        i = r["index"]
        m = REPORT_TEAM[i]
        result = r["result"]
        
        if result.get("success"):
            tokens = result.get("tokens", 0)
            m["tokens"] += tokens
            total_tokens += tokens
            content = result.get("content", "")
            m["code"].append(content)
            
            print("-" * 60)
            print(f"👤 {m['name']} | {m['role']}")
            print(f"📄 处理文件/模块:")
            lines = content.split('\n')[:5]
            for line in lines:
                if line.strip():
                    print(f"   • {line.strip()[:80]}")
        else:
            print(f"\n👤 {m['name']} - 无数据")
    
    # Round 3: 总结
    print("\n" + "=" * 80)
    print("📊 第三部分：团队总结")
    print("=" * 80)
    
    summary_prompt = "作为团队负责人，总结今天6位成员的整体工作成果和团队贡献（100字）"
    idx = REPORT_TEAM[0]["model_index"]
    enabled = get_enabled_models()
    if idx < len(enabled):
        summary_result = call_api(enabled[idx], summary_prompt, 200)
        if summary_result.get("success"):
            print(f"\n【团队总结】")
            print(f"   {summary_result.get('content', '')}")
            total_tokens += summary_result.get("tokens", 0)
    
    # 最终排名
    print("\n" + "=" * 80)
    print("🏆 第四部分：贡献排名")
    print("=" * 80)
    
    sorted_team = sorted(REPORT_TEAM, key=lambda x: x.get("tokens", 0), reverse=True)
    
    print("\n【Token消耗排名】\n")
    medals = ["🥇", "🥈", "🥉", "  ", "  ", "  "]
    for i, m in enumerate(sorted_team):
        token = m.get("tokens", 0)
        if token > 0:
            print(f"  {medals[i]} {m['name']} | {m['role']} | {m['provider']} | {token} tokens")
        else:
            print(f"  {medals[i]} {m['name']} | {m['role']} | API未调用")
    
    # 详细表格
    print("\n" + "=" * 80)
    print("📋 完整工作汇报表")
    print("=" * 80)
    
    print("\n| 序号 | 姓名 | 角色 | 使用模型 | Token消耗 | 工作状态 |")
    print("|------|------|------|----------|-----------|----------|")
    for i, m in enumerate(REPORT_TEAM, 1):
        status = "✅ 正常" if m.get("tokens", 0) > 0 else "❌ 失败"
        print(f"| {i} | {m['name']} | {m['role']} | {m['provider'][:15]} | {m.get('tokens', 0)} | {status} |")
    
    print("\n" + "=" * 80)
    print(f"📈 团队总Token消耗: {total_tokens}")
    print("=" * 80)
    
    return {
        "team": REPORT_TEAM,
        "total_tokens": total_tokens
    }


if __name__ == "__main__":
    result = professional_report()
    
    # 保存报告
    with open("professional_report.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n\n✅ 报告已保存: professional_report.json")
    print("\nSymphony - 智韵交响，共创华章！")
