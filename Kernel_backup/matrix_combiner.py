#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境多引擎矩阵组合系统
2x2 / 3x3 / 4x4 多引擎多模型组合
"""
import os
import sys
from typing import Dict, List, Optional
from datetime import datetime

KERNEL_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KERNEL_PATH)

from combo_skill import get_combo_engine
from data_takeover import get_takeover
from flow_executor import get_flow_executor


class MatrixCombiner:
    """序境多引擎矩阵组合器"""
    
    def __init__(self):
        self.combo_engine = get_combo_engine()
        self.takeover = get_takeover()
        self.flow = get_flow_executor()
        
        # 引擎列表
        self.engines = {
            'flow': self.flow,
            'combo': self.combo_engine
        }
    
    def matrix_2x2(self, user_openid: str) -> Dict:
        """2x2矩阵组合: 2引擎 x 2模型"""
        print()
        print('=' * 50)
        print('2x2 矩阵组合')
        print('=' * 50)
        
        # 数据接管
        self.takeover.takeover_user_data(user_openid, {
            'mode': 'matrix_2x2',
            'timestamp': datetime.now().isoformat()
        }, {'source': 'matrix'})
        
        # 2个模型组合
        tasks = [
            {'role_id': 'role-1', 'messages': [
                {'role': 'system', 'content': '你是陆念昭。用20字介绍序境。'},
                {'role': 'user', 'content': '请回答'}
            ]},
            {'role_id': 'role-10', 'messages': [
                {'role': 'system', 'content': '你是徐浩。用20字介绍序境。'},
                {'role': 'user', 'content': '请回答'}
            ]},
        ]
        
        result = self.combo_engine.execute(tasks, mode='parallel')
        
        return {
            'matrix': '2x2',
            'engines': 2,
            'models': 2,
            'tokens': result['total_tokens'],
            'status': 'ok'
        }
    
    def matrix_3x3(self, user_openid: str) -> Dict:
        """3x3矩阵组合: 3引擎 x 3模型"""
        print()
        print('=' * 50)
        print('3x3 矩阵组合')
        print('=' * 50)
        
        # 数据接管
        self.takeover.takeover_user_data(user_openid, {
            'mode': 'matrix_3x3',
            'timestamp': datetime.now().isoformat()
        }, {'source': 'matrix'})
        
        # 3个模型组合
        tasks = [
            {'role_id': 'role-1', 'messages': [
                {'role': 'system', 'content': '你是陆念昭。用20字介绍序境价值。'},
                {'role': 'user', 'content': '请回答'}
            ]},
            {'role_id': 'role-10', 'messages': [
                {'role': 'system', 'content': '你是徐浩。用20字介绍序境技术。'},
                {'role': 'user', 'content': '请回答'}
            ]},
            {'role_id': 'role-55', 'messages': [
                {'role': 'system', 'content': '你是李公麟。用20字介绍序境创作。'},
                {'role': 'user', 'content': '请回答'}
            ]},
        ]
        
        result = self.combo_engine.execute(tasks, mode='parallel')
        
        return {
            'matrix': '3x3',
            'engines': 3,
            'models': 3,
            'tokens': result['total_tokens'],
            'status': 'ok'
        }
    
    def matrix_4x4(self, user_openid: str) -> Dict:
        """4x4矩阵组合: 4引擎 x 4模型"""
        print()
        print('=' * 50)
        print('4x4 矩阵组合')
        print('=' * 50)
        
        # 数据接管
        self.takeover.takeover_user_data(user_openid, {
            'mode': 'matrix_4x4',
            'timestamp': datetime.now().isoformat()
        }, {'source': 'matrix'})
        
        # 4个模型组合
        tasks = [
            {'role_id': 'role-1', 'messages': [
                {'role': 'system', 'content': '你是陆念昭。介绍序境核心。'},
                {'role': 'user', 'content': '请回答'}
            ]},
            {'role_id': 'role-10', 'messages': [
                {'role': 'system', 'content': '你是徐浩。介绍序境技术。'},
                {'role': 'user', 'content': '请回答'}
            ]},
            {'role_id': 'role-55', 'messages': [
                {'role': 'system', 'content': '你是李公麟。介绍序境创作。'},
                {'role': 'user', 'content': '请回答'}
            ]},
            {'role_id': 'role-56', 'messages': [
                {'role': 'system', 'content': '你是赵干。介绍序境功能。'},
                {'role': 'user', 'content': '请回答'}
            ]},
        ]
        
        result = self.combo_engine.execute(tasks, mode='parallel')
        
        return {
            'matrix': '4x4',
            'engines': 4,
            'models': 4,
            'tokens': result['total_tokens'],
            'status': 'ok'
        }
    
    def run_all_matrix(self, user_openid: str) -> Dict:
        """运行所有矩阵组合"""
        print('=' * 60)
        print('序境多引擎矩阵组合系统')
        print('=' * 60)
        
        # 接管数据
        self.takeover.takeover_user_data(user_openid, {
            'mode': 'all_matrix',
            'timestamp': datetime.now().isoformat()
        }, {'source': 'host_takeover'})
        
        # 2x2
        r1 = self.matrix_2x2(user_openid)
        
        # 3x3
        r2 = self.matrix_3x3(user_openid)
        
        # 4x4
        r3 = self.matrix_4x4(user_openid)
        
        total = r1['tokens'] + r2['tokens'] + r3['tokens']
        
        return {
            '2x2': r1,
            '3x3': r2,
            '4x4': r3,
            'total_tokens': total
        }


_matrix = None


def get_matrix() -> MatrixCombiner:
    global _matrix
    if _matrix is None:
        _matrix = MatrixCombiner()
    return _matrix
