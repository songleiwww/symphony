# =============================================================================
# Symphony 配置文件 - 配置模板
# =============================================================================
# 注意：此文件为配置模板，上传到GitHub前已移除所有API Key
# 用户使用前需要填写自己的API Key

# 模型降级链配置
# 优先级：NVIDIA > MiniMax > 智谱GLM > ModelScope
MODEL_CHAIN = [
    # ==================== NVIDIA Llama 3.1 405B ====================
    {
        "name": "nvidia_llama_405b",
        "provider": "nvidia",
        "model_id": "meta/llama-3.1-405b-instruct",
        "alias": "NVIDIA Llama 3.1 405B",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "YOUR_NVIDIA_API_KEY",  # 替换为你的NVIDIA API Key
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 300,
        "max_retries": 3,
        "enabled": True,
        "priority": 1
    },
    # ==================== NVIDIA Qwen 3.5 397B ====================
    {
        "name": "nvidia_qwen_397b",
        "provider": "nvidia",
        "model_id": "qwen/qwen3.5-397b-a17b",
        "alias": "NVIDIA Qwen 3.5 397B",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "YOUR_NVIDIA_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 300,
        "max_retries": 3,
        "enabled": True,
        "priority": 2
    },
    # ==================== MiniMax M2.5 ====================
    {
        "name": "minimax_m2.5",
        "provider": "minimax",
        "model_id": "MiniMax-M2.5",
        "alias": "MiniMax M2.5",
        "base_url": "https://api.minimaxi.com/anthropic",
        "api_key": "YOUR_MINIMAX_API_KEY",  # 替换为你的MiniMax API Key
        "api_type": "anthropic-messages",
        "context_window": 128000,
        "timeout": 120,
        "max_retries": 3,
        "enabled": True,
        "priority": 3
    },
    # ==================== 智谱 GLM-4-Flash ====================
    {
        "name": "zhipu_glm4_flash",
        "provider": "zhipu",
        "model_id": "glm-4-flash",
        "alias": "智谱GLM-4-Flash",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key": "YOUR_ZHIPU_API_KEY",  # 替换为你的智谱API Key
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 60,
        "max_retries": 3,
        "enabled": True,
        "priority": 4
    },
]

# 交响系统配置
SYMPHONY_CONFIG = {
    "system_name": "交响 (Symphony)",
    "version": "1.4.0",
    "max_concurrent_calls": 5,
    "default_timeout": 120,
    "enable_fallback": True,
    "enable_monitoring": True,
}

# API配置模板
API_CONFIG = {
    "nvidia": {
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "YOUR_NVIDIA_API_KEY",
    },
    "minimax": {
        "base_url": "https://api.minimaxi.com/anthropic",
        "api_key": "YOUR_MINIMAX_API_KEY",
    },
    "zhipu": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key": "YOUR_ZHIPU_API_KEY",
    },
    "modelscope": {
        "base_url": "https://api.modelscope.cn/v1",
        "api_key": "YOUR_MODELSCOPE_API_KEY",
    },
}

print("="*60)
print("Symphony v1.4.0 配置模板")
print("="*60)
print("请将 YOUR_XXX_API_KEY 替换为你的真实API Key")
print("="*60)
