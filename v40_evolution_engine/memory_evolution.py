#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青丘v4.0进化引擎 - 记忆进化模块
QingQiu Evolution Engine v4.0 - Memory Evolution Module

技术总监: 张晓明
设计目标: 实现三层记忆进化架构，支持记忆的动态更新、深度分析和结构优化
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set, Callable
import uuid
import logging
from collections import defaultdict
import hashlib
import numpy as np

# 导入引擎核心类型
from qinqiu_evolution_engine import ExecutionResult, ExecutionStatus

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """记忆类型枚举"""
    EPISODIC = "episodic"      # 情景记忆：具体事件和经历
    SEMANTIC = "semantic"      # 语义记忆：知识和事实
    PROCEDURAL = "procedural"  # 程序记忆：技能和流程
    EMOTIONAL = "emotional"    # 情绪记忆：情感体验
    WORKING = "working"        # 工作记忆：临时处理中的记忆


class MemoryImportance(Enum):
    """记忆重要程度枚举"""
    TRIVIAL = "trivial"        # 琐碎：很快会被遗忘
    LOW = "low"                # 低重要性
    MEDIUM = "medium"          # 中等重要性
    HIGH = "high"              # 高重要性
    CRITICAL = "critical"      # 关键：永久保留


@dataclass
class MemoryItem:
    """记忆项数据类"""
    memory_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: Any = None
    memory_type: MemoryType = MemoryType.EPISODIC
    importance: MemoryImportance = MemoryImportance.MEDIUM
    tags: List[str] = field(default_factory=list)
    source: str = "unknown"
    context: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    modified_at: float = field(default_factory=time.time)
    access_count: int = 0
    relevance_score: float = 0.0
    expiration_time: Optional[float] = None  # None表示永不过期
    is_archived: bool = False
    
    @property
    def is_expired(self) -> bool:
        """检查记忆是否已过期"""
        if self.expiration_time is None:
            return False
        return time.time() > self.expiration_time
    
    @property
    def age(self) -> float:
        """获取记忆存在时间（秒）"""
        return time.time() - self.created_at
    
    def access(self) -> None:
        """记录访问"""
        self.accessed_at = time.time()
        self.access_count += 1
    
    def update_content(self, new_content: Any, context: Optional[Dict[str, Any]] = None) -> None:
        """更新记忆内容"""
        self.content = new_content
        if context:
            self.context.update(context)
        self.modified_at = time.time()
    
    def calculate_importance_score(self) -> float:
        """计算记忆的综合重要性分数"""
        # 基础分数根据重要程度
        base_scores = {
            MemoryImportance.TRIVIAL: 0.1,
            MemoryImportance.LOW: 0.3,
            MemoryImportance.MEDIUM: 0.6,
            MemoryImportance.HIGH: 0.8,
            MemoryImportance.CRITICAL: 1.0
        }
        base_score = base_scores.get(self.importance, 0.5)
        
        # 访问频率加成
        access_factor = min(1.0, self.access_count / 10.0)  # 最多加成100%
        
        # 新鲜度加成（越新的记忆分数越高）
        freshness_factor = max(0.1, np.exp(-self.age / (30 * 24 * 3600)))  # 30天半衰期
        
        # 相关性分数加成
        relevance_factor = min(1.0, self.relevance_score)
        
        # 综合评分
        total_score = base_score * (0.4 + 0.2 * access_factor + 0.2 * freshness_factor + 0.2 * relevance_factor)
        
        return min(1.0, max(0.0, total_score))
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'memory_id': self.memory_id,
            'content': self.content,
            'memory_type': self.memory_type.value,
            'importance': self.importance.value,
            'tags': self.tags,
            'source': self.source,
            'context': self.context,
            'embedding': self.embedding,
            'created_at': self.created_at,
            'accessed_at': self.accessed_at,
            'modified_at': self.modified_at,
            'access_count': self.access_count,
            'relevance_score': self.relevance_score,
            'expiration_time': self.expiration_time,
            'is_archived': self.is_archived
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        """从字典创建记忆项"""
        return cls(
            memory_id=data['memory_id'],
            content=data['content'],
            memory_type=MemoryType(data['memory_type']),
            importance=MemoryImportance(data['importance']),
            tags=data.get('tags', []),
            source=data.get('source', 'unknown'),
            context=data.get('context', {}),
            embedding=data.get('embedding'),
            created_at=data.get('created_at', time.time()),
            accessed_at=data.get('accessed_at', time.time()),
            modified_at=data.get('modified_at', time.time()),
            access_count=data.get('access_count', 0),
            relevance_score=data.get('relevance_score', 0.0),
            expiration_time=data.get('expiration_time'),
            is_archived=data.get('is_archived', False)
        )


