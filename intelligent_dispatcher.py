#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v1.1.0 - Intelligent Model Dispatcher
根据用户输入分析意图，智能适配模型和协作人员
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


# 触发条件配置
TRIGGER_CONDITIONS = {
    # P0: 核心功能触发
    "P0_核心": {
        "keywords": ["交响", "symphony", "多模型", "协作"],
        "team_size": 6,
        "roles": ["产品经理", "架构师", "开发工程师", "测试工程师", "运维工程师", "产品运营"],
        "description": "完整多模型协作"
    },
    # P1: 开发相关
    "P1_开发": {
        "keywords": ["开发", "研发", "实现", "构建", "编程", "代码"],
        "team_size": 3,
        "roles": ["架构师", "开发工程师", "测试工程师"],
        "description": "开发团队协作"
    },
    # P2: 优化相关
    "P2_优化": {
        "keywords": ["优化", "改进", "改善", "提升", "增强"],
        "team_size": 2,
        "roles": ["架构师", "开发工程师"],
        "description": "技术优化"
    },
    # P3: 分析相关
    "P3_分析": {
        "keywords": ["分析", "调研", "评估", "检查"],
        "team_size": 3,
        "roles": ["产品经理", "测试工程师", "产品运营"],
        "description": "分析调研"
    },
    # P4: 文档相关
    "P4_文档": {
        "keywords": ["文档", "说明", "指南", "手册"],
        "team_size": 2,
        "roles": ["产品经理", "文档工程师"],
        "description": "文档编写"
    },
    # P5: 运维相关
    "P5_运维": {
        "keywords": ["部署", "运维", "监控", "维护"],
        "team_size": 2,
        "roles": ["运维工程师", "开发工程师"],
        "description": "运维支持"
    }
}

# 模型类型适配
MODEL_TYPE适配 = {
    "文本对话": {"model_index": 0, "provider": "zhipu"},
    "推理分析": {"model_index": 1, "provider": "zhipu"},
    "图像理解": {"model_index": 2, "provider": "zhipu"},
    "图像生成": {"model_index": 4, "provider": "zhipu"},
    "代码开发": {"model_index": 6, "provider": "modelscope"},
    "深度思考": {"model_index": 8, "provider": "modelscope"},
}


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def analyze_intent(user_input):
    """分析用户输入意图"""
    input_lower = user_input.lower()
    
    # 匹配触发条件
    matched_conditions = []
    for level, config in TRIGGER_CONDITIONS.items():
        for keyword in config["keywords"]:
            if keyword in input_lower:
                matched_conditions.append((level, config))
                break
    
    # 返回最高优先级匹配
    if matched_conditions:
        return matched_conditions[0]
    
    # 默认返回P0
    return ("P0_核心", TRIGGER_CONDITIONS["P0_核心"])


def select_models_by_intent(intent):
    """根据意图选择合适的模型"""
    models = []
    enabled = get_enabled_models()
    
    # 根据角色需求选择模型
    for role in intent.get("roles", []):
        if "架构师" in role and len(enabled) > 1:
            models.append(enabled[1])
        elif "开发工程师" in role and len(enabled) > 6:
            models.append(enabled[6])
        elif "测试工程师" in role and len(enabled) > 8:
            models.append(enabled[8])
        elif "运维工程师" in role and len(enabled) > 9:
            models.append(enabled[9])
        elif "产品运营" in role and len(enabled) > 10:
            models.append(enabled[10])
        else:
            models.append(enabled[0])
    
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


def intelligent_dispatch(user_input):
    """智能调度主函数"""
    print("=" * 70)
    print("Symphony v1.1.0 - Intelligent Model Dispatcher")
    print("=" * 70)
    
    # 1. 分析用户意图
    print("\n[1] 分析用户意图...")
    print("    用户输入: {}".format(user_input))
    
    intent_level, intent_config = analyze_intent(user_input)
    print("    匹配触发: {} - {}".format(intent_level, intent_config["description"]))
    print("    团队规模: {} 人".format(intent_config["team_size"]))
    print("    角色分配: {}".format(", ".join(intent_config["roles"])))
    
    # 2. 选择合适模型
    print("\n[2] 选择适配模型...")
    models = select_models_by_intent(intent_config)
    
    for i, m in enumerate(models):
        print("    Model-{}: {} ({})".format(i+1, m.get("alias", m.get("name")), m.get("provider")))
    
    # 3. 并行调用
    print("\n[3] 执行协作任务...")
    
    prompts = []
    for role in intent_config["roles"]:
        prompts.append("作为{}，请回复用户: {}".format(role, user_input))
    
    results = []
    threads = []
    
    def call_model(i, config, prompt):
        r = call_api(config, prompt)
        results.append({"index": i, "role": intent_config["roles"][i], "result": r})
    
    for i, (config, prompt) in enumerate(zip(models, prompts)):
        t = threading.Thread(target=call_model, args=(i, config, prompt))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # 4. 汇总结果
    print("\n[4] 协作结果汇总:")
    total_tokens = 0
    for r in sorted(results, key=lambda x: x["index"]):
        role = r["role"]
        result = r["result"]
        if result.get("success"):
            total_tokens += result.get("tokens", 0)
            print("\n  【{}】: OK ({} tokens)".format(role, result.get("tokens", 0)))
            print("    {}".format(result.get("content", "")[:150]))
        else:
            print("\n  【{}】: FAILED".format(role))
    
    # 5. 返回调度报告
    report = {
        "user_input": user_input,
        "intent_level": intent_level,
        "intent_description": intent_config["description"],
        "team_size": intent_config["team_size"],
        "roles": intent_config["roles"],
        "results": results,
        "total_tokens": total_tokens
    }
    
    print("\n" + "=" * 70)
    print("调度完成 - 总Token消耗: {}".format(total_tokens))
    print("=" * 70)
    
    return report


# 测试不同场景
test_inputs = [
    "交响 开发一个图片识别系统",
    "交响 优化系统性能",
    "交响 分析用户行为报告",
    "交响 编写部署文档",
    "交响 系统监控告警",
]

print("\n" + "=" * 70)
print("Testing Intelligent Dispatcher")
print("=" * 70)

all_reports = []
for test_input in test_inputs:
    print("\n\n")
    report = intelligent_dispatch(test_input)
    all_reports.append(report)

# 保存报告
with open("intelligent_dispatch_report.json", "w", encoding="utf-8") as f:
    json.dump(all_reports, f, ensure_ascii=False, indent=2)

print("\n\nReport saved: intelligent_dispatch_report.json")
print("\nSymphony - 智韵交响，共创华章！")
