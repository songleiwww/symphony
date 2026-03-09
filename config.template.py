# =============================================================================
# 交响 (Symphony) 配置模板
# 
# 使用方法：
# 1. 复制此文件为 config.py
# 2. 填入你的 API Key
# 3. 运行 python symphony.py
# =============================================================================

# =============================================================================
# API 配置 - 请填入你的 API Key
# =============================================================================

API_CONFIGS = {
    # 智谱 API (https://open.bigmodel.cn)
    "zhipu": {
        "api_key": "YOUR_ZHIPU_API_KEY",
        "base_url": "https://open.bigmodel.cn/api/paas/v4"
    },
    
    # 火山引擎 API (https://ark.cn-beijing.volces.com)
    "doubao": {
        "api_key": "YOUR_DOUBAO_API_KEY", 
        "base_url": "https://ark.cn-beijing.volces.com/api/coding/v3"
    },
    
    # 魔搭 API (https://api-inference.modelscope.cn)
    "modelscope": {
        "api_key": "YOUR_MODELSCOPE_API_KEY",
        "base_url": "https://api-inference.modelscope.cn/v1"
    },
    
    # 英伟达 API (https://integrate.api.nvidia.com)
    "nvidia": {
        "api_key": "YOUR_NVIDIA_API_KEY",
        "base_url": "https://integrate.api.nvidia.com/v1"
    }
}

# =============================================================================
# 模型配置
# =============================================================================

MODELS = {
    # 火山引擎模型
    "ark-code-latest": {"provider": "doubao", "type": "general"},
    "Doubao-Seed-2.0-pro": {"provider": "doubao", "type": "reasoning"},
    "Doubao-Seed-2.0-Code": {"provider": "doubao", "type": "code"},
    "Doubao-Seed-2.0-lite": {"provider": "doubao", "type": "general"},
    "Doubao-Seed-Code": {"provider": "doubao", "type": "code"},
    "MiniMax-M2.5": {"provider": "doubao", "type": "general"},
    "Kimi-K2.5": {"provider": "doubao", "type": "code"},
    "GLM-4.7": {"provider": "doubao", "type": "general"},
    "DeepSeek-V3.2": {"provider": "doubao", "type": "general"},
    
    # 智谱模型
    "glm-4-flash": {"provider": "zhipu", "type": "general"},
    "glm-z1-flash": {"provider": "zhipu", "type": "reasoning"},
    "glm-4.1v-thinking-flash": {"provider": "zhipu", "type": "reasoning"},
    "glm-4v-flash": {"provider": "zhipu", "type": "vision"},
    "cogview-3-flash": {"provider": "zhipu", "type": "image"},
    "cogvideox-flash": {"provider": "zhipu", "type": "video"},
    
    # 魔搭模型
    "ZhipuAI/GLM-4.7-Flash": {"provider": "modelscope", "type": "general"},
    "Tongyi-MAI/Z-Image-Turbo": {"provider": "modelscope", "type": "image"},
    "deepseek-ai/DeepSeek-V3.2": {"provider": "modelscope", "type": "reasoning"},
    "Qwen/Qwen3-Coder-480B-A35B-Instruct": {"provider": "modelscope", "type": "code"},
    "Qwen/Qwen3-235B-A22B-Instruct-2507": {"provider": "modelscope", "type": "general"},
    
    # 英伟达模型
    "meta/llama-3.1-405b-instruct": {"provider": "nvidia", "type": "general"},
    "deepseek-ai/deepseek-v3.2": {"provider": "nvidia", "type": "reasoning"},
    "moonshotai/kimi-k2.5": {"provider": "nvidia", "type": "code"},
    "z-ai/glm4.7": {"provider": "nvidia", "type": "general"},
    "qwen/qwen3-coder-480b-a35b-instruct": {"provider": "nvidia", "type": "code"},
    "qwen/qwen3.5-397b-a17b": {"provider": "nvidia", "type": "general"},
    "minimaxai/minimax-m2.5": {"provider": "nvidia", "type": "general"},
    "z-ai/glm5": {"provider": "nvidia", "type": "general"},
    "openai/gpt-oss-20b": {"provider": "nvidia", "type": "general"},
    "nvidia/llama-3.1-nemotron-70b-instruct": {"provider": "nvidia", "type": "general"}
}

# =============================================================================
# 系统配置
# =============================================================================

SYSTEM_CONFIG = {
    "timeout": 120,
    "max_retries": 3,
    "rate_limit_window": 60,
    "rate_limit_max": 30
}