@dataclass
class MemoryAssociation:
    """记忆关联关系"""
    from_memory_id: str
    to_memory_id: str
    relation_type: str  # "related", "causes", "contradicts", "supports", etc.
    strength: float = 0.5  # 关联强度 0-1
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'from_memory_id': self.from_memory_id,
            'to_memory_id': self.to_memory_id,
            'relation_type': self.relation_type,
            'strength': self.strength,
            'created_at': self.created_at
        }


class RealTimeAdaptationLayer:
    """
    第一层：实时适应层
    Real-Time Adaptation Layer
    
    负责即时记忆的接收、分类和短期存储，支持高速读写
    """
    
    def __init__(self, memory_system: 'MemoryEvolutionSystem'):
        self.memory_system = memory_system
        self.working_memory: Dict[str, MemoryItem] = {}  # 工作记忆（临时存储）
        self.short_term_memory: Dict[str, MemoryItem] = {}  # 短期记忆
        self.max_working_memory_size: int = 50  # 工作记忆最大容量
        self.max_short_term_size: int = 1000  # 短期记忆最大容量
        self.default_short_term_ttl: int = 24 * 3600  # 短期记忆默认存活时间（1天）
        
        # 实时处理队列
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None
        
        logger.info("实时适应层已初始化")
    
    async def start(self) -> None:
        """启动实时处理工作线程"""
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._processing_worker())
            logger.info("实时适应层工作线程已启动")
    
    async def stop(self) -> None:
        """停止实时处理工作线程"""
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("实时适应层工作线程已停止")
    
    async def add_memory(self, memory: MemoryItem) -> str:
        """添加新记忆"""
        # 工作记忆：最近使用的记忆
        memory.access()
        self.working_memory[memory.memory_id] = memory
        
        # 超过容量时，移除最久未使用的
        if len(self.working_memory) > self.max_working_memory_size:
            lru_id = min(self.working_memory.keys(), key=lambda k: self.working_memory[k].accessed_at)
            moved_memory = self.working_memory.pop(lru_id)
            await self._move_to_short_term(moved_memory)
        
        # 加入处理队列进行实时处理
        await self.processing_queue.put(('add', memory))
        
        logger.debug(f"已添加记忆 {memory.memory_id} 到实时适应层")
        return memory.memory_id
    
    async def get_memory(self, memory_id: str) -> Optional[MemoryItem]:
        """获取记忆"""
        # 优先从工作记忆获取
        if memory_id in self.working_memory:
            memory = self.working_memory[memory_id]
            memory.access()
            return memory
        
        # 然后从短期记忆获取
        if memory_id in self.short_term_memory:
            memory = self.short_term_memory[memory_id]
            memory.access()
            # 移回工作记忆
            del self.short_term_memory[memory_id]
            self.working_memory[memory_id] = memory
            return memory
        
        return None
    
    async def search_memory(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[MemoryItem]:
        """搜索记忆"""
        results = []
        
        # 搜索工作记忆
        for memory in self.working_memory.values():
            if await self._memory_matches(memory, query, memory_type, tags):
                memory.access()
                results.append(memory)
        
        # 搜索短期记忆
        for memory in self.short_term_memory.values():
            if await self._memory_matches(memory, query, memory_type, tags):
                memory.access()
                results.append(memory)
        
        # 按相关度排序
        results.sort(key=lambda m: m.relevance_score, reverse=True)
        return results[:limit]
    
    async def _memory_matches(
        self,
        memory: MemoryItem,
        query: str,
        memory_type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """检查记忆是否匹配搜索条件"""
        if memory_type and memory.memory_type != memory_type:
            return False
        
        if tags:
            if not all(tag in memory.tags for tag in tags):
                return False
        
        # 简单的文本匹配（实际可以使用向量相似度搜索）
        query_lower = query.lower()
        if query_lower in str(memory.content).lower():
            return True
        if any(query_lower in tag.lower() for tag in memory.tags):
            return True
        
        return False
    
    async def _move_to_short_term(self, memory: MemoryItem) -> None:
        """将记忆从工作记忆移动到短期记忆"""
        # 设置短期记忆过期时间
        if memory.expiration_time is None:
            memory.expiration_time = time.time() + self.default_short_term_ttl
        
        self.short_term_memory[memory.memory_id] = memory
        
        # 短期记忆超过容量时，清理过期和低重要性的
        if len(self.short_term_memory) > self.max_short_term_size:
            await self._cleanup_short_term_memory()
    
    async def _cleanup_short_term_memory(self) -> None:
        """清理短期记忆"""
        # 首先移除过期的
        expired_ids = [
            mid for mid, mem in self.short_term_memory.items()
            if mem.is_expired
        ]
        for mid in expired_ids:
            del self.short_term_memory[mid]
        
        # 如果还是超过容量，移除重要性最低的
        if len(self.short_term_memory) > self.max_short_term_size:
            sorted_memories = sorted(
                self.short_term_memory.values(),
                key=lambda m: m.calculate_importance_score()
            )
            remove_count = len(self.short_term_memory) - int(self.max_short_term_size * 0.8)  # 清理到80%容量
            for mem in sorted_memories[:remove_count]:
                del self.short_term_memory[mem.memory_id]
                # 发送到反思层进行处理（如果重要性足够）
                if mem.calculate_importance_score() > 0.3:
                    await self.memory_system.reflection_layer.add_for_analysis(mem)
        
        logger.debug(f"短期记忆清理完成，当前大小: {len(self.short_term_memory)}")
    
    async def _processing_worker(self) -> None:
        """实时处理工作线程"""
        while True:
            try:
                action, data = await self.processing_queue.get()
                try:
                    if action == 'add':
                        await self._process_new_memory(data)
                    elif action == 'update':
                        await self._process_memory_update(data)
                finally:
                    self.processing_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"实时记忆处理失败: {str(e)}")
                await asyncio.sleep(0.1)
    
    async def _process_new_memory(self, memory: MemoryItem) -> None:
        """处理新记忆"""
        # 自动分类记忆类型
        if memory.memory_type == MemoryType.EPISODIC:
            await self._classify_memory_type(memory)
        
        # 自动打标签
        await self._auto_tag_memory(memory)
        
        # 生成语义向量（如果有嵌入模型）
        await self._generate_embedding(memory)
        
        # 关联现有记忆
        await self._associate_existing_memories(memory)
    
    async def _process_memory_update(self, memory: MemoryItem) -> None:
        """处理记忆更新"""
        # 更新标签和关联
        await self._auto_tag_memory(memory)
        await self._associate_existing_memories(memory)
    
    async def _classify_memory_type(self, memory: MemoryItem) -> None:
        """自动分类记忆类型"""
        # 这里可以接入大模型进行分类，简化实现
        content_str = str(memory.content).lower()
        
        if any(keyword in content_str for keyword in ['步骤', '流程', '方法', '如何', '教程']):
            memory.memory_type = MemoryType.PROCEDURAL
        elif any(keyword in content_str for keyword in ['知识', '事实', '定义', '概念']):
            memory.memory_type = MemoryType.SEMANTIC
        elif any(keyword in content_str for keyword in ['感觉', '情绪', '开心', '难过', '生气']):
            memory.memory_type = MemoryType.EMOTIONAL
    
    async def _auto_tag_memory(self, memory: MemoryItem) -> None:
        """自动为记忆打标签"""
        # 简化实现：从内容中提取关键词
        content_str = str(memory.content).lower()
        keywords = ['任务', '执行', '错误', '成功', '模型', '代码', '文档', '会议', '计划', '学习']
        
        new_tags = []
        for keyword in keywords:
            if keyword in content_str and keyword not in memory.tags:
                new_tags.append(keyword)
        
        memory.tags.extend(new_tags)
    
    async def _generate_embedding(self, memory: MemoryItem) -> None:
        """生成记忆的语义向量"""
        # 这里可以接入实际的嵌入模型
        # 简化实现：生成随机向量
        if memory.embedding is None:
            memory.embedding = list(np.random.randn(1536))  # 1536维向量，和OpenAI embedding一致
    
    async def _associate_existing_memories(self, memory: MemoryItem) -> None:
        """关联现有的相似记忆"""
        # 查找相似记忆并创建关联
        similar_memories = await self.search_memory(
            str(memory.content),
            limit=5
        )
        
        for similar in similar_memories:
            if similar.memory_id != memory.memory_id:
                # 创建关联关系
                association = MemoryAssociation(
                    from_memory_id=memory.memory_id,
                    to_memory_id=similar.memory_id,
                    relation_type="related",
                    strength=0.7  # 简化实现，固定强度
                )
                await self.memory_system.reflection_layer.add_association(association)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'working_memory_size': len(self.working_memory),
            'short_term_memory_size': len(self.short_term_memory),
            'processing_queue_size': self.processing_queue.qsize()
        }


