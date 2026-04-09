# -*- coding: utf-8 -*-
"""
任务复杂度分级配置
"""
TASK_COMPLEXITY = {
    "简单": {
        "keywords": ["问答", "翻译", "问候", "简单", "what is", "how to", "介绍一下", "是什么"],
        "max_tokens": None,
        "preferred_models": ["GLM-4.7-Flash", "doubao-seed-2.0-lite", "GLM-4V-Flash"],
        "temperature": 0.7
    },
    "中等": {
        "keywords": ["代码", "写", "分析", "总结", "code", "编程", "生成", "创作"],
        "max_tokens": None,
        "preferred_models": ["doubao-seed-2.0-code", "MiniMax-M2.5", "Kimi K2.5"],
        "temperature": 0.8
    },
    "复杂": {
        "keywords": ["战略", "规划", "设计", "架构", "长文", "深度", "系统", "方案"],
        "max_tokens": None,
        "preferred_models": ["Kimi K2.5", "MiniMax-M2.5", "GLM-4.7"],
        "temperature": 0.9
    }
}
