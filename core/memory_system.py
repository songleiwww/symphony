#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆系统 - 短期记忆、长期记忆、语义检索
"""
import os
import json
import time
import sqlite3
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field, asdict

@dataclass
class Memory:
    """记忆数据类"""
    memory_id: str = ""
    content: str = ""
    memory_type: str = "short_term"  # short_term, long_term, working
    importance: float = 0.5  # 0.0-1.0
    source: str = "user"
    tags: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    expires_at: Optional[float] = None  # 短期记忆过期时间
    embedding: Optional[List[float]] = None
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "memory_type": self.memory_type,
            "importance": self.importance,
            "source": self.source,
            "tags": self.tags,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "expires_at": self.expires_at,
            "metadata": self.metadata
        }

class MemorySystem:
    """记忆系统"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "data", 
                "symphony.db"
            )
        else:
            self.db_path = db_path
        
        self._init_memory_tables()
        
        # 记忆配置
        self.config = {
            "short_term_expire_hours": 24,  # 短期记忆24小时过期
            "importance_threshold": 0.7,     # 重要性阈值，超过则晋升为长期记忆
            "max_short_term": 100,           # 最大短期记忆数量
            "max_working": 20,               # 最大工作记忆数量
            "cleanup_interval": 3600         # 清理间隔（秒）
        }
    
    def _init_memory_tables(self):
        """初始化记忆数据表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 记忆表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS 记忆表 (
            memory_id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            memory_type TEXT DEFAULT 'short_term',
            importance REAL DEFAULT 0.5,
            source TEXT DEFAULT 'user',
            tags TEXT,
            created_at REAL NOT NULL,
            last_accessed REAL NOT NULL,
            access_count INTEGER DEFAULT 0,
            expires_at REAL,
            metadata TEXT
        )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_type ON 记忆表(memory_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_importance ON 记忆表(importance)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_created ON 记忆表(created_at)')
        
        conn.commit()
        conn.close()
    
    def add_memory(self, content: str, memory_type: str = "short_term", 
                  importance: float = 0.5, source: str = "user",
                  tags: List[str] = None, **metadata) -> str:
        """添加记忆"""
        import uuid
        memory_id = f"mem_{uuid.uuid4().hex[:12]}"
        
        # 设置过期时间
        expires_at = None
        if memory_type == "short_term":
            expires_at = time.time() + self.config["short_term_expire_hours"] * 3600
        
        # 序列化数据
        tags_json = json.dumps(tags or [], ensure_ascii=False)
        metadata_json = json.dumps(metadata, ensure_ascii=False)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO 记忆表 (
            memory_id, content, memory_type, importance, source, 
            tags, created_at, last_accessed, access_count, expires_at, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            memory_id, content, memory_type, importance, source,
            tags_json, time.time(), time.time(), 0, expires_at, metadata_json
        ))
        
        conn.commit()
        conn.close()
        
        return memory_id
    
    def get_memory(self, memory_id: str) -> Optional[Dict]:
        """获取记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM 记忆表 WHERE memory_id = ?", (memory_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        # 获取列名
        cursor.execute("PRAGMA table_info(记忆表)")
        columns = [col[1] for col in cursor.fetchall()]
        memory_dict = dict(zip(columns, row))
        
        # 反序列化
        memory_dict["tags"] = json.loads(memory_dict["tags"]) if memory_dict["tags"] else []
        memory_dict["metadata"] = json.loads(memory_dict["metadata"]) if memory_dict["metadata"] else {}
        
        # 更新访问记录
        cursor.execute('''
        UPDATE 记忆表 SET last_accessed = ?, access_count = access_count + 1 
        WHERE memory_id = ?
        ''', (time.time(), memory_id))
        
        conn.commit()
        conn.close()
        
        return memory_dict
    
    def search_memory(self, query: str, memory_type: str = None, 
                     limit: int = 10) -> List[Dict]:
        """搜索记忆（简单关键词匹配）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql = "SELECT * FROM 记忆表 WHERE content LIKE ?"
        params = [f"%{query}%"]
        
        if memory_type:
            sql += " AND memory_type = ?"
            params.append(memory_type)
        
        sql += " ORDER BY importance DESC, last_accessed DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        # 获取列名
        cursor.execute("PRAGMA table_info(记忆表)")
        columns = [col[1] for col in cursor.fetchall()]
        
        memories = []
        for row in rows:
            memory_dict = dict(zip(columns, row))
            memory_dict["tags"] = json.loads(memory_dict["tags"]) if memory_dict["tags"] else []
            memory_dict["metadata"] = json.loads(memory_dict["metadata"]) if memory_dict["metadata"] else {}
            memories.append(memory_dict)
        
        conn.close()
        return memories
    
    def promote_to_long_term(self, memory_id: str) -> bool:
        """晋升为长期记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE 记忆表 SET memory_type = 'long_term', expires_at = NULL 
        WHERE memory_id = ?
        ''', (memory_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def cleanup_expired(self) -> int:
        """清理过期记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        DELETE FROM 记忆表 
        WHERE memory_type = 'short_term' 
        AND expires_at IS NOT NULL 
        AND expires_at < ?
        ''', (time.time(),))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted
    
    def auto_promote(self) -> int:
        """自动晋升符合条件的短期记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 查找符合晋升条件的记忆
        cursor.execute('''
        SELECT memory_id FROM 记忆表 
        WHERE memory_type = 'short_term' 
        AND (importance >= ? OR access_count >= 3)
        ''', (self.config["importance_threshold"],))
        
        memory_ids = [row[0] for row in cursor.fetchall()]
        
        # 批量晋升
        for mid in memory_ids:
            cursor.execute('''
            UPDATE 记忆表 SET memory_type = 'long_term', expires_at = NULL 
            WHERE memory_id = ?
            ''', (mid,))
        
        conn.commit()
        conn.close()
        
        return len(memory_ids)
    
    def get_statistics(self) -> Dict:
        """获取记忆统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 按类型统计
        cursor.execute("SELECT memory_type, COUNT(*) FROM 记忆表 GROUP BY memory_type")
        type_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 总数
        cursor.execute("SELECT COUNT(*) FROM 记忆表")
        total = cursor.fetchone()[0]
        
        # 平均重要性
        cursor.execute("SELECT AVG(importance) FROM 记忆表")
        avg_importance = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total": total,
            "by_type": type_stats,
            "avg_importance": round(avg_importance, 2)
        }

# 单例实例
_memory_system_instance: Optional[MemorySystem] = None

def get_memory_system() -> MemorySystem:
    """获取记忆系统单例"""
    global _memory_system_instance
    if _memory_system_instance is None:
        _memory_system_instance = MemorySystem()
    return _memory_system_instance

if __name__ == "__main__":
    # 测试记忆系统
    mem_sys = get_memory_system()
    
    # 添加测试记忆
    mem_id = mem_sys.add_memory(
        content="序境系统核心架构：内核层、核心层、工具层、角色层、数据层、接口层",
        memory_type="short_term",
        importance=0.8,
        source="developer",
        tags=["架构", "序境"]
    )
    
    print(f"添加记忆: {mem_id}")
    
    # 搜索记忆
    results = mem_sys.search_memory("架构")
    print(f"搜索结果: {len(results)} 条")
    
    # 统计
    stats = mem_sys.get_statistics()
    print(f"统计: {stats}")