class ReflectionAnalysisLayer:
    """
    第二层：反思分析层
    Reflection Analysis Layer
    
    对记忆进行深度分析，挖掘关联，提取知识，形成洞见
    """
    
    def __init__(self, memory_system: 'MemoryEvolutionSystem'):
        self.memory_system = memory_system
        self.analysis_queue: asyncio.Queue = asyncio.Queue()
        self.associations: Dict[str, List[MemoryAssociation]] = defaultdict(list)  # 记忆关联关系
        self.knowledge_graph: Dict[str, Any] = {}  # 知识图谱
        self.insights: List[Dict[str, Any]] = []  # 分析得到的洞见
        self._worker_task: Optional[asyncio.Task] = None
        
        logger.info("反思分析层已初始化")
    
    async def start(self) -> None:
        """启动分析工作线程"""
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._analysis_worker())
            logger.info("反思分析层工作线程已启动")
    
    async def stop(self) -> None:
        """停止分析工作线程"""
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("反思分析层工作线程已停止")
    
    async def add_for_analysis(self, memory: MemoryItem) -> None:
        """添加记忆到分析队列"""
        await self.analysis_queue.put(('analyze', memory))
        logger.debug(f"已添加记忆 {memory.memory_id} 到分析队列")
    
    async def add_association(self, association: MemoryAssociation) -> None:
        """添加记忆关联"""
        self.associations[association.from_memory_id].append(association)
        self.associations[association.to_memory_id].append(association)
        logger.debug(f"已创建关联: {association.from_memory_id} <-> {association.to_memory_id}")
    
    async def get_related_memories(self, memory_id: str, min_strength: float = 0.5) -> List[Tuple[MemoryItem, float]]:
        """获取相关记忆"""
        related = []
        
        if memory_id not in self.associations:
            return related
        
        for assoc in self.associations[memory_id]:
            if assoc.strength >= min_strength:
                other_id = assoc.to_memory_id if assoc.from_memory_id == memory_id else assoc.from_memory_id
                memory = await self.memory_system.get_memory(other_id)
                if memory:
                    related.append((memory, assoc.strength))
        
        # 按关联强度排序
        related.sort(key=lambda x: x[1], reverse=True)
        return related
    
    async def analyze_patterns(self, memories: List[MemoryItem]) -> List[Dict[str, Any]]:
        """分析记忆中的模式"""
        patterns = []
        
        if not memories:
            return patterns
        
        # 分析时间模式
        time_pattern = await self._analyze_time_patterns(memories)
        if time_pattern:
            patterns.append(time_pattern)
        
        # 分析内容模式
        content_pattern = await self._analyze_content_patterns(memories)
        if content_pattern:
            patterns.append(content_pattern)
        
        # 分析成功/失败模式
        outcome_pattern = await self._analyze_outcome_patterns(memories)
        if outcome_pattern:
            patterns.append(outcome_pattern)
        
        return patterns
    
    async def _analyze_time_patterns(self, memories: List[MemoryItem]) -> Optional[Dict[str, Any]]:
        """分析时间模式"""
        if len(memories) < 3:
            return None
        
        # 按小时统计
        hour_counts = defaultdict(int)
        for mem in memories:
            hour = datetime.fromtimestamp(mem.created_at).hour
            hour_counts[hour] += 1
        
        peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
        return {
            'type': 'time_pattern',
            'peak_hour': peak_hour,
            'description': f"最活跃时段为{peak_hour}点",
            'confidence': min(1.0, hour_counts[peak_hour] / len(memories))
        }
    
    async def _analyze_content_patterns(self, memories: List[MemoryItem]) -> Optional[Dict[str, Any]]:
        """分析内容模式"""
        tag_counts = defaultdict(int)
        for mem in memories:
            for tag in mem.tags:
                tag_counts[tag] += 1
        
        if not tag_counts:
            return None
        
        top_tag = max(tag_counts.items(), key=lambda x: x[1])[0]
        return {
            'type': 'content_pattern',
            'most_frequent_tag': top_tag,
            'frequency': tag_counts[top_tag] / len(memories),
            'description': f"最常出现的内容类型是{top_tag}"
        }
    
    async def _analyze_outcome_patterns(self, memories: List[MemoryItem]) -> Optional[Dict[str, Any]]:
        """分析结果模式"""
        success_count = 0
        failure_count = 0
        
        for mem in memories:
            content = str(mem.content).lower()
            if '成功' in content or 'success' in content or '完成' in content:
                success_count += 1
            elif '失败' in content or 'error' in content or '失败' in content:
                failure_count += 1
        
        if success_count + failure_count < 5:
            return None
        
        success_rate = success_count / (success_count + failure_count)
        return {
            'type': 'outcome_pattern',
            'success_rate': success_rate,
            'success_count': success_count,
            'failure_count': failure_count,
            'description': f"任务成功率为{success_rate:.1%}"
        }
    
    async def extract_knowledge(self, memories: List[MemoryItem]) -> List[Dict[str, Any]]:
        """从记忆中提取结构化知识"""
        knowledge_items = []
        
        for mem in memories:
            if mem.memory_type == MemoryType.SEMANTIC:
                # 提取事实知识
                knowledge = {
                    'knowledge_id': str(uuid.uuid4()),
                    'content': mem.content,
                    'source_memory_id': mem.memory_id,
                    'confidence': mem.calculate_importance_score(),
                    'extracted_at': time.time()
                }
                knowledge_items.append(knowledge)
                self.knowledge_graph[knowledge['knowledge_id']] = knowledge
        
        return knowledge_items
    
    async def generate_insights(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """根据分析模式生成洞见和建议"""
        insights = []
        
        for pattern in patterns:
            if pattern['type'] == 'outcome_pattern':
                success_rate = pattern['success_rate']
                if success_rate < 0.5:
                    insight = {
                        'insight_id': str(uuid.uuid4()),
                        'type': 'improvement_suggestion',
                        'content': f"近期任务成功率较低（{success_rate:.1%}），建议检查执行流程是否存在问题",
                        'priority': 'high',
                        'related_pattern': pattern,
                        'generated_at': time.time()
                    }
                    insights.append(insight)
                elif success_rate > 0.9:
                    insight = {
                        'insight_id': str(uuid.uuid4()),
                        'type': 'best_practice',
                        'content': f"近期任务表现优秀（成功率{success_rate:.1%}），可以总结相关经验形成最佳实践",
                        'priority': 'medium',
                        'related_pattern': pattern,
                        'generated_at': time.time()
                    }
                    insights.append(insight)
            
            elif pattern['type'] == 'time_pattern':
                peak_hour = pattern['peak_hour']
                insight = {
                    'insight_id': str(uuid.uuid4()),
                    'type': 'productivity_suggestion',
                    'content': f"观察到{peak_hour}点是最高效的时段，建议安排重要任务在此时段执行",
                    'priority': 'low',
                    'related_pattern': pattern,
                    'generated_at': time.time()
                }
                insights.append(insight)
        
        self.insights.extend(insights)
        return insights
    
    async def _analysis_worker(self) -> None:
        """分析工作线程"""
        while True:
            try:
                action, data = await self.analysis_queue.get()
                try:
                    if action == 'analyze':
                        await self._analyze_memory(data)
                    elif action == 'batch_analyze':
                        await self._batch_analyze(data)
                finally:
                    self.analysis_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"记忆分析失败: {str(e)}")
                await asyncio.sleep(0.1)
    
    async def _analyze_memory(self, memory: MemoryItem) -> None:
        """分析单个记忆"""
        logger.debug(f"开始分析记忆 {memory.memory_id}")
        
        # 1. 查找相关记忆
        related = await self.get_related_memories(memory.memory_id)
        logger.debug(f"找到 {len(related)} 条相关记忆")
        
        # 2. 分析模式
        all_memories = [memory] + [m for m, _ in related]
        patterns = await self.analyze_patterns(all_memories)
        logger.debug(f"发现 {len(patterns)} 个模式")
        
        # 3. 提取知识
        knowledge = await self.extract_knowledge(all_memories)
        logger.debug(f"提取到 {len(knowledge)} 条知识")
        
        # 4. 生成洞见
        insights = await self.generate_insights(patterns)
        logger.debug(f"生成 {len(insights)} 条洞见")
        
        # 5. 发送到结构优化层
        if patterns or knowledge or insights:
            await self.memory_system.structural_optimization_layer.add_for_optimization({
                'memory': memory,
                'related_memories': related,
                'patterns': patterns,
                'knowledge': knowledge,
                'insights': insights
            })
        
        logger.debug(f"记忆 {memory.memory_id} 分析完成")
    
    async def _batch_analyze(self, memories: List[MemoryItem]) -> None:
        """批量分析记忆"""
        logger.info(f"开始批量分析 {len(memories)} 条记忆")
        
        patterns = await self.analyze_patterns(memories)
        knowledge = await self.extract_knowledge(memories)
        insights = await self.generate_insights(patterns)
        
        logger.info(f"批量分析完成: {len(patterns)} 个模式, {len(knowledge)} 条知识, {len(insights)} 条洞见")
        
        # 发送到结构优化层
        await self.memory_system.structural_optimization_layer.add_for_optimization({
            'batch_analysis': True,
            'memories_count': len(memories),
            'patterns': patterns,
            'knowledge': knowledge,
            'insights': insights
        })
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'associations_count': sum(len(assoc) for assoc in self.associations.values()) // 2,
            'knowledge_count': len(self.knowledge_graph),
            'insights_count': len(self.insights),
            'analysis_queue_size': self.analysis_queue.qsize()
        }


