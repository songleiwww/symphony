# =============================================================================
# Symphony 配置文件模板
# =============================================================================
# 
# 使用说明：
# 1. 复制此文件为 config.py
# 2. 替换下方的 YOUR_API_KEY_HERE 为您的真实API Key
# 3. 智谱API Key: https://open.bigmodel.cn/
# 4. ModelScope API Key: https://modelscope.cn/
#
# 安全提示：请勿将包含真实API Key的config.py上传到公开仓库！
# =============================================================================

# 模型降级链配置
# 优先级：智谱GLM > ModelScope推理模型
MODEL_CHAIN = [
    # ==================== 智谱 GLM-4-Flash ====================
    {
        "name": "zhipu_glm4_flash",
        "provider": "zhipu",
        "model_id": "glm-4-flash",
        "alias": "智谱GLM-4-Flash",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key": "YOUR_ZHIPU_API_KEY_HERE",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 60,
        "max_retries": 3,
        "enabled": True,
        "priority": 1
    },
    # ==================== 智谱 GLM-Z1-Flash (推理模型) ====================
    {
        "name": "zhipu_glm_z1_flash",
        "provider": "zhipu",
        "model_id": "glm-z1-flash",
        "alias": "智谱GLM-Z1-Flash (推理模型)",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key": "YOUR_ZHIPU_API_KEY_HERE",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 90,
        "max_retries": 3,
        "enabled": True,
        "priority": 2,
        "is_reasoning": True
    },
    # ==================== 智谱 GLM-4.1V-Thinking-Flash (视觉推理) ====================
    {
        "name": "zhipu_glm_4v_thinking_flash",
        "provider": "zhipu",
        "model_id": "glm-4.1v-thinking-flash",
        "alias": "智谱GLM-4.1V-Thinking-Flash (视觉推理)",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key": "YOUR_ZHIPU_API_KEY_HERE",
        "api_type": "openai-completions",
        "context_window": 64000,
        "timeout": 90,
        "max_retries": 3,
        "enabled": True,
        "priority": 3,
        "is_vision": True
    },
    # ==================== 智谱 GLM-4V-Flash (图像理解) ====================
    {
        "name": "zhipu_glm_4v_flash",
        "provider": "zhipu",
        "model_id": "glm-4v-flash",
        "alias": "智谱GLM-4V-Flash (图像理解)",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key": "YOUR_ZHIPU_API_KEY_HERE",
        "api_type": "openai-completions",
        "context_window": 4000,
        "timeout": 60,
        "max_retries": 3,
        "enabled": True,
        "priority": 4,
        "is_vision": True
    },
    # ==================== 智谱 CogView-3-Flash (图像生成) ====================
    {
        "name": "zhipu_cogview_3_flash",
        "provider": "zhipu",
        "model_id": "cogview-3-flash",
        "alias": "智谱CogView-3-Flash (图像生成)",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key": "YOUR_ZHIPU_API_KEY_HERE",
        "api_type": "openai-completions",
        "context_window": 4000,
        "timeout": 90,
        "max_retries": 3,
        "enabled": True,
        "priority": 5,
        "is_image_gen": True
    },
    # ==================== 智谱 CogVideoX-Flash (视频生成) ====================
    {
        "name": "zhipu_cogvideox_flash",
        "provider": "zhipu",
        "model_id": "cogvideox-flash",
        "alias": "智谱CogVideoX-Flash (视频生成)",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key": "YOUR_ZHIPU_API_KEY_HERE",
        "api_type": "openai-completions",
        "context_window": 4000,
        "timeout": 120,
        "max_retries": 3,
        "enabled": True,
        "priority": 6,
        "is_video_gen": True
    },
    # ==================== ModelScope GLM-4.7-Flash ====================
    {
        "name": "modelscope_glm_4_7_flash",
        "provider": "modelscope",
        "model_id": "ZhipuAI/GLM-4.7-Flash",
        "alias": "ModelScope GLM-4.7-Flash",
        "base_url": "https://api-inference.modelscope.cn/v1",
        "api_key": "YOUR_MODELSCOPE_API_KEY_HERE",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 90,
        "max_retries": 3,
        "enabled": True,
        "priority": 6,
        "supports_stream": True
    },
    # ==================== ModelScope Z-Image-Turbo (图像生成) ====================
    {
        "name": "modelscope_z_image_turbo",
        "provider": "modelscope",
        "model_id": "Tongyi-MAI/Z-Image-Turbo",
        "alias": "ModelScope Z-Image-Turbo (图像生成)",
        "base_url": "https://api-inference.modelscope.cn",
        "api_key": "YOUR_MODELSCOPE_API_KEY_HERE",
        "api_type": "modelscope-async",
        "context_window": 4000,
        "timeout": 120,
        "max_retries": 3,
        "enabled": True,
        "priority": 7,
        "is_image_gen": True,
        "async_mode": True
    },
    # ==================== ModelScope DeepSeek-V3.2 ====================
    {
        "name": "modelscope_deepseek_v3_2",
        "provider": "modelscope",
        "model_id": "deepseek-ai/DeepSeek-V3.2",
        "alias": "ModelScope DeepSeek-V3.2",
        "base_url": "https://api-inference.modelscope.cn/v1",
        "api_key": "YOUR_MODELSCOPE_API_KEY_HERE",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 90,
        "max_retries": 3,
        "enabled": True,
        "priority": 8,
        "supports_thinking": True
    },
    # ==================== ModelScope Qwen3-Coder-480B ====================
    {
        "name": "modelscope_qwen3_coder",
        "provider": "modelscope",
        "model_id": "Qwen/Qwen3-Coder-480B-A35B-Instruct",
        "alias": "ModelScope Qwen3-Coder-480B",
        "base_url": "https://api-inference.modelscope.cn/v1",
        "api_key": "YOUR_MODELSCOPE_API_KEY_HERE",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 90,
        "max_retries": 3,
        "enabled": True,
        "priority": 9,
        "supports_stream": True
    },
    # ==================== ModelScope Qwen3-235B ====================
    {
        "name": "modelscope_qwen3_235b",
        "provider": "modelscope",
        "model_id": "Qwen/Qwen3-235B-A22B-Instruct-2507",
        "alias": "ModelScope Qwen3-235B",
        "base_url": "https://api-inference.modelscope.cn/v1",
        "api_key": "YOUR_MODELSCOPE_API_KEY_HERE",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 90,
        "max_retries": 3,
        "enabled": True,
        "priority": 10,
        "supports_stream": True
    },
    # ==================== ModelScope Qwen3-Embedding (向量模型) ====================
    {
        "name": "modelscope_qwen3_embedding",
        "provider": "modelscope",
        "model_id": "Qwen/Qwen3-Embedding-8B",
        "alias": "ModelScope Qwen3-Embedding-8B (向量)",
        "base_url": "https://api-inference.modelscope.cn/v1",
        "api_key": "YOUR_MODELSCOPE_API_KEY_HERE",
        "api_type": "openai-embeddings",
        "context_window": 8192,
        "timeout": 60,
        "max_retries": 3,
        "enabled": True,
        "priority": 11,
        "is_embedding": True,
        "embedding_dim": 4096
    },
    # ==================== ModelScope MiniMax-M2.5 ====================
    {
        "name": "modelscope_minimax_m2_5",
        "provider": "modelscope",
        "model_id": "MiniMax/MiniMax-M2.5",
        "alias": "ModelScope MiniMax-M2.5",
        "base_url": "https://api-inference.modelscope.cn/v1",
        "api_key": "YOUR_MODELSCOPE_API_KEY_HERE",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 90,
        "max_retries": 3,
        "enabled": True,
        "priority": 12,
        "supports_stream": True
    },
    # ==================== ModelScope Kimi-K2.5 (视觉模型) ====================
    {
        "name": "modelscope_kimi_k2_5",
        "provider": "modelscope",
        "model_id": "moonshotai/Kimi-K2.5",
        "alias": "ModelScope Kimi-K2.5 (视觉)",
        "base_url": "https://api-inference.modelscope.cn/v1",
        "api_key": "YOUR_MODELSCOPE_API_KEY_HERE",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 90,
        "max_retries": 3,
        "enabled": True,
        "priority": 5,
        "is_vision": True
    },
    # ==================== ModelScope ZhipuAI/GLM-5 ====================
    {
        "name": "modelscope_glm5",
        "provider": "modelscope",
        "model_id": "ZhipuAI/GLM-5",
        "alias": "ModelScope GLM-5",
        "base_url": "https://api-inference.modelscope.cn/v1",
        "api_key": "YOUR_MODELSCOPE_API_KEY_HERE",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 90,
        "max_retries": 3,
        "enabled": True,
        "priority": 4,
        "supports_stream": True
    },
    # ==================== ModelScope 推理模型 ====================
    {
        "name": "modelscope_deepseek_r1",
        "provider": "modelscope",
        "model_id": "deepseek-ai/DeepSeek-R1-0528",
        "alias": "DeepSeek R1 (推理模型)",
        "base_url": "https://api-inference.modelscope.cn/v1",
        "api_key": "YOUR_MODELSCOPE_API_KEY_HERE",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 90,
        "max_retries": 3,
        "enabled": True,
        "priority": 5,
        "is_reasoning": True
    }
]

