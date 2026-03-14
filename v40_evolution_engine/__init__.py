#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青丘v4.0进化引擎
QingQiu Evolution Engine v4.0

Copyright (c) 2024 青丘团队
All rights reserved.
"""

__version__ = "4.0.0"
__author__ = "青丘研发团队"
__description__ = "青丘v4.0进化引擎 - 具有自我反思、持续进化能力的人工智能引擎"

from .qinqiu_evolution_engine import (
    QingQiuEvolutionEngine,
    SelfIntrospection,
    MUSELoop,
    RuntimeAdaptation,
    IntrospectionLevel,
    ExecutionStatus,
    ExecutionResult,
    IntrospectionResult,
    MUSELoopResult
)

from .memory_evolution import (
    MemoryEvolutionSystem,
    RealTimeAdaptationLayer,
    ReflectionAnalysisLayer,
    StructuralOptimizationLayer,
    MemoryType,
    MemoryImportance,
    MemoryItem,
    MemoryAssociation
)

from .safety_control import (
    SafetyControlSystem,
    BoundaryControlLayer,
    CircuitBreakerLayer,
    AuditControlLayer,
    SecurityLevel,
    RiskLevel,
    CircuitBreakerState,
    SecurityPolicy,
    SecurityEvent,
    AuditLog,
    CircuitBreakerConfig
)

from .performance_optimizer import (
    PerformanceOptimizer,
    CacheAccelerationLayer,
    IncrementalAccelerationLayer,
    ParallelAccelerationLayer,
    CacheStrategy,
    IncrementalUpdateType,
    ParallelStrategy,
    CacheEntry,
    PerformanceMetrics,
    TaskExecutionResult
)

__all__ = [
    # 核心引擎
    "QingQiuEvolutionEngine",
    "SelfIntrospection",
    "MUSELoop",
    "RuntimeAdaptation",
    "IntrospectionLevel",
    "ExecutionStatus",
    "ExecutionResult",
    "IntrospectionResult",
    "MUSELoopResult",
    
    # 记忆进化系统
    "MemoryEvolutionSystem",
    "RealTimeAdaptationLayer",
    "ReflectionAnalysisLayer",
    "StructuralOptimizationLayer",
    "MemoryType",
    "MemoryImportance",
    "MemoryItem",
    "MemoryAssociation",
    
    # 安全控制系统
    "SafetyControlSystem",
    "BoundaryControlLayer",
    "CircuitBreakerLayer",
    "AuditControlLayer",
    "SecurityLevel",
    "RiskLevel",
    "CircuitBreakerState",
    "SecurityPolicy",
    "SecurityEvent",
    "AuditLog",
    "CircuitBreakerConfig",
    
    # 性能优化系统
    "PerformanceOptimizer",
    "CacheAccelerationLayer",
    "IncrementalAccelerationLayer",
    "ParallelAccelerationLayer",
    "CacheStrategy",
    "IncrementalUpdateType",
    "ParallelStrategy",
    "CacheEntry",
    "PerformanceMetrics",
    "TaskExecutionResult"
]