class StructuralOptimizationLayer:
    """
    第三层：结构优化层
    Structural Optimization Layer
    
    负责长期记忆的结构优化、索引构建、冗余清理和持久化
    """
    
    def __init__(self, memory_system: 'MemoryEvolutionSystem'):
        self.memory_system = memory_system
        self.optimization_queue: asyncio.Queue = asyncio.Queue()
        self.long_term_memory: Dict[str, MemoryItem] = {}  # 长期记忆
        self.memory_indexes: Dict[str, Dict[str, Set[str]]] = defaultdict(dict)  # 各种索引
        self.persist_path: Path = Path("memory/long_term")
        self._worker_task: Optional[asyncio.Task] = None
        self._optimization_schedule_task: Optional[asyncio.Task] = None
        
        # 创建持久化目录
        self.persist_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("结构优化层已初始化")
    
    async def start(self) -> None:
        """启动优化工作线程和定时优化任务"""
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._optimization_worker())
            logger.info("结构优化层工作线程已启动")
        
        if self._optimization_schedule_task is None or self._optimization_schedule_task.done():
            self._optimization_schedule_task = asyncio.create_task(self._scheduled_optimization())
            logger.info("定时优化任务已启动")
    
    async def stop(self) -> None:
        """停止所有工作线程"""
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        
        if self._optimization_schedule_task and not self._optimization_schedule_task.done():
            self._optimization_schedule_task.cancel()
            try:
                await self._optimization_schedule_task
            except asyncio.CancelledError:
                pass
        
        # 停止前持久化所有记忆
        await self._persist_all_memories()
        logger.info("结构优化层已停止")
    
    async def add_for_optimization(self, data: Dict[str, Any]) -> None:
        """添加数据到优化队列"""
        await self.optimization_queue.put(data)
        logger.debug("已添加数据到优化队列")
    
    async def add_to_long_term(self, memory: MemoryItem) -> None:
        """将记忆添加到长期记忆"""
        memory.is_archived = False
        memory.expiration_time = None  # 长期记忆永不过期
        self.long_term_memory[memory.memory_id] = memory
        
        # 更新索引
        await self._update_indexes(memory)
        
        logger.debug(f"已添加记忆 {memory.memory_id} 到长期记忆")
    
    async def search_long_term(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[MemoryItem]:
        """搜索长期记忆"""
        candidate_ids = set(self.long_term_memory.keys())
        
        # 按类型过滤
        if memory_type:
            type_key = memory_type.value
            if type_key in self.memory_indexes.get('type', {}):
                candidate_ids &= self.memory_indexes['type'][type_key]
        
        # 按标签过滤
        if tags:
            for tag in tags:
                if tag in self.memory_indexes.get('tag', {}):
                    candidate_ids &= self.memory_indexes['tag'][tag]
        
        # 获取候选记忆
        candidates = [self.long_term_memory[mid] for mid in candidate_ids if mid in self.long_term_memory]
        
        # 简单的相关性排序
        results = []
        query_lower = query.lower()
        for mem in candidates:
            if query_lower in str(mem.content).lower():
                mem.access()
                results.append(mem)
        
        # 按重要性和访问时间排序
        results.sort(key=lambda m: (m.calculate_importance_score(), m.accessed_at), reverse=True)
        return results[:limit]
    
    async def _update_indexes(self, memory: MemoryItem) -> None:
        """更新记忆索引"""
        # 类型索引
        type_key = memory.memory_type.value
        if 'type' not in self.memory_indexes:
            self.memory_indexes['type'] = defaultdict(set)
        self.memory_indexes['type'][type_key].add(memory.memory_id)
        
        # 标签索引
        if 'tag' not in self.memory_indexes:
            self.memory_indexes['tag'] = defaultdict(set)
        for tag in memory.tags:
            self.memory_indexes['tag'][tag].add(memory.memory_id)
        
        # 来源索引
        if 'source' not in self.memory_indexes:
            self.memory_indexes['source'] = defaultdict(set)
        self.memory_indexes['source'][memory.source].add(memory.memory_id)
    
    async def _remove_from_indexes(self, memory_id: str) -> None:
        """从所有索引中移除记忆"""
        for index_type in self.memory_indexes:
            for key in self.memory_indexes[index_type]:
                if memory_id in self.memory_indexes[index_type][key]:
                    self.memory_indexes[index_type][key].remove(memory_id)
    
    async def _optimize_memory_structure(self) -> None:
        """优化整体记忆结构"""
        logger.info("开始记忆结构优化...")
        
        # 1.