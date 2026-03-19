#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统 - 1-20级矩阵算法
陆念昭专用调度引擎
"""
import sqlite3
import requests
from datetime import datetime

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

# ==================== 1-20级矩阵 ====================

class MatrixLevel:
    """矩阵等级"""
    
    # 1-10级: 基础能力
    LEVEL_1 = "单轮对话"
    LEVEL_2 = "多轮对话"
    LEVEL_3 = "上下文记忆"
    LEVEL_4 = "意图识别"
    LEVEL_5 = "技能调用"
    LEVEL_6 = "工具使用"
    LEVEL_7 = "多Agent协作"
    LEVEL_8 = "自主学习"
    LEVEL_9 = "自我进化"
    LEVEL_10 = "完全自治"
    
    # 11-20级: 进阶能力
    LEVEL_11 = "跨域推理"
    LEVEL_12 = "长期记忆"
    LEVEL_13 = "知识图谱"
    LEVEL_14 = "Agent编排"
    LEVEL_15 = "动态路由"
    LEVEL_16 = "熔断机制"
    LEVEL_17 = "负载均衡"
    LEVEL_18 = "故障转移"
    LEVEL_19 = "自适应"
    LEVEL_20 = "通用智能"

# 引擎配置
ENGINES = {
    "火山引擎": {
        "models": [56, 61],  # ark-code-latest, doubao-seed-2.0-code
        "priority": 1
    },
    "英伟达": {
        "models": list(range(1, 21)),
        "priority": 2
    },
    "智谱": {
        "models": list(range(65, 77)),
        "priority": 3
    },
    "魔搭": {
        "models": list(range(77, 87)),
        "priority": 4
    },
    "硅基流动": {
        "models": list(range(87, 96)),
        "priority": 5
    }
}

def get_level_info():
    """获取1-20级矩阵信息"""
    levels = [
        (1, "单轮对话", "简单问答"),
        (2, "多轮对话", "连续交流"),
        (3, "上下文记忆", "记住对话"),
        (4, "意图识别", "理解目的"),
        (5, "技能调用", "使用工具"),
        (6, "工具使用", "执行操作"),
        (7, "多Agent协作", "多人配合"),
        (8, "自主学习", "从经验学"),
        (9, "自我进化", "自动改进"),
        (10, "完全自治", "自主决策"),
        (11, "跨域推理", "跨领域"),
        (12, "长期记忆", "持久存储"),
        (13, "知识图谱", "关系网络"),
        (14, "Agent编排", "任务调度"),
        (15, "动态路由", "智能选路"),
        (16, "熔断机制", "故障保护"),
        (17, "负载均衡", "压力分担"),
        (18, "故障转移", "备用切换"),
        (19, "自适应", "自动调整"),
        (20, "通用智能", "AGI水平")
    ]
    return levels

def get_engine_status():
    """获取引擎状态"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    status = {}
    for engine, config in ENGINES.items():
        # 检查模型可用性
        model_ids = config["models"]
        available = 0
        for mid in model_ids:
            c.execute("SELECT API地址, API密钥 FROM 模型配置表 WHERE id = ?", (mid,))
            row = c.fetchone()
            if row and row[0] and row[1]:
                available += 1
        
        status[engine] = {
            "total": len(model_ids),
            "available": available,
            "priority": config["priority"]
        }
    
    conn.close()
    return status

def call_primary_engine(prompt):
    """调用主引擎(陆念昭绑定)"""
    # 陆念昭绑定: 火山引擎 ark-code-latest
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 模型名称, 模型标识符, API地址, API密钥 FROM 模型配置表 WHERE id = 56")
    row = c.fetchone()
    conn.close()
    
    if not row:
        return {"success": False, "error": "No model config"}
    
    name, api_id, api_url, api_key = row
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": api_id, "messages": [{"role": "user", "content": prompt}], "max_tokens": 200}
    
    try:
        resp = requests.post(api_url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            content = result["choices"][0]["message"]["content"]
            return {"success": True, "response": content, "engine": "火山引擎", "model": name}
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}", "engine": "火山引擎"}
    except Exception as e:
        return {"success": False, "error": str(e), "engine": "火山引擎"}

# ==================== 执行 ====================

def show_matrix():
    """展示1-20级矩阵"""
    print("=" * 70)
    print("🔢 序境1-20级矩阵算法")
    print("=" * 70)
    
    # 1-10级
    print("\n【基础能力 1-10级】")
    print("-" * 50)
    levels = get_level_info()
    for i in range(10):
        lvl, name, desc = levels[i]
        print(f"  {lvl:2}. {name:10} - {desc}")
    
    # 11-20级
    print("\n【进阶能力 11-20级】")
    print("-" * 50)
    for i in range(10, 20):
        lvl, name, desc = levels[i]
        print(f"  {lvl:2}. {name:10} - {desc}")

def show_engines():
    """展示引擎状态"""
    print("\n" + "=" * 70)
    print("🔌 引擎模型组合")
    print("=" * 70)
    
    status = get_engine_status()
    
    for engine, info in sorted(status.items(), key=lambda x: x[1]["priority"]):
        print(f"\n【{engine}】优先级: {info['priority']}")
        print(f"    可用模型: {info['available']}/{info['total']}")

def test_dispatch():
    """测试调度"""
    print("\n" + "=" * 70)
    print("🧪 测试调度: 陆念昭(火山引擎)")
    print("=" * 70)
    
    result = call_primary_engine("你好，请用一句话介绍序境系统")
    
    if result["success"]:
        print(f"\n✅ 引擎: {result['engine']}")
        print(f"   模型: {result['model']}")
        print(f"   响应: {result['response'][:100]}...")
    else:
        print(f"\n❌ 错误: {result['error']}")

if __name__ == "__main__":
    show_matrix()
    show_engines()
    test_dispatch()
