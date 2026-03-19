# -*- coding: utf-8 -*-
"""
序境内核进化 - 三层记忆系统
=============================
智囊博士: 沈星衍
版本: 3.2.0
基于AI Agent记忆系统三层架构设计

设计理念:
- 工作记忆(Working Memory): LLM Context Window管理 - 当前会话即时信息
- 短期记忆(Short-term Memory): 向量数据库+RAG - 会话级上下文保持
- 长期记忆(Long-term Memory): 知识图谱+持久化 - 跨会话知识沉淀

文件结构:
- memory/__init__.py          # 模块入口
- memory/working_memory.py   # 工作记忆层 - Context Window管理
- memory/shortterm_memory.py # 短期记忆层 - 向量+RAG
- memory/longterm_memory.py  # 长期记忆层 - 知识图谱+持久化
- memory/context_manager.py  # Context Window管理器
- memory/summarizer.py       # 自动摘要提取
- memory/importance_scorer.py # 重要性排序
- memory/persistence.py       # 数据库持久化
- memory/integrator.py       # 三层记忆整合器
"""

__version__ = "3.2.0"
__author__ = "沈星衍"

from .working_memory import WorkingMemoryManager
from .shortterm_memory import ShortTermMemoryManager
from .longterm_memory import LongTermMemoryManager
from .context_manager import ContextWindowManager
from .summarizer import MemorySummarizer
from .importance_scorer import ImportanceScorer
from .persistence import MemoryPersistence
from .integrator import TripleMemoryIntegrator

__all__ = [
    "WorkingMemoryManager",
    "ShortTermMemoryManager", 
    "LongTermMemoryManager",
    "ContextWindowManager",
    "MemorySummarizer",
    "ImportanceScorer",
    "MemoryPersistence",
    "TripleMemoryIntegrator"
]
