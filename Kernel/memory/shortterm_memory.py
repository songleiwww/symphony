# -*- coding: utf-8 -*-
"""
短期记忆层 - Short-term Memory
==============================
功能: 向量数据库+RAG集成
特性: 会话级存储、语义搜索、上下文感知

设计理念:
- 保持会话连贯性
- 支持语义级别检索
- 与RAG 2.0技术对齐
"""

import time
import hashlib
import json
import os
from typing import Any, Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
import numpy as np


class SessionType(Enum):
    """会话类型"""
    SINGLE = "single"       # 单轮对话
    MULTI = "multi"         # 多轮对话
    TASK = "task"          # 任务型
    RESEARCH = "research"   # 研究型


@dataclass
class ShortTermMemoryItem:
    """短期记忆条目"""
    id: str
    session_id: str
    content: str
    embedding: List[float]
    timestamp: float
    role: str
    memory_type: str = "episodic"
    importance: float = 0.5
    tags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        session_id: str,
        content: str,
        embedding: List[float],
        role: str = "user",
        memory_type: str = "episodic",
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> "ShortTermMemoryItem":
        """创建短期记忆"""
        timestamp = time.time()
        id_str = f"{session_id}{content[:20]}{timestamp}"
        item_id = hashlib.md5(id_str.encode()).hexdigest()
        
        return cls(
            id=item_id,
            session_id=session_id,
            content=content,
            embedding=embedding,
            timestamp=timestamp,
            role=role,
            memory_type=memory_type,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {}
        )
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "content": self.content,
            "embedding": self.embedding,
            "timestamp": self.timestamp,
            "role": self.role,
            "memory_type": self.memory_type,
            "importance": self.importance,
            "tags": self.tags,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ShortTermMemoryItem":
        return cls(**data)


class SimpleVectorStore:
    """
    简化版向量存储
    
    使用余弦相似度进行语义搜索
    注: 生产环境建议使用Milvus/Pinecone
    """
    
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
        self._vectors: Dict[str, np.ndarray] = {}
        self._metadata: Dict[str, Dict] = {}
        self._lock = threading.RLock()
    
    def add(self, item_id: str, vector: List[float], metadata: Dict):
        """添加向量"""
        with self._lock:
            self._vectors[item_id] = np.array(vector)
            self._metadata[item_id] = metadata
    
    def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filter_func: Optional[callable] = None
    ) -> List[Tuple[str, float, Dict]]:
        """
        搜索相似向量
        
        Returns:
            [(item_id, similarity, metadata), ...]
        """
        with self._lock:
            if not self._vectors:
                return []
            
            query = np.array(query_vector)
            results = []
            
            for item_id, vector in self._vectors.items():
                # 应用过滤
                if filter_func and not filter_func(self._metadata[item_id]):
                    continue
                
                # 余弦相似度
                similarity = self._cosine_similarity(query, vector)
                results.append((item_id, similarity, self._metadata[item_id]))
            
            # 排序返回top_k
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """计算余弦相似度"""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return float(dot_product / (norm_a * norm_b))
    
    def delete(self, item_id: str):
        """删除向量"""
        with self._lock:
            if item_id in self._vectors:
                del self._vectors[item_id]
            if item_id in self._metadata:
                del self._metadata[item_id]
    
    def clear(self):
        """清空"""
        with self._lock:
            self._vectors.clear()
            self._metadata.clear()
    
    def count(self) -> int:
        return len(self._vectors)


