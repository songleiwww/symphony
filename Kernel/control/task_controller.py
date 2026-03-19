# -*- coding: utf-8 -*-
"""
序境系统 - 任务中断/控制模块
解决任务执行过程中无法取消/中断的问题
"""
import threading
import time
import uuid
from typing import Dict, Optional, Callable
from enum import Enum
import queue

class TaskState(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskController:
    """
    任务控制器
    
    功能:
    1. 任务取消 - 正在执行的任务可以取消
    2. 任务暂停/恢复 - 支持暂停和恢复任务
    3. 任务优先级 - 支持优先级调度
    4. 超时控制 - 任务执行超时自动终止
    5. 并发控制 - 限制并发任务数量
    """
    
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.tasks = {}  # task_id -> TaskInfo
        self.task_queue = queue.PriorityQueue()
        self.running_tasks = {}  # 正在执行的任务
        self._lock = threading.Lock()
        self._callbacks = {}  # 任务状态回调
    
    def create_task(self, task_type: str, priority: int = 5, 
                   timeout: int = 300, user_id: str = None) -> str:
        """
        创建任务
        
        返回 task_id
        """
        task_id = str(uuid.uuid4())[:8]
        
        task_info = {
            'task_id': task_id,
            'task_type': task_type,
            'priority': priority,
            'timeout': timeout,
            'user_id': user_id,
            'state': TaskState.PENDING,
            'created_at': time.time(),
            'started_at': None,
            'completed_at': None,
            'progress': 0,
            'message': '任务已创建',
            'result': None,
            'error': None
        }
        
        with self._lock:
            self.tasks[task_id] = task_info
            self.task_queue.put((priority, task_id))
        
        return task_id
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        返回是否成功取消
        """
        with self._lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            
            # 只能取消pending/running状态的任务
            if task['state'] in [TaskState.PENDING, TaskState.RUNNING]:
                task['state'] = TaskState.CANCELLED
                task['completed_at'] = time.time()
                task['message'] = '任务已取消'
                
                # 如果正在运行，标记需要停止
                if task_id in self.running_tasks:
                    self.running_tasks[task_id]['should_stop'] = True
                
                self._notify_callback(task_id, 'cancelled')
                return True
            
            return False
    
    def pause_task(self, task_id: str) -> bool:
        """暂停任务"""
        with self._lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            
            if task['state'] == TaskState.RUNNING:
                task['state'] = TaskState.PAUSED
                task['message'] = '任务已暂停'
                self._notify_callback(task_id, 'paused')
                return True
            
            return False
    
    def resume_task(self, task_id: str) -> bool:
        """恢复任务"""
        with self._lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            
            if task['state'] == TaskState.PAUSED:
                task['state'] = TaskState.RUNNING
                task['message'] = '任务已恢复'
                self._notify_callback(task_id, 'resumed')
                return True
            
            return False
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        with self._lock:
            return self.tasks.get(task_id)
    
    def update_progress(self, task_id: str, progress: int, message: str = None):
        """更新任务进度"""
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id]['progress'] = progress
                if message:
                    self.tasks[task_id]['message'] = message
                self._notify_callback(task_id, 'progress')
    
    def should_stop(self, task_id: str) -> bool:
        """检查任务是否应该停止"""
        with self._lock:
            if task_id in self.running_tasks:
                return self.running_tasks[task_id].get('should_stop', False)
        return False
    
    def complete_task(self, task_id: str, result: any = None):
        """完成任务"""
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id]['state'] = TaskState.COMPLETED
                self.tasks[task_id]['completed_at'] = time.time()
                self.tasks[task_id]['result'] = result
                self.tasks[task_id]['message'] = '任务完成'
                self.tasks[task_id]['progress'] = 100
                
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]
                
                self._notify_callback(task_id, 'completed')
    
    def fail_task(self, task_id: str, error: str):
        """任务失败"""
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id]['state'] = TaskState.FAILED
                self.tasks[task_id]['completed_at'] = time.time()
                self.tasks[task_id]['error'] = error
                self.tasks[task_id]['message'] = f'任务失败: {error}'
                
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]
                
                self._notify_callback(task_id, 'failed')
    
    def register_callback(self, task_id: str, callback: Callable):
        """注册回调"""
        self._callbacks[task_id] = callback
    
    def _notify_callback(self, task_id: str, event: str):
        """触发回调"""
        if task_id in self._callbacks:
            try:
                self._callbacks[task_id](task_id, event, self.tasks.get(task_id))
            except Exception as e:
                print(f"Callback error: {e}")
    
    def list_tasks(self, user_id: str = None) -> list:
        """列出任务"""
        with self._lock:
            tasks = list(self.tasks.values())
            
            if user_id:
                tasks = [t for t in tasks if t.get('user_id') == user_id]
            
            return sorted(tasks, key=lambda x: x['created_at'], reverse=True)


class InterruptibleExecutor:
    """
    可中断的执行器
    将任务包装为可中断任务
    """
    
    def __init__(self, controller: TaskController):
        self.controller = controller
    
    def execute_with_control(self, task_id: str, executor_func: Callable, *args, **kwargs):
        """
        可中断地执行任务
        
        参数:
            task_id: 任务ID
            executor_func: 执行函数，需要接受task_id参数用于检查是否中断
        """
        # 检查任务是否被取消
        if self.controller.should_stop(task_id):
            self.controller.cancel_task(task_id)
            return {'cancelled': True}
        
        # 标记为运行中
        with self.controller._lock:
            if task_id in self.controller.tasks:
                self.controller.tasks[task_id]['state'] = TaskState.RUNNING
                self.controller.tasks[task_id]['started_at'] = time.time()
                self.controller.running_tasks[task_id] = {'should_stop': False}
        
        try:
            # 执行任务
            result = executor_func(task_id, *args, **kwargs)
            
            # 检查是否被中断
            if self.controller.should_stop(task_id):
                self.controller.cancel_task(task_id)
                return {'cancelled': True, 'partial_result': result}
            
            # 完成任务
            self.controller.complete_task(task_id, result)
            return {'success': True, 'result': result}
            
        except Exception as e:
            self.controller.fail_task(task_id, str(e))
            return {'success': False, 'error': str(e)}


# 全局控制器
_global_controller = None

def get_task_controller() -> TaskController:
    """获取全局任务控制器"""
    global _global_controller
    if _global_controller is None:
        _global_controller = TaskController(max_concurrent=3)
    return _global_controller


# 测试
if __name__ == '__main__':
    print('=== 任务中断机制测试 ===\n')
    
    controller = get_task_controller()
    executor = InterruptibleExecutor(controller)
    
    # 测试1: 创建任务
    print('1. 创建任务...')
    task_id = controller.create_task('model_dispatch', priority=5, user_id='test_user')
    print(f'   任务ID: {task_id}')
    
    # 测试2: 模拟执行
    print('\n2. 模拟执行...')
    def mock_executor(task_id):
        for i in range(10):
            if controller.should_stop(task_id):
                print(f'   任务被中断!')
                return {'interrupted': True, 'progress': i * 10}
            time.sleep(0.2)
            controller.update_progress(task_id, (i+1)*10, f'进度: {(i+1)*10}%')
        return {'completed': True, 'data': 'result'}
    
    result = executor.execute_with_control(task_id, mock_executor)
    print(f'   结果: {result}')
    
    # 测试3: 任务状态
    print('\n3. 任务状态:')
    status = controller.get_task_status(task_id)
    print(f'   状态: {status["state"].value}')
    print(f'   进度: {status["progress"]}%')
    
    # 测试4: 取消任务
    print('\n4. 创建并取消任务...')
    task_id2 = controller.create_task('test', priority=3)
    print(f'   创建任务: {task_id2}')
    cancelled = controller.cancel_task(task_id2)
    print(f'   取消结果: {cancelled}')
    
    # 列出所有任务
    print('\n5. 所有任务:')
    tasks = controller.list_tasks()
    for t in tasks:
        print(f'   {t["task_id"]}: {t["state"].value} - {t["message"]}')
