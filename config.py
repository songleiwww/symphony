# 配置文件
# 多模型协作系统配置

# 天气查询工具配置
# WeatherAPI.com API Key
# 请访问 https://www.weatherapi.com/ 注册获取免费API Key
API_KEY = "YOUR_API_KEY_HERE"

# API基础URL
BASE_URL = "https://api.weatherapi.com/v1"

# 请求超时时间（秒）
REQUEST_TIMEOUT = 10

# 重试次数
MAX_RETRIES = 2

# 语言设置（zh: 中文, en: 英文）
LANGUAGE = "zh"


# =============================================================================
# 多模型协作系统配置
# =============================================================================

# 模型降级链配置（按优先级排序）
# 基于用户OpenClaw配置的17个模型
MODEL_CHAIN = [
    # ==================== 提供商1: cherry-doubao (5个模型) ====================
    {
        "name": "doubao_ark_code",
        "provider": "cherry-doubao",
        "model_id": "ark-code-latest",
        "alias": "Doubao Ark Code",
        "base_url": "https://ark.cn-beijing.volces.com/api/coding/v3",
        "api_key": "YOUR_CHERRY_DOUBAO_API_KEY",  # 用户需填入真实Key
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 30,
        "max_retries": 3,
        "enabled": True,
        "priority": 1
    },
    {
        "name": "doubao_deepseek_v32",
        "provider": "cherry-doubao",
        "model_id": "deepseek-v3.2",
        "alias": "DeepSeek V3.2",
        "base_url": "https://ark.cn-beijing.volces.com/api/coding/v3",
        "api_key": "YOUR_CHERRY_DOUBAO_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 30,
        "max_retries": 3,
        "enabled": True,
        "priority": 2
    },
    {
        "name": "doubao_seed_code",
        "provider": "cherry-doubao",
        "model_id": "doubao-seed-2.0-code",
        "alias": "Doubao Seed Code",
        "base_url": "https://ark.cn-beijing.volces.com/api/coding/v3",
        "api_key": "YOUR_CHERRY_DOUBAO_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 30,
        "max_retries": 3,
        "enabled": True,
        "priority": 3
    },
    {
        "name": "doubao_glm_47",
        "provider": "cherry-doubao",
        "model_id": "glm-4.7",
        "alias": "GLM 4.7",
        "base_url": "https://ark.cn-beijing.volces.com/api/coding/v3",
        "api_key": "YOUR_CHERRY_DOUBAO_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 30,
        "max_retries": 3,
        "enabled": True,
        "priority": 4
    },
    {
        "name": "doubao_kimi_k25",
        "provider": "cherry-doubao",
        "model_id": "kimi-k2.5",
        "alias": "Kimi K2.5",
        "base_url": "https://ark.cn-beijing.volces.com/api/coding/v3",
        "api_key": "YOUR_CHERRY_DOUBAO_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 30,
        "max_retries": 3,
        "enabled": True,
        "priority": 5
    },
    
    # ==================== 提供商2: cherry-minimax (1个模型) ====================
    {
        "name": "minimax_m25",
        "provider": "cherry-minimax",
        "model_id": "MiniMax-M2.5",
        "alias": "MiniMax M2.5",
        "base_url": "https://api.minimaxi.com/anthropic",
        "api_key": "YOUR_CHERRY_MINIMAX_API_KEY",
        "api_type": "anthropic-messages",
        "context_window": 128000,
        "timeout": 30,
        "max_retries": 3,
        "enabled": True,
        "priority": 6
    },
    
    # ==================== 提供商3: cherry-nvidia (10个模型) ====================
    {
        "name": "nvidia_llama_31_405b",
        "provider": "cherry-nvidia",
        "model_id": "meta/llama-3.1-405b-instruct",
        "alias": "Llama 3.1 405B",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "YOUR_CHERRY_NVIDIA_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 30,
        "max_retries": 3,
        "enabled": True,
        "priority": 7
    },
    {
        "name": "nvidia_deepseek_v32",
        "provider": "cherry-nvidia",
        "model_id": "deepseek-ai/deepseek-v3.2",
        "alias": "DeepSeek V3.2 (NVIDIA)",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "YOUR_CHERRY_NVIDIA_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 30,
        "max_retries": 3,
        "enabled": True,
        "priority": 8
    },
    {
        "name": "nvidia_kimi_k25",
        "provider": "cherry-nvidia",
        "model_id": "moonshotai/kimi-k2.5",
        "alias": "Kimi K2.5 (NVIDIA)",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "YOUR_CHERRY_NVIDIA_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 30,
        "max_retries": 3,
        "enabled": True,
        "priority": 9
    },
    {
        "name": "nvidia_glm_47",
        "provider": "cherry-nvidia",
        "model_id": "z-ai/glm4.7",
        "alias": "GLM 4.7 (NVIDIA)",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "YOUR_CHERRY_NVIDIA_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 30,
        "max_retries": 3,
        "enabled": True,
        "priority": 10
    },
    {
        "name": "nvidia_qwen3_coder",
        "provider": "cherry-nvidia",
        "model_id": "qwen/qwen3-coder-480b-a35b-instruct",
        "alias": "Qwen3 Coder 480B",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "YOUR_CHERRY_NVIDIA_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 30,
        "max_retries": 3,
        "enabled": True,
        "priority": 11
    },
    {
        "name": "nvidia_qwen35_397b",
        "provider": "cherry-nvidia",
        "model_id": "qwen/qwen3.5-397b-a17b",
        "alias": "Qwen3.5 397B",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "YOUR_CHERRY_NVIDIA_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 30,
        "max_retries": 3,
        "enabled": True,
        "priority": 12
    },
    {
        "name": "nvidia_minimax_m25",
        "provider": "cherry-nvidia",
        "model_id": "minimaxai/minimax-m2.5",
        "alias": "MiniMax M2.5 (NVIDIA)",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "YOUR_CHERRY_NVIDIA_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 30,
        "max_retries": 3,
        "enabled": True,
        "priority": 13
    },
    {
        "name": "nvidia_glm5",
        "provider": "cherry-nvidia",
        "model_id": "z-ai/glm5",
        "alias": "GLM 5",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "YOUR_CHERRY_NVIDIA_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 30,
        "max_retries": 3,
        "enabled": True,
        "priority": 14
    },
    {
        "name": "nvidia_gpt_oss_20b",
        "provider": "cherry-nvidia",
        "model_id": "openai/gpt-oss-20b",
        "alias": "GPT OSS 20B",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "YOUR_CHERRY_NVIDIA_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 30,
        "max_retries": 3,
        "enabled": True,
        "priority": 15
    },
    
    # ==================== 提供商4: cherry-modelscope (2个模型) ====================
    {
        "name": "modelscope_deepseek_r1",
        "provider": "cherry-modelscope",
        "model_id": "deepseek-ai/DeepSeek-R1-0528",
        "alias": "DeepSeek R1",
        "base_url": "https://api-inference.modelscope.cn",
        "api_key": "YOUR_CHERRY_MODELSCOPE_API_KEY",
        "api_type": "anthropic-messages",
        "context_window": 128000,
        "timeout": 30,
        "max_retries": 3,
        "enabled": True,
        "priority": 16
    },
    {
        "name": "modelscope_qwen3_235b",
        "provider": "cherry-modelscope",
        "model_id": "Qwen/Qwen3-235B-A22B-Instruct-2507",
        "alias": "Qwen3 235B",
        "base_url": "https://api-inference.modelscope.cn",
        "api_key": "YOUR_CHERRY_MODELSCOPE_API_KEY",
        "api_type": "anthropic-messages",
        "context_window": 128000,
        "timeout": 30,
        "max_retries": 3,
        "enabled": True,
        "priority": 17
    }
]

