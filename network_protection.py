#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境网络防护系统
解决网络阻塞、任务接续、故障恢复
"""
import os
import sys
import time
import random
from typing import Dict, List, Optional, Callable
from datetime import datetime
from queue import Queue
import threading

KERNEL_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KERNEL_PATH)

from combo_skill import get_combo_engine
from data_takeover import get_takeover
from flow_executor import get_flow_executor


class NetworkProtection:
    """网络防护系统"""
    
    def __init__(self):
        self.combo_engine = get_combo_engine()
        self.takeover = get_takeover()
        self.flow = get_flow_executor()
        
        # 防护配置
        self.max_retries = 3
        self.retry_delay = 1
        self.failover_enabled = True
        
        # 备用线路池
        self.backup_lines = []
        self.current_line = 0
        
        # 任务队列
        self.task_queue = Queue()
        self.completed_tasks = []
        
        # 状态
        self.network_status = 'normal'
        self.blocked_count = 0
        self.recovered_count = 0
    
    def check_network_health(self) -> Dict:
        """检测网络健康状态"""
        # 模拟网络检测
        status = 'normal'
        
        # 随机模拟网络波动
        if random.random() < 0.2:
            status = 'congested'
            self.blocked_count += 1
        else:
            status = 'normal'
            if self.blocked_count > 0:
                self.recovered_count += 1
        
        return {
            'status': status,
            'blocked_count': self.blocked_count,
            'recovered_count': self.recovered_count,
            'timestamp': datetime.now().isoformat()
        }
    
    def add_backup_line(self, provider: str, priority: int = 0):
        """添加备用线路"""
        self.backup_lines.append({
            'provider': provider,
            'priority': priority,
            'active': False
        })
        self.backup_lines.sort(key=lambda x: x['priority'], reverse=True)
    
    def switch_to_backup(self) -> Optional[Dict]:
        """切换到备用线路"""
        if not self.backup_lines:
            return None
        
        # 找到下一个可用的备用线路
        for i, line in enumerate(self.backup_lines):
            if not line['active']:
                line['active'] = True
                self.current_line = i
                return {
                    'status': 'switched',
                    'provider': line['provider'],
                    'line_index': i
                }
        
        return None
    
    def execute_with_protection(self, user_openid: str, task: Dict) -> Dict:
        """带防护的任务执行"""
        print()
        print('=' * 50)
        print('网络防护执行')
        print('=' * 50)
        
        # 数据接管
        self.takeover.takeover_user_data(user_openid, {
            'mode': 'protected_execution',
            'task': task.get('task_id', 'unknown'),
            'timestamp': datetime.now().isoformat()
        }, {'source': 'protection'})
        
        # 检测网络
        health = self.check_network_health()
        print('  网络状态: ' + health['status'])
        
        last_error = None
        
        # 主线路尝试
        for attempt in range(self.max_retries):
            try:
                # 模拟执行
                result = self._execute_task(task)
                if result.get('status') == 'ok':
                    result['attempts'] = attempt + 1
                    result['network_status'] = health['status']
                    return result
            except Exception as e:
                last_error = str(e)
                print('  尝试 ' + str(attempt + 1) + ' 失败: ' + e)
                time.sleep(self.retry_delay)
        
        # 切换备用线路
        if self.failover_enabled:
            print('  主线路失效，切换备用线路...')
            backup = self.switch_to_backup()
            
            if backup:
                print('  已切换到: ' + backup['provider'])
                # 尝试备用线路
                try:
                    result = self._execute_task(task)
                    result['failover'] = backup
                    result['network_status'] = 'recovered'
                    return result
                except Exception as e:
                    last_error = str(e)
        
        return {
            'status': 'error',
            'error': last_error or 'All attempts failed',
            'network_status': 'blocked'
        }
    
    def _execute_task(self, task: Dict) -> Dict:
        """执行单个任务"""
        # 模拟网络调用
        if random.random() < 0.1:  # 10%概率失败模拟网络问题
            raise Exception('Network timeout')
        
        return {
            'status': 'ok',
            'result': 'Task completed',
            'tokens': random.randint(100, 500)
        }
    
    def resume_interrupted(self, user_openid: str) -> Dict:
        """恢复中断的任务"""
        print()
        print('=' * 50)
        print('任务接续执行')
        print('=' * 50)
        
        # 获取未完成的任务
        pending = []
        while not self.task_queue.empty():
            task = self.task_queue.get()
            pending.append(task)
        
        # 重新执行
        completed = []
        for task in pending:
            result = self.execute_with_protection(user_openid, task)
            completed.append(result)
            self.completed_tasks.append(result)
        
        return {
            'status': 'resumed',
            'completed': len(completed),
            'results': completed
        }


class ComboProtectionMatrix:
    """组合防护矩阵"""
    
    def __init__(self):
        self.protection = NetworkProtection()
        self.combo_engine = get_combo_engine()
        
        # 添加备用线路
        self.protection.add_backup_line('火山引擎-备用1', priority=3)
        self.protection.add_backup_line('火山引擎-备用2', priority=2)
        self.protection.add_backup_line('智谱-备用', priority=1)
    
    def execute_protected_combo(self, user_openid: str, tasks: List[Dict]) -> Dict:
        """带防护的组合执行"""
        print()
        print('=' * 60)
        print('组合防护矩阵执行')
        print('=' * 60)
        
        # 数据接管
        self.protection.takeover.takeover_user_data(user_openid, {
            'mode': 'protected_combo',
            'tasks': len(tasks),
            'timestamp': datetime.now().isoformat()
        }, {'source': 'protection'})
        
        results = []
        total_tokens = 0
        
        # 逐个执行，带防护
        for i, task in enumerate(tasks):
            print()
            print('  任务 ' + str(i+1) + '/' + str(len(tasks)))
            
            result = self.protection.execute_with_protection(user_openid, task)
            results.append(result)
            
            if result.get('status') == 'ok':
                total_tokens += result.get('tokens', 0)
        
        # 统计
        success_count = sum(1 for r in results if r.get('status') == 'ok')
        
        return {
            'status': 'completed' if success_count == len(tasks) else 'partial',
            'total': len(tasks),
            'success': success_count,
            'failed': len(tasks) - success_count,
            'tokens': total_tokens,
            'network_blocked': self.protection.blocked_count,
            'network_recovered': self.protection.recovered_count
        }


# 全局实例
_protection_matrix = None


def get_protection_matrix() -> ComboProtectionMatrix:
    global _protection_matrix
    if _protection_matrix is None:
        _protection_matrix = ComboProtectionMatrix()
    return _protection_matrix
