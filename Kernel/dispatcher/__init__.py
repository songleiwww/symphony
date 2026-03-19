# -*- coding: utf-8 -*-
"""
序境系统调度器模块 - Dispatcher Module

统一调度入口，整合所有调度能力

模块结构：
- adaptive_scheduler.py: 自适应调度器
- batch_scheduler.py: 批处理调度器
- legacy/: 历史调度器（兼容性保留）
"""
from .adaptive_scheduler import AdaptiveScheduler
from .batch_scheduler import BatchScheduler

# 导出核心类
__all__ = [
    "AdaptiveScheduler",
    "BatchScheduler",
]

# 版本信息
__version__ = "3.2.0"
