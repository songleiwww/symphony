# -*- coding: utf-8 -*-
"""
🎼 Symphony 多模型协作调度系统
Symphony - Multi-Model Collaboration Dispatch System

版本 Version: 2.3.0
作者 Author: 造梦者 & 交交 (Dreamer & Jiaojiao)
许可证 License: MIT

简介 Description:
    交响(Symphony)是一个智能多模型协作调度系统，
    支持多模型并行调用、故障转移、任务调度等功能。
    
    Symphony is an intelligent multi-model collaboration dispatch system
    that supports parallel model calling, fault tolerance, task scheduling, etc.

安装 Installation:
    pip install symphony-ai

快速开始 Quick Start:
    from symphony import SymphonyCore
    
    symphony = SymphonyCore()
    result = symphony.dispatch("你的任务描述")
"""

__version__ = "2.3.0"
__author__ = "造梦者 & 交交 (Dreamer & Jiaojiao)"
__email__ = "songlei_www@qq.com"
__license__ = "MIT"

# 导入核心类 | Import core classes
from symphony_core import SymphonyCore

# 导出公共接口 | Export public interfaces
__all__ = [
    "SymphonyCore",
    "__version__",
    "__author__",
]
