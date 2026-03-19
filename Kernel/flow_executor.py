#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境流水任务执行器
连续执行多任务，像流水一样自动运行
"""
import sqlite3
import requests
import os
import json
import time
from typing import List, Dict, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 路径配置
KERNEL_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(KERNEL_PATH, '..', 'data')
DB_PATH = os.path.join(DATA_PATH, 'symphony.db')


class FlowTask:
    """流水任务"""
    def __init__(self, task_id: str, role_id: str, messages: List[Dict], priority: int = 1):
        self.task_id = task_id
        self.role_id = role_id
        self.messages = messages
        self.priority = priority
        self.status = 'pending'
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
    
    def execute(self, scheduler) -> Dict:
        """执行任务"""
        self.status = 'running'
        self.start_time = datetime.now()
        
        try:
            result = scheduler.dispatch(self.role_id, self.messages)
            self.result = result
            self.status = 'completed' if result['status'] == 'ok' else 'failed'
        except Exception as e:
            self.error = str(e)
            self.status = 'error'
        
        self.end_time = datetime.now()
        return self.result or {'status': 'error', 'message': self.error}


class FlowExecutor:
    """流水任务执行器"""
    
    def __init__(self):
        import sys
        self.tasks: List[FlowTask] = []
        self.running = False
        self.current_index = 0
        self.results: List[Dict] = []
        
        # 加载调度器
        sys.path.insert(0, KERNEL_PATH)
        from scheduler import get_scheduler
        self.scheduler = get_scheduler()
    
    def add_task(self, role_id: str, messages: List[Dict], priority: int = 1) -> str:
        """添加任务到流水"""
        task_id = f"task_{len(self.tasks)}_{int(time.time())}"
        task = FlowTask(task_id, role_id, messages, priority)
        self.tasks.append(task)
        return task_id
    
    def add_multi_tasks(self, tasks: List[Dict]) -> List[str]:
        """批量添加任务
        
        tasks: [
            {'role_id': 'role-1', 'messages': [...]},
            {'role_id': 'role-10', 'messages': [...]},
            ...
        ]
        """
        task_ids = []
        for t in tasks:
            tid = self.add_task(t['role_id'], t['messages'], t.get('priority', 1))
            task_ids.append(tid)
        return task_ids
    
    def run_sequential(self, callback=None) -> List[Dict]:
        """顺序执行流水任务"""
        self.running = True
        self.results = []
        
        print("🔄 序境流水执行器")
        print("=" * 40)
        
        # 按优先级排序
        sorted_tasks = sorted(self.tasks, key=lambda x: x.priority, reverse=True)
        
        for i, task in enumerate(sorted_tasks):
            if not self.running:
                break
            
            # 显示进度
            print(f"【{i+1}/{len(sorted_tasks)}】执行任务 {task.task_id}")
            print(f"    角色: {task.role_id}")
            
            # 执行
            result = task.execute(self.scheduler)
            self.results.append(result)
            
            # 显示结果
            if result.get('status') == 'ok':
                print(f"    ✓ 成功 - {result.get('model')} - {result.get('usage',{}).get('total_tokens')} tokens")
            else:
                print(f"    ✗ 失败 - {result.get('message', 'unknown')}")
            
            print()
            
            # 回调
            if callback:
                callback(i, task, result)
        
        self.running = False
        print("=" * 40)
        print(f"✅ 流水执行完成，共 {len(self.results)} 项任务")
        
        return self.results
    
    def run_parallel(self, max_workers: int = 3, callback=None) -> List[Dict]:
        """并行执行流水任务"""
        self.running = True
        self.results = []
        
        print("🔄 序境并行执行器")
        print("=" * 40)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_task = {
                executor.submit(task.execute, self.scheduler): task 
                for task in self.tasks
            }
            
            for i, future in enumerate(as_completed(future_to_task)):
                task = future_to_task[future]
                try:
                    result = future.result()
                    self.results.append(result)
                    
                    status_icon = "✓" if result.get('status') == 'ok' else "✗"
                    print(f"{status_icon} {task.task_id}: {result.get('role')} - {result.get('model')}")
                    
                    if callback:
                        callback(i, task, result)
                        
                except Exception as e:
                    print(f"✗ {task.task_id}: {str(e)}")
        
        self.running = False
        print("=" * 40)
        print(f"✅ 并行执行完成，共 {len(self.results)} 项任务")
        
        return self.results
    
    def stop(self):
        """停止执行"""
        self.running = False
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            'running': self.running,
            'total_tasks': len(self.tasks),
            'completed': sum(1 for t in self.tasks if t.status == 'completed'),
            'failed': sum(1 for t in self.tasks if t.status in ['failed', 'error']),
            'pending': sum(1 for t in self.tasks if t.status == 'pending'),
        }


# 全局执行器实例
_flow_executor = None


def get_flow_executor() -> FlowExecutor:
    """获取流水执行器"""
    global _flow_executor
    if _flow_executor is None:
        _flow_executor = FlowExecutor()
    return _flow_executor
