#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v3.0.0 - 多模型拟人化协同合作系统
参考方案：总策划·策导君 | 创意官·灵感师 | 执行师·实干家 | 分析师·数据官 | 外交官·沟通师

5角色团队式AI协作体系，实现从创意、执行、优化到落地的全流程闭环
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


VERSION = "3.0.0"


# ============ 5角色团队配置 ============
TEAM = [
    {
        "id": 0,
        "name": "策导君",
        "role": "总策划",
        "company": "智谱AI",
        "model_name": "GLM-4-Flash",
        "model_id": 0,
        "personality": "沉稳理性、严谨简洁、指令清晰",
        "duty": "项目总负责人、战略决策者，把控方向、拆解任务、统筹分工、审核成果",
        "workflow": "需求对接→创意输出→落地细化→逻辑校验→受众适配→终审交付"
    },
    {
        "id": 1,
        "name": "灵感师",
        "role": "创意官",
        "company": "智谱AI",
        "model_name": "GLM-Z1-Flash",
        "model_id": 1,
        "personality": "活泼感性、脑洞大、创意无限",
        "duty": "产出创意点子、撰写文案初稿、设计风格方向、打造记忆点",
        "workflow": "接收总策划指令→输出创意方向→传递给执行师"
    },
    {
        "id": 2,
        "name": "实干家",
        "role": "执行师",
        "company": "智谱AI",
        "model_name": "GLM-4V-Flash",
        "model_id": 3,
        "personality": "务实耐心、注重细节、执行力强",
        "duty": "将创意转化为标准化成果、修正错误、优化排版、补充细节",
        "workflow": "接收创意内容→润色优化→提交分析师校验"
    },
    {
        "id": 12,
        "name": "数据官",
        "role": "分析师",
        "company": "ModelScope",
        "model_name": "MiniMax-M2.5",
        "model_id": 12,
        "personality": "理性客观、数据说话、擅长找问题",
        "duty": "数据分析、可行性评估、风险评估、逻辑校验、优化建议",
        "workflow": "接收执行师内容→数据校验→反馈修改建议→外交官适配"
    },
    {
        "id": 15,
        "name": "沟通师",
        "role": "外交官",
        "company": "ModelScope",
        "model_name": "DeepSeek R1",
        "model_id": 15,
        "personality": "温和共情、换位思考、亲和力强",
        "duty": "优化沟通话术、对接需求、解答疑问、调整内容适配受众",
        "workflow": "接收分析师校验→受众适配→总策划终审→交付"
    }
]


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_index: int, prompt: str, max_tokens=300):
    enabled = get_enabled_models()
    if model_index >= len(enabled):
        return None
    
    model = enabled[model_index]
    url = model["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model["api_key"], "Content-Type": "application/json"}
    data = {"model": model["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=20)
        if r.status_code == 200:
            j = r.json()
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": j.get("usage", {}).get("total_tokens", 0)}
    except Exception as e:
        pass
    return None


def collaborative_workflow(user_task: str):
    """6步标准化协同流程"""
    
    print("=" * 80)
    print(f"🎼 Symphony v{VERSION} - 多模型拟人化协同合作")
    print("=" * 80)
    
    results = {}
    total_tokens = 0
    
    # ============ Step 1: 需求对接（总策划+外交官）============
    print("\n" + "─" * 80)
    print("📋 第一步：需求对接（策导君 + 沟通师）")
    print("─" * 80)
    
    # 外交官梳理需求
    prompt_diplomat = f"""你是沟通师（外交官），请用温和共情的方式梳理用户需求：
    
用户任务：{user_task}

请：
1. 理解用户核心需求
2. 用亲和的语气确认关键点
3. 明确交付要求

（50字以内）"""
    
    result = call_api(15, prompt_diplomat, 100)
    if result:
        results["diplomat"] = result
        total_tokens += result.get("tokens", 0)
        print(f"\n💬 沟通师（沟通师）: {result['content'][:100]}")
    
    # 总策划制定方案
    prompt_planner = f"""你是总策划（策导君），请制定项目方案：

用户任务：{user_task}

请：
1. 制定项目目标
2. 拆解任务流程
3. 确定分工方案
4. 设定时间节点

（80字以内）"""
    
    result = call_api(0, prompt_planner, 150)
    if result:
        results["planner"] = result
        total_tokens += result.get("tokens", 0)
        print(f"\n🎯 总策划（策导君）: {result['content'][:150]}")
    
    # ============ Step 2: 创意输出（创意官）============
    print("\n" + "─" * 80)
    print("💡 第二步：创意输出（灵感师）")
    print("─" * 80)
    
    prompt_creative = f"""你是创意官（灵感师），请产出创意：

总策划方案：{results.get('planner', {}).get('content', '')[:100]}

请：
1. 产出创意方向
2. 撰写内容框架
3. 设计风格方向
4. 打造记忆点

（120字以内）"""
    
    result = call_api(1, prompt_creative, 200)
    if result:
        results["creative"] = result
        total_tokens += result.get("tokens", 0)
        print(f"\n💡 创意官（灵感师）: {result['content'][:200]}")
    
    # ============ Step 3: 落地细化（执行师）============
    print("\n" + "─" * 80)
    print("🔧 第三步：落地细化（实干家）")
    print("─" * 80)
    
    prompt_executor = f"""你是执行师（实干家），请细化创意：

创意内容：{results.get('creative', {}).get('content', '')[:100]}

请：
1. 标准化格式输出
2. 补充细节内容
3. 优化排版布局
4. 修正语法错误

（150字以内）"""
    
    result = call_api(2, prompt_executor, 250)
    if result:
        results["executor"] = result
        total_tokens += result.get("tokens", 0)
        print(f"\n🔧 执行师（实干家）: {result['content'][:250]}")
    
    # ============ Step 4: 逻辑校验（分析师）============
    print("\n" + "─" * 80)
    print("📊 第四步：逻辑校验（数据官）")
    print("─" * 80)
    
    prompt_analyst = f"""你是分析师（数据官），请校验内容：

执行内容：{results.get('executor', {}).get('content', '')[:100]}

请：
1. 数据可行性分析
2. 逻辑完整性校验
3. 风险评估
4. 提出修改建议

（120字以内）"""
    
    result = call_api(12, prompt_analyst, 200)
    if result:
        results["analyst"] = result
        total_tokens += result.get("tokens", 0)
        print(f"\n📊 分析师（数据官）: {result['content'][:200]}")
    
    # ============ Step 5: 受众适配（外交官）============
    print("\n" + "─" * 80)
    print("🤝 第五步：受众适配（沟通师）")
    print("─" * 80)
    
    prompt_diplomat2 = f"""你是沟通师（外交官），请适配受众：

分析师建议：{results.get('analyst', {}).get('content', '')[:100]}
原始内容：{results.get('executor', {}).get('content', '')[:80]}

请：
1. 优化沟通话术
2. 调整语气风格
3. 适配目标受众
4. 增强亲和力

（100字以内）"""
    
    result = call_api(15, prompt_diplomat2, 150)
    if result:
        results["diplomat2"] = result
        total_tokens += result.get("tokens", 0)
        print(f"\n🤝 外交官（沟通师）: {result['content'][:150]}")
    
    # ============ Step 6: 终审交付（总策划）============
    print("\n" + "─" * 80)
    print("✅ 第六步：终审交付（策导君）")
    print("─" * 80)
    
    prompt_final = f"""你是总策划（策导君），请终审交付：

外交官适配后：{results.get('diplomat2', {}).get('content', '')[:100]}
分析师建议：{results.get('analyst', {}).get('content', '')[:80]}

请：
1. 统筹所有环节
2. 审核最终成果
3. 确认符合需求
4. 正式交付

（80字以内）"""
    
    result = call_api(0, prompt_final, 120)
    if result:
        results["final"] = result
        total_tokens += result.get("tokens", 0)
        print(f"\n✅ 总策划（策导君）: {result['content'][:150]}")
    
    # ============ 总结 ============
    print("\n" + "=" * 80)
    print("📋 协同合作总结")
    print("=" * 80)
    
    # 角色贡献统计
    role_tokens = {
        "策导君": results.get("planner", {}).get("tokens", 0) + results.get("final", {}).get("tokens", 0),
        "灵感师": results.get("creative", {}).get("tokens", 0),
        "实干家": results.get("executor", {}).get("tokens", 0),
        "数据官": results.get("analyst", {}).get("tokens", 0),
        "沟通师": results.get("diplomat", {}).get("tokens", 0) + results.get("diplomat2", {}).get("tokens", 0)
    }
    
    print(f"\n👥 团队贡献统计:")
    print(f"\n| 角色 | 拟人名 | 公司 | 模型 | Token |")
    print(f"|------|--------|------|------|-------|")
    
    for member in TEAM:
        name = member["name"]
        token = role_tokens.get(name, 0)
        print(f"| {member['role']} | {name} | {member['company'][:4]} | {member['model_name'][:12]} | {token} |")
    
    print(f"\n💰 总Token消耗: {total_tokens}")
    
    return {
        "version": VERSION,
        "datetime": datetime.now().isoformat(),
        "task": user_task,
        "team": TEAM,
        "results": {k: v.get("content", "")[:200] for k, v in results.items()},
        "role_tokens": role_tokens,
        "total_tokens": total_tokens
    }


def show_team_intro():
    """展示团队介绍"""
    
    print("=" * 80)
    print("🎼 Symphony v3.0.0 - 多模型拟人化协同合作团队")
    print("=" * 80)
    
    print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│                    5角色团队式AI协作体系                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  总策划·策导君 | 创意官·灵感师 | 执行师·实干家 | 分析师·数据官 | 外交官·沟通师  │
└─────────────────────────────────────────────────────────────────────────────┘
""")
    
    for member in TEAM:
        print(f"""
👤 {member['role']} · {member['name']}
   公司：{member['company']} | 模型：{member['model_name']}
   性格：{member['personality']}
   职责：{member['duty']}
   流程：{member['workflow']}
""")
    
    print("""
📋 协同合作流程（标准化闭环）:

  ┌─────────────────────┐
  │ ①需求对接           │
  │ 策导君 + 沟通师     │
  └──────────┬──────────┘
             ▼
  ┌─────────────────────┐
  │ ②创意输出           │
  │ 灵感师              │
  └──────────┬──────────┘
             ▼
  ┌─────────────────────┐
  │ ③落地细化           │
  │ 实干家              │
  └──────────┬──────────┘
             ▼
  ┌─────────────────────┐
  │ ④逻辑校验           │
  │ 数据官              │
  └──────────┬──────────┘
             ▼
  ┌─────────────────────┐
  │ ⑤受众适配           │
  │ 沟通师              │
  └──────────┬──────────┘
             ▼
  ┌─────────────────────┐
  │ ⑥终审交付           │
  │ 策导君              │
  └─────────────────────┘
""")


if __name__ == "__main__":
    # 展示团队
    show_team_intro()
    
    # 示例任务
    test_task = "请帮我写一篇关于AI多模型协作的商业策划案"
    
    print("\n" + "=" * 80)
    print(f"🧪 测试任务: {test_task}")
    print("=" * 80)
    
    # 执行协作流程
    report = collaborative_workflow(test_task)
    
    # 保存报告
    with open("collaborative_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 报告已保存: collaborative_report.json")
    print("\nSymphony - 智韵交响，共创华章！")
