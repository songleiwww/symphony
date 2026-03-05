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
MODEL_CHAIN = [
    {
        "name": "primary_model",
        "model_type": "gpt-4",
        "api_key": "PRIMARY_API_KEY",
        "base_url": "https://api.openai.com/v1",
        "timeout": 30,
        "max_retries": 3,
        "enabled": True
    },
    {
        "name": "backup_model",
        "model_type": "gpt-3.5-turbo",
        "api_key": "BACKUP_API_KEY",
        "base_url": "https://api.openai.com/v1",
        "timeout": 30,
        "max_retries": 3,
        "enabled": True
    },
    {
        "name": "fallback_model",
        "model_type": "claude-3-haiku",
        "api_key": "FALLBACK_API_KEY",
        "base_url": "https://api.anthropic.com/v1",
        "timeout": 30,
        "max_retries": 3,
        "enabled": True
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

