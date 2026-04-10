# -*- coding: utf-8 -*-
"""
序境系统 - Kernel 内核模块
========================

核心内核级秩序规则（必须严格遵守）:

1. **向量存储规则**: 保存原始文本数据，不持久化存储向量
   - 当向量模型更换时，可基于原始文本直接重建向量索引
   - 不影响数据完整性，保证模型可平滑切换
   - 此规则为内核级秩序，所有模块必须遵守

2. **Token预算优化规则**: 尽量节省主模型tokens消耗
   - 多调度中小模型完成思考、分析、预处理工作
   - 主模型只处理最终汇总、决策、生成工作
   - 降低总体成本，提高系统并发能力

核心模块:
- WisdomAwakeningEngine: 智慧觉醒引擎（100%验证通过，正式晋升）
- IntelligentStrategyScheduler: 智能策略调度器（主调度器）
- EvolutionKernel: 进化内核
- AdaptiveAlgorithmCoordinator: 自适应算法协调器
"""

from .wisdom_engine import WisdomAwakeningEngine
from .intelligent_strategy_scheduler import IntelligentStrategyScheduler
from .evolution_kernel import EvolutionKernel
from .adaptive_algorithm_coordinator import AdaptiveAlgorithmCoordinator
from .tavily_mcp_search import TavilyMcpSearchScheduler, quick_search, quick_extract
from .provider_health_checker import ProviderHealthChecker, ProviderHealth, print_health_report
from .bypass_protection import (
    BypassDetector, BypassViolation,
    get_detector, enforce_no_bypass, protected_function,
    verify_priority_order, audit_core_integrity, print_audit_report,
    FIXED_PRIORITY_ORDER
)
import sys
import os
from .code_auditor import (
    KernelCodeAuditor,
    AuditRule,
    AuditFinding,
    AuditResult,
    AuditStatus,
    quick_audit,
)

# 兵家智慧增强调度（兵法启发落地）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from symphony_scheduler_military import (
    MilitarySchedulerStats,
    military_stats,
    PromptCache,
    prompt_cache,
    symphony_scheduler_military,
    symphony_scheduler_with_cache,
    get_suitable_models,
    kernel_call as military_kernel_call,
)
# 序境管家 - 内核级AI机器人
from .symphony_steward import (
    SymphonySteward,
    KernelModuleInfo,
    ModelCapability,
    ExternalAgentInfo,
    KernelStatusReport,
)

__all__ = [
    'WisdomAwakeningEngine',
    'IntelligentStrategyScheduler',
    'EvolutionKernel',
    'AdaptiveAlgorithmCoordinator',
    'TavilyMcpSearchScheduler',
    'quick_search',
    'quick_extract',
    'ProviderHealthChecker',
    'ProviderHealth',
    'print_health_report',
    # 内核旁路防护
    'BypassDetector',
    'BypassViolation',
    'get_detector',
    'enforce_no_bypass',
    'protected_function',
    'verify_priority_order',
    'audit_core_integrity',
    'print_audit_report',
    'FIXED_PRIORITY_ORDER',
    # 内核级代码审计
    'KernelCodeAuditor',
    'AuditRule',
    'AuditFinding',
    'AuditResult',
    'AuditStatus',
    'quick_audit',
    # 兵家智慧增强调度
    'MilitarySchedulerStats',
    'military_stats',
    'PromptCache',
    'prompt_cache',
    'symphony_scheduler_military',
    'symphony_scheduler_with_cache',
    'get_suitable_models',
    'military_kernel_call',
    # 序境管家 - 内核级AI机器人
    'SymphonySteward',
    'KernelModuleInfo',
    'ModelCapability',
    'ExternalAgentInfo',
    'KernelStatusReport',
]

__version__ = '4.5.0'
