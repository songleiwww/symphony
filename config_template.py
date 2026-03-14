#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境 Symphony 2.3.0 设置模板
复制此文件并修改配置
"""

# =============================================================================
# 🎼 序境 Symphony 2.3.0 配置模板
# =============================================================================

# 基础配置
SYMPHONY_VERSION = "2.3.0"
SYMPHONY_NAME = "序境智能Skills系统"

# API配置
API_CONFIG = {
    "siliconflow": {
        "api_key": "YOUR_API_KEY",
        "base_url": "https://api.siliconflow.cn/v1",
        "models": {
            "primary": "Qwen/Qwen2.5-14B-Instruct",
            "fallback": ["Qwen/Qwen2.5-7B-Instruct", "THUDM/glm-4-9b-chat"]
        }
    }
}

# 少府监成员配置
MEMBERS_CONFIG = [
    {"name": "沈清弦", "title": "枢密使", "model": "Qwen/Qwen2.5-14B-Instruct"},
    {"name": "苏云渺", "title": "工部尚书", "model": "Qwen/Qwen2.5-14B-Instruct"},
    {"name": "顾清歌", "title": "翰林学士", "model": "THUDM/glm-4-9b-chat"},
    {"name": "沈星衍", "title": "智囊博士", "model": "Qwen/Qwen2.5-14B-Instruct"},
    {"name": "叶轻尘", "title": "行走使", "model": "Qwen/Qwen2.5-7B-Instruct"},
    {"name": "林码", "title": "营造司正", "model": "Qwen/Qwen2.5-72B-Instruct"},
    {"name": "顾至尊", "title": "首辅大学士", "model": "Qwen/Qwen2.5-14B-Instruct"},
    {"name": "陆念昭", "title": "少府监", "model": "Qwen/Qwen2.5-7B-Instruct"},
]

# 调度配置
SCHEDULER_CONFIG = {
    "timeout": 30,
    "max_retries": 3,
    "load_balance": True,
    "auto_fallback": True
}

# 技能配置
SKILLS_CONFIG = {
    "auto_activate": True,
    "cooldown": 60,
    "upgrade_threshold": 100
}

# 进化配置
EVOLUTION_CONFIG = {
    "enabled": True,
    "max_level": 10,
    "passive_learning": True,
    "active_learning": True
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",
    "file": "symphony.log",
    "max_size": 10485760
}

# 导出配置
def get_config():
    return {
        "version": SYMPHONY_VERSION,
        "name": SYMPHONY_NAME,
        "api": API_CONFIG,
        "members": MEMBERS_CONFIG,
        "scheduler": SCHEDULER_CONFIG,
        "skills": SKILLS_CONFIG,
        "evolution": EVOLUTION_CONFIG,
        "log": LOG_CONFIG
    }

if __name__ == "__main__":
    import json
    print(json.dumps(get_config(), indent=2, ensure_ascii=False))
