#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony Async Task Queue - 交响异步任务队列
Priority-based task queue with asyncio - 基于优先级的asyncio任务队列
"""

import sys
import os
import asyncio
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from queue import PriorityQueue

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TaskPriority(Enum):
    """Task priority - 任务优先级"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class TaskStatus(Enum):
    """Task status - 任务状态"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(order=True)
class QueuedTask:
    """Queued task - 队列中的任务"""
    priority: int
    created_at: float = field(compare=False)
    task_id: str = field(compare=False)
    name: str = field(compare=False)
    func: Callable = field(compare=False, repr=False)
    args: tuple = field(compare=False)
    kwargs: Dict[str, Any] = field(compare=False)
    retries: int = field(compare=False, default=0)
    max_retries: int = field(compare=False, default=3)


@dataclass
class TaskResult:
    """Task result - 任务结果"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: str = None
    start_time: float = None
    end_time: float = None
    execution_time: float = None
    retries: int = 0


class AsyncTaskQueue:
    """异步任务队列"""
    
    def __init__(self):
        self.queue: PriorityQueue = PriorityQueue()
        self.results: Dict[str, TaskResult] = {}
        self._task_counter = 0
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None
        self._queue_lock = asyncio.Lock()
    
    def create_task(self, name: str, func: Callable, args: tuple = None, 
                   kwargs: Dict[str, Any] = None, 
                   priority: TaskPriority = TaskPriority.NORMAL,
                   max_retries: int = 3) -> str:
        """Create a task - 创建一个任务"""
        self._task_counter += 1
        task_id = f"task_{self._task_counter}"
        
        queued_task = QueuedTask(
            priority=priority.value,
            created_at=time.time(),
            task_id=task_id,
            name=name,
            func=func,
            args=args or (),
            kwargs=kwargs or {},
            retries=0,
            max_retries=max_retries
        )
        
        self.queue.put(queued_task)
        
        self.results[task_id] = TaskResult(
            task_id=task_id,
            status=TaskStatus.QUEUED
        )
        
        return task_id
    
    async def _worker(self):
        """Worker coroutine - 工作协程"""
        while self._running:
            try:
                # Try to get a task (non-blocking check first)
                if self.queue.empty():
                    await asyncio.sleep(0.1)
                    continue
                
                async with self._queue_lock:
                    if self.queue.empty():
                        continue
                    queued_task = self.queue.get()
                
                # Execute task
                result = self.results[queued_task.task_id]
                result.status = TaskStatus.RUNNING
                result.start_time = time.time()
                
                try:
                    # Run the task (in thread pool for sync functions)
                    if asyncio.iscoroutinefunction(queued_task.func):
                        # Async function
                        task_result = await queued_task.func(*queued_task.args, **queued_task.kwargs)
                    else:
                        # Sync function - run in executor
                        loop = asyncio.get_event_loop()
                        task_result = await loop.run_in_executor(
                            None, 
                            lambda: queued_task.func(*queued_task.args, **queued_task.kwargs)
                        )
                    
                    result.result = task_result
                    result.status = TaskStatus.COMPLETED
                    
                except Exception as e:
                    result.error = str(e)
                    result.retries = queued_task.retries + 1
                    
                    if result.retries < queued_task.max_retries:
                        # Retry
                        queued_task.retries += 1
                        self.queue.put(queued_task)
                        result.status = TaskStatus.QUEUED
                    else:
                        # Max retries exceeded
                        result.status = TaskStatus.FAILED
                
                result.end_time = time.time()
                if result.start_time:
                    result.execution_time = result.end_time - result.start_time
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Worker error: {e}")
                await asyncio.sleep(0.1)
    
    async def start(self):
        """Start worker - 启动工作协程"""
        if self._running:
            return
        self._running = True
        self._worker_task = asyncio.create_task(self._worker())
    
    async def stop(self):
        """Stop worker - 停止工作协程"""
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
    
    async def wait_for_task(self, task_id: str, timeout: float = 30.0) -> TaskResult:
        """Wait for a task to complete - 等待任务完成"""
        start = time.time()
        while time.time() - start < timeout:
            result = self.results.get(task_id)
            if result and result.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
                return result
            await asyncio.sleep(0.1)
        raise TimeoutError(f"Task {task_id} timed out")
    
    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """Get task result - 获取任务结果"""
        return self.results.get(task_id)
    
    def get_queue_size(self) -> int:
        """Get queue size - 获取队列大小"""
        return self.queue.qsize()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue stats - 获取队列统计"""
        status_counts: Dict[str, int] = {}
        for result in self.results.values():
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "queue_size": self.get_queue_size(),
            "total_tasks": len(self.results),
            "status_counts": status_counts,
            "running": self._running
        }


def create_async_task_queue() -> AsyncTaskQueue:
    """Create async task queue - 创建异步任务队列"""
    return AsyncTaskQueue()


if __name__ == "__main__":
    print("Symphony Async Task Queue")
    print("交响异步任务队列")
    print("=" * 60)
    
    async def test_async():
        queue = create_async_task_queue()
        
        # Test 1: Create tasks
        print("\n[Test 1] Create tasks...")
        
        def sync_task(x):
            time.sleep(0.1)
            return x * 2
        
        async def async_task(x):
            await asyncio.sleep(0.1)
            return x * 3
        
        task_id1 = queue.create_task("Sync Task", sync_task, args=(21,), priority=TaskPriority.NORMAL)
        task_id2 = queue.create_task("Async Task", async_task, args=(14,), priority=TaskPriority.HIGH)
        
        print(f"  Task 1: {task_id1}")
        print(f"  Task 2: {task_id2}")
        print(f"  OK: Tasks created")
        
        # Test 2: Start worker
        print("\n[Test 2] Start worker...")
        await queue.start()
        print(f"  OK: Worker started")
        
        # Test 3: Wait for results
        print("\n[Test 3] Wait for results...")
        result1 = await queue.wait_for_task(task_id1, timeout=5.0)
        result2 = await queue.wait_for_task(task_id2, timeout=5.0)
        
        print(f"  Result 1: {result1.result}, status: {result1.status}")
        print(f"  Result 2: {result2.result}, status: {result2.status}")
        print(f"  OK: Results retrieved")
        
        # Test 4: Stop worker
        print("\n[Test 4] Stop worker...")
        await queue.stop()
        print(f"  OK: Worker stopped")
        
        # Test 5: Get stats
        print("\n[Test 5] Get stats...")
        stats = queue.get_stats()
        print(f"  Stats: {stats}")
        print(f"  OK: Stats retrieved")
    
    # Run tests
    asyncio.run(test_async())
    
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)
