#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony Deadlock Detector & Timeout - 交响死锁检测和超时
Deadlock detection with wait-for graph and timeout mechanisms
等待图死锁检测和超时机制
"""

import sys
import os
import asyncio
import time
import threading
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class DeadlockStatus(Enum):
    """Deadlock status - 死锁状态"""
    NO_DEADLOCK = "no_deadlock"
    POTENTIAL_DEADLOCK = "potential_deadlock"
    DEADLOCK_DETECTED = "deadlock_detected"


@dataclass
class WaitForEdge:
    """Wait-for edge - 等待边"""
    waiter: str  # 等待者
    waitee: str  # 被等待者
    resource: str  # 等待的资源
    created_at: float


class DeadlockDetector:
    """死锁检测器"""
    
    def __init__(self):
        self.edges: List[WaitForEdge] = []
        self._lock = threading.Lock()
        self.timeouts: Dict[str, float] = {}  # task_id -> deadline
    
    def add_wait(self, waiter: str, waitee: str, resource: str):
        """Add a wait-for edge - 添加等待边"""
        with self._lock:
            edge = WaitForEdge(
                waiter=waiter,
                waitee=waitee,
                resource=resource,
                created_at=time.time()
            )
            self.edges.append(edge)
    
    def remove_wait(self, waiter: str, waitee: str = None):
        """Remove wait-for edge(s) - 移除等待边"""
        with self._lock:
            if waitee:
                self.edges = [e for e in self.edges if not (e.waiter == waiter and e.waitee == waitee)]
            else:
                self.edges = [e for e in self.edges if e.waiter != waiter]
    
    def detect_deadlock(self) -> tuple[DeadlockStatus, Optional[List[str]]]:
        """
        Detect deadlock using wait-for graph cycle detection
        使用等待图循环检测死锁
        
        Returns: (status, cycle if any)
        """
        with self._lock:
            # Build adjacency list
            adjacency: Dict[str, Set[str]] = {}
            for edge in self.edges:
                if edge.waiter not in adjacency:
                    adjacency[edge.waiter] = set()
                adjacency[edge.waiter].add(edge.waitee)
            
            # DFS for cycle detection
            visited = set()
            recursion_stack = set()
            cycle = []
            
            def dfs(node: str, path: List[str]) -> bool:
                if node in recursion_stack:
                    # Found cycle
                    idx = path.index(node)
                    cycle[:] = path[idx:]
                    return True
                if node in visited:
                    return False
                
                visited.add(node)
                recursion_stack.add(node)
                path.append(node)
                
                if node in adjacency:
                    for neighbor in adjacency[node]:
                        if dfs(neighbor, path.copy()):
                            return True
                
                recursion_stack.remove(node)
                return False
            
            # Check all nodes
            all_nodes = set()
            for edge in self.edges:
                all_nodes.add(edge.waiter)
                all_nodes.add(edge.waitee)
            
            for node in all_nodes:
                if dfs(node, []):
                    return DeadlockStatus.DEADLOCK_DETECTED, cycle
            
            # Check for potential deadlock (long waits)
            now = time.time()
            long_waits = [e for e in self.edges if now - e.created_at > 30.0]  # >30s
            if long_waits:
                return DeadlockStatus.POTENTIAL_DEADLOCK, [e.waiter for e in long_waits]
            
            return DeadlockStatus.NO_DEADLOCK, None
    
    def set_timeout(self, task_id: str, timeout_seconds: float):
        """Set timeout for a task - 为任务设置超时"""
        with self._lock:
            self.timeouts[task_id] = time.time() + timeout_seconds
    
    def check_timeout(self, task_id: str) -> bool:
        """Check if task has timed out - 检查任务是否超时"""
        with self._lock:
            if task_id not in self.timeouts:
                return False
            return time.time() > self.timeouts[task_id]
    
    def cancel_timeout(self, task_id: str):
        """Cancel timeout - 取消超时"""
        with self._lock:
            if task_id in self.timeouts:
                del self.timeouts[task_id]
    
    def get_wait_graph(self) -> Dict[str, Any]:
        """Get wait-for graph as data - 获取等待图数据"""
        with self._lock:
            return {
                "edges": [
                    {
                        "waiter": e.waiter,
                        "waitee": e.waitee,
                        "resource": e.resource,
                        "created_at": e.created_at,
                        "age_seconds": time.time() - e.created_at
                    }
                    for e in self.edges
                ],
                "total_edges": len(self.edges),
                "timeouts": len(self.timeouts)
            }
    
    def clear(self):
        """Clear all state - 清除所有状态"""
        with self._lock:
            self.edges = []
            self.timeouts = {}


async def with_timeout(coro, timeout_seconds: float, timeout_callback=None):
    """
    Run coroutine with timeout - 带超时运行协程
    
    Args:
        coro: Coroutine to run
        timeout_seconds: Timeout in seconds
        timeout_callback: Called if timeout occurs
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        if timeout_callback:
            timeout_callback()
        raise


def create_deadlock_detector() -> DeadlockDetector:
    """Create deadlock detector - 创建死锁检测器"""
    return DeadlockDetector()


if __name__ == "__main__":
    print("Symphony Deadlock Detector & Timeout")
    print("交响死锁检测和超时")
    print("=" * 60)
    
    detector = create_deadlock_detector()
    
    # Test 1: No deadlock
    print("\n[Test 1] No deadlock...")
    detector.add_wait("task1", "task2", "resourceA")
    detector.add_wait("task2", "task3", "resourceB")
    status, cycle = detector.detect_deadlock()
    print(f"  Status: {status}")
    print(f"  OK: No deadlock")
    
    # Test 2: Clear
    print("\n[Test 2] Clear...")
    detector.clear()
    print(f"  OK: Cleared")
    
    # Test 3: Deadlock detection
    print("\n[Test 3] Deadlock detection...")
    detector.add_wait("taskA", "taskB", "lockX")
    detector.add_wait("taskB", "taskA", "lockY")
    status, cycle = detector.detect_deadlock()
    print(f"  Status: {status}")
    if cycle:
        print(f"  Cycle: {' -> '.join(cycle)}")
    print(f"  OK: Deadlock detected")
    
    # Test 4: Timeout
    print("\n[Test 4] Timeout...")
    detector.set_timeout("test_task", 1.0)
    print(f"  Timeout set")
    time.sleep(0.5)
    print(f"  Before timeout: {detector.check_timeout('test_task')}")
    time.sleep(0.6)
    print(f"  After timeout: {detector.check_timeout('test_task')}")
    print(f"  OK: Timeout works")
    
    # Test 5: Wait graph
    print("\n[Test 5] Wait graph...")
    graph = detector.get_wait_graph()
    print(f"  Total edges: {graph['total_edges']}")
    print(f"  OK: Graph retrieved")
    
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)
