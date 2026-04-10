#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境3.0记忆系统 (Memory System V2)
===============================
作者: 少府监·翰林学士 孟浩然
版本: 3.0
描述: 三层记忆架构 - 工作记忆 + 长期记忆 + 索引记忆

记忆分层设计理念:
- 工作记忆(Working Memory): 短期高频访问，当前会话上下文
- 长期记忆(Long-term Memory): 持久化存储，语义关联
- 索引记忆(Index Memory): 元数据索引，快速检索
"""

import json
import time
import hashlib
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import OrderedDict
from datetime import datetime
from enum import Enum
import threading


class MemoryType(Enum):
    """记忆类型枚举"""
    EPISODIC = "episodic"      # 情景记忆 - 具体事件
    SEMANTIC = "semantic"      # 语义记忆 - 知识概念
    PROCEDURAL = "procedural"  # 程序记忆 - 技能流程
    EMOTIONAL = "emotional"    # 情感记忆 - 情感关联


class MemoryPriority(Enum):
    """记忆优先级"""
    CRITICAL = 3   # 关键记忆 - 永久保存
    HIGH = 2       # 高优先级
    NORMAL = 1     # 普通记忆
    LOW = 0        # 低优先级 - 可被清理


@dataclass
class MemoryBlock:
    """记忆块 - 记忆的基本单元"""
    id: str
    content: str
    memory_type: MemoryType
    priority: MemoryPriority
    timestamp: float
    tags: List[str] = field(default_factory=list)
    embeddings: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    importance_score: float = 0.5
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "tags": self.tags,
            "embeddings": self.embeddings,
            "metadata": self.metadata,
            "access_count": self.access_count,
            "last_access": self.last_access,
            "importance_score": self.importance_score
        }


class WorkingMemory:
    """
    工作记忆层
    特性: 高频访问、容量有限、时间衰减、快速检索
    实现: LRU缓存 + 访问频率权重
    """
    
    def __init__(self, capacity: int = 100, decay_factor: float = 0.95):
        """
        初始化工作记忆
        
        Args:
            capacity: 最大容量
            decay_factor: 时间衰减因子
        """
        self.capacity = capacity
        self.decay_factor = decay_factor
        self._storage: OrderedDict[str, MemoryBlock] = OrderedDict()
        self._lock = threading.RLock()
        
    def add(self, memory: MemoryBlock) -> bool:
        """添加记忆到工作记忆"""
        with self._lock:
            memory_id = memory.id
            if memory_id in self._storage:
                self._storage.move_to_end(memory_id)
                self._storage[memory_id] = memory
                return True
            while len(self._storage) >= self.capacity:
                self._evict_lru()
            self._storage[memory_id] = memory
            return True
    
    def get(self, memory_id: str) -> Optional[MemoryBlock]:
        """获取记忆"""
        with self._lock:
            if memory_id not in self._storage:
                return None
            self._storage.move_to_end(memory_id)
            memory = self._storage[memory_id]
            memory.access_count += 1
            memory.last_access = time.time()
            return memory
    
    def search_by_content(self, query: str, top_k: int = 10) -> List[MemoryBlock]:
        """基于内容的搜索"""
        with self._lock:
            results = []
            query_lower = query.lower()
            for memory in self._storage.values():
                if query_lower in memory.content.lower():
                    score = self._calculate_relevance(memory, query)
                    results.append((score, memory))
            results.sort(key=lambda x: x[0], reverse=True)
            return [m for _, m in results[:top_k]]
    
    def search_by_tags(self, tags: List[str], top_k: int = 10) -> List[MemoryBlock]:
        """基于标签的搜索"""
        with self._lock:
            results = []
            tag_set = set(tags)
            for memory in self._storage.values():
                if tag_set.intersection(set(memory.tags)):
                    score = len(tag_set.intersection(set(memory.tags)))
                    results.append((score, memory))
            results.sort(key=lambda x: x[0], reverse=True)
            return [m for _, m in results[:top_k]]
    
    def _calculate_relevance(self, memory: MemoryBlock, query: str) -> float:
        """计算记忆与查询的相关性分数"""
        score = 0.0
        if query.lower() in memory.content.lower():
            score += 0.3
        for tag in memory.tags:
            if tag.lower() in query.lower():
                score += 0.2
        score += min(memory.access_count * 0.05, 0.2)
        score += memory.importance_score * 0.2
        score += memory.priority.value * 0.1
        return score
    
    def _evict_lru(self):
        """淘汰最少使用的记忆"""
        if not self._storage:
            return
        to_evict = None
        min_score = float('inf')
        for memory_id, memory in self._storage.items():
            recency = 1.0 / (time.time() - memory.last_access + 1)
            lru_score = recency * (memory.priority.value + 1)
            if lru_score < min_score:
                min_score = lru_score
                to_evict = memory_id
        if to_evict:
            del self._storage[to_evict]
    
    def get_all(self) -> List[MemoryBlock]:
        """获取所有工作记忆"""
        with self._lock:
            return list(self._storage.values())
    
    def size(self) -> int:
        """获取当前容量"""
        return len(self._storage)
    
    def clear(self):
        """清空工作记忆"""
        with self._lock:
            self._storage.clear()


class LongTermMemory:
    """
    长期记忆层
    特性: 持久化存储、语义关联、自动摘要、遗忘机制
    实现: 文件系统存储 + 语义索引
    """
    
    def __init__(self, storage_path: str = "./memory_storage"):
        """初始化长期记忆"""
        self.storage_path = storage_path
        self._ensure_storage_dir()
        self._memory_index: Dict[str, MemoryBlock] = {}
        self._semantic_graph: Dict[str, List[str]] = {}
        self._lock = threading.RLock()
        self._load_index()
    
    def _ensure_storage_dir(self):
        """确保存储目录存在"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def _load_index(self):
        """加载索引"""
        index_file = os.path.join(self.storage_path, "index.json")
        if os.path.exists(index_file):
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for mem_id, mem_data in data.items():
                        mem_data['memory_type'] = MemoryType(mem_data['memory_type'])
                        mem_data['priority'] = MemoryPriority(mem_data['priority'])
                        self._memory_index[mem_id] = MemoryBlock(**mem_data)
            except Exception as e:
                print(f"加载索引失败: {e}")
    
    def _save_index(self):
        """保存索引"""
        index_file = os.path.join(self.storage_path, "index.json")
        try:
            data = {k: v.to_dict() for k, v in self._memory_index.items()}
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存索引失败: {e}")
    
    def add(self, memory: MemoryBlock) -> bool:
        """添加记忆到长期记忆"""
        with self._lock:
            memory_file = os.path.join(self.storage_path, f"{memory.id}.json")
            try:
                with open(memory_file, 'w', encoding='utf-8') as f:
                    json.dump(memory.to_dict(), f, ensure_ascii=False, indent=2)
                self._memory_index[memory.id] = memory
                self._update_semantic_graph(memory)
                self._save_index()
                return True
            except Exception as e:
                print(f"保存记忆失败: {e}")
                return False
    
    def get(self, memory_id: str) -> Optional[MemoryBlock]:
        """获取记忆"""
        with self._lock:
            if memory_id in self._memory_index:
                return self._memory_index[memory_id]
            memory_file = os.path.join(self.storage_path, f"{memory_id}.json")
            if os.path.exists(memory_file):
                try:
                    with open(memory_file, 'r', encoding='utf-8') as f:
                        mem_data = json.load(f)
                        mem_data['memory_type'] = MemoryType(mem_data['memory_type'])
                        mem_data['priority'] = MemoryPriority(mem_data['priority'])
                        memory = MemoryBlock(**mem_data)
                        self._memory_index[memory_id] = memory
                        return memory
                except Exception as e:
                    print(f"加载记忆失败: {e}")
            return None
    
    def delete(self, memory_id: str) -> bool:
        """删除记忆"""
        with self._lock:
            memory_file = os.path.join(self.storage_path, f"{memory_id}.json")
            try:
                if os.path.exists(memory_file):
                    os.remove(memory_file)
                if memory_id in self._memory_index:
                    del self._memory_index[memory_id]
                if memory_id in self._semantic_graph:
                    for related in self._semantic_graph[memory_id]:
                        if related in self._semantic_graph:
                            if memory_id in self._semantic_graph[related]:
                                self._semantic_graph[related].remove(memory_id)
                    del self._semantic_graph[memory_id]
                self._save_index()
                return True
            except Exception as e:
                print(f"删除记忆失败: {e}")
                return False
    
    def _update_semantic_graph(self, memory: MemoryBlock):
        """更新语义关联图"""
        for tag in memory.tags:
            tag_key = f"tag:{tag}"
            if tag_key not in self._semantic_graph:
                self._semantic_graph[tag_key] = []
            for mem_id, mem in self._memory_index.items():
                if mem_id != memory.id and tag in mem.tags:
                    if memory.id not in self._semantic_graph.get(tag_key, []):
                        if tag_key not in self._semantic_graph:
                            self._semantic_graph[tag_key] = []
                        self._semantic_graph[tag_key].append(mem_id)
        keywords = self._extract_keywords(memory.content)
        for keyword in keywords:
            kw_key = f"kw:{keyword}"
            if kw_key not in self._semantic_graph:
                self._semantic_graph[kw_key] = []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        stopwords = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '看', '好', '这'}
        words = text.replace('\n', ' ').split()
        return [w for w in words if w not in stopwords and len(w) > 1]
    
    def search_by_semantics(self, query: str, top_k: int = 10) -> List[Tuple[float, MemoryBlock]]:
        """语义搜索"""
        with self._lock:
            results = []
            query_keywords = self._extract_keywords(query)
            for memory in self._memory_index.values():
                score = 0.0
                for tag in memory.tags:
                    if tag in query_keywords:
                        score += 0.5
                content_lower = memory.content.lower()
                for kw in query_keywords:
                    if kw in content_lower:
                        score += 0.3
                for kw in query_keywords:
                    kw_key = f"kw:{kw}"
                    if kw_key in self._semantic_graph:
                        if memory.id in self._semantic_graph[kw_key]:
                            score += 0.4
                if score > 0:
                    results.append((score, memory))
            results.sort(key=lambda x: x[0], reverse=True)
            return results[:top_k]
    
    def get_related(self, memory_id: str, max_related: int = 5) -> List[MemoryBlock]:
        """获取相关记忆"""
        with self._lock:
            if memory_id not in self._semantic_graph:
                return []
            related_ids = self._semantic_graph[memory_id][:max_related]
            related_memories = []
            for rid in related_ids:
                mem = self.get(rid)
                if mem:
                    related_memories.append(mem)
            return related_memories
    
    def get_by_timerange(self, start_time: float, end_time: float) -> List[MemoryBlock]:
        """按时间范围获取记忆"""
        with self._lock:
            return [m for m in self._memory_index.values() 
                    if start_time <= m.timestamp <= end_time]
    
    def get_by_type(self, memory_type: MemoryType) -> List[MemoryBlock]:
        """按类型获取记忆"""
        with self._lock:
            return [m for m in self._memory_index.values() 
                    if m.memory_type == memory_type]
    
    def size(self) -> int:
        """获取记忆数量"""
        return len(self._memory_index)
    
    def get_all(self) -> List[MemoryBlock]:
        """获取所有记忆"""
        with self._lock:
            return list(self._memory_index.values())


