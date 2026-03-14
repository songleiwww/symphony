#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v1.2.0 - Dynamic Model Dispatcher
根据用户输入动态分析，智能适配不同数量的协作人员
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


# 角色定义（可动态组合）
AVAILABLE_ROLES = {
    "产品经理": {"keywords": ["产品", "需求", "规划", "设计"], "weight": 1.0},
    "架构师": {"keywords": ["架构", "设计", "技术选型", "系统"], "weight": 1.2},
    "开发工程师": {"keywords": ["开发", "编程", "代码", "实现", "构建"], "weight": 1.0},
    "测试工程师": {"keywords": ["测试", "验证", "质量", "Bug"], "weight": 0.8},
    "运维工程师": {"keywords": ["运维", "部署", "监控", "维护"], "weight": 0.8},
    "产品运营": {"keywords": ["运营", "增长", "用户", "推广"], "weight": 0.8},
    "安全工程师": {"keywords": ["安全", "加密", "权限"], "weight": 0.6},
    "数据分析师": {"keywords": ["分析", "数据", "统计", "报告"], "weight": 0.7},
    "UI设计师": {"keywords": ["界面", "UI", "设计", "美观"], "weight": 0.5},
    "算法工程师": {"keywords": ["算法", "AI", "机器学习", "模型"], "weight": 0.8},
}


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def analyze_intent_dynamic(user_input):
    """动态分析用户意图，返回需要的角色列表"""
    input_lower = user_input.lower()
    
    # 计算每个角色的匹配度
    role_scores = {}
    for role, config in AVAILABLE_ROLES.items():
        score = 0
        for keyword in config["keywords"]:
            if keyword in input_lower:
                score += config["weight"]
        if score > 0:
            role_scores[role] = score
    
    # 根据得分排序，返回需要的角色（最多6个）
    sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
    
    # 根据任务复杂度动态调整团队规模
    team_size = min(6, max(2, len(sorted_roles)))
    
    # 如果没有匹配，返回默认角色
    if not sorted_roles:
        return ["产品经理", "架构师", "开发工程师"], 3
    
    selected_roles = [r[0] for r in sorted_roles[:team_size]]
    
    return selected_roles, team_size


def select_models_for_roles(roles):
    """为角色列表选择合适的模型"""
    models = []
    enabled = get_enabled_models()
    
    # 角色到模型索引的映射
    role_to_index = {
        "架构师": 1,
        "开发工程师": 6,
        "测试工程师": 8,
        "运维工程师": 9,
        "产品运营": 10,
        "算法工程师": 8,
        "数据分析师": 0,
        "产品经理": 0,
        "安全工程师": 1,
        "UI设计师": 0,
    }
    
    used_indices = set()
    for role in roles:
        idx = role_to_index.get(role, 0)
        # 确保不重复使用模型
        while idx in used_indices and idx < len(enabled):
            idx += 1
        if idx < len(enabled):
            models.append({"role": role, "config": enabled[idx], "index": idx})
            used_indices.add(idx)
    
    return models


def call_api(model_config, prompt, max_tokens=300):
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


def dynamic_dispatch(user_input):
    """动态调度主函数"""
    print("=" * 70)
    print("Symphony v1.2.0 - Dynamic Model Dispatcher")
    print("=" * 70)
    
    # 1. 动态分析用户意图
    print("\n[1] 动态分析用户意图...")
    print("    用户输入: {}".format(user_input))
    
    roles, team_size = analyze_intent_dynamic(user_input)
    print("    动态团队规模: {} 人".format(team_size))
    print("    适配角色: {}".format(", ".join(roles)))
    
    # 2. 智能选择模型
    print("\n[2] 智能选择适配模型...")
    role_models = select_models_for_roles(roles)
    
    for i, rm in enumerate(role_models):
        print("    【{}】-> {} ({})".format(rm["role"], rm["config"].get("alias"), rm["config"].get("provider")))
    
    # 3. 并行执行
    print("\n[3] 并行执行任务...")
    
    prompts = []
    for role in roles:
        prompts.append("作为{}，请简洁回复用户问题：{}".format(role, user_input))
    
    results = []
    threads = []
    
    def call_model(i, config, prompt):
        r = call_api(config, prompt)
        results.append({"index": i, "role": roles[i], "result": r})
    
    for i, (config, prompt) in enumerate(zip([rm["config"] for rm in role_models], prompts)):
        t = threading.Thread(target=call_model, args=(i, config, prompt))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # 4. 汇总结果
    print("\n[4] 动态协作结果:")
    total_tokens = 0
    success_count = 0
    for r in sorted(results, key=lambda x: x["index"]):
        role = r["role"]
        result = r["result"]
        if result.get("success"):
            total_tokens += result.get("tokens", 0)
            success_count += 1
            print("\n  【{}】: ✅ ({} tokens)".format(role, result.get("tokens", 0)))
            print("    {}".format(result.get("content", "")[:120]))
        else:
            print("\n  【{}】: ❌ {}".format(role, result.get("error", "Unknown")))
    
    # 5. 生成报告
    report = {
        "user_input": user_input,
        "team_size": team_size,
        "roles": roles,
        "results_count": len(results),
        "success_count": success_count,
        "total_tokens": total_tokens
    }
    
    print("\n" + "=" * 70)
    print("动态调度完成 - 团队: {}人 | 成功: {} | Tokens: {}".format(
        team_size, success_count, total_tokens))
    print("=" * 70)
    
    return report


# 测试不同场景
test_inputs = [
    "交响 开发一个图片识别系统",      # 需要: 开发+算法+架构
    "交响 优化系统性能",              # 需要: 架构+开发+运维
    "交响 分析用户行为报告",           # 需要: 数据分析+产品运营+产品经理
    "交响 部署上线",                   # 需要: 运维+开发
    "交响 编写安全方案",               # 需要: 安全+架构
    "交响 界面美化",                   # 需要: UI设计
    "交响 写代码",                     # 仅需: 开发
    "交响 多模型协作",                 # 默认团队
]

print("\n" + "=" * 70)
print("Testing Dynamic Dispatcher")
print("=" * 70)

all_reports = []
for test_input in test_inputs:
    print("\n")
    report = dynamic_dispatch(test_input)
    all_reports.append(report)
    time.sleep(0.5)

# 保存报告
with open("dynamic_dispatch_report.json", "w", encoding="utf-8") as f:
    json.dump(all_reports, f, ensure_ascii=False, indent=2)

print("\n\nReport saved: dynamic_dispatch_report.json")
print("\nSymphony - 智韵交响，共创华章！")
