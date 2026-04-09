# -*- coding: utf-8 -*-
"""
序境系统 - 持久化记忆数据库适配 v1.0.0
=======================================
兼容SQLite/PostgreSQL，实现记忆长链持久化、跨会话共享
支持记忆分类、向量检索、会话隔离、跨会话共享
"""

import os
import json
import time
import sqlite3
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging
import threading

# 尝试导入PostgreSQL驱动
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== 配置 ====================
DATA_DIR = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data'
DEFAULT_SQLITE_PATH = f'{DATA_DIR}/symphony_memory.db'

# 记忆类型枚举
MEMORY_TYPES = {
    "USER_PREFERENCE": "用户偏好",
    "SESSION_CONTEXT": "会话上下??,
    "KNOWLEDGE": "知识内容",
    "TOOL_HISTORY": "工具调用历史",
    "TASK_RECORD": "任务记录",
    "SYSTEM_SETTING": "系统配置"
}

# ==================== 数据结构 ====================
@dataclass
class MemoryItem:
    """记忆条目"""
    memory_id: Optional[str] = None
    memory_type: str = "SESSION_CONTEXT"
    content: Union[str, Dict] = ""
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    is_shared: bool = False  # 是否跨会话共??    metadata: Dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    expire_at: Optional[float] = None  # 过期时间，None表示永久有效
    
    def to_dict(self) -> Dict:
        return {
            "memory_id": self.memory_id,
            "memory_type": self.memory_type,
            "content": json.dumps(self.content) if isinstance(self.content, dict) else self.content,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "is_shared": 1 if self.is_shared else 0,
            "metadata": json.dumps(self.metadata),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "expire_at": self.expire_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryItem':
        try:
            content = json.loads(data["content"]) if data["content"].startswith("{") or data["content"].startswith("[") else data["content"]
        except:
            content = data["content"]
        
        try:
            metadata = json.loads(data["metadata"]) if data["metadata"] else {}
        except:
            metadata = {}
        
        return cls(
            memory_id=data.get("memory_id"),
            memory_type=data.get("memory_type", "SESSION_CONTEXT"),
            content=content,
            session_id=data.get("session_id"),
            user_id=data.get("user_id"),
            is_shared=bool(data.get("is_shared", 0)),
            metadata=metadata,
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            expire_at=data.get("expire_at")
        )

# ==================== 抽象基类 ====================
class MemoryDB(ABC):
    """记忆数据库抽象基??"""
    
    @abstractmethod
    def connect(self) -> bool:
        """连接数据??"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """关闭数据库连??"""
        pass
    
    @abstractmethod
    def init_tables(self) -> bool:
        """初始化数据库??"""
        pass
    
    @abstractmethod
    def add_memory(self, memory: MemoryItem) -> Optional[str]:
        """添加记忆，返回记忆ID"""
        pass
    
    @abstractmethod
    def get_memory(self, memory_id: str) -> Optional[MemoryItem]:
        """根据ID获取记忆"""
        pass
    
    @abstractmethod
    def update_memory(self, memory_id: str, updates: Dict) -> bool:
        """更新记忆"""
        pass
    
    @abstractmethod
    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        pass
    
    @abstractmethod
    def search_memories(self, 
                       query: Optional[str] = None,
                       memory_type: Optional[str] = None,
                       session_id: Optional[str] = None,
                       user_id: Optional[str] = None,
                       include_shared: bool = True,
                       limit: int = 20,
                       offset: int = 0) -> List[MemoryItem]:
        """搜索记忆"""
        pass
    
    @abstractmethod
    def delete_expired(self) -> int:
        """删除过期记忆，返回删除数??"""
        pass

# ==================== SQLite 实现 ====================
class SQLiteMemoryDB(MemoryDB):
    """SQLite记忆数据库实??"""
    
    def __init__(self, db_path: str = DEFAULT_SQLITE_PATH):
        self.db_path = db_path
        self.conn = None
        self._lock = threading.Lock()
        # 确保数据目录存在
        if db_path and db_path != ":memory:":
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
    
    def connect(self) -> bool:
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Connected to SQLite database: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"SQLite connection failed: {e}")
            return False
    
    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("SQLite connection closed")
    
    def init_tables(self) -> bool:
        if not self.conn:
            if not self.connect():
                return False
        
        try:
            c = self.conn.cursor()
            # 创建??            c.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    memory_id TEXT PRIMARY KEY,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    session_id TEXT,
                    user_id TEXT,
                    is_shared INTEGER DEFAULT 0,
                    metadata TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    expire_at REAL
                )
            ''')
            # 创建索引
            c.execute('CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON memories(session_id)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON memories(user_id)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_is_shared ON memories(is_shared)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_expire_at ON memories(expire_at)')
            self.conn.commit()
            logger.info("SQLite memory tables initialized")
            return True
        except Exception as e:
            logger.error(f"SQLite init tables failed: {e}")
            return False
    
    def add_memory(self, memory: MemoryItem) -> Optional[str]:
        if not self.conn:
            if not self.connect():
                return None
        
        try:
            memory.memory_id = f"mem_{int(time.time() * 1000)}_{os.urandom(4).hex()}"
            memory_dict = memory.to_dict()
            
            with self._lock:
                c = self.conn.cursor()
                c.execute('''
                    INSERT INTO memories (
                        memory_id, memory_type, content, session_id, user_id, 
                        is_shared, metadata, created_at, updated_at, expire_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    memory_dict["memory_id"],
                    memory_dict["memory_type"],
                    memory_dict["content"],
                    memory_dict["session_id"],
                    memory_dict["user_id"],
                    memory_dict["is_shared"],
                    memory_dict["metadata"],
                    memory_dict["created_at"],
                    memory_dict["updated_at"],
                    memory_dict["expire_at"]
                ))
                self.conn.commit()
            
            logger.info(f"Added memory: {memory.memory_id}, type: {memory.memory_type}")
            return memory.memory_id
        except Exception as e:
            logger.error(f"Add memory failed: {e}")
            return None
    
    def get_memory(self, memory_id: str) -> Optional[MemoryItem]:
        if not self.conn:
            if not self.connect():
                return None
        
        try:
            with self._lock:
                c = self.conn.cursor()
                c.execute('SELECT * FROM memories WHERE memory_id = ?', (memory_id,))
                row = c.fetchone()
                if row:
                    return MemoryItem.from_dict(dict(row))
            return None
        except Exception as e:
            logger.error(f"Get memory failed: {e}")
            return None
    
    def update_memory(self, memory_id: str, updates: Dict) -> bool:
        if not self.conn:
            if not self.connect():
                return False
        
        try:
            updates["updated_at"] = time.time()
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [memory_id]
            
            with self._lock:
                c = self.conn.cursor()
                c.execute(f'UPDATE memories SET {set_clause} WHERE memory_id = ?', values)
                self.conn.commit()
            
            return c.rowcount > 0
        except Exception as e:
            logger.error(f"Update memory failed: {e}")
            return False
    
    def delete_memory(self, memory_id: str) -> bool:
        if not self.conn:
            if not self.connect():
                return False
        
        try:
            with self._lock:
                c = self.conn.cursor()
                c.execute('DELETE FROM memories WHERE memory_id = ?', (memory_id,))
                self.conn.commit()
            
            logger.info(f"Deleted memory: {memory_id}")
            return c.rowcount > 0
        except Exception as e:
            logger.error(f"Delete memory failed: {e}")
            return False
    
    def search_memories(self, 
                       query: Optional[str] = None,
                       memory_type: Optional[str] = None,
                       session_id: Optional[str] = None,
                       user_id: Optional[str] = None,
                       include_shared: bool = True,
                       limit: int = 20,
                       offset: int = 0) -> List[MemoryItem]:
        if not self.conn:
            if not self.connect():
                return []
        
        try:
            conditions = []
            params = []
            
            if query:
                conditions.append("content LIKE ?")
                params.append(f"%{query}%")
            
            if memory_type:
                conditions.append("memory_type = ?")
                params.append(memory_type)
            
            if user_id:
                conditions.append("user_id = ?")
                params.append(user_id)
            
            # 会话过滤：当前会?? 共享记忆（如允许??            session_conditions = []
            if session_id:
                session_conditions.append("session_id = ?")
                params.append(session_id)
            if include_shared:
                session_conditions.append("is_shared = 1")
            
            if session_conditions:
                conditions.append(f"({ ' OR '.join(session_conditions) })")
            
            # 不过??            conditions.append("(expire_at IS NULL OR expire_at > ?)")
            params.append(time.time())
            
            sql = "SELECT * FROM memories"
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            
            sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            with self._lock:
                c = self.conn.cursor()
                c.execute(sql, params)
                rows = c.fetchall()
            
            return [MemoryItem.from_dict(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Search memories failed: {e}")
            return []
    
    def delete_expired(self) -> int:
        if not self.conn:
            if not self.connect():
                return 0
        
        try:
            with self._lock:
                c = self.conn.cursor()
                c.execute('DELETE FROM memories WHERE expire_at <= ?', (time.time(),))
                self.conn.commit()
            
            count = c.rowcount
            if count > 0:
                logger.info(f"Deleted {count} expired memories")
            return count
        except Exception as e:
            logger.error(f"Delete expired memories failed: {e}")
            return 0

# ==================== PostgreSQL 实现 ====================
class PostgreSQLMemoryDB(MemoryDB):
    """PostgreSQL记忆数据库实??"""
    
    def __init__(self, host: str = "localhost", port: int = 5432, 
                 database: str = "symphony", user: str = "postgres", 
                 password: str = ""):
        if not POSTGRESQL_AVAILABLE:
            raise ImportError("psycopg2 is required for PostgreSQL support, install with: pip install psycopg2-binary")
        
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.conn = None
        self._lock = threading.Lock()
    
    def connect(self) -> bool:
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logger.info(f"Connected to PostgreSQL database: {self.host}:{self.port}/{self.database}")
            return True
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            return False
    
    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("PostgreSQL connection closed")
    
    def init_tables(self) -> bool:
        if not self.conn:
            if not self.connect():
                return False
        
        try:
            with self.conn.cursor() as cur:
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS memories (
                        memory_id VARCHAR(64) PRIMARY KEY,
                        memory_type VARCHAR(32) NOT NULL,
                        content TEXT NOT NULL,
                        session_id VARCHAR(64),
                        user_id VARCHAR(64),
                        is_shared BOOLEAN DEFAULT FALSE,
                        metadata JSONB,
                        created_at DOUBLE PRECISION NOT NULL,
                        updated_at DOUBLE PRECISION NOT NULL,
                        expire_at DOUBLE PRECISION
                    )
                ''')
                
                # 创建索引
                cur.execute('CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)')
                cur.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON memories(session_id)')
                cur.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON memories(user_id)')
                cur.execute('CREATE INDEX IF NOT EXISTS idx_is_shared ON memories(is_shared)')
                cur.execute('CREATE INDEX IF NOT EXISTS idx_expire_at ON memories(expire_at)')
                cur.execute('''
                    CREATE INDEX IF NOT EXISTS idx_content_gin 
                    ON memories USING GIN (to_tsvector('chinese', content))
                ''')
                
                self.conn.commit()
                logger.info("PostgreSQL memory tables initialized")
                return True
        except Exception as e:
            logger.error(f"PostgreSQL init tables failed: {e}")
            return False
    
    def add_memory(self, memory: MemoryItem) -> Optional[str]:
        if not self.conn:
            if not self.connect():
                return None
        
        try:
            memory.memory_id = f"mem_{int(time.time() * 1000)}_{os.urandom(4).hex()}"
            memory_dict = memory.to_dict()
            memory_dict["is_shared"] = bool(memory_dict["is_shared"])
            
            with self._lock:
                with self.conn.cursor() as cur:
                    cur.execute('''
                        INSERT INTO memories (
                            memory_id, memory_type, content, session_id, user_id, 
                            is_shared, metadata, created_at, updated_at, expire_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        memory_dict["memory_id"],
                        memory_dict["memory_type"],
                        memory_dict["content"],
                        memory_dict["session_id"],
                        memory_dict["user_id"],
                        memory_dict["is_shared"],
                        json.dumps(memory.metadata),
                        memory_dict["created_at"],
                        memory_dict["updated_at"],
                        memory_dict["expire_at"]
                    ))
                    self.conn.commit()
            
            logger.info(f"Added memory: {memory.memory_id}, type: {memory.memory_type}")
            return memory.memory_id
        except Exception as e:
            logger.error(f"Add memory failed: {e}")
            return None
    
    def get_memory(self, memory_id: str) -> Optional[MemoryItem]:
        if not self.conn:
            if not self.connect():
                return None
        
        try:
            with self._lock:
                with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute('SELECT * FROM memories WHERE memory_id = %s', (memory_id,))
                    row = cur.fetchone()
                    if row:
                        return MemoryItem.from_dict(dict(row))
            return None
        except Exception as e:
            logger.error(f"Get memory failed: {e}")
            return None
    
    def update_memory(self, memory_id: str, updates: Dict) -> bool:
        if not self.conn:
            if not self.connect():
                return False
        
        try:
            updates["updated_at"] = time.time()
            set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
            values = list(updates.values()) + [memory_id]
            
            with self._lock:
                with self.conn.cursor() as cur:
                    cur.execute(f'UPDATE memories SET {set_clause} WHERE memory_id = %s', values)
                    self.conn.commit()
                    return cur.rowcount > 0
        except Exception as e:
            logger.error(f"Update memory failed: {e}")
            return False
    
    def delete_memory(self, memory_id: str) -> bool:
        if not self.conn:
            if not self.connect():
                return False
        
        try:
            with self._lock:
                with self.conn.cursor() as cur:
                    cur.execute('DELETE FROM memories WHERE memory_id = %s', (memory_id,))
                    self.conn.commit()
                    logger.info(f"Deleted memory: {memory_id}")
                    return cur.rowcount > 0
        except Exception as e:
            logger.error(f"Delete memory failed: {e}")
            return False
    
    def search_memories(self, 
                       query: Optional[str] = None,
                       memory_type: Optional[str] = None,
                       session_id: Optional[str] = None,
                       user_id: Optional[str] = None,
                       include_shared: bool = True,
                       limit: int = 20,
                       offset: int = 0) -> List[MemoryItem]:
        if not self.conn:
            if not self.connect():
                return []
        
        try:
            conditions = []
            params = []
            
            if query:
                conditions.append("to_tsvector('chinese', content) @@ plainto_tsquery('chinese', %s)")
                params.append(query)
            
            if memory_type:
                conditions.append("memory_type = %s")
                params.append(memory_type)
            
            if user_id:
                conditions.append("user_id = %s")
                params.append(user_id)
            
            # 会话过滤
            session_conditions = []
            if session_id:
                session_conditions.append("session_id = %s")
                params.append(session_id)
            if include_shared:
                session_conditions.append("is_shared = TRUE")
            
            if session_conditions:
                conditions.append(f"({ ' OR '.join(session_conditions) })")
            
            # 不过??            conditions.append("(expire_at IS NULL OR expire_at > %s)")
            params.append(time.time())
            
            sql = "SELECT * FROM memories"
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            
            sql += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            with self._lock:
                with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(sql, params)
                    rows = cur.fetchall()
                    return [MemoryItem.from_dict(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Search memories failed: {e}")
            return []
    
    def delete_expired(self) -> int:
        if not self.conn:
            if not self.connect():
                return 0
        
        try:
            with self._lock:
                with self.conn.cursor() as cur:
                    cur.execute('DELETE FROM memories WHERE expire_at <= %s', (time.time(),))
                    self.conn.commit()
                    count = cur.rowcount
                    if count > 0:
                        logger.info(f"Deleted {count} expired memories")
                    return count
        except Exception as e:
            logger.error(f"Delete expired memories failed: {e}")
            return 0

# ==================== 工厂方法 ====================
_memory_db_instance = None
_memory_db_lock = threading.Lock()


def get_memory_db(db_type: str = "sqlite", **kwargs) -> MemoryDB:
    """
    获取记忆数据库实??    :param db_type: 数据库类型，支持 sqlite/postgresql
    :param kwargs: 数据库配置参??    """
    if db_type.lower() == "sqlite":
        db = SQLiteMemoryDB(**kwargs)
    elif db_type.lower() == "postgresql":
        if not POSTGRESQL_AVAILABLE:
            raise ImportError("PostgreSQL support requires psycopg2 package, install with: pip install psycopg2-binary")
        db = PostgreSQLMemoryDB(**kwargs)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
    
    # 自动初始化表
    db.connect()
    db.init_tables()
    return db


def get_memory_db_singleton(db_type: str = "sqlite", **kwargs) -> MemoryDB:
    """
    获取记忆数据库单??    :param db_type: 数据库类??    :param kwargs: 数据库配置参??    """
    global _memory_db_instance
    if _memory_db_instance is None:
        with _memory_db_lock:
            if _memory_db_instance is None:
                _memory_db_instance = get_memory_db(db_type, **kwargs)
    return _memory_db_instance


# ==================== 全局实例 ====================
# 默认使用SQLite单例
memory_db = get_memory_db_singleton()

# 导出接口
__all__ = [
    "MemoryItem", 
    "MemoryDB", 
    "SQLiteMemoryDB", 
    "PostgreSQLMemoryDB", 
    "get_memory_db", 
    "get_memory_db_singleton", 
    "memory_db", 
    "MEMORY_TYPES"
]

