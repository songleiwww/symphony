# -*- coding: utf-8 -*-
"""
序境系统自适应调度配置 v2.0
===================================
⚠️ 已废弃 - 请使用独立模块导入
   from skills.symphony.config import load_all
   或单独导入: from skills.symphony.config.task_complexity import TASK_COMPLEXITY

本文件作为向后兼容存根，加载所有分片配置并合并为单一命名空间。
新版代码请直接从各子模块导入，避免加载无关配置。
"""
import warnings
warnings.warn(
    "adaptive_scheduler.py 已废弃，请使用 skills.symphony.config 模块",
    DeprecationWarning,
    stacklevel=2
)

# 向后兼容导入
from .task_complexity import TASK_COMPLEXITY
from .scheduling_strategy import SCHEDULING_STRATEGY
from .hot_update import HOT_UPDATE
from .tokens_config import TOKENS_CONFIG
from .provider_mapping import PROVIDER_MAPPING
from .official_bindings import OFFICIAL_BINDINGS

# 运行时统计（保持与原接口一致）
SCHEDULING_STATS = {
    "total_dispatches": 0,
    "successful_dispatches": 0,
    "failed_dispatches": 0,
    "avg_response_time": 0,
    "model_usage": {}
}
