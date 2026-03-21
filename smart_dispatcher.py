# -*- coding: utf-8 -*-
"""
序境系统 - 智能调度执行器
集成意图分析 + 安全检测 + Tokens计算
"""
import sys
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony')

from intent_analyzer import IntentAnalyzer
from safety_checker import intercept as safety_check
from token_calculator import calculate, get_summary

class SmartDispatcher:
    """智能调度执行器"""
    
    def __init__(self):
        self.intent_analyzer = IntentAnalyzer()
        self.execution_log = []
    
    def dispatch(self, user_input, params=None):
        """智能调度"""
        # 1. 意图分析
        intent_result = self.intent_analyzer.analyze(user_input)
        intent = intent_result['意图']
        
        # 2. 安全检测
        if intent == '删除':
            safe, risk, msg = safety_check('DELETE', params or {})
        elif intent == '新增':
            safe, risk, msg = safety_check('INSERT', params or {})
        elif intent == '修改':
            safe, risk, msg = safety_check('UPDATE', params or {})
        else:
            safe, risk, msg = True, 'NONE', '通过'
        
        # 3. 记录执行
        record = {
            'input': user_input,
            'intent': intent,
            'safe': safe,
            'risk': risk,
            'message': msg
        }
        
        self.execution_log.append(record)
        
        return {
            'intent': intent,
            'allowed': safe,
            'risk': risk,
            'message': msg
        }
    
    def get_log(self):
        """获取执行日志"""
        return self.execution_log
    
    def get_summary(self):
        """获取汇总"""
        return get_summary()

# 全局实例
_dispatcher = SmartDispatcher()

def dispatch(user_input, params=None):
    """智能调度"""
    return _dispatcher.dispatch(user_input, params)

def get_log():
    """获取日志"""
    return _dispatcher.get_log()

if __name__ == '__main__':
    # 测试
    print('[智能调度测试]')
    
    result = dispatch('删除 模型', {'服务商': '测试', '模型标识符': 'test'})
    print(f'意图: {result[\"intent\"]}, 允许: {result[\"allowed\"]}, 风险: {result[\"risk\"]}')
    
    result = dispatch('新增 模型', {'服务商': '智谱', '模型标识符': 'GLM-4'})
    print(f'意图: {result[\"intent\"]}, 允许: {result[\"allowed\"]}, 风险: {result[\"risk\"]}')
    
    print('\n执行日志:')
    for log in get_log():
        print(f'  {log}')