class IndexMemory:
    """
    索引记忆层
    特性: 快速检索、多维索引、元数据管理
    实现: 倒排索引
    """
    
    def __init__(self):
        """初始化索引记忆"""
        self._tag_index: Dict[str, List[str]] = {}
        self._type_index: Dict[MemoryType, List[str]] = {}
        self._time_index: Dict[str, List[str]] = {}
        self._keyword_index: Dict[str, List[str]] = {}
        self._priority_index: Dict[MemoryPriority, List[str]] = {}
        self._lock = threading.RLock()
    
    def add_index(self, memory: MemoryBlock):
        """为记忆建立索引"""
        with self._lock:
            mem_id = memory.id
            for tag in memory.tags:
                if tag not in self._tag_index:
                    self._tag_index[tag] = []
                if mem_id not in self._tag_index[tag]:
                    self._tag_index[tag].append(mem_id)
            if memory.memory_type not in self._type_index:
                self._type_index[memory.memory_type] = []
            if mem_id not in self._type_index[memory.memory_type]:
                self._type_index[memory.memory_type].append(mem_id)
            day_key = datetime.fromtimestamp(memory.timestamp).strftime("%Y-%m-%d")
            if day_key not in self._time_index:
                self._time_index[day_key] = []
            if mem_id not in self._time_index[day_key]:
                self._time_index[day_key].append(mem_id)
            keywords = self._extract_keywords(memory.content)
            for kw in keywords:
                if kw not in self._keyword_index:
                    self._keyword_index[kw] = []
                if mem_id not in self._keyword_index[kw]:
                    self._keyword_index[kw].append(mem_id)
            if memory.priority not in self._priority_index:
                self._priority_index[memory.priority] = []
            if mem_id not in self._priority_index[memory.priority]:
                self._priority_index[memory.priority].append(mem_id)
    
    def remove_index(self, memory: MemoryBlock):
        """移除记忆的索引"""
        with self._lock:
            mem_id = memory.id
            for tag in memory.tags:
                if tag in self._tag_index and mem_id in self._tag_index[tag]:
                    self._tag_index[tag].remove(mem_id)
            if memory.memory_type in self._type_index:
                if mem_id in self._type_index[memory.memory_type]:
                    self._type_index[memory.memory_type].remove(mem_id)
            day_key = datetime.fromtimestamp(memory.timestamp).strftime("%Y-%m-%d")
            if day_key in self._time_index and mem_id in self._time_index[day_key]:
                self._time_index[day_key].remove(mem_id)
            keywords = self._extract_keywords(memory.content)
            for kw in keywords:
                if kw in self._keyword_index and mem_id in self._keyword_index[kw]:
                    self._keyword_index[kw].remove(mem_id)
            if memory.priority in self._priority_index:
                if mem_id in self._priority_index[memory.priority]:
                    self._priority_index[memory.priority].remove(mem_id)
    
    def search_by_tag(self, tag: str) -> List[str]:
        """按标签搜索"""
        with self._lock:
            return self._tag_index.get(tag, [])
    
    def search_by_type(self, memory_type: MemoryType) -> List[str]:
        """按类型搜索"""
        with self._lock:
            return self._type_index.get(memory_type, [])
    
    def search_by_date(self, date: str) -> List[str]:
        """按日期搜索"""
        with self._lock:
            return self._time_index.get(date, [])
    
    def search_by_keyword(self, keyword: str) -> List[str]:
        """按关键词搜索"""
        with self._lock:
            return self._keyword_index.get(keyword, [])
    
    def search_by_priority(self, priority: MemoryPriority) -> List[str]:
        """按优先级搜索"""
        with self._lock:
            return self._priority_index.get(priority, [])
    
    def compound_search(self, 
                        tags: Optional[List[str]] = None,
                        memory_type: Optional[MemoryType] = None,
                        date: Optional[str] = None,
                        keyword: Optional[str] = None,
                        priority: Optional[MemoryPriority] = None) -> List[str]:
        """复合搜索 (交集)"""
        with self._lock:
            result_sets = []
            if tags:
                tag_results = set()
                for tag in tags:
                    tag_results.update(self._tag_index.get(tag, []))
                if tag_results:
                    result_sets.append(tag_results)
            if memory_type:
                type_results = set(self._type_index.get(memory_type, []))
                if type_results:
                    result_sets.append(type_results)
            if date:
                date_results = set(self._time_index.get(date, []))
                if date_results:
                    result_sets.append(date_results)
            if keyword:
                kw_results = set(self._keyword_index.get(keyword, []))
                if kw_results:
                    result_sets.append(kw_results)
            if priority:
                prio_results = set(self._priority_index.get(priority, []))
                if prio_results:
                    result_sets.append(prio_results)
            if not result_sets:
                return []
            result = result_sets[0]
            for s in result_sets[1:]:
                result = result.intersection(s)
            return list(result)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        stopwords = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '看', '好', '这'}
        words = text.replace('\n', ' ').split()
        return [w for w in words if w not in stopwords and len(w) > 1]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        with self._lock:
            return {
                "tag_count": len(self._tag_index),
                "type_count": len(self._type_index),
                "date_count": len(self._time_index),
                "keyword_count": len(self._keyword_index),
                "priority_count": len(self._priority_index),
                "tags": list(self._tag_index.keys())[:20],
                "dates": sorted(list(self._time_index.keys()))[-10:]
            }