# 熔断器配置
CIRCUIT_BREAKER_CONFIG = {
    # 失败次数阈值，超过此阈值触发熔断
    "failure_threshold": 5,
    # 熔断时间窗口（秒），在此时间内的失败会被计数
    "failure_window": 60,
    # 恢复时间（秒），熔断后等待此时间才会尝试半开状态
    "recovery_timeout": 30,
    # 半开状态下允许的请求数
    "half_open_max_calls": 2,
    # 半开状态下的成功率阈值（0-1），超过此阈值则恢复闭合
    "half_open_success_threshold": 0.5
}

# 重试配置（指数退避）
RETRY_CONFIG = {
    # 最大重试次数
    "max_retries": 3,
    # 初始延迟（秒）
    "initial_delay": 1.0,
    # 延迟倍数（指数退避）
    "backoff_factor": 2.0,
    # 最大延迟（秒）
    "max_delay": 30.0,
    # 随机抖动因子（0-1），避免惊群效应
    "jitter_factor": 0.1
}

# 健康检查配置
HEALTH_CHECK_CONFIG = {
    # 健康检查间隔（秒）
    "check_interval": 30,
    # 健康检查超时（秒）
    "check_timeout": 5,
    # 连续失败次数阈值，超过此阈值标记为不健康
    "failure_threshold": 3,
    # 连续成功次数阈值，超过此阈值标记为健康
    "success_threshold": 2
}

# 日志配置
LOGGING_CONFIG = {
    # 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
    "level": "INFO",
    # 日志格式
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    # 日期格式
    "date_format": "%Y-%m-%d %H:%M:%S",
    # 是否输出到控制台
    "console_output": True,
    # 日志文件路径（可选）
    "log_file": None
}


# =============================================================================
# Symphony 统一调度器配置
# =============================================================================

SYMPHONY_CONFIG = {
    # 工作线程数量
    "num_workers": 4,

    # 任务队列配置
    "task_queue": {
        "max_size": 1000,
        "default_priority": 0,
        "default_max_retries": 3
    },

    # 技能配置
    "skills": {
        "auto_register_builtins": True,
        "custom_skills_path": "./skills",
        "enabled_skills": ["greet", "calculate"]
    },

    # MCP配置
    "mcp": {
        "enabled": True,
        "servers": {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/"]
            },
            "brave_search": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-brave-search"]
            }
        },
        "auto_connect": False
    },

    # 指标配置
    "metrics": {
        "enabled": True,
        "export_interval": 60,  # 秒
        "export_path": "./metrics",
        "retention_days": 7
    },

    # 健康检查配置
    "health_check": {
        "enabled": True,
        "interval": 30,  # 秒
        "check_skills": True,
        "check_models": True,
        "check_workers": True
    }
}

