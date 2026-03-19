# 序境系统自适应调度配置 v2.0
# 版本: 2.0
# 更新日期: 2026-03-18

# ==================== 1. 任务复杂度分级配置 ====================
TASK_COMPLEXITY = {
    "简单": {
        "keywords": ["问答", "翻译", "问候", "简单", "what is", "how to", "介绍一下", "是什么"],
        "max_tokens": None,  # 不限制
        "preferred_models": ["GLM-4.7-Flash", "doubao-seed-2.0-lite", "GLM-4V-Flash"],
        "temperature": 0.7
    },
    "中等": {
        "keywords": ["代码", "写", "分析", "总结", "code", "编程", "生成", "创作"],
        "max_tokens": None,  # 不限制
        "preferred_models": ["doubao-seed-2.0-code", "MiniMax-M2.5", "Kimi K2.5"],
        "temperature": 0.8
    },
    "复杂": {
        "keywords": ["战略", "规划", "设计", "架构", "长文", "深度", "系统", "方案"],
        "max_tokens": None,  # 不限制
        "preferred_models": ["Kimi K2.5", "MiniMax-M2.5", "GLM-4.7"],
        "temperature": 0.9
    }
}

# ==================== 2. 动态调度策略配置 ====================
SCHEDULING_STRATEGY = {
    "load_balancing": True,  # 负载均衡
    "failover": True,        # 故障转移
    "adaptive_weight": True,  # 自适应权重
    "weights": {
        "response_time": 0.3,
        "success_rate": 0.4,
        "cost": 0.3
    },
    "fallback_chain": {
        "逻辑推理": ["MiniMax-M2.5", "Kimi K2.5", "GLM-4.7"],
        "代码生成": ["doubao-seed-2.0-code", "MiniMax-M2.5", "Kimi K2.5"],
        "创意生成": ["GLM-4.7", "Kimi K2.5", "MiniMax-M2.5"]
    }
}

# ==================== 3. 热更新配置 ====================
HOT_UPDATE = {
    "enabled": True,
    "config_path": "skills/symphony/config/",
    "watch_interval": 5,  # 秒
    "auto_reload": True,
    "version": "2.0"
}

# ==================== 4. Tokens限制配置 ====================
TOKENS_CONFIG = {
    "max_tokens": None,  # None表示不限制，解除最大限制
    "default_temperature": 0.7,
    "default_top_p": 0.9,
    "default_top_k": 50
}

# ==================== 5. 模型服务商完整映射 ====================
PROVIDER_MAPPING = {
    "火山引擎": {
        "models": ["GLM-4.7", "GLM-4.7-Flash", "Kimi K2.5", "MiniMax-M2.5", 
                   "doubao-seed-2.0-code", "doubao-seed-2.0-lite", "ark-code-latest"],
        "endpoint": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        "priority": 1
    },
    "智谱": {
        "models": ["GLM-4.7-Flash", "GLM-Z1-Flash", "GLM-4.6V-Flash", "GLM-4V-Flash",
                   "GLM-4.1V-Thinking-Flash", "CogView-3-Flash", "CogVideoX-Flash"],
        "endpoint": "https://open.bigmodel.cn/api/paas/v4/",
        "priority": 2
    },
    "魔搭": {
        "models": ["ZhipuAI/GLM-5", "moonshotai/Kimi-K2.5", "MiniMax/MiniMax-M2.5",
                   "Qwen/Qwen3.5-397B-A17B", "ZhipuAI/GLM-4.7-Flash"],
        "endpoint": "https://api-inference.modelscope.cn/v1",
        "priority": 3
    },
    "英伟达": {
        "models": ["meta/llama-3.1-70b-instruct", "deepseek-ai/deepseek-r1-distill-qwen-32b",
                   "nvidia/llama-3.3-nemotron-super-49b-v1.5"],
        "endpoint": "https://integrate.api.nvidia.com/v1/chat/completions",
        "priority": 4
    },
    "硅基流动": {
        "models": ["deepseek-ai/DeepSeek-V2-Chat", "01ai/Yi-1.5-9B-Chat"],
        "endpoint": "https://api.siliconflow.cn/v1/chat/completions",
        "priority": 5
    }
}

# ==================== 6. 调度官署人员完整绑定 ====================
OFFICIAL_BINDINGS = {
    "沈星衍": {
        "model": "MiniMax-M2.5",
        "provider": "火山引擎",
        "role": "智囊博士",
        "expertise": ["智能决策", "系统架构", "算法优化"],
        "priority": 1
    },
    "顾至尊": {
        "model": "Kimi K2.5",
        "provider": "火山引擎",
        "role": "首辅大学士",
        "expertise": ["战略规划", "决策辅助", "内阁机要"],
        "priority": 2
    },
    "顾清歌": {
        "model": "doubao-seed-2.0-code",
        "provider": "火山引擎",
        "role": "翰林学士",
        "expertise": ["代码生成", "诏书起草", "国史编修"],
        "priority": 3
    },
    "苏云渺": {
        "model": "GLM-4.7",
        "provider": "火山引擎",
        "role": "工部尚书",
        "expertise": ["工程营造", "器械制造", "系统设计"],
        "priority": 4
    },
    "杜子美": {
        "model": "MiniMax-M2.5",
        "provider": "魔搭",
        "role": "诗博士",
        "expertise": ["创意写作", "诗歌创作", "文化研究"],
        "priority": 5
    }
}

# ==================== 7. 调度统计 ====================
SCHEDULING_STATS = {
    "total_dispatches": 0,
    "successful_dispatches": 0,
    "failed_dispatches": 0,
    "avg_response_time": 0,
    "model_usage": {}
}
