#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境高级组合引擎
数据多引擎汇聚 + 超长结果流式输出 + 失效阻塞替补机制
"""
import os
import sys
import time
import threading
from typing import Dict, List, Optional, Callable
from datetime import datetime
from queue import Queue
import json

KERNEL_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KERNEL_PATH)

from combo_skill import get_combo_engine
from data_takeover import get_takeover
from flow_executor import get_flow_executor


class StreamOutput:
    """流式输出管理器"""
    
    def __init__(self):
        self.queue = Queue()
        self.callbacks = []
    
    def add_callback(self, callback: Callable):
        self.callbacks.append(callback)
    
    def push(self, chunk: str):
        self.queue.put(chunk)
        for cb in self.callbacks:
            cb(chunk)
    
    def stream(self, content: str, chunk_size: int = 50):
        """流式输出内容"""
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i+chunk_size]
            self.push(chunk)
            time.sleep(0.05)  # 模拟流式输出


class FailoverManager:
    """失效阻塞替补管理器"""
    
    def __init__(self):
        self.backup_chain = []
        self.failover_enabled = True
        self.max_retries = 3
        self.retry_delay = 1
    
    def set_backup_chain(self, chain: List[Dict]):
        """设置备份链"""
        self.backup_chain = chain
    
    def execute_with_failover(self, primary_func: Callable, *args, **kwargs) -> Dict:
        """执行带失效转移的功能"""
        last_error = None
        
        # 尝试主函数
        for attempt in range(self.max_retries):
            try:
                result = primary_func(*args, **kwargs)
                if result.get('status') == 'ok':
                    result['failover_attempts'] = attempt + 1
                    return result
            except Exception as e:
                last_error = str(e)
                print(f'  尝试 {attempt + 1} 失败: {e}')
        
        # 主函数失败，使用备份链
        if self.backup_chain and self.failover_enabled:
            print('  主函数失效，启用备份链...')
            for i, backup in enumerate(self.backup_chain):
                try:
                    print(f'  尝试备份 {i+1}: {backup.get("name", "unknown")}')
                    result = backup['func'](*args, **kwargs)
                    if result.get('status') == 'ok':
                        result['failover_used'] = backup.get('name', f'backup_{i}')
                        result['failover_attempts'] = self.max_retries + i + 1
                        return result
                except Exception as e:
                    print(f'  备份 {i+1} 也失败: {e}')
                    continue
        
        return {
            'status': 'error',
            'error': last_error or 'All attempts failed',
            'failover_attempts': self.max_retries
        }


class AdvancedCombiner:
    """高级组合引擎"""
    
    def __init__(self):
        self.combo_engine = get_combo_engine()
        self.takeover = get_takeover()
        self.flow = get_flow_executor()
        
        self.stream = StreamOutput()
        self.failover = FailoverManager()
        
        # 备份链
        self.failover.set_backup_chain([
            {'name': 'backup_flow', 'func': self._backup_flow},
            {'name': 'backup_simple', 'func': self._backup_simple}
        ])
    
    def _backup_flow(self, *args, **kwargs) -> Dict:
        """备份1: 流水执行器"""
        tasks = kwargs.get('tasks', [])
        result = self.flow.run_sequential()
        return {'status': 'ok', 'result': result}
    
    def _backup_simple(self, *args, **kwargs) -> Dict:
        """备份2: 简单执行"""
        return {'status': 'ok', 'message': 'Simple fallback', 'result': []}
    
    def multi_engine_gather(self, user_openid: str, tasks: List[Dict]) -> Dict:
        """数据多引擎汇聚"""
        print()
        print('=' * 50)
        print('数据多引擎汇聚')
        print('=' * 50)
        
        # 接管数据
        self.takeover.takeover_user_data(user_openid, {
            'mode': 'multi_engine_gather',
            'tasks': len(tasks),
            'timestamp': datetime.now().isoformat()
        }, {'source': 'advanced'})
        
        # 使用失效转移执行
        result = self.failover.execute_with_failover(
            self._execute_gather,
            tasks=tasks
        )
        
        return result
    
    def _execute_gather(self, tasks: List[Dict]) -> Dict:
        """执行汇聚"""
        result = self.combo_engine.execute(tasks, mode='parallel')
        
        gathered_data = []
        for r in result.get('individual_results', []):
            if r.get('status') == 'ok':
                gathered_data.append({
                    'model': r.get('model'),
                    'response': r.get('response', ''),
                    'tokens': r.get('usage', {}).get('total_tokens', 0)
                })
        
        return {
            'status': 'ok',
            'gathered': gathered_data,
            'total_tokens': result.get('total_tokens', 0)
        }
    
    def long_result_stream(self, user_openid: str, content: str) -> Dict:
        """超长结果流式输出"""
        print()
        print('=' * 50)
        print('超长结果流式输出')
        print('=' * 50)
        
        # 数据接管
        self.takeover.takeover_user_data(user_openid, {
            'mode': 'long_result_stream',
            'content_length': len(content),
            'timestamp': datetime.now().isoformat()
        }, {'source': 'advanced'})
        
        # 流式输出
        print('  开始流式输出...')
        streamed = []
        
        def on_chunk(chunk):
            streamed.append(chunk)
            print(f'  [流] {chunk[:30]}...')
        
        self.stream.add_callback(on_chunk)
        self.stream.stream(content)
        
        return {
            'status': 'ok',
            'total_chunks': len(streamed),
            'total_length': len(''.join(streamed))
        }
    
    def failover_process(self, user_openid: str, primary_task: Dict) -> Dict:
        """失效阻塞替补处理"""
        print()
        print('=' * 50)
        print('失效阻塞替补处理')
        print('=' * 50)
        
        # 接管数据
        self.takeover.takeover_user_data(user_openid, {
            'mode': 'failover_process',
            'timestamp': datetime.now().isoformat()
        }, {'source': 'advanced'})
        
        # 执行失效转移
        result = self.failover.execute_with_failover(
            self._primary_execute,
            task=primary_task
        )
        
        if result.get('failover_used'):
            print(f'  使用了备份: {result["failover_used"]}')
        
        return result
    
    def _primary_execute(self, task: Dict) -> Dict:
        """主执行函数"""
        # 模拟可能失败
        import random
        if random.random() < 0.3:  # 30%概率失败
            raise Exception('Simulated failure for testing')
        
        return {
            'status': 'ok',
            'response': f'Executed: {task.get("task_id", "unknown")}',
            'tokens': 100
        }


# 全局实例
_advanced = None


def get_advanced() -> AdvancedCombiner:
    global _advanced
    if _advanced is None:
        _advanced = AdvancedCombiner()
    return _advanced
