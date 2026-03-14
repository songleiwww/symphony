# -*- coding: utf-8 -*-
"""
交响独立配置文件
Symphony 专用模型配置
"""

# =============================================================================
# 交响独立模型配置
# 不依赖OpenClaw，使用自己的模型池
# =============================================================================

# 主模型 - 交响的主要思考引擎
PRIMARY_MODEL = "doubao-seed-code"

# 备用模型列表 - 当主模型失败时自动切换
FALLBACK_MODELS = [
    "glm-4.7",
    "deepseek-v3.2", 
    "kimi-k2.5",
    "minimax-m2.5",
]

# 模型提供商配置
PROVIDERS = {
    "cherry-doubao": {
        "name": "字节豆包",
        "models": ["ark-code-latest", "deepseek-v3.2", "glm-4.7", "kimi-k2.5"],
        "base_url": "https://ark.cn-beijing.volces.com/api/coding/v3",
    },
    "cherry-minimax": {
        "name": "MiniMax",
        "models": ["MiniMax-M2.5"],
        "base_url": "https://api.minimax.chat/v1",
    },
    "cherry-nvidia": {
        "name": "NVIDIA",
        "models": ["meta/llama-3.1-405b-instruct", "nvidia/llama-3.1-nemotron-70b-instruct"],
        "base_url": "https://integrate.api.nvidia.com/v1",
    },
}

# 调度策略
SCHEDULING_STRATEGY = {
    "primary": "round_robin",  # 主模型轮询
    "fallback": "sequential",  # 备用模型顺序尝试
    "retry": 3,               # 重试次数
    "timeout": 60,             # 超时秒数
}

# 独立运行配置
INDEPENDENT_MODE = {
    "enabled": True,
    "config_file": "symphony_config.py",
    "log_file": "symphony.log",
    "data_dir": "./data",
}

# print("🎼 交响独立配置已加载")
# print(f"   主模型: {PRIMARY_MODEL}")
# print(f"   备用: {len(FALLBACK_MODELS)} 个")
