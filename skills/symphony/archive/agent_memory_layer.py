# -*- coding: utf-8 -*-
"""
序境系统 - Agent 记忆存储架构 v2.0
====================================
整合: 分层记忆 + Vector Store + Graph DB + RAG + 持续预训�?
基于少府监预学批次第二轮知识整合

作�? 少府监·翰林学�?
版本: 2.0.0
"""

import sqlite3
import hashlib
import time
import json
import os
import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from collections import defaultdict, OrderedDict

# ==================== 枚举定义 ====================

class MemoryStorageType(Enum):
    """存储类型枚举"""
    VECTOR_STORE = "vector_store"           # 快速语义检�?
    RAG_STORE = "rag_store"                # 即时精确检�?
    GRAPH_DB = "graph_db"                  # 可审计链�?
    HYBRID_STORE = "hybrid_store"           # 上下文深�?
    GRAPH_VECTOR_HYBRID = "graph_vector_hybrid"  # 多跳推理


class MemoryTier(Enum):
    """记忆层次"""
    WORKING = "working"           # 工作记忆（短期）
    LONG_TERM = "long_term"      # 长期记忆
    INDEX = "index"              # 索引记忆
    SEMANTIC = "semantic"        # 语义记忆
    EPISODIC = "episodic"         # 情景记忆


class MemoryType(Enum):
    """存储器类�?""
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    EMOTIONAL = "emotional"
    # 兼容 MemoryStorageType 的值（解决跨存储层类型识别�?
    VECTOR_STORE = "vector_store"
    RAG_STORE = "rag_store"
    GRAPH_DB = "graph_db"
    HYBRID_STORE = "hybrid_store"
    GRAPH_VECTOR_HYBRID = "graph_vector_hybrid"




# ==================== 数据结构 ====================

@dataclass
class MemoryBlock:
    """记忆�?- 记忆的基本单�?""
    id: str
    content: str
    memory_type: MemoryType
    tier: MemoryTier
    embedding: List[float] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    importance_score: float = 0.5

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "tier": self.tier.value,
            "tags": self.tags,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "access_count": self.access_count,
            "importance_score": self.importance_score
        }


@dataclass
class MemoryQuery:
    """记忆查询请求"""
    query_text: str
    storage_type: MemoryStorageType
    top_k: int = 10
    filters: Dict = None
    require_audit: bool = False  # 合规审计需�?


