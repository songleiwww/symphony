#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理器 - 统一任务生命周期管理
"""
import uuid
import time
from enum import Enum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"           # 等待调度
    SCHEDULED = "scheduled"       # 已调度
    RUNNING = "running"           # 执行中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 失败
    CANCELLED = "cancelled"       # 已取消

@dataclass
class Task:
    """任务数据类"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    task_type: str = "通用任务"
    priority: int = 3  # 1最高，5最低
    status: TaskStatus = TaskStatus.PENDING
    created_by: str = "system"
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    assigned_roles: List[str] = field(default_factory=list)
    results: List[Dict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    parent_task_id: Optional[str] = None
    subtasks: List[str] = field(default_factory=list)
    features: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "content": self.content,
            "task_type": self.task_type,
            "priority": self.priority,
            "status": self.status.value,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "assigned_roles": self.assigned_roles,
            "results": self.results,
            "errors": self.errors,
            "parent_task_id": self.parent_task_id,
            "subtasks": self.subtasks,
            "features": self.features,
            "metadata": self.metadata,
            "duration": self.completed_at - self.started_at if self.completed_at and self.started_at else None
        }

class TaskManager:
    """任务管理器"""
    def __init__(self, db_path: str = None):
        if db_path is None:
            import os
            self.db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "data", 
                "symphony.db"
            )
        else:
            self.db_path = db_path
            
        self._init_task_tables()
    
    def _init_task_tables(self):
        """初始化任务相关数据表"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 任务表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS 任务表 (
            task_id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            task_type TEXT DEFAULT '通用任务',
            priority INTEGER DEFAULT 3,
            status TEXT DEFAULT 'pending',
            created_by TEXT DEFAULT 'system',
            created_at REAL NOT NULL,
            started_at REAL,
            completed_at REAL,
            parent_task_id TEXT,
            features TEXT,
            metadata TEXT,
            FOREIGN KEY (parent_task_id) REFERENCES 任务表(task_id)
        )
        ''')
        
        # 任务结果表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS 任务结果表 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            role_id TEXT NOT NULL,
            result_content TEXT,
            token_usage INTEGER DEFAULT 0,
            duration REAL DEFAULT 0,
            success INTEGER DEFAULT 1,
            created_at REAL NOT NULL,
            FOREIGN KEY (task_id) REFERENCES 任务表(task_id)
        )
        ''')
        
        # 任务错误表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS 任务错误表 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            error_message TEXT NOT NULL,
            error_type TEXT,
            created_at REAL NOT NULL,
            FOREIGN KEY (task_id) REFERENCES 任务表(task_id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_task(self, content: str, task_type: str = "通用任务", priority: int = 3, 
                   created_by: str = "system", parent_task_id: str = None, **kwargs) -> Task:
        """创建新任务"""
        task = Task(
            content=content,
            task_type=task_type,
            priority=priority,
            created_by=created_by,
            parent_task_id=parent_task_id,
            metadata=kwargs
        )
        
        # 保存到数据库
        import sqlite3
        import json
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO 任务表 (
            task_id, content, task_type, priority, status, created_by, 
            created_at, parent_task_id, features, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.task_id, task.content, task.task_type, task.priority, 
            task.status.value, task.created_by, task.created_at, 
            task.parent_task_id, json.dumps(task.features), json.dumps(task.metadata)
        ))
        
        conn.commit()
        conn.close()
        
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务信息"""
        import sqlite3
        import json
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM 任务表 WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        # 获取列名
        cursor.execute("PRAGMA table_info(任务表)")
        columns = [col[1] for col in cursor.fetchall()]
        task_dict = dict(zip(columns, row))
        
        # 获取任务结果
        cursor.execute("SELECT * FROM 任务结果表 WHERE task_id = ? ORDER BY created_at", (task_id,))
        result_rows = cursor.fetchall()
        cursor.execute("PRAGMA table_info(任务结果表)")
        result_columns = [col[1] for col in cursor.fetchall()]
        results = [dict(zip(result_columns, r)) for r in result_rows]
        
        # 获取任务错误
        cursor.execute("SELECT * FROM 任务错误表 WHERE task_id = ? ORDER BY created_at", (task_id,))
        error_rows = cursor.fetchall()
        cursor.execute("PRAGMA table_info(任务错误表)")
        error_columns = [col[1] for col in cursor.fetchall()]
        errors = [dict(zip(error_columns, e)) for e in error_rows]
        
        conn.close()
        
        # 构建Task对象
        task = Task(
            task_id=task_dict["task_id"],
            content=task_dict["content"],
            task_type=task_dict["task_type"],
            priority=task_dict["priority"],
            status=TaskStatus(task_dict["status"]),
            created_by=task_dict["created_by"],
            created_at=task_dict["created_at"],
            started_at=task_dict["started_at"],
            completed_at=task_dict["completed_at"],
            parent_task_id=task_dict["parent_task_id"],
            features=json.loads(task_dict["features"]) if task_dict["features"] else {},
            metadata=json.loads(task_dict["metadata"]) if task_dict["metadata"] else {}
        )
        
        task.results = results
        task.errors = [e["error_message"] for e in errors]
        
        return task
    
    def update_task_status(self, task_id: str, status: TaskStatus, **kwargs) -> bool:
        """更新任务状态"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        update_fields = ["status = ?"]
        params = [status.value]
        
        if status == TaskStatus.RUNNING and "started_at" not in kwargs:
            kwargs["started_at"] = time.time()
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED] and "completed_at" not in kwargs:
            kwargs["completed_at"] = time.time()
        
        for key, value in kwargs.items():
            update_fields.append(f"{key} = ?")
            params.append(value)
        
        params.append(task_id)
        
        try:
            cursor.execute(f'''
            UPDATE 任务表 SET {', '.join(update_fields)} WHERE task_id = ?
            ''', params)
            conn.commit()
            success = cursor.rowcount > 0
        except Exception as e:
            print(f"更新任务状态失败: {e}")
            success = False
        
        conn.close()
        return success
    
    def add_task_result(self, task_id: str, role_id: str, result_content: str, 
                       token_usage: int = 0, duration: float = 0, success: bool = True) -> bool:
        """添加任务结果"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO 任务结果表 (
                task_id, role_id, result_content, token_usage, duration, success, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                task_id, role_id, result_content, token_usage, 
                duration, 1 if success else 0, time.time()
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"添加任务结果失败: {e}")
            return False
        finally:
            conn.close()
    
    def add_task_error(self, task_id: str, error_message: str, error_type: str = "unknown") -> bool:
        """添加任务错误"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO 任务错误表 (
                task_id, error_message, error_type, created_at
            ) VALUES (?, ?, ?, ?)
            ''', (task_id, error_message, error_type, time.time()))
            conn.commit()
            return True
        except Exception as e:
            print(f"添加任务错误失败: {e}")
            return False
        finally:
            conn.close()
    
    def list_tasks(self, status: Optional[TaskStatus] = None, limit: int = 100, offset: int = 0) -> List[Task]:
        """列出任务"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
            SELECT task_id FROM 任务表 WHERE status = ? 
            ORDER BY priority ASC, created_at DESC LIMIT ? OFFSET ?
            ''', (status.value, limit, offset))
        else:
            cursor.execute('''
            SELECT task_id FROM 任务表 
            ORDER BY priority ASC, created_at DESC LIMIT ? OFFSET ?
            ''', (limit, offset))
        
        task_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # 获取完整任务信息
        tasks = []
        for task_id in task_ids:
            task = self.get_task(task_id)
            if task:
                tasks.append(task)
        
        return tasks
    
    def get_pending_tasks(self, limit: int = 10) -> List[Task]:
        """获取待执行任务"""
        return self.list_tasks(status=TaskStatus.PENDING, limit=limit)
    
    def create_subtask(self, parent_task_id: str, content: str, **kwargs) -> Task:
        """创建子任务"""
        subtask = self.create_task(
            content=content,
            parent_task_id=parent_task_id,
            **kwargs
        )
        
        # 更新父任务的子任务列表
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 这里简化处理，实际应该更新父任务的subtasks字段
        # 暂时不实现复杂的子任务管理
        
        conn.close()
        return subtask
    
    def get_task_statistics(self) -> Dict:
        """获取任务统计信息"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 按状态统计
        cursor.execute("SELECT status, COUNT(*) FROM 任务表 GROUP BY status")
        status_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 总任务数
        cursor.execute("SELECT COUNT(*) FROM 任务表")
        total = cursor.fetchone()[0]
        
        # 今日任务数
        today_start = time.mktime(datetime.now().date().timetuple())
        cursor.execute("SELECT COUNT(*) FROM 任务表 WHERE created_at >= ?", (today_start,))
        today_total = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_tasks": total,
            "today_tasks": today_total,
            "status_stats": status_stats,
            "pending": status_stats.get("pending", 0),
            "running": status_stats.get("running", 0),
            "completed": status_stats.get("completed", 0),
            "failed": status_stats.get("failed", 0)
        }

# 单例实例
_task_manager_instance: Optional[TaskManager] = None

def get_task_manager() -> TaskManager:
    """获取任务管理器单例"""
    global _task_manager_instance
    if _task_manager_instance is None:
        _task_manager_instance = TaskManager()
    return _task_manager_instance

if __name__ == "__main__":
    # 测试任务管理器
    task_manager = get_task_manager()
    
    # 创建测试任务
    task = task_manager.create_task(
        content="写一个Python多线程爬虫",
        task_type="代码开发",
        priority=2,
        created_by="test"
    )
    
    print(f"创建任务成功: {task.task_id}")
    
    # 更新任务状态
    task_manager.update_task_status(task.task_id, TaskStatus.RUNNING)
    
    # 添加任务结果
    task_manager.add_task_result(
        task_id=task.task_id,
        role_id="role_001",
        result_content="这是爬虫代码...",
        token_usage=1024,
        duration=5.2
    )
    
    # 更新为完成
    task_manager.update_task_status(task.task_id, TaskStatus.COMPLETED)
    
    # 获取任务信息
    saved_task = task_manager.get_task(task.task_id)
    print(f"\n任务信息: {saved_task.status.value}")
    print(f"结果数量: {len(saved_task.results)}")
    
    # 统计信息
    stats = task_manager.get_task_statistics()
    print(f"\n任务统计: 总任务数 {stats['total_tasks']}, 今日 {stats['today_tasks']}")
