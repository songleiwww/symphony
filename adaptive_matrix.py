#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境自适应矩阵系统
高速开发+降级策略：5矩阵→4矩阵→3矩阵 自动调整
"""
import os
import sys
import random
from typing import Dict, List, Optional
from datetime import datetime

KERNEL_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KERNEL_PATH)

from combo_skill import get_combo_engine
from data_takeover import get_takeover
from flow_executor import get_flow_executor


class AdaptiveMatrixSystem:
    """自适应矩阵系统"""
    
    def __init__(self):
        self.combo_engine = get_combo_engine()
        self.takeover = get_takeover()
        self.flow = get_flow_executor()
        
        # 当前矩阵级别
        self.current_level = 5
        self.max_level = 5
        self.min_level = 2
        
        # 降级历史
        self.history = []
        
        # 成功/失败计数
        self.success_count = 0
        self.fail_count = 0
        self.upgrade_threshold = 2  # 连续成功2次升级
        self.downgrade_threshold = 1  # 失败1次降级
    
    def get_tasks_for_level(self, level: int) -> List[Dict]:
        """根据级别获取任务配置"""
        tasks = []
        
        for i in range(level):
            role_id = ['role-1', 'role-10', 'role-55', 'role-56', 'role-57'][i % 5]
            tasks.append({
                'role_id': role_id,
                'messages': [
                    {'role': 'system', 'content': '你是序境官员。简要介绍序境优势，30字以内。'},
                    {'role': 'user', 'content': '请回答'}
                ]
            })
        
        return tasks
    
    def execute_with_adaptation(self, user_openid: str) -> Dict:
        """自适应执行"""
        print()
        print('=' * 60)
        print('序境自适应矩阵系统')
        print('=' * 60)
        
        # 数据接管
        self.takeover.takeover_user_data(user_openid, {
            'mode': 'adaptive_matrix',
            'current_level': self.current_level,
            'timestamp': datetime.now().isoformat()
        }, {'source': 'adaptive'})
        
        print('  当前级别: ' + str(self.current_level) + ' 矩阵')
        
        # 获取任务
        tasks = self.get_tasks_for_level(self.current_level)
        print('  任务数: ' + str(len(tasks)))
        
        # 执行
        result = self.combo_engine.execute(tasks, mode='parallel')
        
        # 检查结果
        success = result.get('total_tokens', 0) > 0
        
        if success:
            self.success_count += 1
            self.fail_count = 0
            print('  执行成功!')
        else:
            self.fail_count += 1
            self.success_count = 0
            print('  执行失败!')
        
        # 记录历史
        self.history.append({
            'level': self.current_level,
            'success': success,
            'tokens': result.get('total_tokens', 0),
            'timestamp': datetime.now().isoformat()
        })
        
        # 自动调整级别
        old_level = self.current_level
        
        if success and self.success_count >= self.upgrade_threshold:
            if self.current_level < self.max_level:
                self.current_level += 1
                self.success_count = 0
                print('  >> 升级到 ' + str(self.current_level) + ' 矩阵!')
        
        if not success or self.fail_count >= self.downgrade_threshold:
            if self.current_level > self.min_level:
                self.current_level -= 1
                self.fail_count = 0
                print('  >> 降级到 ' + str(self.current_level) + ' 矩阵!')
        
        return {
            'status': 'ok' if success else 'degraded',
            'level': old_level,
            'new_level': self.current_level,
            'level_changed': old_level != self.current_level,
            'tokens': result.get('total_tokens', 0),
            'history': self.history
        }
    
    def run_adaptive_cycle(self, user_openid: str, cycles: int = 5) -> Dict:
        """运行自适应循环"""
        print()
        print('=' * 60)
        print('序境自适应矩阵循环测试')
        print('=' * 60)
        
        results = []
        
        for i in range(cycles):
            print()
            print('--- 循环 ' + str(i+1) + '/' + str(cycles) + ' ---')
            
            result = self.execute_with_adaptation(user_openid)
            results.append(result)
            
            # 显示级别变化
            if result.get('level_changed'):
                print('  *** 矩阵级别调整: ' + str(result['level']) + ' -> ' + str(result['new_level']))
        
        # 统计
        success_count = sum(1 for r in results if r.get('status') == 'ok')
        
        return {
            'cycles': cycles,
            'success': success_count,
            'failed': cycles - success_count,
            'final_level': self.current_level,
            'history': self.history
        }


# 全局实例
_adaptive_matrix = None


def get_adaptive_matrix() -> AdaptiveMatrixSystem:
    global _adaptive_matrix
    if _adaptive_matrix is None:
        _adaptive_matrix = AdaptiveMatrixSystem()
    return _adaptive_matrix
