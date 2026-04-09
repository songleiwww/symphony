# -*- coding: utf-8 -*-
"""
序境系统 - Kernel 内核模块
========================

核心模块:
- WisdomEmergenceEngine: 智慧涌现引擎
- IntelligentStrategyScheduler: 智能策略调度器（主调度器）
- EvolutionKernel: 进化内核
- AdaptiveAlgorithmCoordinator: 自适应算法协调器
"""

from .wisdom_engine import WisdomEmergenceEngine
from .intelligent_strategy_scheduler import IntelligentStrategyScheduler
from .evolution_kernel import EvolutionKernel
from .adaptive_algorithm_coordinator import AdaptiveAlgorithmCoordinator

__all__ = [
    'WisdomEmergenceEngine',
    'IntelligentStrategyScheduler',
    'EvolutionKernel',
    'AdaptiveAlgorithmCoordinator',
]

__version__ = '4.3.0'
