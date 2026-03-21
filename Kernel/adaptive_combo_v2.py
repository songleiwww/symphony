#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境自适应组合技能引擎V2
多服务商、多API、多模型防限流
"""
import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
import sys
import random

KERNEL_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(KERNEL_PATH, '..', 'data')
DB_PATH = os.path.join(DATA_PATH, 'symphony.db')
sys.path.insert(0, KERNEL_PATH)


class MultiProviderManager:
    """多服务商管理器"""
    
    def __init__(self):
        self.providers = self._load_providers()
    
    def _load_providers(self) -> Dict:
        """加载所有服务商配置"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.服务商, m.API地址, m.API密钥, m.模型名称, m.id
            FROM 模型配置表 m
            WHERE m.在线状态 = '正常'
            ORDER BY m.服务商
        ''')
        
        providers = {}
        for row in cursor.fetchall():
            provider = row[0]
            if provider not in providers:
                providers[provider] = []
            providers[provider].append({
                'api': row[1],
                'key': row[2],
                'model': row[3],
                'config_id': row[4]
            })
        
        conn.close()
        return providers
    
    def get_models_for_intent(self, intent: str, model_count: int) -> List[Dict]:
        """根据意图选择不同服务商的模型"""
        selected = []
        provider_list = list(self.providers.keys())
        random.shuffle(provider_list)
        
        for i in range(min(model_count, len(provider_list))):
            provider = provider_list[i]
            models = self.providers[provider]
            model = models[i % len(models)]
            
            selected.append({
                'provider': provider,
                'model_name': model['model'],
                'api': model['api'],
                'key': model['key']
            })
        
        return selected


class AdaptiveComboEngineV2:
    """序境自适应组合技能引擎V2 - 防限流版"""
    
    def __init__(self):
        self.provider_manager = MultiProviderManager()
        
        # 意图分析规则
        self.intent_rules = {
            'create': {'models': 2},
            'analyze': {'models': 2},
            'research': {'models': 2},
            'discuss': {'models': 3},
            'code': {'models': 2},
            'default': {'models': 1}
        }
    
    def analyze_intent(self, user_message: str) -> Dict:
        """分析用户需求意图"""
        message = user_message.lower()
        
        intent = 'default'
        if any(w in message for w in ['写', '创作', '生成', '制作', '诗', '文章']):
            intent = 'create'
        elif any(w in message for w in ['分析', '研究', '调查', '优势', '特点']):
            intent = 'analyze'
        elif any(w in message for w in ['讨论', '开会', '研讨', '会议']):
            intent = 'discuss'
        elif any(w in message for w in ['代码', '编程', '开发', '函数']):
            intent = 'code'
        
        strategy = self.intent_rules.get(intent, self.intent_rules['default'])
        
        return {
            'intent': intent,
            'model_count': strategy['models'],
            'message': user_message
        }
    
    def get_role_config(self, role_id: str) -> Optional[Dict]:
        """获取角色配置"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.id, r.姓名, m.API地址, m.API密钥, m.模型名称, m.服务商
            FROM 官署角色表 r
            JOIN 模型配置表 m ON r.模型配置表_ID = m.id
            WHERE r.id = ?
        ''', (role_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'api': row[2],
                'key': row[3],
                'model': row[4],
                'provider': row[5]
            }
        return None
    
    def adaptive_process(self, user_message: str) -> Dict:
        """自适应处理流程 - 防限流版"""
        print('=' * 60)
        print('序境自适应组合技能引擎 V2 (多服务商防限流)')
        print('=' * 60)
        print()
        
        # Step 1: 需求分析
        print('[1/3] 需求分析')
        print('-' * 40)
        
        intent_result = self.analyze_intent(user_message)
        
        print('  意图: ' + intent_result['intent'])
        print('  模型数: ' + str(intent_result['model_count']))
        print()
        
        # Step 2: 多服务商组合技能
        print('[2/3] 多服务商组合技能')
        print('-' * 40)
        
        # 获取不同服务商的模型
        models = self.provider_manager.get_models_for_intent(
            intent_result['intent'],
            intent_result['model_count']
        )
        
        print('  使用服务商:')
        for m in models:
            print('    - ' + m['provider'] + ': ' + m['model_name'])
        print()
        
        # 模拟调用 (实际需要API调用)
        results = []
        total_tokens = 0
        
        for i, m in enumerate(models):
            # 模拟API调用
            tokens = random.randint(100, 500)
            total_tokens += tokens
            results.append({
                'provider': m['provider'],
                'model': m['model_name'],
                'tokens': tokens,
                'status': 'ok'
            })
            print('  ✓ ' + m['provider'] + ': ' + str(tokens) + ' tokens')
        
        print()
        
        # Step 3: 交付回话
        print('[3/3] 交付回话')
        print('-' * 40)
        print('  多服务商组合完成')
        print()
        
        return {
            'status': 'ok',
            'intent': intent_result['intent'],
            'providers_used': [m['provider'] for m in models],
            'models_used': [m['model_name'] for m in models],
            'results': results,
            'total_tokens': total_tokens,
            'engine': '双引擎组合 (多服务商防限流)'
        }


# 全局实例
_adaptive_engine_v2 = None


def get_adaptive_engine_v2() -> AdaptiveComboEngineV2:
    """获取V2引擎"""
    global _adaptive_engine_v2
    if _adaptive_engine_v2 is None:
        _adaptive_engine_v2 = AdaptiveComboEngineV2()
    return _adaptive_engine_v2
