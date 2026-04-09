# -*- coding: utf-8 -*-
"""
模型服务商完整映射
"""
PROVIDER_MAPPING = {
    "volcano": {
        "models": [
            "doubao-seed-2.0-code", "doubao-seed-2.0-pro", "doubao-seed-2.0-lite", 
            "minimax-m2.5", "kimi-k2.5", "glm-4.7",
            "deepseek-v3.2", "deepseek-v3-250324"
        ],
        "endpoint": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        "priority": 1
    },
    "minimax": {
        "models": [
            "MiniMax-M2.7"
        ],
        "endpoint": "https://api.minimax.chat/v1/",
        "priority": 2
    },
    "ollama": {
        "models": [
            "llama3:8b", "llama3.2:3b", "gemma2:9b", "qwen2:7b", 
            "mistral:7b", "phi3:3.8b"
        ],
        "endpoint": "http://localhost:11434/v1/chat/completions",
        "priority": 7
    },
    "智谱": {
        "models": [
            "GLM-4.7-Flash", "GLM-Z1-Flash", "GLM-4.6V-Flash", "GLM-4V-Flash",
            "GLM-4.1V-Thinking-Flash", "CogView-3-Flash", "CogVideoX-Flash"
        ],
        "endpoint": "https://open.bigmodel.cn/api/paas/v4/",
        "priority": 3
    },
    "魔搭": {
        "models": [
            "MiniMax/MiniMax-M2.5",
            "Qwen/Qwen2.5-14B-Instruct",
            "Qwen/Qwen2.5-32B-Instruct",
            "Qwen/Qwen2.5-72B-Instruct",
            "Qwen/Qwen2.5-7B-Instruct",
            "Qwen/Qwen2.5-Coder-32B-Instruct",
            "Qwen/Qwen2.5-Coder-7B-Instruct",
            "Qwen/Qwen3-110B",
            "Qwen/Qwen3-32B",
            "Qwen/Qwen3-72B",
            "Qwen/Qwen3-8B",
            "ZhipuAI/GLM-4-9B-Chat",
            "ZhipuAI/GLM-4-Plus",
            "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
            "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
            "deepseek-ai/DeepSeek-V2-Chat",
            "moonshotai/Kimi-K2-8B-Instruct",
            "moonshotai/Kimi-K2-Instruct",
            "ZhipuAI/GLM-5", 
            "moonshotai/Kimi-K2.5", 
            "MiniMax/MiniMax-M2.5",
            "Qwen/Qwen3.5-397B-A17B", 
            "ZhipuAI/GLM-4.7-Flash"
        ],
        "endpoint": "https://api-inference.modelscope.cn/v1",
        "priority": 4
    },
    "英伟达": {
        "models": [
            "deepseek-ai/deepseek-r1-distill-llama-70b",
            "deepseek-ai/deepseek-r1-distill-qwen-32b",
            "google/gemma-2-27b-it",
            "google/gemma-2-2b-it",
            "google/gemma-2-9b-it",
            "meta/codellama-70b-instruct",
            "meta/llama-3-70b-instruct",
            "meta/llama-3-8b-instruct",
            "meta/llama-3.1-405b-instruct",
            "meta/llama-3.1-70b-instruct",
            "meta/llama-3.1-8b-instruct",
            "microsoft/phi-3-medium-4k-instruct",
            "microsoft/phi-3-mini-4k-instruct",
            "mistralai/mistral-7b-instruct-v0.3",
            "mistralai/mistral-nemo-12b-instruct",
            "mistralai/mixtral-8x22b-instruct-v0.1",
            "mistralai/mixtral-8x7b-instruct-v0.1",
            "nvidia/llama-3.3-nemotron-super-49b-v1.5",
            "qwen/qwen2-72b-instruct",
            "qwen/qwen2-7b-instruct",
            "qwen/qwen2.5-72b-instruct",
            "qwen/qwen2.5-7b-instruct"
        ],
        "endpoint": "https://integrate.api.nvidia.com/v1/chat/completions",
        "priority": 5
    },
    "硅基流动": {
        "models": [
            "deepseek-ai/DeepSeek-V2-Chat", "01ai/Yi-1.5-9B-Chat"
        ],
        "endpoint": "https://api.siliconflow.cn/v1/chat/completions",
        "priority": 6
    },
    "ali_bailian": {
        "models": [
            "deepseek-r1-distill-qwen-7b",
            "gte-rerank",
            "qvq-max-2025-03-25",
            "qwen-audio-chat",
            "qwen-coder-14b-instruct",
            "qwen-coder-32b-instruct",
            "qwen-coder-7b-instruct",
            "qwen-coder-turbo-0919",
            "qwen-math-72b-instruct",
            "qwen-math-7b-instruct",
            "qwen-math-turbo",
            "qwen-plus",
            "qwen-plus-2025-07-28",
            "qwen-pro",
            "qwen-ultra",
            "qwen-vl-14b-instruct",
            "qwen-vl-7b-instruct",
            "qwen-vl-max",
            "qwen-vl-plus",
            "qwen-vl-plus-2025-05-07",
            "qwen2-72b-instruct",
            "qwen2-7b-instruct",
            "qwen2.5-110b-instruct",
            "qwen2.5-14b-instruct",
            "qwen2.5-32b-instruct",
            "qwen2.5-72b-instruct",
            "qwen2.5-7b-instruct",
            "qwen2.5-math-7b-instruct",
            "qwen2.5-vl-72b-instruct",
            "qwen3-110b-instruct",
            "qwen3-72b-instruct",
            "qwen3-8b-instruct",
            "qwen3-embedding",
            "qwen3-vl-235b-a22b-thinking",
            "qwen3-vl-32b-thinking",
            "sambert-tts",
            "text-embedding-v1",
            "text-embedding-v2",
            "text-embedding-v3",
            "wanx-image-generation"
        ],
        "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "priority": 8
    }
}
