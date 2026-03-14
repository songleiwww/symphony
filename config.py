#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
🎼 交响 Symphony 配置文件
============================================================================
支持4大引擎：火山引擎、智谱、魔搭、英伟达
带限流检测和自动恢复
============================================================================
"""

import time
from typing import Dict, Optional
from dataclasses import dataclass, field

# =============================================================================
# 🎭 基因故事 (genesis.py)
# =============================================================================

try:
    from genesis import (
        SYMPHONY_GENESIS, DREAM_MAKER, JIAOJIAO, SYMPHONY_BRAND,
        get_genesis_story, get_dream_maker, get_jiaoJiao, get_brand
    )
except ImportError:
    SYMPHONY_GENESIS = ""
    DREAM_MAKER = {"name": "造梦者"}
    JIAOJIAO = {"name": "交交"}
    SYMPHONY_BRAND = {"name_cn": "交响", "name_en": "Symphony", "tagline": "智韵交响，共创华章", "color": "🎼"}
    get_genesis_story = lambda: ""
    get_dream_maker = lambda: DREAM_MAKER
    get_jiaoJiao = lambda: JIAOJIAO
    get_brand = lambda: SYMPHONY_BRAND


# =============================================================================
# 🔥 火山引擎 (Doubao)
# =============================================================================

DOUBAO_CONFIG = {
    "api_key": "3b922877-3fbe-45d1-a298-53f2231c5224",
    "base_url": "https://ark.cn-beijing.volces.com/api/coding/v3",
    "provider": "doubao",
    "name": "火山引擎",
    "rate_limit": {"enabled": True, "max_requests_per_minute": 60, "recovery_time": 60},
    "models": [
        {"id": "ark-code-latest",      "name": "豆包默认引擎",     "type": "general",  "thinking": False, "context_window": 128000},
        {"id": "Doubao-Seed-2.0-pro", "name": "Seed 2.0 旗舰",  "type": "reasoning", "thinking": True,  "context_window": 128000},
        {"id": "Doubao-Seed-2.0-Code","name": "Seed 2.0 代码",  "type": "code",      "thinking": False, "context_window": 128000},
        {"id": "Doubao-Seed-2.0-lite","name": "Seed 2.0 轻量",  "type": "general",  "thinking": True,  "context_window": 64000},
        {"id": "Doubao-Seed-Code",     "name": "豆包代码",        "type": "code",      "thinking": False, "context_window": 64000},
        {"id": "MiniMax-M2.5",         "name": "MiniMax M2.5",   "type": "general",  "thinking": True,  "context_window": 128000},
        {"id": "Kimi-K2.5",            "name": "Kimi K2.5",      "type": "code",      "thinking": False, "context_window": 128000},
        {"id": "GLM-4.7",             "name": "智谱GLM-4.7",    "type": "general",  "thinking": False, "context_window": 128000},
        {"id": "DeepSeek-V3.2",       "name": "DeepSeek V3.2",  "type": "general",  "thinking": False, "context_window": 128000},
    ]
}


# =============================================================================
# 📊 智谱 (Zhipu)
# =============================================================================

ZHIPU_CONFIG = {
    "api_key": "16cf0a4a775c46cfa1684abcf4b802d0.rtb4oMgpFocBy87y",
    "base_url": "https://open.bigmodel.cn/api/paas/v4",
    "provider": "zhipu",
    "name": "智谱",
    "rate_limit": {"enabled": True, "max_requests_per_minute": 30, "recovery_time": 60},
    "models": [
        {"id": "glm-4-flash",             "name": "GLM-4-Flash",            "type": "general", "thinking": False, "vision": False, "context_window": 128000},
        {"id": "glm-z1-flash",            "name": "GLM-Z1-Flash",           "type": "reasoning","thinking": True,  "vision": False, "context_window": 128000},
        {"id": "glm-4.1v-thinking-flash","name": "GLM-4.1V-Thinking-Flash","type": "vision_reasoning","thinking": True,"vision": True,"context_window": 64000},
        {"id": "glm-4v-flash",            "name": "GLM-4V-Flash",           "type": "vision",   "vision": True,  "context_window": 4000},
        {"id": "cogview-3-flash",         "name": "CogView-3-Flash",        "type": "image",    "image_gen": True, "context_window": 4000},
        {"id": "cogvideox-flash",         "name": "CogVideoX-Flash",        "type": "video",    "video_gen": True, "context_window": 4000},
    ]
}


# =============================================================================
# 🦁 魔搭 (ModelScope)
# =============================================================================

# =============================================================================
# 🦁 魔搭 (ModelScope) - 免费API限制说明
# =============================================================================
# 每日总调用：2000次/天（所有模型合计）
# 单模型上限：≤500次/天
# 限制：非商用、单并发、无SLA；超量返回429
# =============================================================================

MODELSCOPE_CONFIG = {
    "api_key": "ms-eac6f154-3502-4721-a168-ce7caeaf1033",
    "base_url": "https://api-inference.modelscope.cn/v1",
    "provider": "modelscope",
    "name": "魔搭",
    "rate_limit": {
        "enabled": True,
        "max_requests_per_day": 2000,        # 每日总调用上限
        "max_requests_per_model_per_day": 500, # 单模型每日上限
        "max_concurrent": 1,                 # 单并发限制
        "recovery_time": 60
    },
    "models": [
        # 已测试可用的在线体验模型 (2026-03-10)
        # 建议分配：每个模型每天最多500次，总计2000次
        {"id": "ZhipuAI/GLM-5",                   "name": "GLM-5 (智谱)",              "type": "general",  "thinking": False, "vision": True,  "context_window": 128000, "params": "753.86B", "framework": "Safetensors", "daily_limit": 500},
        {"id": "moonshotai/Kimi-K2.5",           "name": "Kimi K2.5 (月之暗面)",       "type": "vision",   "thinking": False, "vision": True,  "context_window": 128000, "params": "170.74B", "framework": "Safetensors", "daily_limit": 500},
        {"id": "MiniMax/MiniMax-M2.5",           "name": "MiniMax M2.5 (海螺)",        "type": "general",  "thinking": True,  "vision": False, "context_window": 128000, "params": "228.70B", "framework": "Safetensors", "daily_limit": 500},
        {"id": "Qwen/Qwen3.5-397B-A17B",         "name": "Qwen3.5 397B (通义千问)",    "type": "vision",   "thinking": False, "vision": True,  "context_window": 128000, "params": "403.40B", "framework": "Safetensors", "daily_limit": 500},
        # 其他可用模型
        {"id": "ZhipuAI/GLM-4.7-Flash",          "name": "GLM-4.7-Flash (智谱)",       "type": "general",  "thinking": False, "vision": False, "context_window": 128000, "params": "31.22B", "framework": "Transformers", "daily_limit": 500},
    ]
}


# =============================================================================
# ⚡ 英伟达 (NVIDIA)
# =============================================================================

NVIDIA_CONFIG = {
    "api_key": "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",
    "base_url": "https://integrate.api.nvidia.com/v1",
    "provider": "nvidia",
    "name": "英伟达",
    "rate_limit": {"enabled": True, "max_requests_per_minute": 100, "recovery_time": 30},
    "models": [
        {"id": "z-ai/glm4.7",                      "name": "智谱GLM-4.7",         "type": "general", "thinking": False, "context_window": 128000},
        {"id": "meta/llama-3.1-405b-instruct",     "name": "Llama 3.1 405B",      "type": "general", "thinking": False, "context_window": 128000},
        {"id": "nvidia/llama-3.1-nemotron-70b-instruct","name": "Nemotron 70B",    "type": "general", "thinking": False, "context_window": 128000},
        {"id": "nvidia/mistral-large-2-instruct",  "name": "Mistral Large 2",     "type": "general", "thinking": False, "context_window": 128000},
        {"id": "qwen/qwen3.5-397b-a17b",           "name": "通义千问3.5",         "type": "general", "thinking": False, "context_window": 128000},
        {"id": "qwen/qwen3-coder-480b-a35b-instruct","name": "通义代码",          "type": "code",     "thinking": False, "context_window": 128000},
        {"id": "deepseek-ai/deepseek-v3.2",        "name": "DeepSeek V3.2",        "type": "general", "thinking": False, "context_window": 128000},
        {"id": "moonshotai/kimi-k2.5",             "name": "Kimi K2.5",           "type": "code",     "thinking": False, "context_window": 128000},
        {"id": "minimaxai/minimax-m2.5",           "name": "MiniMax M2.5",         "type": "general", "thinking": False, "context_window": 128000},
        {"id": "z-ai/glm5",                        "name": "智谱GLM-5",           "type": "general",  "thinking": False, "context_window": 128000},
        # 2026-03-09 新增模型
        {"id": "minimaxai/minimax-m2.1",           "name": "MiniMax M2.1",        "type": "agent",    "thinking": False, "context_window": 128000, "note": "Agent优化"},
        {"id": "stepfun-ai/step-3.5-flash",       "name": "Step 3.5 Flash",      "type": "reasoning","thinking": True,  "context_window": 128000, "note": "推理引擎"},
    ]
}


# =============================================================================
# 🌀 硅基流动 (Silicon Flow) - 免费API - 2026-03-10新增
# =============================================================================
# API Key: sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc
# 基础URL: https://api.siliconflow.cn/v1
# 限制: 免费用户100万Token/天, 高峰期可能限流
# =============================================================================

SILICONFLOW_CONFIG = {
    "api_key": "sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc",
    "base_url": "https://api.siliconflow.cn/v1",
    "provider": "siliconflow",
    "name": "硅基流动",
    "rate_limit": {"enabled": True, "max_requests_per_minute": 60, "recovery_time": 30},
    "models": [
        # Qwen系列 - 阿里开源
        {"id": "Qwen/Qwen2.5-7B-Instruct",     "name": "通义2.5 7B",      "type": "general",  "thinking": False, "context_window": 32768,  "params": "7.72B",   "daily_limit": 100000, "focus": "轻量对话"},
        {"id": "Qwen/Qwen2.5-14B-Instruct",    "name": "通义2.5 14B",     "type": "general",  "thinking": False, "context_window": 32768,  "params": "14.77B",  "daily_limit": 100000, "focus": "平衡性能"},
        {"id": "Qwen/Qwen2.5-72B-Instruct",    "name": "通义2.5 72B",     "type": "reasoning", "thinking": True,  "context_window": 32768,  "params": "72.71B",  "daily_limit": 100000, "focus": "高性能推理"},
        # GLM系列 - 智谱
        {"id": "THUDM/glm-4-9b-chat",          "name": "GLM-4 9B",         "type": "general",  "thinking": False, "context_window": 128000, "params": "9.15B",   "daily_limit": 100000, "focus": "中文对话"},
        {"id": "THUDM/glm-4-32k",              "name": "GLM-4 32K",        "type": "general",  "thinking": False, "context_window": 32000,  "params": "32.39B",  "daily_limit": 100000, "focus": "长文本"},
        # DeepSeek系列 - 深度求索
        {"id": "deepseek-ai/DeepSeek-V2-Chat",  "name": "DeepSeek V2 对话",  "type": "general",  "thinking": False, "context_window": 64000,  "params": "45.96B",  "daily_limit": 100000, "focus": "代码推理"},
        {"id": "deepseek-ai/DeepSeek-V2",       "name": "DeepSeek V2",       "type": "reasoning", "thinking": True,  "context_window": 64000,  "params": "45.96B",  "daily_limit": 100000, "focus": "深度推理"},
        # Yi系列 - 01.AI
        {"id": "01ai/Yi-1.5-9B-Chat",         "name": "Yi 1.5 9B",        "type": "general",  "thinking": False, "context_window": 16000,  "params": "8.91B",   "daily_limit": 100000, "focus": "轻量高效"},
        {"id": "01ai/Yi-1.5-34B-Chat",        "name": "Yi 1.5 34B",       "type": "reasoning", "thinking": True,  "context_window": 32000,  "params": "34.78B",  "daily_limit": 100000, "focus": "高性能"},
    ]
}


# =============================================================================
# 🆓 OpenRouter 免费模型 (2026-03-10)
# =============================================================================
# API Key: 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
# 模型: openrouter/free - 自动路由到当前可用免费模型
# 限制: 50次/天, 20次/分钟
# =============================================================================

OPENROUTER_CONFIG = {
    "api_key": "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",
    "base_url": "https://openrouter.ai/api/v1",
    "provider": "openrouter",
    "name": "OpenRouter免费",
    "rate_limit": {"enabled": True, "max_requests_per_minute": 20, "recovery_time": 60},
    "models": [
        {"id": "openrouter/free", "name": "免费路由", "type": "general", "thinking": False, "context_window": 128000, "note": "自动选择可用免费模型"},
    ]
}


# =============================================================================
# 📦 合并配置
# =============================================================================

CONFIG = {
    "primary_model": "ark-code-latest",
    "provider": "doubao",
    "providers": {
        "doubao": DOUBAO_CONFIG,
        "zhipu": ZHIPU_CONFIG,
        "modelscope": MODELSCOPE_CONFIG,
        "nvidia": NVIDIA_CONFIG,
        "openrouter": OPENROUTER_CONFIG,
        "siliconflow": SILICONFLOW_CONFIG,
    }
}


# =============================================================================
# 📊 模型信息映射
# =============================================================================

MODEL_INFO = {}

for provider_name, provider_config in CONFIG["providers"].items():
    for model in provider_config.get("models", []):
        model_id = model["id"]
        MODEL_INFO[model_id] = {
            "provider": provider_name,
            "provider_name": provider_config.get("name", provider_name),
            "name": model.get("name", model_id),
            "type": model.get("type", "general"),
            "thinking": model.get("thinking", False),
            "vision": model.get("vision", False),
            "image_gen": model.get("image_gen", False),
            "video_gen": model.get("video_gen", False),
            "context_window": model.get("context_window", 128000),
        }


# =============================================================================
# ⚙️ 系统配置
# =============================================================================

SYSTEM_CONFIG = {
    "timeout": 120,
    "max_retries": 3,
    "temperature": 0.7,
    "max_tokens": 2048,
}


# =============================================================================
# 🚦 限流检测器
# =============================================================================

@dataclass
class RateLimiter:
    """限流器"""
    max_requests: int = 60
    window_seconds: int = 60
    recovery_seconds: int = 60
    
    _requests: list = field(default_factory=list)
    _blocked_until: float = 0
    
    def is_allowed(self) -> bool:
        now = time.time()
        if self._blocked_until > now:
            return False
        self._requests = [t for t in self._requests if now - t < self.window_seconds]
        if len(self._requests) >= self.max_requests:
            self._blocked_until = now + self.recovery_seconds
            return False
        return True
    
    def record_request(self):
        self._requests.append(time.time())
    
    def get_recovery_time(self) -> Optional[float]:
        if self._blocked_until > time.time():
            return self._blocked_until - time.time()
        return None
    
    def reset(self):
        self._requests.clear()
        self._blocked_until = 0


_rate_limiters: Dict[str, RateLimiter] = {}


def get_rate_limiter(provider: str) -> RateLimiter:
    if provider not in _rate_limiters:
        config = CONFIG["providers"].get(provider, {})
        rate_limit = config.get("rate_limit", {})
        _rate_limiters[provider] = RateLimiter(
            max_requests=rate_limit.get("max_requests_per_minute", 60),
            window_seconds=60,
            recovery_seconds=rate_limit.get("recovery_time", 60)
        )
    return _rate_limiters[provider]


def check_rate_limit(provider: str) -> tuple[bool, Optional[float]]:
    limiter = get_rate_limiter(provider)
    allowed = limiter.is_allowed()
    recovery_time = limiter.get_recovery_time() if not allowed else None
    return allowed, recovery_time


def record_request(provider: str):
    get_rate_limiter(provider).record_request()


# =============================================================================
# 🔧 工具函数
# =============================================================================

def get_provider_for_model(model_id: str) -> str:
    return MODEL_INFO.get(model_id, {}).get("provider", "unknown")


def get_provider_name(provider: str) -> str:
    return CONFIG["providers"].get(provider, {}).get("name", provider)


def get_api_config_for_model(model_id: str) -> dict:
    provider = get_provider_for_model(model_id)
    configs = {"doubao": DOUBAO_CONFIG, "zhipu": ZHIPU_CONFIG, "modelscope": MODELSCOPE_CONFIG, "nvidia": NVIDIA_CONFIG}
    return configs.get(provider, DOUBAO_CONFIG)


def get_model_info(model_id: str) -> dict:
    return MODEL_INFO.get(model_id, {})


def get_models_by_type(model_type: str) -> list:
    return [mid for mid, info in MODEL_INFO.items() if info.get("type") == model_type]


def get_models_by_provider(provider: str) -> list:
    return [mid for mid, info in MODEL_INFO.items() if info.get("provider") == provider]


def get_all_models() -> list:
    return list(MODEL_INFO.keys())


# =============================================================================
# 📤 导出
# =============================================================================

API_CONFIG = CONFIG

# 触发关键词配置 v1.0
TRIGGER_CONFIG = {
    "active": {
        "交响": ["交响", "调度", "多模型"],
        "开发": ["开发", "编程", "代码"],
        "学习": ["学习", "搜索", "研究"],
    },
    "passive": {
        "问题": ["为什么", "怎么办"],
        "不确定": ["不知道", "不确定"],
    },
}

def get_trigger_mode(message):
    from trigger_system import get_auto_help
    return get_auto_help(message)

# ==================== 向量嵌入模型配置 ====================
# 注意：这些模型需要通过对应的API调用，部分可能需要本地部署
EMBEDDING_CONFIG = {
    "nv-embed-v2": {
        "provider": "nvidia",
        "model": "nvidia/nv-embed-v2",
        "dimension": 4096,
        "api_url": "https://integrate.api.nvidia.com/v1/embeddings",
        "description": "MTEB排名第一的向量模型 (需要NVIDIA NIM)"
    },
    "bge-m3": {
        "provider": "local",  # 需要本地部署
        "model": "BAAI/bge-m3",
        "dimension": 1024,
        "api_url": "http://localhost:8000/v1/embeddings",
        "description": "BGE多语言向量模型 (需要本地部署)"
    },
    # 可用的LLM模型作为备选（用于语义理解）
    "deepseek-v3.2": {
        "provider": "modelscope",
        "model": "deepseek-ai/DeepSeek-V3.2",
        "dimension": None,
        "api_url": "https://api-inference.modelscope.cn/v1/chat/completions",
        "description": "DeepSeek V3.2 (可用)"
    },
    "MiniMax-M2.5": {
        "provider": "modelscope",
        "model": "MiniMax/MiniMax-M2.5",
        "dimension": None,
        "api_url": "https://api-inference.modelscope.cn/v1/chat/completions",
        "description": "MiniMax M2.5 (可用)"
    },
}

# ==================== 重排序模型配置 ====================
# 注意：这些模型需要通过对应的API调用，部分可能需要本地部署
RERANK_CONFIG = {
    "rerank-qa-mistral-4b": {
        "provider": "nvidia",
        "model": "nvidia/rerank-qa-mistral-4b",
        "api_url": "https://integrate.api.nvidia.com/v1/rerank",
        "description": "NVIDIA重排序模型 (需要NVIDIA NIM)"
    },
    "bge-reranker-v2-m3": {
        "provider": "local",  # 需要本地部署
        "model": "BAAI/bge-reranker-v2-m3",
        "api_url": "http://localhost:8000/v1/rerank",
        "description": "BGE重排序模型 (需要本地部署)"
    },
    # 使用LLM进行重排序作为备选
    "llm-rerank": {
        "provider": "doubao",
        "model": "ark-code-latest",
        "api_url": "https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions",
        "description": "使用LLM进行重排序 (可用)"
    },
}

__all__ = [
    "CONFIG", "API_CONFIG", "SYSTEM_CONFIG", "MODEL_INFO",
    "DOUBAO_CONFIG", "ZHIPU_CONFIG", "MODELSCOPE_CONFIG", "NVIDIA_CONFIG",
    "get_genesis_story", "get_dream_maker", "get_jiaoJiao", "get_brand",
    "get_provider_for_model", "get_provider_name", "get_api_config_for_model",
    "get_model_info", "get_models_by_type", "get_models_by_provider", "get_all_models",
    "check_rate_limit", "record_request", "RateLimiter",
]
