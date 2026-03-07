#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v2.1.0 - 自动进化技能改进讨论会
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


VERSION = "2.1.0"

DISCUSSION_TEAM = [
    {"name": "林思远", "role": "产品经理", "model_index": 0},
    {"name": "陈美琪", "role": "架构师", "model_index": 1},
    {"name": "王浩然", "role": "开发工程师", "model_index": 10},
    {"name": "赵敏", "role": "产品运营", "model_index": 12},
]


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_config, prompt, max_tokens=300):
    url = model_config["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model_config["api_key"], "Content-Type": "application/json"}
    data = {"model": model_config["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    try:
        r = requests.post(url, headers=headers, json=data, timeout=20)
        if r.status_code == 200:
            j = r.json()
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": j.get("usage", {}).get("total_tokens", 0)}
        else:
            return {"success": False, "error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)[:50]}


print("=" * 70)
print(f"🎼 Symphony v{VERSION} - 自动进化技能改进讨论会")
print("=" * 70)

enabled = get_enabled_models()

# Round 1: 当前技能现状分析
print("\n[Round 1] 当前技能现状分析")
print("-" * 50)

current_skills = """
当前已实现的技能：
1. 被动触发引擎 - 多模式智能触发
2. 真正多模型协作 - 并行调用不同模型
3. 模型验证系统 - 真实API调用验证
4. 技能有效性验证 - 技能测试与优化
5. 多模型类型正确使用 - 图像/向量/排序模型
6. Debug追踪系统 - Bug检测与修复
7. 自动发布系统 - GitHub自动发布
8. 调度容错改进 - 错误处理与降级
9. 记忆协调系统 - OpenClaw同步
10. 限流检测与自动恢复 - 429处理
11. 标准化汇报系统 - Tokens明细/模型状态/限流恢复
"""
print(current_skills)

# Round 2: 改进建议
print("\n[Round 2] 各专家改进建议")
print("-" * 50)

suggestions = []

prompts = [
    (0, "作为产品经理，分析当前技能哪些需要改进？提出3个最优先的改进方向（80字）"),
    (1, "作为架构师，从技术角度分析系统需要哪些新技能来提升能力（80字）"),
    (10, "作为开发工程师，列出代码层面可以自动化的技能（80字）"),
    (12, "作为产品运营，从用户角度思考需要什么新功能（80字）"),
]

results = []
threads = []

def get_suggestion(idx, prompt):
    enabled = get_enabled_models()
    if idx < len(enabled):
        r = call_api(enabled[idx], prompt)
        results.append({"idx": idx, "result": r})

for idx, prompt in prompts:
    t = threading.Thread(target=get_suggestion, args=(idx, prompt))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

for r in results:
    idx = r["idx"]
    member = DISCUSSION_TEAM[idx] if idx < len(DISCUSSION_TEAM) else {"name": "未知", "role": "未知"}
    result = r["result"]
    
    if result.get("success"):
        content = result.get("content", "")
        tokens = result.get("tokens", 0)
        print(f"\n【{member['role']} {member['name']}】")
        print(f"  {content[:150]}")
        print(f"  🔢 {tokens} tokens")
        suggestions.append({"role": member["role"], "content": content, "tokens": tokens})
    else:
        print(f"\n【{member['role']}】调用失败")

# Round 3: 总结新技能需求
print("\n[Round 3] 新技能需求总结")
print("-" * 50)

summary_prompt = "总结以上4位专家的建议，提炼出5个最需要发展的新技能（100字）"
if 0 < len(enabled):
    summary = call_api(enabled[0], summary_prompt, 150)
    if summary.get("success"):
        print("\n【新技能需求清单】")
        print(f"  {summary.get('content', '')}")

# 技能发展建议
print("\n【技能发展建议】")
new_skills = """
1. 🔄 自动代码优化技能
   - 自动分析代码质量
   - 提出优化建议
   - 自动修复常见问题

2. 📊 智能数据分析技能
   - 自动分析项目状态
   - 生成趋势报告
   - 预测潜在问题

3. 🎯 意图理解增强技能
   - 更精准识别用户意图
   - 上下文理解
   - 多轮对话管理

4. 🛡️ 安全审计技能
   - 代码安全扫描
   - 漏洞检测
   - 权限检查

5. 📚 文档自动生成技能
   - API文档自动生成
   - 代码注释增强
   - README自动维护
"""
print(new_skills)

print("\n" + "=" * 70)
print("讨论会结束")
print("=" * 70)

# 保存报告
report = {
    "version": VERSION,
    "datetime": datetime.now().isoformat(),
    "current_skills": current_skills,
    "suggestions": suggestions,
    "new_skills": new_skills
}

with open("evolution_discussion_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("\n✅ 报告已保存: evolution_discussion_report.json")
print("\nSymphony - 智韵交响，共创华章！")
