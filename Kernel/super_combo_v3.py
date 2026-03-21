#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境超级组合引擎 v3
- 多服务商动态组合
- 推理模型+视觉模型组合
- 失效转移+替补机制
- 智能互补
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
import sqlite3

DATA_PATH = os.path.join(KERNEL_PATH, '..', 'data')
DB_PATH = os.path.join(DATA_PATH, 'symphony.db')


class SuperCombinerV3:
    """序境超级组合引擎 v3"""
    
    def __init__(self):
        self.combo_engine = get_combo_engine()
        self.takeover = get_takeover()
        self.flow = get_flow_executor()
        
        # 加载模型配置
        self.models = self._load_models()
        self.reasoning_models = self._get_reasoning_models()
        self.vision_models = self._get_vision_models()
        self.providers = self._get_providers()
    
    def _load_models(self) -> List[Dict]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.id, r.姓名, m.模型名称, m.服务商, m.API地址
            FROM 官署角色表 r
            JOIN 模型配置表 m ON r.模型配置表_ID = m.id
            WHERE m.在线状态 = '正常'
            ORDER BY m.服务商
        ''')
        
        models = []
        for row in cursor.fetchall():
            models.append({
                'role_id': row[0],
                'name': row[1],
                'model': row[2],
                'provider': row[3],
                'api': row[4]
            })
        
        conn.close()
        return models
    
    def _get_reasoning_models(self) -> List[Dict]:
        """获取推理模型"""
        return [m for m in self.models if 'R1' in m['model'] or 'reasoning' in m['model'].lower()]
    
    def _get_vision_models(self) -> List[Dict]:
        """获取视觉模型"""
        return [m for m in self.models if 'vision' in m['model'].lower() or 'VL' in m['model'] or 'BLIP' in m['model'] or 'Neva' in m['model']]
    
    def _get_providers(self) -> Dict:
        """获取服务商分布"""
        providers = {}
        for m in self.models:
            p = m['provider']
            if p not in providers:
                providers[p] = []
            providers[p].append(m)
        return providers
    
    def dynamic_multi_provider_combo(self, user_openid: str, provider_count: int) -> Dict:
        """动态多服务商组合"""
        print()
        print('=' * 60)
        print('动态多服务商组合')
        print('=' * 60)
        
        # 数据接管
        self.takeover.takeover_user_data(user_openid, {
            'mode': 'dynamic_multi_provider',
            'providers': provider_count,
            'timestamp': datetime.now().isoformat()
        }, {'source': 'super_combo'})
        
        # 随机选择不同服务商
        provider_names = list(self.providers.keys())
        selected_providers = random.sample(provider_names, min(provider_count, len(provider_names)))
        
        print('  使用服务商: ' + ', '.join(selected_providers))
        
        # 构建任务
        tasks = []
        for p in selected_providers:
            model = random.choice(self.providers[p])
            tasks.append({
                'role_id': model['role_id'],
                'messages': [
                    {'role': 'system', 'content': '你是' + model['name'] + '。用20字介绍序境。'},
                    {'role': 'user', 'content': '请回答'}
                ]
            })
        
        # 执行
        result = self.combo_engine.execute(tasks, mode='parallel')
        
        return {
            'status': 'ok',
            'providers_used': selected_providers,
            'models_used': [t['role_id'] for t in tasks],
            'tokens': result['total_tokens']
        }
    
    def reasoning_vision_combo(self, user_openid: str) -> Dict:
        """推理+视觉模型组合"""
        print()
        print('=' * 60)
        print('推理+视觉模型组合')
        print('=' * 60)
        
        # 数据接管
        self.takeover.takeover_user_data(user_openid, {
            'mode': 'reasoning_vision',
            'timestamp': datetime.now().isoformat()
        }, {'source': 'super_combo'})
        
        # 选择推理模型
        reasoning = random.choice(self.reasoning_models) if self.reasoning_models else self.models[0]
        
        # 选择视觉模型
        vision = random.choice(self.vision_models) if self.vision_models else self.models[1]
        
        print('  推理模型: ' + reasoning['name'] + ' - ' + reasoning['model'])
        print('  视觉模型: ' + vision['name'] + ' - ' + vision['model'])
        
        # 构建任务
        tasks = [
            {
                'role_id': reasoning['role_id'],
                'messages': [
                    {'role': 'system', 'content': '你是' + reasoning['name'] + '。深度推理分析序境的优势。'},
                    {'role': 'user', 'content': '请分析'}
                ]
            },
            {
                'role_id': vision['role_id'],
                'messages': [
                    {'role': 'system', 'content': '你是' + vision['name'] + '。从视觉角度描述序境。'},
                    {'role': 'user', 'content': '请描述'}
                ]
            }
        ]
        
        # 执行
        result = self.combo_engine.execute(tasks, mode='parallel')
        
        return {
            'status': 'ok',
            'reasoning_model': reasoning['model'],
            'vision_model': vision['model'],
            'tokens': result['total_tokens']
        }
    
    def full_matrix_combo(self, user_openid: str) -> Dict:
        """完整矩阵组合: 2+3+4 引擎"""
        print()
        print('=' * 60)
        print('完整矩阵组合 (2+3+4)')
        print('=' * 60)
        
        # 数据接管
        self.takeover.takeover_user_data(user_openid, {
            'mode': 'full_matrix',
            'timestamp': datetime.now().isoformat()
        }, {'source': 'super_combo'})
        
        results = {}
        
        # 2引擎
        print('  2引擎组合...')
        tasks_2 = [
            {'role_id': self.models[0]['role_id'], 'messages': [{'role': 'user', 'content': '介绍序境'}]},
            {'role_id': self.models[1]['role_id'], 'messages': [{'role': 'user', 'content': '介绍序境'}]}
        ]
        r2 = self.combo_engine.execute(tasks_2, mode='parallel')
        results['2_engine'] = r2['total_tokens']
        
        # 3引擎
        print('  3引擎组合...')
        tasks_3 = [
            {'role_id': self.models[0]['role_id'], 'messages': [{'role': 'user', 'content': '分析序境'}]},
            {'role_id': self.models[1]['role_id'], 'messages': [{'role': 'user', 'content': '分析序境'}]},
            {'role_id': self.models[2]['role_id'], 'messages': [{'role': 'user', 'content': '分析序境'}]}
        ]
        r3 = self.combo_engine.execute(tasks_3, mode='parallel')
        results['3_engine'] = r3['total_tokens']
        
        # 4引擎
        print('  4引擎组合...')
        tasks_4 = [
            {'role_id': self.models[0]['role_id'], 'messages': [{'role': 'user', 'content': '评价序境'}]},
            {'role_id': self.models[1]['role_id'], 'messages': [{'role': 'user', 'content': '评价序境'}]},
            {'role_id': self.models[2]['role_id'], 'messages': [{'role': 'user', 'content': '评价序境'}]},
            {'role_id': self.models[3]['role_id'], 'messages': [{'role': 'user', 'content': '评价序境'}]}
        ]
        r4 = self.combo_engine.execute(tasks_4, mode='parallel')
        results['4_engine'] = r4['total_tokens']
        
        return {
            'status': 'ok',
            'results': results,
            'total': sum(results.values())
        }


# 全局实例
_super_v3 = None


def get_super_v3() -> SuperCombinerV3:
    global _super_v3
    if _super_v3 is None:
        _super_v3 = SuperCombinerV3()
    return _super_v3
