#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务队列系统 - Task Queue System
基于 MiniMax-M2.5 的设计
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Callable
from datetime import datetime
import asyncio
import uuid


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


@dataclass
class Task:
    task_id: str
    name: str
    description: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


class TaskQueue:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.tasks: dict[str, Task] = {}
        self.pending_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.running_tasks: set = set()
        self.lock = asyncio.Lock()
    
    async def submit(
        self,
        name: str,
        func: Callable,
        *args,
        description: str = "",
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task = Task(
            task_id=task_id,
            name=name,
            description=description,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            max_retries=max_retries
        )
        self.tasks[task_id] = task
        await self.pending_queue.put((priority.value, task_id))
        return task_id
    
    async def execute_task(self, task: Task) -> Any:
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        try:
            if asyncio.iscoroutinefunction(task.func):
                result = await task.func(*task.args, **task.kwargs)
            else:
                result = task.func(*task.args, **task.kwargs)
            
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now()
            return result
            
        except Exception as e:
            task.retry_count += 1
            if task.retry_count < task.max_retries:
                task.status = TaskStatus.PENDING
                await self.pending_queue.put((task.priority.value, task.task_id))
            else:
                task.status = TaskStatus.FAILED
                task.error = str(e)
            raise
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        if task_id in self.tasks:
            return self.tasks[task_id].status
        return None
    
    def get_queue_stats(self) -> dict:
        return {
            "total": len(self.tasks),
            "pending": sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING),
            "running": sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING),
            "completed": sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED),
            "failed": sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
        }


# 示例函数
async def example_task(name: str, delay: float = 1.0):
    await asyncio.sleep(delay)
    return f"Task {name} completed!"


async def main():
    queue = TaskQueue(max_workers=4)
    
    # 提交任务
    task1 = await queue.submit(
        "数据处理",
        example_task,
        "data_processing",
        description="处理用户数据",
        priority=TaskPriority.HIGH
    )
    
    task2 = await queue.submit(
        "发送通知",
        example_task,
        "send_notification",
        description="发送邮件通知",
        priority=TaskPriority.NORMAL
    )
    
    # 查询状态
    stats = queue.get_queue_stats()
    print(f"队列状态: {stats}")
    print(f"任务1状态: {queue.get_task_status(task1)}")
    print(f"任务2状态: {queue.get_task_status(task2)}")


if __name__ == "__main__":
    asyncio.run(main())