@dataclass
class GraphRelation:
    """图关�?""
    source_id: str
    target_id: str
    relation: str
    weight: float = 1.0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)


# ==================== 向量存储引擎 ====================

class VectorStore:
    """
    向量存储引擎
    使用 hash-based 模拟向量嵌入，避免外部依�?
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
        self._lock = threading.RLock()

    def _init_db(self):
        """初始化向量存储表"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS vector_store (
                id TEXT PRIMARY KEY,
                content TEXT,
                embedding BLOB,
                memory_type TEXT,
                tags TEXT,
                metadata TEXT,
                timestamp REAL,
                access_count INTEGER DEFAULT 0
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS vector_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id TEXT,
                dimension INTEGER,
                created_at REAL
            )
        ''')
        conn.commit()
        conn.close()

    def add(self, block: MemoryBlock) -> bool:
        """添加记忆到向量存�?""
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                embedding_bytes = json.dumps(block.embedding).encode('utf-8')
                c.execute('''
                    INSERT OR REPLACE INTO vector_store
                    (id, content, embedding, memory_type, tags, metadata, timestamp, access_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    block.id,
                    block.content,
                    embedding_bytes,
                    block.memory_type.value,
                    json.dumps(block.tags),
                    json.dumps(block.metadata),
                    block.timestamp,
                    block.access_count
                ))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"向量存储添加失败: {e}")
                return False

    def search(self, query_embedding: List[float], top_k: int = 10) -> List[Tuple[MemoryBlock, float]]:
        """
        向量相似度搜�?
        使用余弦相似度模�?
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('SELECT id, content, embedding, memory_type, tags, metadata, timestamp, access_count FROM vector_store')
            rows = c.fetchall()
            conn.close()

            results = []
            for row in rows:
                emb = json.loads(row[2])
                similarity = self._cosine_similarity(query_embedding, emb)
                block = MemoryBlock(
                    id=row[0], content=row[1],
                    embedding=emb,
                    memory_type=MemoryType(row[3]),
                    tier=MemoryTier.LONG_TERM,
                    tags=json.loads(row[4]),
                    metadata=json.loads(row[5]),
                    timestamp=row[6], access_count=row[7]
                )
                results.append((block, similarity))

            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """计算余弦相似�?""
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


# ==================== RAG存储引擎 ====================

class RAGStore:
    """
    RAG存储引擎
    基于关键词和标签的精确检�?
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
        self._lock = threading.RLock()

    def _init_db(self):
        """初始化RAG存储�?""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS rag_store (
                id TEXT PRIMARY KEY,
                content TEXT,
                keywords TEXT,
                memory_type TEXT,
                tags TEXT,
                metadata TEXT,
                timestamp REAL,
                access_count INTEGER DEFAULT 0
            )
        ''')
        # 全文搜索索引
        c.execute('''
            CREATE TABLE IF NOT EXISTS rag_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id TEXT,
                keyword TEXT,
                position INTEGER,
                frequency INTEGER DEFAULT 1
            )
        ''')
        conn.commit()
        conn.close()

    def add(self, block: MemoryBlock) -> bool:
        """添加记忆到RAG存储"""
        with self._lock:
            try:
                keywords = self._extract_keywords(block.content)
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                c.execute('''
                    INSERT OR REPLACE INTO rag_store
                    (id, content, keywords, memory_type, tags, metadata, timestamp, access_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    block.id, block.content, json.dumps(keywords),
                    block.memory_type.value, json.dumps(block.tags),
                    json.dumps(block.metadata), block.timestamp, block.access_count
                ))
                # 索引关键�?
                for pos, kw in enumerate(keywords):
                    c.execute('''
                        INSERT OR IGNORE INTO rag_index (memory_id, keyword, position, frequency)
                        VALUES (?, ?, ?, 1)
                    ''', (block.id, kw, pos))
                    c.execute('''
                        UPDATE rag_index SET frequency = frequency + 1
                        WHERE memory_id = ? AND keyword = ?
                    ''', (block.id, kw))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"RAG存储添加失败: {e}")
                return False

    def search(self, query_text: str, top_k: int = 10) -> List[Tuple[MemoryBlock, float]]:
        """基于关键词的精确检�?""
        with self._lock:
            keywords = self._extract_keywords(query_text)
            if not keywords:
                return []

            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            placeholders = ','.join('?' * len(keywords))
            c.execute(f'''
                SELECT r.id, r.content, r.memory_type, r.tags, r.metadata,
                       r.timestamp, r.access_count, COUNT(DISTINCT ri.keyword) as match_count
                FROM rag_store r
                LEFT JOIN rag_index ri ON r.id = ri.memory_id AND ri.keyword IN ({placeholders})
                GROUP BY r.id
                ORDER BY match_count DESC, r.timestamp DESC
                LIMIT ?
            ''', keywords + [top_k])

            rows = c.fetchall()
            conn.close()

            results = []
            for row in rows:
                block = MemoryBlock(
                    id=row[0], content=row[1],
                    memory_type=MemoryType(row[2]),
                    tags=json.loads(row[3]),
                    metadata=json.loads(row[4]),
                    timestamp=row[5], access_count=row[6]
                )
                score = row[7] / len(keywords) if keywords else 0
                results.append((block, score))
            return results

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键�?""
        stop_words = {'�?, '�?, '�?, '�?, '�?, '�?, '�?, '�?, '�?, '�?, '�?, '一', '一�?, '�?, '�?, '�?, '�?, '�?, '�?, '�?, '�?, '�?, '着', '没有', '�?, '�?, '自己', '�?, '�?, '�?, '�?, '�?, '�?}
        words = [w for w in text if len(w) >= 2 and w not in stop_words]
        return list(set(words))


# ==================== 图数据库引擎 ====================

class GraphStore:
    """
    图数据库引擎
    实现关系存储与多跳遍�?
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
        self._lock = threading.RLock()

    def _init_db(self):
        """初始化图数据库表"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # 节点�?
        c.execute('''
            CREATE TABLE IF NOT EXISTS graph_nodes (
                id TEXT PRIMARY KEY,
                content TEXT,
                memory_type TEXT,
                metadata TEXT,
                timestamp REAL
            )
        ''')
        # 边表
        c.execute('''
            CREATE TABLE IF NOT EXISTS graph_edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT,
                target_id TEXT,
                relation TEXT,
                weight REAL DEFAULT 1.0,
                timestamp REAL,
                metadata TEXT,
                FOREIGN KEY (source_id) REFERENCES graph_nodes(id),
                FOREIGN KEY (target_id) REFERENCES graph_nodes(id)
            )
        ''')
        # 审计�?
        c.execute('''
            CREATE TABLE IF NOT EXISTS graph_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT,
                target_id TEXT,
                relation TEXT,
                action TEXT,
                timestamp REAL,
                details TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def add_node(self, block: MemoryBlock) -> bool:
        """添加节点"""
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                c.execute('''
                    INSERT OR REPLACE INTO graph_nodes
                    (id, content, memory_type, metadata, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (block.id, block.content, block.memory_type.value,
                      json.dumps(block.metadata), block.timestamp))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"图节点添加失�? {e}")
                return False

    def add_edge(self, relation: GraphRelation) -> bool:
        """添加�?""
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                c.execute('''
                    INSERT INTO graph_edges
                    (source_id, target_id, relation, weight, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (relation.source_id, relation.target_id, relation.relation,
                      relation.weight, relation.timestamp, json.dumps(relation.metadata)))
                # 记录审计
                c.execute('''
                    INSERT INTO graph_audit
                    (source_id, target_id, relation, action, timestamp, details)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (relation.source_id, relation.target_id, relation.relation,
                      'CREATE', relation.timestamp, json.dumps(relation.metadata)))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"图边添加失败: {e}")
                return False

    def traverse(self, node_id: str, depth: int = 3) -> List[Dict]:
        """
        图遍历：多跳推理
        使用BFS实现
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            visited = set()
            queue = [(node_id, 0)]
            results = []

            while queue:
                current_id, current_depth = queue.pop(0)
                if current_id in visited or current_depth > depth:
                    continue
                visited.add(current_id)

                # 获取节点信息
                c.execute('SELECT id, content, memory_type, metadata FROM graph_nodes WHERE id = ?', (current_id,))
                node_row = c.fetchone()
                if node_row:
                    results.append({
                        "node_id": node_row[0],
                        "content": node_row[1],
                        "memory_type": node_row[2],
                        "metadata": json.loads(node_row[3]) if node_row[3] else {},
                        "depth": current_depth
                    })

                # 获取邻居节点
                c.execute('''
                    SELECT target_id, relation, weight FROM graph_edges
                    WHERE source_id = ?
                ''', (current_id,))
                for edge_row in c.fetchall():
                    if edge_row[0] not in visited:
                        queue.append((edge_row[0], current_depth + 1))

            conn.close()
            return results

    def get_audit_trail(self, node_id: str) -> List[Dict]:
        """获取审计链路"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                SELECT source_id, target_id, relation, action, timestamp, details
                FROM graph_audit
                WHERE source_id = ? OR target_id = ?
                ORDER BY timestamp DESC
            ''', (node_id, node_id))
            rows = c.fetchall()
            conn.close()
            return [{"source": r[0], "target": r[1], "relation": r[2],
                     "action": r[3], "timestamp": r[4], "details": json.loads(r[5])}
                    for r in rows]


# ==================== 混合存储引擎 ====================

class HybridStore:
    """
    混合存储引擎
    结合向量存储和RAG存储的优�?
    """

    def __init__(self, vector_store: VectorStore, rag_store: RAGStore):
        self.vector_store = vector_store
        self.rag_store = rag_store

    def add(self, block: MemoryBlock) -> bool:
        """添加记忆到混合存�?""
        vs_ok = self.vector_store.add(block)
        rs_ok = self.rag_store.add(block)
        return vs_ok and rs_ok

    def search(self, query_text: str, query_embedding: List[float],
               top_k: int = 10, alpha: float = 0.5) -> List[Tuple[MemoryBlock, float]]:
        """
        混合搜索
        alpha: 向量权重 (1-alpha给RAG)
        """
        vector_results = self.vector_store.search(query_embedding, top_k * 2)
        rag_results = self.rag_store.search(query_text, top_k * 2)

        # 归一化分数并融合
        scores = defaultdict(float)
        blocks_map = {}

        for block, vs_score in vector_results:
            blocks_map[block.id] = block
            scores[block.id] += alpha * vs_score

        for block, rs_score in rag_results:
            if block.id not in blocks_map:
                blocks_map[block.id] = block
            scores[block.id] += (1 - alpha) * rs_score

        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        return [(blocks_map[iid], scores[iid]) for iid in sorted_ids[:top_k]]


# ==================== 主控制器 ====================

class AgentMemoryLayer:
    """
    Agent 记忆存储�?v2.0
    实现分层架构 + 多存储引�?+ 智能路由

    核心理念: AI Agent 不应知道数据在哪里，只应知道需要什�?
    """

    def __init__(self, db_dir: str = None):
        if db_dir is None:
            db_dir = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data'
        os.makedirs(db_dir, exist_ok=True)

        # 初始化各存储引擎
        self.vector_store = VectorStore(f'{db_dir}/memory_vector.db')
        self.rag_store = RAGStore(f'{db_dir}/memory_rag.db')
        self.graph_store = GraphStore(f'{db_dir}/memory_graph.db')
        self.hybrid_store = HybridStore(self.vector_store, self.rag_store)

        # 记忆层次存储（内存）
        self.working_memory: OrderedDict[str, MemoryBlock] = OrderedDict()
        self.working_capacity = 100
        self.long_term_memory: OrderedDict[str, MemoryBlock] = OrderedDict()
        self.semantic_memory: OrderedDict[str, MemoryBlock] = OrderedDict()
        self.episodic_memory: OrderedDict[str, MemoryBlock] = OrderedDict()

        # 元数据索�?
        self.index_memory: Dict[str, List[str]] = defaultdict(list)  # tag -> memory_ids

        # 审计日志
        self.audit_log: List[Dict] = []
        self._lock = threading.RLock()

        # 加载持久化数据到内存
        self._load_from_persistence()

    def _load_from_persistence(self):
        """从持久化存储加载数据到内�?""
        print("[AgentMemoryLayer] 从持久化存储加载记忆...")

    # ==================== 核心方法 ====================

    def select_storage(self, query: MemoryQuery) -> MemoryStorageType:
        """
        智能存储选择
        根据查询需求自动选择最优存储类�?

        决策规则:
        - 对话�?语义相关 �?VECTOR_STORE
        - 任务自动�?精确匹配 �?RAG_STORE
        - 合规审计/链路追溯 �?GRAPH_DB
        - 复杂上下�?深度理解 �?HYBRID_STORE
        - 多跳推理/关系探索 �?GRAPH_VECTOR_HYBRID
        """
        explicit = query.storage_type
        if explicit != MemoryStorageType.GRAPH_VECTOR_HYBRID:
            # 用户明确指定了类�?
            return explicit

        # 自动推断
        query_lower = query.query_text.lower()
        if any(kw in query_lower for kw in ['�?, '什�?, '�?, '怎样', '如何', 'why', 'what', 'who', 'how']):
            # 探索性问�?�?向量
            return MemoryStorageType.VECTOR_STORE
        elif any(kw in query_lower for kw in ['查找', '搜索', '找到', '检�?, 'search', 'find']):
            # 精确查找 �?RAG
            return MemoryStorageType.RAG_STORE
        elif query.require_audit:
            # 合规审计 �?�?
            return MemoryStorageType.GRAPH_DB
        elif len(query.filters or {}) > 0:
            # 有过滤条�?�?混合
            return MemoryStorageType.HYBRID_STORE
        else:
            # 默认 �?混合
            return MemoryStorageType.HYBRID_STORE

    def store(self, block: MemoryBlock, tier: MemoryTier = None) -> bool:
        """
        存储记忆到对应层�?
        自动分配层次并持久化
        """
        if tier is None:
            tier = block.tier

        with self._lock:
            # 1. 存储到对应层次（内存�?
            if tier == MemoryTier.WORKING:
                if len(self.working_memory) >= self.working_capacity:
                    # LRU淘汰
                    self.working_memory.popitem(last=False)
                self.working_memory[block.id] = block
            elif tier == MemoryTier.LONG_TERM:
                self.long_term_memory[block.id] = block
            elif tier == MemoryTier.SEMANTIC:
                self.semantic_memory[block.id] = block
            elif tier == MemoryTier.EPISODIC:
                self.episodic_memory[block.id] = block

            # 2. 持久化到各存储引�?
            self.hybrid_store.add(block)
            self.graph_store.add_node(block)

            # 3. 更新索引
            for tag in block.tags:
                self.index_memory[tag].append(block.id)

            return True

    def retrieve(self, query: MemoryQuery) -> List[Tuple[MemoryBlock, float]]:
        """
        从最优存储中检索记�?
        """
        storage_type = self.select_storage(query)
        query_embedding = self.compute_embedding(query.query_text)

        if storage_type == MemoryStorageType.VECTOR_STORE:
            return self.vector_store.search(query_embedding, query.top_k)
        elif storage_type == MemoryStorageType.RAG_STORE:
            return self.rag_store.search(query.query_text, query.top_k)
        elif storage_type == MemoryStorageType.GRAPH_DB:
            # 图存储不支持文本查询，转用混�?
            return self.hybrid_store.search(query.query_text, query_embedding, query.top_k)
        elif storage_type == MemoryStorageType.GRAPH_VECTOR_HYBRID:
            # 先图遍历，再向量搜索
            # 简化：直接用混�?
            return self.hybrid_store.search(query.query_text, query_embedding, query.top_k)
        else:  # HYBRID_STORE
            return self.hybrid_store.search(query.query_text, query_embedding, query.top_k)

    def retrieve_with_audit(self, query: MemoryQuery) -> Tuple[List[Tuple[MemoryBlock, float]], Dict]:
        """
        带合规审计的检�?
        返回: (结果列表, 审计信息)
        """
        results = self.retrieve(query)

        audit_info = {
            "query_text": query.query_text,
            "storage_type": query.storage_type.value,
            "result_count": len(results),
            "timestamp": time.time(),
            "audit_trail": []
        }

        # 如果涉及图存储，收集审计信息
        if query.require_audit:
            for block, score in results:
                trail = self.graph_store.get_audit_trail(block.id)
                audit_info["audit_trail"].extend(trail)

        return results, audit_info

    def consolidate(self):
        """
        记忆整合: 将工作记忆定期写入长期记�?
        使用访问频率和重要性评分决定提�?
        """
        with self._lock:
            promoted = []
            demoted = []

            # 检查工作记忆中的高频访问项
            for mid, block in list(self.working_memory.items()):
                # 访问次数多或重要性高�?�?提升到长期记�?
                if block.access_count >= 3 or block.importance_score >= 0.7:
                    block.tier = MemoryTier.LONG_TERM
                    self.long_term_memory[mid] = block
                    del self.working_memory[mid]
                    self.hybrid_store.add(block)
                    promoted.append(mid)

                # 长时间未访问�?�?降低优先�?
                elif time.time() - block.last_access > 3600:  # 1小时
                    block.importance_score *= 0.9
                    if block.importance_score < 0.1:
                        demoted.append(mid)

            if promoted or demoted:
                print(f"[记忆整合] 提升: {len(promoted)}, 降级: {len(demoted)}")

            return {"promoted": promoted, "demoted": demoted}

    def compute_embedding(self, text: str) -> List[float]:
        """
        计算文本向量嵌入
        使用hash模拟，输出固定维度向�?
        """
        import struct
        hash_bytes = hashlib.sha256(text.encode('utf-8')).digest()
        values = list(struct.unpack('32f', (hash_bytes * 4)[:128]))
        # L2归一�?
        norm = sum(v * v for v in values) ** 0.5
        if norm > 0:
            values = [v / norm for v in values]
        return values

    def graph_link(self, source_id: str, target_id: str, relation: str, weight: float = 1.0):
        """
        在图数据库中建立关系链接
        """
        rel = GraphRelation(
            source_id=source_id,
            target_id=target_id,
            relation=relation,
            weight=weight,
            timestamp=time.time()
        )
        return self.graph_store.add_edge(rel)

    def graph_traverse(self, node_id: str, depth: int = 3) -> List[Dict]:
        """
        图遍�? 多跳推理
        """
        return self.graph_store.traverse(node_id, depth)

    def get_memory_stats(self) -> Dict:
        """获取记忆统计"""
        return {
            "working_memory": len(self.working_memory),
            "long_term_memory": len(self.long_term_memory),
            "semantic_memory": len(self.semantic_memory),
            "episodic_memory": len(self.episodic_memory),
            "index_tags": len(self.index_memory),
            "audit_log_size": len(self.audit_log)
        }


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("Xujing System - Agent Memory Layer v2.0 Test")
    print("=" * 60)

    db_dir = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data'
    os.makedirs(db_dir, exist_ok=True)

    # 初始�?
    memory_layer = AgentMemoryLayer(db_dir)

    # 测试1: 存储记忆
    print("\n=== 测试1: 存储记忆 ===")
    test_block = MemoryBlock(
        id="test_001",
        content="量子计算是一种利用量子力学原理进行计算的技�?,
        memory_type=MemoryType.SEMANTIC,
        tier=MemoryTier.LONG_TERM,
        tags=["量子计算", "科技", "前沿"],
        importance_score=0.9
    )
    memory_layer.store(test_block)
    print(f"[OK] 存储记忆: {test_block.id}")

    test_block2 = MemoryBlock(
        id="test_002",
        content="深度学习是机器学习的一个分支，使用神经网络进行学习",
        memory_type=MemoryType.SEMANTIC,
        tier=MemoryTier.LONG_TERM,
        tags=["深度学习", "AI", "机器学习"],
        importance_score=0.8
    )
    memory_layer.store(test_block2)

    test_block3 = MemoryBlock(
        id="test_003",
        content="2025�?�?8日，少府监完成预学批次第二轮",
        memory_type=MemoryType.EPISODIC,
        tier=MemoryTier.EPISODIC,
        tags=["少府�?, "预学", "里程�?],
        importance_score=0.95
    )
    memory_layer.store(test_block3)
    print(f"[OK] 共存�?3 条记�?)

    # 测试2: 图关�?
    print("\n=== 测试2: 图关�?===")
    memory_layer.graph_link("test_001", "test_002", "related_to", 0.8)
    memory_layer.graph_link("test_002", "test_003", "happened_before", 1.0)
    print("[OK] 建立图关�? test_001 �?test_002 �?test_003")

    # 测试3: 智能存储选择
    print("\n=== 测试3: 智能存储选择 ===")
    query1 = MemoryQuery(
        query_text="量子计算的工作原理是什么？",
        storage_type=MemoryStorageType.VECTOR_STORE
    )
    selected = memory_layer.select_storage(query1)
    print(f"查询1 选择存储: {selected.value}")

    query2 = MemoryQuery(
        query_text="查找关于深度学习的内�?,
        storage_type=MemoryStorageType.RAG_STORE
    )
    selected2 = memory_layer.select_storage(query2)
    print(f"查询2 选择存储: {selected2.value}")

    query3 = MemoryQuery(
        query_text="哪些记忆被关联？",
        storage_type=MemoryStorageType.GRAPH_DB,
        require_audit=True
    )
    selected3 = memory_layer.select_storage(query3)
    print(f"查询3(需审计) 选择存储: {selected3.value}")

    # 测试4: 检索记�?
    print("\n=== 测试4: 检索记�?===")
    query = MemoryQuery(
        query_text="关于AI和机器学习的内容",
        storage_type=MemoryStorageType.HYBRID_STORE,
        top_k=5
    )
    results = memory_layer.retrieve(query)
    print(f"找到 {len(results)} 条相关记�?")
    for block, score in results:
        print(f"  [{score:.3f}] {block.content[:40]}...")

    # 测试5: 带审计的检�?
    print("\n=== 测试5: 带审计的检�?===")
    audit_query = MemoryQuery(
        query_text="量子计算",
        storage_type=MemoryStorageType.GRAPH_DB,
        require_audit=True
    )
    results, audit = memory_layer.retrieve_with_audit(audit_query)
    print(f"审计信息: 结果�?{audit['result_count']}, 存储类型={audit['storage_type']}")

    # 测试6: 图遍�?
    print("\n=== 测试6: 图遍�?多跳推理) ===")
    traversal = memory_layer.graph_traverse("test_001", depth=3)
    print(f"�?test_001 遍历得到 {len(traversal)} 个节�?")
    for node in traversal:
        print(f"  [深度{node['depth']}] {node['node_id']}: {node['content'][:30]}...")

    # 测试7: 记忆整合
    print("\n=== 测试7: 记忆整合 ===")
    consolidation = memory_layer.consolidate()
    print(f"整合结果: 提升 {len(consolidation['promoted'])} �? 降级 {len(consolidation['demoted'])} �?)

    # 测试8: 统计信息
    print("\n=== 测试8: 记忆统计 ===")
    stats = memory_layer.get_memory_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("[OK] Agent 记忆存储架构 v2.0 测试完成")
    print("=" * 60)

