#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响v2.0 - 真实模型协作开发
使用真实API调用，每个模型都有真实的Token统计
"""

import sys
import json
import time
import requests
from datetime import datetime
from config import MODEL_CHAIN

# Windows编码修复
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# =============================================================================
# 6位专家模型配置（使用真实API）
# =============================================================================

MODELS = [
    {
        "name": "林思远",
        "role": "产品经理",
        "emoji": "📋",
        "model_config": None,  # 稍后填充
        "tasks_completed": 0,
        "total_tokens": 0,
        "total_response_time": 0,
        "responses": []
    },
    {
        "name": "陈美琪",
        "role": "架构师",
        "emoji": "🏗️",
        "model_config": None,
        "tasks_completed": 0,
        "total_tokens": 0,
        "total_response_time": 0,
        "responses": []
    },
    {
        "name": "王浩然",
        "role": "开发工程师",
        "emoji": "💻",
        "model_config": None,
        "tasks_completed": 0,
        "total_tokens": 0,
        "total_response_time": 0,
        "responses": []
    },
    {
        "name": "刘心怡",
        "role": "测试工程师",
        "emoji": "🧪",
        "model_config": None,
        "tasks_completed": 0,
        "total_tokens": 0,
        "total_response_time": 0,
        "responses": []
    },
    {
        "name": "张明远",
        "role": "运维工程师",
        "emoji": "🔧",
        "model_config": None,
        "tasks_completed": 0,
        "total_tokens": 0,
        "total_response_time": 0,
        "responses": []
    },
    {
        "name": "赵敏",
        "role": "产品运营",
        "emoji": "📈",
        "model_config": None,
        "tasks_completed": 0,
        "total_tokens": 0,
        "total_response_time": 0,
        "responses": []
    }
]


# =============================================================================
# 分配模型配置
# =============================================================================

def assign_model_configs():
    """为每个角色分配模型配置"""
    # 分配真实可用的模型配置
    model_configs = [m for m in MODEL_CHAIN if m.get("enabled", True)]
    
    # 按优先级分配
    for i, model in enumerate(MODELS):
        if i < len(model_configs):
            model["model_config"] = model_configs[i]
            model["model_id"] = model_configs[i]["model_id"]
            model["provider"] = model_configs[i]["provider"]
            print(f"  {model['emoji']} {model['name']} -> {model_configs[i]['alias']}")


# =============================================================================
# 真实API调用
# =============================================================================

def call_real_api(model_config: dict, prompt: str, max_tokens: int = 500) -> dict:
    """调用真实API"""
    url = f"{model_config['base_url']}/chat/completions"
    headers = {
        "Authorization": f"Bearer {model_config['api_key']}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model_config["model_id"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"] if result.get("choices") else ""
            usage = result.get("usage", {})
            
            return {
                "success": True,
                "content": content,
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
                "response_time": elapsed
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text[:100]}",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "response_time": elapsed
            }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "response_time": elapsed
        }


# =============================================================================
# 主开发流程
# =============================================================================

def main():
    print("="*70)
    print("【交响v2.0】真实模型协作开发")
    print("6位专家模型 + 真实API调用 + 真实Token统计")
    print("="*70)
    
    # 分配模型配置
    print("\n📡 分配模型配置...")
    assign_model_configs()
    
    # 开发任务
    tasks = [
        {"phase": "需求分析", "model_idx": 0, "prompt": "作为产品经理，请分析'被动触发功能'的需求，列出关键功能点"},
        {"phase": "架构设计", "model_idx": 1, "prompt": "作为架构师，请设计'被动触发功能'的系统架构"},
        {"phase": "代码开发", "model_idx": 2, "prompt": "作为开发工程师，请给出'被动触发功能'的核心代码实现思路"},
        {"phase": "测试用例", "model_idx": 3, "prompt": "作为测试工程师，请编写'被动触发功能'的测试用例大纲"},
        {"phase": "部署配置", "model_idx": 4, "prompt": "作为运维工程师，请提供'被动触发功能'的部署配置建议"},
        {"phase": "数据分析", "model_idx": 5, "prompt": "作为产品运营，请分析'被动触发功能'的用户价值"},
    ]
    
    print("\n" + "="*70)
    print("开始真实模型协作开发...")
    print("="*70)
    
    for task in tasks:
        model = MODELS[task["model_idx"]]
        config = model["model_config"]
        
        print(f"\n{model['emoji']} {model['name']} ({model['role']})")
        print(f"  任务: {task['phase']}")
        print(f"  模型: {config['alias']}")
        print(f"  调用API...")
        
        result = call_real_api(config, task["prompt"])
        
        if result["success"]:
            model["tasks_completed"] += 1
            model["total_tokens"] += result["total_tokens"]
            model["total_response_time"] += result["response_time"]
            model["responses"].append({
                "phase": task["phase"],
                "content": result["content"][:200],
                "tokens": result["total_tokens"],
                "time": result["response_time"]
            })
            
            print(f"  ✅ 成功")
            print(f"  📊 Tokens: {result['total_tokens']} (P:{result['prompt_tokens']} C:{result['completion_tokens']})")
            print(f"  ⏱️  耗时: {result['response_time']:.2f}s")
            print(f"  📝 回复: {result['content'][:100]}...")
        else:
            print(f"  ❌ 失败: {result['error']}")
    
    # 输出最终报告
    print("\n" + "="*70)
    print("📊 真实模型协作开发报告")
    print("="*70)
    
    # 按Token消耗排序
    sorted_models = sorted(MODELS, key=lambda x: x["total_tokens"], reverse=True)
    
    for i, m in enumerate(sorted_models, 1):
        avg_time = m["total_response_time"] / m["tasks_completed"] if m["tasks_completed"] > 0 else 0
        print(f"\n{i}. {m['emoji']} {m['name']} ({m['role']})")
        print(f"   模型: {m['model_config']['alias']}")
        print(f"   完成任务: {m['tasks_completed']} 个")
        print(f"   总Token: {m['total_tokens']}")
        print(f"   平均响应: {avg_time:.2f}s")
    
    # 团队汇总
    total_tokens = sum(m["total_tokens"] for m in MODELS)
    total_tasks = sum(m["tasks_completed"] for m in MODELS)
    total_time = sum(m["total_response_time"] for m in MODELS)
    
    print("\n" + "="*70)
    print("🎯 团队汇总统计")
    print("="*70)
    print(f"参会模型: {len(MODELS)}")
    print(f"总任务数: {total_tasks}")
    print(f"总Token消耗: {total_tokens}")
    print(f"总耗时: {total_time:.2f}s")
    
    # 保存报告
    report = {
        "title": "交响v2.0 真实模型协作开发报告",
        "datetime": datetime.now().isoformat(),
        "models": MODELS,
        "summary": {
            "total_models": len(MODELS),
            "total_tasks": total_tasks,
            "total_tokens": total_tokens,
            "total_time": round(total_time, 2)
        }
    }
    
    with open("real_model_dev_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 报告已保存: real_model_dev_report.json")
    print("\n" + "="*70)
    print("🎼 智韵交响，共创华章！")
    print("="*70)


if __name__ == "__main__":
    main()
