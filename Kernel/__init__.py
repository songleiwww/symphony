# -*- coding: utf-8 -*-
"""
序境交响内核
策略: 现在进行时永远优先过去进行时
数据源: symphony.db (唯一数据源)
"""
__version__ = "2.0.0"
__author__ = "序境系统"

from .kernel_loader import KernelLoader
from .config_manager import ConfigManager
from .dispatch_manager import DispatchManager

__all__ = ['KernelLoader', 'ConfigManager', 'DispatchManager']
