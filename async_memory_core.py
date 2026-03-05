#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony Async Memory Core - 交响异步记忆核心
Improved memory system + safe async/parallel execution
改善的记忆系统 + 安全的异步/并行执行
"""

import sys
import os
import time
import asyncio
import threading
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json
from enum import Enum


class ExecutionMode(Enum):
    """Execution mode - 执行模式"""
    SEQUENTIAL = "sequential"  # 顺序执行（安全）
    PARALLEL_SAFE = "parallel_safe"  # 并行安全（无依赖）
    PARALLEL_DEPENDENT = "parallel_dependent"  # 并行有依赖（禁用）


class SafetyLevel(Enum):
    """Safety level - 安全级别"""
    SAFE = "safe"  # 完全安全
    CAUTION = "caution"  # 需要注意
    RISKY = "risky"  # 有风险，禁用
    FORBIDDEN = "forbidden"  # 绝对禁止


@dataclass
class Task:
    """Async task - 异步任务"""
    task_id: str
    name: str
    func: Callable
    args: tuple = ()
    kwargs: dict = None
    depends_on: List[str] = None  # 依赖的任务ID
    model: str = None
    provider: str = None
    safety_level: SafetyLevel = SafetyLevel.SAFE
    rate_limit_key: str = None  # 限流键（如模型名）
    
    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}
        if self.depends_on is None:
            self.depends_on = []


@dataclass
class TaskResult:
    """Task result - 任务结果"""
    task_id: str
    success: bool
    result: Any = None
    error: str = None
    start_time: float = None
    end_time: float = None
    execution_time: float = None


class RateLimiter:
    """Rate limiter - 限流器"""
    
    def __init__(self, max_concurrent: int = 3, time_window: float = 1.0):
        self.max_concurrent = max_concurrent  # 最大并发数
        self.time_window = time_window  # 时间窗口（秒）
        self.active: Dict[str, int] = {}  # 每个键的活跃数
        self.history: Dict[str, List[float]] = {}  # 每个键的历史时间
        self._lock = threading.Lock()
    
    def acquire(self, key: str) -> bool:
        """Acquire a slot - 获取一个槽位"""
        with self._lock:
            now = time.time()
            
            # Clean old history
            if key in self.history:
                self.history[key] = [t for t in self.history[key] if now - t < self.time_window]
            
            # Check concurrent
            current_active = self.active.get(key, 0)
            if current_active >= self.max_concurrent:
                return False
            
            # Check rate
            recent_calls = len(self.history.get(key, []))
            if recent_calls >= self.max_concurrent:
                return False
            
            # Acquire
            self.active[key] = current_active + 1
            if key not in self.history:
                self.history[key] = []
            self.history[key].append(now)
            return True
    
    def release(self, key: str):
        """Release a slot - 释放一个槽位"""
        with self._lock:
            if key in self.active:
                self.active[key] = max(0, self.active[key] - 1)


class ImprovedMemoryItem:
    """Improved memory item - 改善的记忆项"""
    def __init__(self, id: str, content: str, memory_type: str, 
                 importance: float, tags: List[str], category: str):
        self.id = id
        self.content = content
        self.memory_type = memory_type
        self.importance = importance
        self.tags = tags
        self.category = category
        self.created_at = datetime.now().isoformat()
        self.access_count = 0
        self.last_accessed: Optional[str] = None
        self.version = 1


class ImprovedSymphonyCore:
    """Improved Symphony Core with safe async/parallel execution"""
    
    def __init__(self, memory_path: str = "symphony_memory_v2.json"):
        self.memory_path = Path(memory_path)
        self.memories: Dict[str, ImprovedMemoryItem] = {}
        self.preferences: Dict[str, Any] = {}
        self.session_start = datetime.now().isoformat()
        
        # Async/parallel safety
        self.rate_limiter = RateLimiter(max_concurrent=3, time_window=1.0)
        self._execution_lock = threading.Lock()
        self._task_counter = 0
        
        # Load memory
        self._load_memory()
        
        # Record session start
        self.add_memory(
            f"Improved Symphony session started at {self.session_start}",
            "short_term",
            0.5,
            ["session", "startup", "v2"],
            "system"
        )
    
    def _load_memory(self):
        """Load memory from file - 从文件加载记忆"""
        if self.memory_path.exists():
            try:
                data = json.loads(self.memory_path.read_text(encoding='utf-8'))
                for mem_data in data.get("memories", []):
                    mem = ImprovedMemoryItem(
                        id=mem_data["id"],
                        content=mem_data["content"],
                        memory_type=mem_data["memory_type"],
                        importance=mem_data["importance"],
                        tags=mem_data.get("tags", []),
                        category=mem_data.get("category", "general")
                    )
                    mem.access_count = mem_data.get("access_count", 0)
                    mem.last_accessed = mem_data.get("last_accessed")
                    mem.version = mem_data.get("version", 1)
                    self.memories[mem.id] = mem
                self.preferences = data.get("preferences", {})
            except Exception as e:
                print(f"Warning: Could not load memory: {e}")
    
    def _save_memory(self):
        """Save memory to file - 保存记忆到文件"""
        data = {
            "version": "2.0",
            "saved_at": datetime.now().isoformat(),
            "preferences": self.preferences,
            "memories": [
                {
                    "id": m.id,
                    "content": m.content,
                    "memory_type": m.memory_type,
                    "importance": m.importance,
                    "tags": m.tags,
                    "category": m.category,
                    "created_at": m.created_at,
                    "access_count": m.access_count,
                    "last_accessed": m.last_accessed,
                    "version": m.version
                }
                for m in self.memories.values()
            ]
        }
        self.memory_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def add_memory(self, content: str, memory_type: str, importance: float, 
                   tags: List[str], category: str) -> str:
        """Add a new memory (thread-safe) - 添加新记忆（线程安全）"""
        with self._execution_lock:
            memory_id = f"mem_v2_{len(self.memories) + 1}_{int(datetime.now().timestamp())}"
            mem = ImprovedMemoryItem(
                id=memory_id,
                content=content,
                memory_type=memory_type,
                importance=importance,
                tags=tags,
                category=category
            )
            self.memories[memory_id] = mem
            self._save_memory()
            return memory_id
    
    def get_memory(self, memory_id: str) -> Optional[ImprovedMemoryItem]:
        """Get a memory by ID (thread-safe) - 获取记忆（线程安全）"""
        with self._execution_lock:
            if memory_id in self.memories:
                mem = self.memories[memory_id]
                mem.access_count += 1
                mem.last_accessed = datetime.now().isoformat()
                self._save_memory()
                return mem
        return None
    
    def set_preference(self, key: str, value: Any):
        """Set a preference (thread-safe) - 设置偏好（线程安全）"""
        with self._execution_lock:
            self.preferences[key] = value
            self._save_memory()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a preference (thread-safe) - 获取偏好（线程安全）"""
        with self._execution_lock:
            return self.preferences.get(key, default)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics - 获取记忆统计"""
        with self._execution_lock:
            return {
                "total_memories": len(self.memories),
                "long_term": len([m for m in self.memories.values() if m.memory_type == "long_term"]),
                "short_term": len([m for m in self.memories.values() if m.memory_type == "short_term"]),
                "total_preferences": len(self.preferences),
                "session_start": self.session_start,
                "version": "2.0"
            }
    
    def analyze_task_safety(self, tasks: List[Task]) -> tuple[ExecutionMode, List[str]]:
        """
        Analyze if tasks can be safely executed in parallel
        分析任务是否可以安全并行执行
        
        Returns: (mode, warnings)
        """
        warnings = []
        
        # Check for dependencies
        has_dependencies = any(len(t.depends_on) > 0 for t in tasks)
        if has_dependencies:
            warnings.append("Tasks have dependencies - sequential execution required")
            return ExecutionMode.SEQUENTIAL, warnings
        
        # Check for shared rate limit keys
        rate_keys: Dict[str, List[Task]] = {}
        for task in tasks:
            key = task.rate_limit_key or "default"
            if key not in rate_keys:
                rate_keys[key] = []
            rate_keys[key].append(task)
        
        # Check if any rate limit key has too many tasks
        for key, key_tasks in rate_keys.items():
            if len(key_tasks) > 3:
                warnings.append(f"Rate limit key '{key}' has {len(key_tasks)} tasks - throttling required")
        
        # Check safety levels
        has_risky = any(t.safety_level in (SafetyLevel.RISKY, SafetyLevel.FORBIDDEN) for t in tasks)
        if has_risky:
            warnings.append("Some tasks are risky/forbidden - sequential execution only")
            return ExecutionMode.SEQUENTIAL, warnings
        
        # If we get here, parallel is safe (but we'll still respect rate limits)
        if warnings:
            return ExecutionMode.PARALLEL_SAFE, warnings
        return ExecutionMode.PARALLEL_SAFE, warnings
    
    async def execute_task_safe(self, task: Task) -> TaskResult:
        """
        Execute a single task safely (with rate limiting)
        安全执行单个任务（带限流）
        """
        result = TaskResult(task_id=task.task_id, success=False)
        result.start_time = time.time()
        
        # Acquire rate limit slot
        rate_key = task.rate_limit_key or "default"
        acquired = False
        max_wait = 5.0
        wait_start = time.time()
        
        while not acquired and (time.time() - wait_start) < max_wait:
            if self.rate_limiter.acquire(rate_key):
                acquired = True
                break
            await asyncio.sleep(0.1)
        
        if not acquired:
            result.error = f"Rate limit exceeded for '{rate_key}'"
            result.end_time = time.time()
            result.execution_time = result.end_time - result.start_time
            return result
        
        try:
            # Execute task
            result.result = task.func(*task.args, **task.kwargs)
            result.success = True
        except Exception as e:
            result.error = str(e)
        finally:
            # Release rate limit slot
            self.rate_limiter.release(rate_key)
        
        result.end_time = time.time()
        result.execution_time = result.end_time - result.start_time
        return result
    
    async def execute_tasks(self, tasks: List[Task]) -> Dict[str, TaskResult]:
        """
        Execute tasks with intelligent safety - 智能安全执行任务
        
        Auto-detects if parallel is safe, falls back to sequential
        自动检测并行是否安全，否则回退到顺序
        """
        results: Dict[str, TaskResult] = {}
        
        # Analyze safety
        mode, warnings = self.analyze_task_safety(tasks)
        
        if warnings:
            print(f"⚠️ Warnings: {warnings}")
        
        if mode == ExecutionMode.SEQUENTIAL:
            print("🔒 Sequential execution (safety first)")
            for task in tasks:
                result = await self.execute_task_safe(task)
                results[task.task_id] = result
        else:
            print("⚡ Parallel execution (safe)")
            # Still respect rate limits via per-task acquire/release
            task_coroutines = [self.execute_task_safe(task) for task in tasks]
            task_results = await asyncio.gather(*task_coroutines)
            for result in task_results:
                results[result.task_id] = result
        
        return results
    
    def run_tasks_sync(self, tasks: List[Task]) -> Dict[str, TaskResult]:
        """Synchronous wrapper for async execute - 同步包装器"""
        return asyncio.run(self.execute_tasks(tasks))
    
    def create_task(self, name: str, func: Callable, args: tuple = None, 
                   kwargs: dict = None, depends_on: List[str] = None,
                   model: str = None, provider: str = None,
                   safety_level: SafetyLevel = SafetyLevel.SAFE,
                   rate_limit_key: str = None) -> Task:
        """Create a task - 创建一个任务"""
        with self._execution_lock:
            self._task_counter += 1
            task_id = f"task_{self._task_counter}"
        
        return Task(
            task_id=task_id,
            name=name,
            func=func,
            args=args or (),
            kwargs=kwargs or {},
            depends_on=depends_on or [],
            model=model,
            provider=provider,
            safety_level=safety_level,
            rate_limit_key=rate_limit_key
        )


# Convenience function
def create_improved_core(memory_path: str = "symphony_memory_v2.json") -> ImprovedSymphonyCore:
    """Create improved Symphony core - 创建改善的交响核心"""
    return ImprovedSymphonyCore(memory_path)


if __name__ == "__main__":
    print("Symphony Async Memory Core v2.0")
    print("交响异步记忆核心 v2.0")
    print("=" * 60)
    
    core = create_improved_core()
    
    # Add some test memories
    core.add_memory(
        "Improved memory system v2.0 with thread safety",
        "long_term",
        0.9,
        ["memory", "v2", "thread-safe"],
        "system"
    )
    
    core.add_memory(
        "Safe async/parallel execution with rate limiting",
        "long_term",
        0.9,
        ["async", "parallel", "safety", "rate-limit"],
        "system"
    )
    
    # Show stats
    stats = core.get_stats()
    print(f"\nStats:")
    print(f"  Total memories: {stats['total_memories']}")
    print(f"  Version: {stats['version']}")
    
    print("\n✅ Improved Symphony Core v2.0 created!")
    print("=" * 60)