# 模型统计
MODEL_STATS = {
    "total_models": 16,
    "providers": [
        {"name": "zhipu", "count": 6, "alias": "智谱"},
        {"name": "modelscope", "count": 10, "alias": "ModelScope"}
    ],
    "last_updated": "2026-03-06"
}

# 故障恢复配置
FAULT_RECOVERY_CONFIG = {
    "auto_retry": True,
    "max_retries": 3,
    "retry_delay": 2.0,
    "exponential_backoff": True,
    "jitter_factor": 0.1
}

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "console_output": True,
    "log_file": None
}

# Symphony统一调度器配置
SYMPHONY_CONFIG = {
    "num_workers": 4,
    "task_queue": {
        "max_size": 1000,
        "default_priority": 0,
        "default_max_retries": 3
    },
    "skills": {
        "auto_register_builtins": True,
        "custom_skills_path": "./skills",
        "enabled_skills": ["greet", "calculate"]
    },
    "mcp": {
        "enabled": True,
        "auto_connect": False
    },
    "metrics": {
        "enabled": True,
        "export_interval": 60,
        "export_path": "./metrics",
        "retention_days": 7
    },
    "health_check": {
        "enabled": True,
        "interval": 30,
        "check_skills": True,
        "check_models": True,
        "check_workers": True
    }
}
