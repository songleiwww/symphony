# -*- coding: utf-8 -*-
"""
动态调度策略配置
"""
SCHEDULING_STRATEGY = {
    "load_balancing": True,
    "failover": True,
    "adaptive_weight": True,
    "weights": {
        "response_time": 0.3,
        "success_rate": 0.4,
        "cost": 0.3
    },
    "default_model": "deepseek-v3-250324",
    "default_provider": "volcano",
    "fallback_chain": {
        "逻辑推理": ["deepseek-v3-250324", "doubao-seed-2.0-pro", "MiniMax-M2.5", "Kimi-K2.5", "GLM-4.7"],
        "代码生成": ["doubao-seed-2.0-code", "deepseek-v3-250324", "doubao-seed-code", "MiniMax-M2.5"],
        "创意生成": ["doubao-seed-2.0-pro", "glm-4.7", "Kimi-K2.5", "MiniMax-M2.5"],
        "通用对话": ["deepseek-v3-250324", "doubao-seed-2.0-pro"]
    }
}
