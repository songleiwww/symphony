# 配置文件（无敏感信息版本）
# 多模型协作系统配置
# 后缀 .d 表示 "distribution"（发布版）

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
# 基于用户OpenClaw配置的18个模型
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
        "base_url": "https://api.minimax.chat/v1",
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
        "timeout": 60,
        "max_retries": 3,
        "enabled": True,
        "priority": 7
    },
    {
        "name": "nvidia_deepseek_v32",
        "provider": "cherry-nvidia",
        "model_id": "deepseek-ai/deepseek-v3.2",
        "alias": "DeepSeek V3.2 NVIDIA",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "YOUR_CHERRY_NVIDIA_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 60,
        "max_retries": 3,
        "enabled": True,
        "priority": 8
    },
    {
        "name": "nvidia_kimi_k25",
        "provider": "cherry-nvidia",
        "model_id": "moonshotai/kimi-k2.5",
        "alias": "Kimi K2.5 NVIDIA",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "YOUR_CHERRY_NVIDIA_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 60,
        "max_retries": 3,
        "enabled": True,
        "priority": 9
    },
    {
        "name": "nvidia_glm_47",
        "provider": "cherry-nvidia",
        "model_id": "z-ai/glm4.7",
        "alias": "GLM 4.7 NVIDIA",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "YOUR_CHERRY_NVIDIA_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 60,
        "max_retries": 3,
        "enabled": True,
        "priority": 10
    },
    {
        "name": "nvidia_qwen3_coder_480b",
        "provider": "cherry-nvidia",
        "model_id": "qwen/qwen3-coder-480b-a35b-instruct",
        "alias": "Qwen3 Coder 480B",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "YOUR_CHERRY_NVIDIA_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 60,
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
        "timeout": 60,
        "max_retries": 3,
        "enabled": True,
        "priority": 12
    },
    {
        "name": "nvidia_minimax_m25",
        "provider": "cherry-nvidia",
        "model_id": "minimaxai/minimax-m2.5",
        "alias": "MiniMax M2.5 NVIDIA",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "YOUR_CHERRY_NVIDIA_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 60,
        "max_retries": 3,
        "enabled": True,
        "priority": 13
    },
    {
        "name": "nvidia_glm_5",
        "provider": "cherry-nvidia",
        "model_id": "z-ai/glm5",
        "alias": "GLM 5 NVIDIA",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "YOUR_CHERRY_NVIDIA_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 60,
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
        "timeout": 60,
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
        "base_url": "https://api-inference.modelscope.cn/v1",
        "api_key": "YOUR_CHERRY_MODELSCOPE_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 60,
        "max_retries": 3,
        "enabled": True,
        "priority": 16
    },
    {
        "name": "modelscope_qwen3_235b",
        "provider": "cherry-modelscope",
        "model_id": "Qwen/Qwen3-235B-A22B-Instruct-2507",
        "alias": "Qwen3 235B",
        "base_url": "https://api-inference.modelscope.cn/v1",
        "api_key": "YOUR_CHERRY_MODELSCOPE_API_KEY",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 60,
        "max_retries": 3,
        "enabled": True,
        "priority": 17
    }
]

# =============================================================================
# 熔断器配置
# =============================================================================
CIRCUIT_BREAKER_CONFIG = {
    "failure_threshold": 5,           # 失败阈值
    "failure_window": 60,             # 失败窗口（秒）
    "recovery_timeout": 30,           # 恢复超时（秒）
    "half_open_max_calls": 2,         # 半开状态最大调用数
    "half_open_success_threshold": 0.5 # 半开状态成功阈值
}

# =============================================================================
# 重试策略配置
# =============================================================================
RETRY_CONFIG = {
    "max_retries": 3,                 # 最大重试次数
    "initial_delay": 1.0,              # 初始延迟（秒）
    "backoff_factor": 2.0,             # 退避因子
    "max_delay": 30.0,                 # 最大延迟（秒）
    "jitter_factor": 0.1               # 抖动因子
}

# =============================================================================
# 健康检查配置
# =============================================================================
HEALTH_CHECK_CONFIG = {
    "check_interval": 30,              # 检查间隔（秒）
    "failure_threshold": 3,             # 失败阈值
    "success_threshold": 2,             # 成功阈值
    "health_check_prompt": "你好，请回复OK",  # 健康检查提示词
    "health_check_timeout": 10           # 健康检查超时（秒）
}

# =============================================================================
# 日志配置
# =============================================================================
LOGGING_CONFIG = {
    "level": "INFO",                   # 日志级别
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # 日志格式
    "file": "symphony.log",            # 日志文件
    "max_bytes": 10 * 1024 * 1024,     # 单个日志文件最大字节（10MB）
    "backup_count": 5                   # 保留的日志文件数量
}

# =============================================================================
# 记忆系统配置
# =============================================================================
MEMORY_CONFIG = {
    "storage_path": "symphony_memory",  # 记忆存储路径
    "short_term_max": 100,              # 短期记忆最大数量
    "long_term_threshold": 0.7,          # 长期记忆阈值（重要性）
    "auto_manage_interval": 3600,        # 自动管理间隔（秒）
    "auto_promote_threshold": 0.7,       # 自动晋升阈值
    "auto_promote_access_count": 3       # 自动晋升访问次数
}

# =============================================================================
# 配置说明
# =============================================================================
"""
配置使用说明：

1. 模型配置：
   - 将 "YOUR_XXX_API_KEY" 替换为您的真实API Key
   - 可以禁用不需要的模型（enabled: False）
   - 可以调整模型优先级（priority: 数字越小优先级越高）

2. 安全说明：
   - 此文件（config.py.d）是发布版，不含敏感信息
   - 本地使用时请复制为 config.py 并填入真实Key
   - 不要将包含真实Key的 config.py 上传到GitHub

3. .gitignore已配置：
   - config.py（本地配置，含真实Key）
   - config.py.d（发布配置，不含敏感信息）会上传

4. 模型统计：
   - 总模型数：18个
   - 提供商数：4个（cherry-doubao, cherry-minimax, cherry-nvidia, cherry-modelscope）
"""
