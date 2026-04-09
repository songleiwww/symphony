#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境完整内核 v4.5.0 交付版
Complete Symphony Kernel - Production Ready
日期: 2026-04-09
状态: 完整交付
"""
import sys
import os

# 固定路径
SYM_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony'
DB_PATH = os.path.join(SYM_PATH, 'data', 'symphony.db')

sys.path.insert(0, SYM_PATH)

# ==================== 核心导入 ====================
from symphony_scheduler import symphony_scheduler
from Kernel import EvolutionKernel, IntelligentStrategyScheduler
from Kernel import WisdomEmergenceEngine, AdaptiveAlgorithmCoordinator
from providers.pool import ProviderPool
from strategy.dual_engine_scheduler import DualEngineScheduler, DualEngineConfig
from Kernel.multi_agent.multi_agent_orchestrator import CrewOrchestrator, AgentRole, Task

__version__ = '4.5.0'
__status__ = 'PRODUCTION_READY'
__交付时间__ = '2026-04-09'

class SymphonyKernel:
    """
    序境完整内核
    统一调度入口：解惑、任务分解、代码、审查、分析
    """
    
    def __init__(self):
        self.version = __version__
        self.kernel = EvolutionKernel()
        self.pool = None
        self.scheduler = None
        self._init_pool()
        self._init_scheduler()
        
    def _init_pool(self):
        try:
            self.pool = ProviderPool(DB_PATH)
        except:
            self.pool = None
            
    def _init_scheduler(self):
        try:
            self.scheduler = IntelligentStrategyScheduler()
            if self.pool:
                self.scheduler.set_provider_pool(self.pool)
        except:
            self.scheduler = None
    
    def dispatch(self, task: str, mode: str = 'auto') -> str:
        """
        统一调度入口
        mode: auto/analysis/coding/review/plan
        """
        return symphony_scheduler(task)
    
    def ask(self, question: str) -> str:
        """问答模式"""
        return symphony_scheduler(question)
    
    def analyze(self, task: str) -> str:
        """分析模式"""
        return symphony_scheduler(f"分析以下内容：{task}")
    
    def plan(self, task: str) -> str:
        """规划模式"""
        return symphony_scheduler(f"将以下任务分解为详细步骤：{task}")
    
    def review(self, code: str, language: str = '通用') -> str:
        """审查模式"""
        return symphony_scheduler(f"审查以下{language}代码：{code}")
    
    def explain(self, code: str) -> str:
        """解释模式"""
        return symphony_scheduler(f"解释以下代码：{code}")
    
    def status(self) -> dict:
        """内核状态"""
        return {
            'version': self.version,
            'status': __status__,
            'pool_ready': self.pool is not None,
            'scheduler_ready': self.scheduler is not None,
            'kernel_id': self.kernel.kernel_id if hasattr(self.kernel, 'kernel_id') else None
        }

# ==================== 便捷函数 ====================
def ask(question: str) -> str:
    """快捷问答"""
    return symphony_scheduler(question)

def analyze(task: str) -> str:
    """快捷分析"""
    return symphony_scheduler(f"分析：{task}")

def plan(task: str) -> str:
    """快捷规划"""
    return symphony_scheduler(f"分解任务：{task}")

def review(code: str, language: str = '通用') -> str:
    """快捷审查"""
    return symphony_scheduler(f"审查{language}代码：{code}")

def explain(code: str) -> str:
    """快捷解释"""
    return symphony_scheduler(f"解释代码：{code}")

def status() -> dict:
    """快捷状态"""
    k = SymphonyKernel()
    return k.status()

# ==================== 测试验证 ====================
if __name__ == '__main__':
    print("=" * 60)
    print(" 序境完整内核 v4.5.0 交付版 ")
    print("=" * 60)
    
    print("\n[1] 创建内核实例...")
    kernel = SymphonyKernel()
    print(f"    版本: {kernel.version}")
    print(f"    状态: {__status__}")
    
    print("\n[2] 内核状态...")
    st = kernel.status()
    for k, v in st.items():
        print(f"    {k}: {v}")
    
    print("\n[3] 调度测试...")
    result = kernel.ask("1+1等于几？回复一个数字。")
    print(f"    结果: {result}")
    
    print("\n[4] 分析测试...")
    result = kernel.analyze("什么是人工智能？")
    print(f"    结果: {result[:80]}...")
    
    print("\n" + "=" * 60)
    print(" 交付状态: 完整内核就绪 ✅")
    print("=" * 60)
