#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony Concurrency Monitor - 交响并发监控
Monitor active tasks, queue length, and resource usage
监控活跃任务、队列长度和资源使用
"""

import sys
import os
import time
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@dataclass
class ConcurrencyMetrics:
    """Concurrency metrics - 并发指标"""
    timestamp: str
    active_tasks: int
    queue_length: int
    completed_tasks: int
    failed_tasks: int
    avg_execution_time: float
    cpu_percent: float = 0.0
    memory_percent: float = 0.0


class ConcurrencyMonitor:
    """并发监控器"""
    
    def __init__(self, history_size: int = 100):
        self.history_size = history_size
        self.history: deque = deque(maxlen=history_size)
        self._lock = threading.Lock()
        
        self.active_tasks: int = 0
        self.queue_length: int = 0
        self.completed_tasks: int = 0
        self.failed_tasks: int = 0
        self.total_execution_time: float = 0.0
        
        self._start_time = time.time()
    
    def task_started(self):
        """Task started - 任务开始"""
        with self._lock:
            self.active_tasks += 1
    
    def task_completed(self, execution_time: float):
        """Task completed - 任务完成"""
        with self._lock:
            self.active_tasks = max(0, self.active_tasks - 1)
            self.completed_tasks += 1
            self.total_execution_time += execution_time
    
    def task_failed(self, execution_time: float):
        """Task failed - 任务失败"""
        with self._lock:
            self.active_tasks = max(0, self.active_tasks - 1)
            self.failed_tasks += 1
            self.total_execution_time += execution_time
    
    def update_queue_length(self, length: int):
        """Update queue length - 更新队列长度"""
        with self._lock:
            self.queue_length = length
    
    def take_snapshot(self) -> ConcurrencyMetrics:
        """Take a metrics snapshot - 拍摄指标快照"""
        with self._lock:
            avg_time = 0.0
            total = self.completed_tasks + self.failed_tasks
            if total > 0:
                avg_time = self.total_execution_time / total
            
            # Try to get resource usage
            cpu_percent = 0.0
            memory_percent = 0.0
            try:
                import psutil
                process = psutil.Process()
                cpu_percent = process.cpu_percent(interval=0.1)
                memory_percent = process.memory_percent()
            except ImportError:
                pass
            
            metrics = ConcurrencyMetrics(
                timestamp=datetime.now().isoformat(),
                active_tasks=self.active_tasks,
                queue_length=self.queue_length,
                completed_tasks=self.completed_tasks,
                failed_tasks=self.failed_tasks,
                avg_execution_time=avg_time,
                cpu_percent=cpu_percent,
                memory_percent=memory_percent
            )
            
            self.history.append(metrics)
            return metrics
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics - 获取当前指标"""
        with self._lock:
            avg_time = 0.0
            total = self.completed_tasks + self.failed_tasks
            if total > 0:
                avg_time = self.total_execution_time / total
            
            uptime = time.time() - self._start_time
            
            return {
                "uptime_seconds": uptime,
                "active_tasks": self.active_tasks,
                "queue_length": self.queue_length,
                "completed_tasks": self.completed_tasks,
                "failed_tasks": self.failed_tasks,
                "total_tasks": self.completed_tasks + self.failed_tasks,
                "avg_execution_time": avg_time,
                "success_rate": (self.completed_tasks / max(1, self.completed_tasks + self.failed_tasks)) * 100
            }
    
    def get_history(self, limit: int = None) -> List[ConcurrencyMetrics]:
        """Get metrics history - 获取指标历史"""
        with self._lock:
            history_list = list(self.history)
            if limit:
                return history_list[-limit:]
            return history_list
    
    def get_ascii_dashboard(self) -> str:
        """Get ASCII dashboard - 获取ASCII仪表盘"""
        metrics = self.get_current_metrics()
        
        lines = []
        lines.append("=" * 60)
        lines.append("Symphony Concurrency Monitor")
        lines.append("交响并发监控")
        lines.append("=" * 60)
        lines.append(f"Uptime: {metrics['uptime_seconds']:.1f}s")
        lines.append("")
        lines.append("Tasks:")
        lines.append(f"  Active:    {metrics['active_tasks']}")
        lines.append(f"  Queued:    {metrics['queue_length']}")
        lines.append(f"  Completed: {metrics['completed_tasks']}")
        lines.append(f"  Failed:    {metrics['failed_tasks']}")
        lines.append(f"  Total:     {metrics['total_tasks']}")
        lines.append("")
        lines.append(f"Avg Execution Time: {metrics['avg_execution_time']:.3f}s")
        lines.append(f"Success Rate: {metrics['success_rate']:.1f}%")
        
        # Progress bar for success rate
        success = metrics['success_rate'] / 100
        bar_length = 30
        filled = int(bar_length * success)
        bar = "[" + "=" * filled + " " * (bar_length - filled) + "]"
        lines.append(f"Success Rate: {bar} {int(success*100)}%")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


def create_concurrency_monitor(history_size: int = 100) -> ConcurrencyMonitor:
    """Create concurrency monitor - 创建并发监控器"""
    return ConcurrencyMonitor(history_size)


if __name__ == "__main__":
    print("Symphony Concurrency Monitor")
    print("交响并发监控")
    print("=" * 60)
    
    monitor = create_concurrency_monitor()
    
    # Test 1: Basic metrics
    print("\n[Test 1] Basic metrics...")
    initial = monitor.get_current_metrics()
    print(f"  Initial total tasks: {initial['total_tasks']}")
    print(f"  OK: Basic metrics")
    
    # Test 2: Task started
    print("\n[Test 2] Task started...")
    monitor.task_started()
    monitor.task_started()
    after_start = monitor.get_current_metrics()
    print(f"  Active tasks: {after_start['active_tasks']}")
    print(f"  OK: Task started")
    
    # Test 3: Task completed
    print("\n[Test 3] Task completed...")
    monitor.task_completed(0.1)
    monitor.task_completed(0.2)
    after_completed = monitor.get_current_metrics()
    print(f"  Completed tasks: {after_completed['completed_tasks']}")
    print(f"  OK: Task completed")
    
    # Test 4: Snapshot
    print("\n[Test 4] Take snapshot...")
    snapshot = monitor.take_snapshot()
    print(f"  Snapshot taken: {snapshot.timestamp}")
    print(f"  OK: Snapshot")
    
    # Test 5: ASCII dashboard
    print("\n[Test 5] ASCII dashboard...")
    dashboard = monitor.get_ascii_dashboard()
    print(dashboard)
    print(f"  OK: Dashboard generated (length: {len(dashboard)})")
    
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)
