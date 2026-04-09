# -*- coding: utf-8 -*-
"""
模型服务商完整映�?"""
PROVIDER_MAPPING = {
    # "火山引擎": {  # �?已暂�?(2026-03-28) - 避免触发限流错误
    #     "models": [
    #         "GLM-4.7", "GLM-4.7-Flash", "Kimi K2.5", "MiniMax-M2.5",
    #         "doubao-seed-2.0-code", "doubao-seed-2.0-lite", "ark-code-latest"
    #     ],
    #     "endpoint": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
    #     "priority": 1
    # },
    "智谱": {
        "models": [
            "GLM-4.7-Flash", "GLM-Z1-Flash", "GLM-4.6V-Flash", "GLM-4V-Flash",
            "GLM-4.1V-Thinking-Flash", "CogView-3-Flash", "CogVideoX-Flash"
        ],
        "endpoint": "https://open.bigmodel.cn/api/paas/v4/",
        "priority": 2
    },
    "魔搭": {
        "models": [
            "ZhipuAI/GLM-5", "moonshotai/Kimi-K2.5", "MiniMax/MiniMax-M2.5",
            "Qwen/Qwen3.5-397B-A17B", "ZhipuAI/GLM-4.7-Flash"
        ],
        "endpoint": "https://api-inference.modelscope.cn/v1",
        "priority": 3
    },
    "英伟�?: {
        "models": [
            "meta/llama-3.1-70b-instruct", "deepseek-ai/deepseek-r1-distill-qwen-32b",
            "nvidia/llama-3.3-nemotron-super-49b-v1.5"
        ],
        "endpoint": "https://integrate.api.nvidia.com/v1/chat/completions",
        "priority": 4
    },
}

