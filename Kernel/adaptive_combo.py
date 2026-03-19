#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境自适应组合技能引擎
数据接管 → 需求分析 → 组合技能处理 → 交付回话
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import sys

KERNEL_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KERNEL_PATH)

from combo_skill import get_combo_engine
from data_takeover import get_takeover
from flow_executor import get_flow_executor


class AdaptiveComboEngine:
    """序境自适应组合技能引擎"""
    
    def __init__(self):
        self.combo_engine = get_combo_engine()
        self.takeover = get_takeover()
        self.flow_executor = get_flow_executor()
        
        # 需求分析规则
        self.intent_rules = {
            'create': {'mode': 'parallel', 'models': 2},
            'analyze': {'mode': 'parallel', 'models': 2},
            'research': {'mode': 'sequential', 'models': 2},
            'discuss': {'mode': 'parallel', 'models': 3},
            'code': {'mode': 'parallel', 'models': 2},
            'default': {'mode': 'parallel', 'models': 1}
        }
    
    def analyze_intent(self, user_message: str) -> Dict:
        """分析用户需求意图"""
        message = user_message.lower()
        
        # 意图识别
        intent = 'default'
        if any(w in message for w in ['写', '创作', '生成', '制作']):
            intent = 'create'
        elif any(w in message for w in ['分析', '研究', '调查']):
            intent = 'analyze'
        elif any(w in message for w in ['讨论', '开会', '研讨']):
            intent = 'discuss'
        elif any(w in message for w in ['代码', '编程', '开发']):
            intent = 'code'
        
        # 选择策略
        strategy = self.intent_rules.get(intent, self.intent_rules['default'])
        
        return {
            'intent': intent,
            'mode': strategy['mode'],
            'model_count': strategy['models'],
            'raw_message': user_message
        }
    
    def adaptive_process(self, user_openid: str, user_message: str) -> Dict:
        """自适应处理流程
        
        1. 接管数据
        2. 需求分析
        3. 组合技能处理
        4. 交付回话
        """
        print('=' * 60)
        print('序境自适应组合技能引擎')
        print('=' * 60)
        print()
        
        # Step 1: 数据接管
        print('[1/4] 数据接管')
        print('-' * 40)
        
        input_data = {
            'user_message': user_message,
            'timestamp': datetime.now().isoformat()
        }
        
        takeover_result = self.takeover.takeover_user_data(
            user_openid, 
            input_data,
            {'source': 'adaptive_process'}
        )
        
        print('  用户ID: ' + takeover_result['user_id'])
        print('  数据ID: ' + takeover_result['data_id'])
        print()
        
        # Step 2: 需求分析
        print('[2/4] 需求分析')
        print('-' * 40)
        
        intent_result = self.analyze_intent(user_message)
        
        print('  意图: ' + intent_result['intent'])
        print('  模式: ' + intent_result['mode'])
        print('  模型数: ' + str(intent_result['model_count']))
        print()
        
        # Step 3: 组合技能处理
        print('[3/4] 组合技能处理')
        print('-' * 40)
        
        # 根据意图选择模型
        role_ids = ['role-1', 'role-10', 'role-55'][:intent_result['model_count']]
        
        tasks = []
        for role_id in role_ids:
            tasks.append({
                'role_id': role_id,
                'messages': [
                    {'role': 'system', 'content': '你是序境官员。请回应用户需求。'},
                    {'role': 'user', 'content': user_message}
                ]
            })
        
        # 执行组合技能
        if intent_result['mode'] == 'sequential':
            combo_result = self.combo_engine.execute(tasks, mode='sequential')
        else:
            combo_result = self.combo_engine.execute(tasks, mode='parallel')
        
        print('  执行结果:')
        for r in combo_result['individual_results']:
            status = 'OK' if r.get('status') == 'ok' else 'FAIL'
            model = r.get('model', 'unknown')
            tokens = r.get('usage', {}).get('total_tokens', 0)
            print('    ' + status + ' ' + model + ': ' + str(tokens) + ' tokens')
        print()
        
        # Step 4: 交付回话
        print('[4/4] 交付回话')
        print('-' * 40)
        
        # 汇总回复
        responses = []
        for r in combo_result['individual_results']:
            if r.get('status') == 'ok':
                responses.append({
                    'model': r.get('model', ''),
                    'response': r.get('response', '')
                })
        
        # 构建最终回复
        final_response = self._build_response(user_message, responses, intent_result)
        
        print('  已生成回复')
        print()
        
        return {
            'status': 'ok',
            'intent': intent_result['intent'],
            'mode': intent_result['mode'],
            'engine_used': '双引擎组合',
            'responses': responses,
            'final_response': final_response,
            'total_tokens': combo_result['total_tokens']
        }
    
    def _build_response(self, user_message: str, responses: List[Dict], intent: Dict) -> str:
        """构建最终回复"""
        response_text = ''
        
        if len(responses) == 1:
            response_text = responses[0]['response']
        else:
            response_text = '【序境自适应组合技能处理完成】\n\n'
            for i, r in enumerate(responses):
                response_text += '--- 模型 ' + str(i+1) + ': ' + r['model'] + ' ---\n'
                response_text += r['response'] + '\n\n'
        
        return response_text


# 全局实例
_adaptive_engine = None


def get_adaptive_engine() -> AdaptiveComboEngine:
    """获取自适应组合引擎"""
    global _adaptive_engine
    if _adaptive_engine is None:
        _adaptive_engine = AdaptiveComboEngine()
    return _adaptive_engine
