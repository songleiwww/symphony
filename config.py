# =============================================================================
# Symphony 配置文件 - 多模型配置
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
        "api_key": "16cf0a4a775c46cfa1684abcf4b802d0.rtb4oMgpFocBy87y",
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
        "api_key": "16cf0a4a775c46cfa1684abcf4b802d0.rtb4oMgpFocBy87y",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 90,
        "max_retries": 3,
        "enabled": True,
        "priority": 2,
        "is_reasoning": True
    },
    # ==================== ModelScope 推理模型 ====================
    {
        "name": "modelscope_deepseek_r1",
        "provider": "modelscope",
        "model_id": "deepseek-ai/DeepSeek-R1-0528",
        "alias": "DeepSeek R1 (推理模型)",
        "base_url": "https://api-inference.modelscope.cn/v1",
        "api_key": "ms-eac6f154-3502-4721-a168-ce7caeaf1033",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 90,
        "max_retries": 3,
        "enabled": True,
        "priority": 3,
        "is_reasoning": True
    }
]

# 模型统计
MODEL_STATS = {
    "total_models": 3,
    "providers": [
        {"name": "zhipu", "count": 2, "alias": "智谱"},
        {"name": "modelscope", "count": 1, "alias": "ModelScope"}
    ],
    "last_updated": "2026-03-06 14:16"
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
