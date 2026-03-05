#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息排队优先级系统 - v1.0.0
Priority Queue System

核心功能：
1. 任务排队
2. 优先级管理（1-5，1最高）
3. FIFO + 优先级混合调度
4. 任务状态跟踪
5. 统计信息
"""

import sys
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# 协议常量
# =============================================================================

PROTOCOL_VERSION = "1.0.0"
PROTOCOL_NAME = "Priority Queue System"


# =============================================================================
# 任务优先级枚举
# =============================================================================

class Priority(Enum):
    """任务优先级（1-5，1最高）"""
    CRITICAL = 1    # 紧急
    HIGH = 2        # 高
    NORMAL = 3      # 普通（默认）
    LOW = 4         # 低
    BACKGROUND = 5  # 后台
    
    @classmethod
    def from_int(cls, value: int) -> 'Priority':
        """从整数创建"""
        for p in cls:
            if p.value == value:
                return p
        return cls.NORMAL


# =============================================================================
# 任务状态枚举
# =============================================================================

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"        # 等待中
    RUNNING = "running"        # 运行中
    COMPLETED = "completed"    # 已完成
    FAILED = "failed"          # 失败
    CANCELLED = "cancelled"    # 已取消


# =============================================================================
# 任务数据结构
# =============================================================================

@dataclass
class QueuedTask:
    """排队任务"""
    task_id: str
    task_description: str
    priority: Priority
    task_type: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: TaskStatus = TaskStatus.PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "task_description": self.task_description,
            "priority": self.priority.value,
            "priority_name": self.priority.name,
            "task_type": self.task_type,
            "created_at": self.created_at,
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result,
            "error": self.error,
            "execution_time": self.execution_time,
            "metadata": self.metadata
        }


# =============================================================================
# 优先级排队系统
# =============================================================================

class PriorityQueueSystem:
    """
    优先级排队系统
    
    调度策略：
    1. 优先级高的先执行
    2. 相同优先级按FIFO（先进先出）
    """
    
    def __init__(self):
        self.queue: List[QueuedTask] = []
        self.history: List[QueuedTask] = []
        self.current_task: Optional[QueuedTask] = None
        self._task_counter: int = 0
    
    def add_task(
        self,
        task_description: str,
        priority: int = 3,
        task_type: str = "general",
        metadata: Optional[Dict] = None
    ) -> QueuedTask:
        """
        添加任务到队列
        
        参数：
        - task_description: 任务描述
        - priority: 优先级（1-5，1最高，默认3）
        - task_type: 任务类型
        - metadata: 附加元数据
        """
        self._task_counter += 1
        task_id = f"task_{self._task_counter}_{int(time.time())}"
        
        task = QueuedTask(
            task_id=task_id,
            task_description=task_description,
            priority=Priority.from_int(priority),
            task_type=task_type,
            metadata=metadata or {}
        )
        
        self.queue.append(task)
        self._sort_queue()
        
        print(f"[添加任务] {task_id}")
        print(f"  描述: {task_description}")
        print(f"  优先级: {task.priority.name} ({task.priority.value})")
        print(f"  类型: {task_type}")
        
        return task
    
    def _sort_queue(self):
        """排序队列：优先级高的在前，相同优先级按创建时间"""
        self.queue.sort(
            key=lambda t: (t.priority.value, t.created_at)
        )
    
    def get_next_task(self) -> Optional[QueuedTask]:
        """获取下一个要执行的任务"""
        if not self.queue:
            return None
        
        # 取第一个（已排序）
        task = self.queue.pop(0)
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now().isoformat()
        self.current_task = task
        
        print(f"[开始执行] {task.task_id}")
        print(f"  描述: {task.task_description}")
        print(f"  优先级: {task.priority.name}")
        
        return task
    
    def complete_task(self, task_id: str, result: Optional[Dict] = None) -> bool:
        """完成任务"""
        if self.current_task and self.current_task.task_id == task_id:
            task = self.current_task
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            task.result = result
            if task.started_at:
                start = datetime.fromisoformat(task.started_at)
                end = datetime.fromisoformat(task.completed_at)
                task.execution_time = (end - start).total_seconds()
            
            self.history.append(task)
            self.current_task = None
            
            print(f"[完成任务] {task_id}")
            print(f"  耗时: {task.execution_time:.2f}秒")
            
            return True
        return False
    
    def fail_task(self, task_id: str, error: str) -> bool:
        """任务失败"""
        if self.current_task and self.current_task.task_id == task_id:
            task = self.current_task
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now().isoformat()
            task.error = error
            if task.started_at:
                start = datetime.fromisoformat(task.started_at)
                end = datetime.fromisoformat(task.completed_at)
                task.execution_time = (end - start).total_seconds()
            
            self.history.append(task)
            self.current_task = None
            
            print(f"[任务失败] {task_id}")
            print(f"  错误: {error}")
            
            return True
        return False
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        # 检查是否在队列中
        for i, task in enumerate(self.queue):
            if task.task_id == task_id:
                task.status = TaskStatus.CANCELLED
                self.history.append(self.queue.pop(i))
                print(f"[取消任务] {task_id}")
                return True
        
        # 检查是否是当前任务
        if self.current_task and self.current_task.task_id == task_id:
            self.current_task.status = TaskStatus.CANCELLED
            self.current_task.completed_at = datetime.now().isoformat()
            self.history.append(self.current_task)
            self.current_task = None
            print(f"[取消任务] {task_id}")
            return True
        
        return False
    
    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        pending = [t for t in self.queue if t.status == TaskStatus.PENDING]
        pending.sort(key=lambda t: (t.priority.value, t.created_at))
        
        return {
            "queue_length": len(self.queue),
            "pending_count": len(pending),
            "current_task": self.current_task.to_dict() if self.current_task else None,
            "pending_tasks": [t.to_dict() for t in pending[:10]],  # 前10个
            "by_priority": {
                p.name: len([t for t in self.queue if t.priority == p])
                for p in Priority
            }
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.history:
            return {"total": 0}
        
        total = len(self.history)
        completed = sum(1 for t in self.history if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.history if t.status == TaskStatus.FAILED)
        cancelled = sum(1 for t in self.history if t.status == TaskStatus.CANCELLED)
        
        avg_time = 0.0
        completed_tasks = [t for t in self.history if t.status == TaskStatus.COMPLETED]
        if completed_tasks:
            avg_time = sum(t.execution_time for t in completed_tasks) / len(completed_tasks)
        
        by_priority = {}
        for p in Priority:
            p_tasks = [t for t in self.history if t.priority == p]
            if p_tasks:
                p_completed = sum(1 for t in p_tasks if t.status == TaskStatus.COMPLETED)
                by_priority[p.name] = {
                    "total": len(p_tasks),
                    "completed": p_completed,
                    "success_rate": p_completed / len(p_tasks)
                }
        
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "cancelled": cancelled,
            "success_rate": completed / total if total > 0 else 0,
            "average_execution_time": avg_time,
            "by_priority": by_priority,
            "queue_length": len(self.queue)
        }
    
    def list_all_tasks(self, limit: int = 20) -> List[Dict]:
        """列出所有任务（最近的）"""
        all_tasks = self.history + self.queue
        if self.current_task:
            all_tasks.append(self.current_task)
        
        all_tasks.sort(key=lambda t: t.created_at, reverse=True)
        return [t.to_dict() for t in all_tasks[:limit]]


# =============================================================================
# 使用示例
# =============================================================================

def main():
    """主程序"""
    print("=" * 80)
    print("Priority Queue System v1.0.0")
    print("=" * 80)
    
    # 修复Windows编码
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    # 创建排队系统
    queue_system = PriorityQueueSystem()
    print(f"\n✅ 排队系统已启动")
    
    # 1. 添加任务（不同优先级）
    print("\n[1] 添加任务（不同优先级）")
    
    queue_system.add_task(
        task_description="紧急：修复生产环境bug",
        priority=1,  # 紧急
        task_type="debug"
    )
    
    queue_system.add_task(
        task_description="高优先级：开发新功能",
        priority=2,  # 高
        task_type="coding"
    )
    
    queue_system.add_task(
        task_description="普通：写文档",
        priority=3,  # 普通
        task_type="writing"
    )
    
    queue_system.add_task(
        task_description="低优先级：清理日志",
        priority=4,  # 低
        task_type="maintenance"
    )
    
    queue_system.add_task(
        task_description="后台：数据备份",
        priority=5,  # 后台
        task_type="backup"
    )
    
    # 2. 查看队列状态
    print("\n[2] 队列状态")
    status = queue_system.get_queue_status()
    print(f"  队列长度: {status['queue_length']}")
    print(f"  按优先级:")
    for p_name, count in status['by_priority'].items():
        if count > 0:
            print(f"    {p_name}: {count}个")
    
    # 3. 执行任务（按优先级）
    print("\n[3] 执行任务（按优先级）")
    
    def mock_execute(task: QueuedTask) -> tuple[bool, Dict, str]:
        """模拟执行"""
        time.sleep(0.5)  # 模拟耗时
        if task.priority == Priority.CRITICAL:
            return (True, {"fixed": True}, None)
        elif task.priority == Priority.HIGH:
            return (True, {"feature": "done"}, None)
        elif task.priority == Priority.NORMAL:
            return (True, {"doc": "written"}, None)
        elif task.priority == Priority.LOW:
            return (True, {"cleaned": True}, None)
        else:
            return (True, {"backup": "done"}, None)
    
    while True:
        task = queue_system.get_next_task()
        if not task:
            break
        
        success, result, error = mock_execute(task)
        
        if success:
            queue_system.complete_task(task.task_id, result)
        else:
            queue_system.fail_task(task.task_id, error)
    
    # 4. 统计信息
    print("\n[4] 统计信息")
    stats = queue_system.get_statistics()
    print(f"  总任务: {stats['total']}")
    print(f"  已完成: {stats['completed']}")
    print(f"  失败: {stats['failed']}")
    print(f"  成功率: {stats['success_rate']:.0%}")
    print(f"  平均耗时: {stats['average_execution_time']:.2f}秒")
    
    print("\n" + "=" * 80)
    print("✅ 优先级排队系统演示完成！")
    print("=" * 80)
    print("\n调度策略:")
    print("  1. 优先级高的先执行")
    print("  2. 相同优先级按FIFO（先进先出）")
    print("  3. 完整的状态跟踪和统计")


if __name__ == "__main__":
    main()