class MemorySystemV2:
    """
    序境3.0记忆系统 - 核心类
    =========================
    
    三层记忆架构:
    1. WorkingMemory (工作记忆): 当前会话的高速缓存
    2. LongTermMemory (长期记忆): 持久化的语义存储
    3. IndexMemory (索引记忆): 快速多维检索
    
    特性:
    - 自动分层存储
    - 语义关联发现
    - 遗忘与强化机制
    - 跨层检索
    """
    
    def __init__(self, 
                 working_capacity: int = 100,
                 storage_path: str = "./memory_storage"):
        """
        初始化记忆系统
        
        Args:
            working_capacity: 工作记忆容量
            storage_path: 长期记忆存储路径
        """
        self.working_memory = WorkingMemory(capacity=working_capacity)
        self.longterm_memory = LongTermMemory(storage_path=storage_path)
        self.index_memory = IndexMemory()
        self._rebuild_index()
        self._sync_to_working()
    
    def _rebuild_index(self):
        """重建索引"""
        for memory in self.longterm_memory.get_all():
            self.index_memory.add_index(memory)
    
    def _sync_to_working(self):
        """同步最近记忆到工作记忆"""
        all_memories = self.longterm_memory.get_all()
        sorted_memories = sorted(all_memories, key=lambda m: m.last_access, reverse=True)
        for memory in sorted_memories[:self.working_memory.capacity]:
            self.working_memory.add(memory)
    
    def store(self, 
              content: str,
              memory_type: MemoryType = MemoryType.EPISODIC,
              priority: MemoryPriority = MemoryPriority.NORMAL,
              tags: Optional[List[str]] = None,
              metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        存储记忆
        
        Args:
            content: 记忆内容
            memory_type: 记忆类型
            priority: 优先级
            tags: 标签列表
            metadata: 元数据
            
        Returns:
            记忆ID
        """
        timestamp = time.time()
        id_str = f"{content[:50]}{timestamp}"
        memory_id = hashlib.md5(id_str.encode()).hexdigest()
        
        memory = MemoryBlock(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            priority=priority,
            timestamp=timestamp,
            tags=tags or [],
            metadata=metadata or {},
            importance_score=self._calculate_importance(priority, memory_type)
        )
        
        self.working_memory.add(memory)
        self.longterm_memory.add(memory)
        self.index_memory.add_index(memory)
        
        return memory_id
    
    def _calculate_importance(self, priority: MemoryPriority, 
                             memory_type: MemoryType) -> float:
        """计算重要性分数"""
        base_score = priority.value / 3.0
        type_weights = {
            MemoryType.EMOTIONAL: 0.2,
            MemoryType.PROCEDURAL: 0.15,
            MemoryType.SEMANTIC: 0.1,
            MemoryType.EPISODIC: 0.05
        }
        return min(base_score + type_weights.get(memory_type, 0), 1.0)
    
    def retrieve(self, memory_id: str) -> Optional[MemoryBlock]:
        """检索记忆"""
        memory = self.working_memory.get(memory_id)
        if memory:
            return memory
        memory = self.longterm_memory.get(memory_id)
        if memory:
            self.working_memory.add(memory)
            return memory
        return None
    
    def search(self, 
               query: str,
               search_type: str = "hybrid",
               top_k: int = 10) -> List[Tuple[float, MemoryBlock]]:
        """
        搜索记忆
        
        Args:
            query: 查询内容
            search_type: 搜索类型 (working/longterm/index/hybrid)
            top_k: 返回数量
            
        Returns:
            (相关性分数, 记忆块)列表
        """
        if search_type == "working":
            results = self.working_memory.search_by_content(query, top_k)
            return [(self._calculate_relevance(m, query), m) for m in results]
        
        elif search_type == "longterm":
            return self.longterm_memory.search_by_semantics(query, top_k)
        
        elif search_type == "index":
            memory_ids = self.index_memory.search_by_keyword(query)
            results = []
            for mem_id in memory_ids[:top_k]:
                mem = self.longterm_memory.get(mem_id)
                if mem:
                    results.append((1.0, mem))
            return results
        
        else:  # hybrid
            all_results: Dict[str, float] = {}
            memory_blocks: Dict[str, MemoryBlock] = {}
            
            wm_results = self.working_memory.search_by_content(query, top_k * 2)
            for mem in wm_results:
                all_results[mem.id] = all_results.get(mem.id, 0) + 0.4
                memory_blocks[mem.id] = mem
            
            ltm_results = self.longterm_memory.search_by_semantics(query, top_k * 2)
            for score, mem in ltm_results:
                all_results[mem.id] = all_results.get(mem.id, 0) + score * 0.6
                memory_blocks[mem.id] = mem
            
            idx_results = self.index_memory.search_by_keyword(query)
            for mem_id in idx_results[:top_k * 2]:
                all_results[mem_id] = all_results.get(mem_id, 0) + 0.3
                if mem_id not in memory_blocks:
                    mem = self.longterm_memory.get(mem_id)
                    if mem:
                        memory_blocks[mem_id] = mem
            
            sorted_results = sorted(all_results.items(), key=lambda x: x[1], reverse=True)[:top_k]
            return [(score, memory_blocks[mem_id]) for mem_id, score in sorted_results if mem_id in memory_blocks]
    
    def _calculate_relevance(self, memory: MemoryBlock, query: str) -> float:
        """计算相关性"""
        score = 0.0
        if query.lower() in memory.content.lower():
            score += 0.3
        for tag in memory.tags:
            if tag.lower() in query.lower():
                score += 0.2
        score += min(memory.access_count * 0.05, 0.2)
        score += memory.importance_score * 0.2
        score += memory.priority.value * 0.1
        return score
    
    def get_related(self, memory_id: str, max_related: int = 5) -> List[MemoryBlock]:
        """获取相关记忆"""
        return self.longterm_memory.get_related(memory_id, max_related)
    
    def delete(self, memory_id: str) -> bool:
        """删除记忆"""
        memory = self.longterm_memory.get(memory_id)
        if memory:
            self.index_memory.remove_index(memory)
        with self.working_memory._lock:
            if memory_id in self.working_memory._storage:
                del self.working_memory._storage[memory_id]
        return self.longterm_memory.delete(memory_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取记忆系统统计信息"""
        return {
            "working_memory": {"size": self.working_memory.size(), "capacity": self.working_memory.capacity},
            "longterm_memory": {"size": self.longterm_memory.size()},
            "index_memory": self.index_memory.get_stats(),
            "total_memories": self.longterm_memory.size()
        }
    
    def consolidate(self):
        """记忆整合: 将工作记忆持久化，更新长期记忆索引"""
        self._rebuild_index()
    
    def clear_working(self):
        """清空工作记忆(保留长期记忆)"""
        self.working_memory.clear()
        self._sync_to_working()


def create_memory_system(working_capacity: int = 100, 
                         storage_path: str = "./memory_storage") -> MemorySystemV2:
    """创建记忆系统实例"""
    return MemorySystemV2(working_capacity=working_capacity, storage_path=storage_path)


if __name__ == "__main__":
    ms = create_memory_system()
    print("=== 测试记忆系统 ===")
    
    id1 = ms.store(
        content="今天在序境中与李白讨论了诗歌创作，他建议我多观察自然。",
        memory_type=MemoryType.EPISODIC,
        priority=MemoryPriority.HIGH,
        tags=["李白", "诗歌", "自然", "序境"]
    )
    print(f"添加记忆1: {id1}")
    
    id2 = ms.store(
        content="序境3.0采用三层记忆架构: 工作记忆、长期记忆、索引记忆。",
        memory_type=MemoryType.SEMANTIC,
        priority=MemoryPriority.CRITICAL,
        tags=["序境", "架构", "记忆系统", "技术"]
    )
    print(f"添加记忆2: {id2}")
    
    id3 = ms.store(
        content="每日晨读流程: 诵读唐诗三百首 -> 记录感悟 -> 温故而知新。",
        memory_type=MemoryType.PROCEDURAL,
        priority=MemoryPriority.NORMAL,
        tags=["晨读", "流程", "学习"]
    )
    print(f"添加记忆3: {id3}")
    
    print("\n=== 搜索测试 ===")
    results = ms.search("序境 记忆", top_k=3)
    for score, mem in results:
        print(f"- [{score:.2f}] {mem.content[:50]}...")
    
    print("\n=== 统计信息 ===")
    print(ms.get_stats())