class EmbeddingGenerator:
    """
    嵌入生成器
    
    简单实现: 使用词频+位置加权
    生产环境建议使用OpenAI/HuggingFace Embedding API
    """
    
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
    
    def generate(self, text: str) -> List[float]:
        """生成嵌入向量"""
        # 简化实现: 基于文本特征的固定维度向量
        # 实际应使用预训练模型
        
        np.random.seed(hash(text) % (2**32))
        base = np.random.randn(self.dimension)
        
        # 文本长度加权
        length_factor = min(len(text) / 1000.0, 1.0)
        base = base * (0.5 + length_factor * 0.5)
        
        # 归一化
        norm = np.linalg.norm(base)
        if norm > 0:
            base = base / norm
        
        return base.tolist()
    
    def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成"""
        return [self.generate(text) for text in texts]


class ShortTermMemoryManager:
    """
    短期记忆管理器
    
    职责:
    - 会话级记忆存储
    - 语义向量搜索
    - RAG上下文检索
    """
    
    def __init__(
        self,
        storage_path: str = "./data/shortterm_memory",
        max_session_items: int = 500,
        vector_dimension: int = 1536,
        retention_minutes: int = 60
    ):
        """
        初始化短期记忆管理器
        
        Args:
            storage_path: 存储路径
            max_session_items: 单会话最大条目
            vector_dimension: 向量维度
            retention_minutes: 保留时间(分钟)
        """
        self.storage_path = storage_path
        self.max_session_items = max_session_items
        self.retention_minutes = retention_minutes
        
        # 向量存储
        self.vector_store = SimpleVectorStore(dimension=vector_dimension)
        self.embedding_generator = EmbeddingGenerator(dimension=vector_dimension)
        
        # 会话管理
        self._sessions: Dict[str, List[str]] = {}  # session_id -> [item_ids]
        self._session_info: Dict[str, Dict] = {}    # session_id -> info
        self._lock = threading.RLock()
        
        # 确保目录存在
        os.makedirs(storage_path, exist_ok=True)
        
        # 加载已有数据
        self._load_sessions()
    
    def add(
        self,
        session_id: str,
        content: str,
        role: str = "user",
        memory_type: str = "episodic",
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        添加短期记忆
        
        Args:
            session_id: 会话ID
            content: 内容
            role: 角色
            memory_type: 记忆类型
            importance: 重要性
            tags: 标签
            metadata: 元数据
            
        Returns:
            记忆ID
        """
        # 生成嵌入
        embedding = self.embedding_generator.generate(content)
        
        # 创建记忆项
        item = ShortTermMemoryItem.create(
            session_id=session_id,
            content=content,
            embedding=embedding,
            role=role,
            memory_type=memory_type,
            importance=importance,
            tags=tags,
            metadata=metadata
        )
        
        with self._lock:
            # 添加到向量存储
            self.vector_store.add(item.id, embedding, item.to_dict())
            
            # 更新会话
            if session_id not in self._sessions:
                self._sessions[session_id] = []
                self._session_info[session_id] = {
                    "created_at": time.time(),
                    "type": "multi",
                    "last_active": time.time()
                }
            
            self._sessions[session_id].append(item.id)
            self._session_info[session_id]["last_active"] = time.time()
            
            # 检查会话容量
            if len(self._sessions[session_id]) > self.max_session_items:
                self._evict_session(session_id)
            
            # 保存到磁盘
            self._save_item(item)
        
        return item.id
    
    def get(self, memory_id: str) -> Optional[ShortTermMemoryItem]:
        """获取记忆"""
        # 先从内存获取
        with self._lock:
            results = self.vector_store.search(
                [0] * self.vector_store.dimension,  # dummy
                top_k=1
            )
            
            for item_id, _, meta in results:
                if item_id == memory_id:
                    return ShortTermMemoryItem.from_dict(meta)
        
        # 从磁盘加载
        item = self._load_item(memory_id)
        return item
    
    def get_session(self, session_id: str) -> List[ShortTermMemoryItem]:
        """获取会话所有记忆"""
        with self._lock:
            item_ids = self._sessions.get(session_id, [])
            
            items = []
            for item_id in item_ids:
                # 从向量存储获取元数据
                for _, _, meta in self.vector_store.search(
                    [0] * self.vector_store.dimension,
                    top_k=len(item_ids)
                ):
                    if meta.get("id") == item_id:
                        items.append(ShortTermMemoryItem.from_dict(meta))
                        break
            
            return items
    
    def search(
        self,
        query: str,
        session_id: Optional[str] = None,
        top_k: int = 5
    ) -> List[Tuple[float, ShortTermMemoryItem]]:
        """
        语义搜索
        
        Args:
            query: 查询内容
            session_id: 可选，限定会话
            top_k: 返回数量
            
        Returns:
            [(相似度, 记忆项), ...]
        """
        # 生成查询向量
        query_embedding = self.embedding_generator.generate(query)
        
        # 搜索向量存储
        def session_filter(meta: Dict) -> bool:
            if session_id is None:
                return True
            return meta.get("session_id") == session_id
        
        results = self.vector_store.search(
            query_embedding,
            top_k=top_k,
            filter_func=session_filter
        )
        
        return [
            (sim, ShortTermMemoryItem.from_dict(meta))
            for item_id, sim, meta in results
        ]
    
    def retrieve_for_rag(
        self,
        query: str,
        session_id: Optional[str] = None,
        max_tokens: int = 4000
    ) -> List[str]:
        """
        RAG检索 - 获取上下文相关记忆
        
        Args:
            query: 查询内容
            session_id: 会话ID
            max_tokens: 最大token
            
        Returns:
            记忆内容列表
        """
        results = self.search(query, session_id=session_id, top_k=10)
        
        context = []
        total_tokens = 0
        
        for similarity, item in results:
            # 估算token
            tokens = len(item.content) // 2
            
            if total_tokens + tokens > max_tokens:
                continue
            
            context.append(item.content)
            total_tokens += tokens
        
        return context
    
    def _evict_session(self, session_id: str):
        """淘汰会话中旧的记忆"""
        if session_id not in self._sessions:
            return
        
        item_ids = self._sessions[session_id]
        
        # 保留最近的
        keep_count = self.max_session_items // 2
        to_remove = item_ids[:-keep_count]
        
        for item_id in to_remove:
            self.vector_store.delete(item_id)
            self._delete_item(item_id)
        
        self._sessions[session_id] = item_ids[-keep_count:]
    
    def cleanup_expired(self):
        """清理过期记忆"""
        now = time.time()
        expired_threshold = self.retention_minutes * 60
        
        with self._lock:
            to_remove_sessions = []
            
            for session_id, info in self._session_info.items():
                if now - info["last_active"] > expired_threshold:
                    to_remove_sessions.append(session_id)
            
            for session_id in to_remove_sessions:
                # 删除该会话所有记忆
                for item_id in self._sessions.get(session_id, []):
                    self.vector_store.delete(item_id)
                    self._delete_item(item_id)
                
                del self._sessions[session_id]
                del self._session_info[session_id]
    
    def _save_item(self, item: ShortTermMemoryItem):
        """保存到磁盘"""
        filepath = os.path.join(self.storage_path, f"{item.id}.json")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(item.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存失败: {e}")
    
    def _load_item(self, item_id: str) -> Optional[ShortTermMemoryItem]:
        """从磁盘加载"""
        filepath = os.path.join(self.storage_path, f"{item_id}.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return ShortTermMemoryItem.from_dict(data)
            except Exception as e:
                print(f"加载失败: {e}")
        return None
    
    def _delete_item(self, item_id: str):
        """删除磁盘文件"""
        filepath = os.path.join(self.storage_path, f"{item_id}.json")
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"删除失败: {e}")
    
    def _load_sessions(self):
        """加载会话"""
        if not os.path.exists(self.storage_path):
            return
        
        try:
            index_file = os.path.join(self.storage_path, "index.json")
            if os.path.exists(index_file):
                with open(index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._sessions = data.get("sessions", {})
                    self._session_info = data.get("session_info", {})
        except Exception as e:
            print(f"加载会话失败: {e}")
    
    def _save_sessions(self):
        """保存会话索引"""
        try:
            index_file = os.path.join(self.storage_path, "index.json")
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "sessions": self._sessions,
                    "session_info": self._session_info
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存会话索引失败: {e}")
    
    def get_stats(self) -> Dict:
        """获取统计"""
        with self._lock:
            return {
                "version": "3.2.0",
                "type": "shortterm_memory",
                "total_items": self.vector_store.count(),
                "active_sessions": len(self._sessions),
                "storage_path": self.storage_path,
                "retention_minutes": self.retention_minutes
            }


# 全局实例
_shortterm_memory: Optional[ShortTermMemoryManager] = None
_stm_lock = threading.Lock()


def get_shortterm_memory() -> ShortTermMemoryManager:
    """获取全局短期记忆实例"""
    global _shortterm_memory
    with _stm_lock:
        if _shortterm_memory is None:
            _shortterm_memory = ShortTermMemoryManager()
        return _shortterm_memory


if __name__ == "__main__":
    print("=== 短期记忆测试 ===")
    
    stm = ShortTermMemoryManager(storage_path="./data/test_stm")
    
    # 添加记忆
    session_id = "test_session_001"
    
    stm.add(session_id, "用户: 今天天气怎么样？", role="user", importance=0.6)
    stm.add(session_id, "助手: 今天天气晴朗，适合出行。", role="assistant", importance=0.8)
    stm.add(session_id, "用户: 那明天呢？", role="user", importance=0.6)
    stm.add(session_id, "助手: 明天预计有雨，建议带伞。", role="assistant", importance=0.7)
    
    print(f"当前条目: {stm.get_stats()['total_items']}")
    print(f"活跃会话: {stm.get_stats()['active_sessions']}")
    
    # 搜索
    print("\n搜索'天气':")
    results = stm.search("天气")
    for sim, item in results:
        print(f"  [{sim:.2f}] {item.content}")
    
    # RAG检索
    print("\nRAG检索:")
    context = stm.retrieve_for_rag("天气")
    for c in context:
        print(f"  - {c}")
    
    print("\n统计:", stm.get_stats())
