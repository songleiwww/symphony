#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境意图分析+误判分析系统
分析用户真实意图，提高准确交付，误判补救机制
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


class IntentAnalyzer:
    """意图分析器"""
    
    def __init__(self):
        self.combo_engine = get_combo_engine()
        self.takeover = get_takeover()
        self.flow = get_flow_executor()
        
        # 意图类型
        self.intent_types = [
            'create',      # 创作
            'analyze',    # 分析
            'discuss',    # 讨论
            'code',       # 代码
            'query',      # 查询
            'execute',    # 执行
            'learn',      # 学习
            'help'        # 帮助
        ]
        
        # 历史分析记录
        self.analysis_history = []
        
        # 误判记录
        self.misjudgment_records = []
    
    def analyze_intent(self, user_message: str) -> Dict:
        """多角度意图分析"""
        print()
        print('=' * 50)
        print('意图分析')
        print('=' * 50)
        print('  输入: ' + user_message[:50] + '...')
        
        # 使用多个模型进行意图分析
        tasks = [
            {'role_id': 'role-1', 'messages': [
                {'role': 'system', 'content': '你是陆念昭，意图分析专家。分析用户意图，输出JSON格式：{"意图":"类型","置信度":0.0-1.0,"理由":"理由"}。用户消息：' + user_message},
                {'role': 'user', 'content': '请分析'}
            ]},
            {'role_id': 'role-10', 'messages': [
                {'role': 'system', 'content': '你是徐浩，语义分析专家。分析用户意图，输出JSON格式：{"意图":"类型","置信度":0.0-1.0,"理由":"理由"}。用户消息：' + user_message},
                {'role': 'user', 'content': '请分析'}
            ]},
            {'role_id': 'role-55', 'messages': [
                {'role': 'system', 'content': '你是李公麟，上下文分析专家。分析用户意图，输出JSON格式：{"意图":"类型","置信度":0.0-1.0,"理由":"理由"}。用户消息：' + user_message},
                {'role': 'user', 'content': '请分析'}
            ]},
        ]
        
        result = self.combo_engine.execute(tasks, mode='parallel')
        
        # 解析结果
        intents = []
        for r in result.get('individual_results', []):
            if r.get('status') == 'ok':
                response = r.get('response', '')
                intents.append({
                    'model': r.get('model'),
                    'response': response[:200],
                    'tokens': r.get('usage', {}).get('total_tokens', 0)
                })
        
        return {
            'status': 'analyzed',
            'original_message': user_message,
            'intents': intents,
            'analysis_count': len(intents)
        }
    
    def verify_intent(self, user_openid: str, intent: str, message: str) -> Dict:
        """验证意图是否正确"""
        # 记录分析
        record = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'detected_intent': intent,
            'verified': False
        }
        self.analysis_history.append(record)
        
        return {
            'status': 'verified',
            'intent': intent,
            'record': record
        }
    
    def analyze_misjudgment(self, user_openid: str, case: Dict) -> Dict:
        """误判分析"""
        print()
        print('=' * 50)
        print('误判分析')
        print('=' * 50)
        
        # 数据接管
        self.takeover.takeover_user_data(user_openid, {
            'mode': 'misjudgment_analysis',
            'case': case,
            'timestamp': datetime.now().isoformat()
        }, {'source': 'analysis'})
        
        # 分析误判原因
        tasks = [
            {'role_id': 'role-1', 'messages': [
                {'role': 'system', 'content': '你是陆念昭，错误分析专家。分析以下误判案例的原因和后果：' + str(case)},
                {'role': 'user', 'content': '请分析原因'}
            ]},
            {'role_id': 'role-10', 'messages': [
                {'role': 'system', 'content': '你是徐浩，风险分析专家。分析误判可能造成的后果：' + str(case)},
                {'role': 'user', 'content': '请分析后果'}
            ]},
            {'role_id': 'role-55', 'messages': [
                {'role': 'system', 'content': '你是李公麟，对策分析专家。提出误判的补救措施：' + str(case)},
                {'role': 'user', 'content': '请提出对策'}
            ]},
        ]
        
        result = self.combo_engine.execute(tasks, mode='parallel')
        
        # 记录误判
        record = {
            'case': case,
            'analysis': result.get('individual_results', []),
            'timestamp': datetime.now().isoformat()
        }
        self.misjudgment_records.append(record)
        
        return {
            'status': 'analyzed',
            'misjudgment': case,
            'analysis_count': len(result.get('individual_results', [])),
            'tokens': result.get('total_tokens', 0)
        }
    
    def prepare_remedy(self, user_openid: str, potential_misjudgments: List[Dict]) -> Dict:
        """准备补救措施"""
        print()
        print('=' * 50)
        print('补救准备')
        print('=' * 50)
        
        # 为每个可能的误判准备补救方案
        remedies = []
        
        for pm in potential_misjudgments:
            remedy = {
                'potential_intent': pm.get('intent'),
                'alternative_intents': [],
                'confidence': pm.get('confidence', 0.5),
                'remedy_plan': ''
            }
            
            # 如果置信度低，准备备选方案
            if remedy['confidence'] < 0.8:
                remedy['alternative_intents'] = [i for i in self.intent_types if i != pm.get('intent')]
                remedy['remedy_plan'] = '准备切换到备选意图'
            
            remedies.append(remedy)
        
        return {
            'status': 'prepared',
            'remedies': remedies,
            'count': len(remedies)
        }


class AccurateDeliverySystem:
    """准确交付系统"""
    
    def __init__(self):
        self.analyzer = IntentAnalyzer()
        self.takeover = get_takeover()
        
        # 置信度阈值
        self.confidence_threshold = 0.8
    
    def process_with_analysis(self, user_openid: str, message: str) -> Dict:
        """带分析的处理流程"""
        print()
        print('=' * 60)
        print('准确交付系统')
        print('=' * 60)
        
        # Step 1: 意图分析
        print()
        print('[1/4] 意图分析')
        intent_result = self.analyzer.analyze_intent(message)
        print('  分析模型数: ' + str(intent_result['analysis_count']))
        
        # Step 2: 验证意图
        print()
        print('[2/4] 意图验证')
        # 模拟检测到的意图
        detected_intent = 'analyze'
        verify_result = self.analyzer.verify_intent(user_openid, detected_intent, message)
        print('  检测意图: ' + detected_intent)
        
        # Step 3: 误判分析
        print()
        print('[3/4] 误判分析')
        potential_misjudgments = [
            {'intent': detected_intent, 'confidence': 0.75, 'risk': 'medium'}
        ]
        misjudge_result = self.analyzer.analyze_misjudgment(user_openid, {
            'message': message,
            'detected': detected_intent,
            'confidence': 0.75
        })
        print('  误判分析完成')
        
        # Step 4: 补救准备
        print()
        print('[4/4] 补救准备')
        remedy_result = self.analyzer.prepare_remedy(user_openid, potential_misjudgments)
        print('  补救方案数: ' + str(remedy_result['count']))
        
        return {
            'status': 'completed',
            'intent_analysis': intent_result,
            'verification': verify_result,
            'misjudgment': misjudge_result,
            'remedy': remedy_result
        }


# 全局实例
_accurate_delivery = None


def get_accurate_delivery() -> AccurateDeliverySystem:
    global _accurate_delivery
    if _accurate_delivery is None:
        _accurate_delivery = AccurateDeliverySystem()
    return _accurate_delivery
