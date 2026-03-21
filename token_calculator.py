# -*- coding: utf-8 -*-
"""
序境系统 - Tokens计算模块
执行阶段汇报Tokens消耗
"""
import sqlite3
from datetime import datetime

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

class TokenCalculator:
    """Tokens计算器"""
    
    def __init__(self):
        self.usage_records = []
    
    def calculate(self, model_name, provider, prompt_tokens, completion_tokens):
        """计算Tokens消耗"""
        total = prompt_tokens + completion_tokens
        
        record = {
            'model': model_name,
            'provider': provider,
            'prompt': prompt_tokens,
            'completion': completion_tokens,
            'total': total,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.usage_records.append(record)
        return record
    
    def get_summary(self):
        """获取汇总"""
        if not self.usage_records:
            return {'total': 0, 'count': 0}
        
        total = sum(r['total'] for r in self.usage_records)
        return {
            'total': total,
            'count': len(self.usage_records),
            'records': self.usage_records
        }
    
    def get_provider_summary(self):
        """按服务商汇总"""
        summary = {}
        for r in self.usage_records:
            p = r['provider']
            if p not in summary:
                summary[p] = 0
            summary[p] += r['total']
        return summary

# 全局实例
_calculator = TokenCalculator()

def calculate(model_name, provider, prompt_tokens, completion_tokens):
    """计算Tokens"""
    return _calculator.calculate(model_name, provider, prompt_tokens, completion_tokens)

def get_summary():
    """获取汇总"""
    return _calculator.get_summary()

def get_provider_summary():
    """按服务商汇总"""
    return _calculator.get_provider_summary()

if __name__ == '__main__':
    # 测试
    print('[Token计算测试]')
    
    calculate('GLM-4.7', '智谱', 1000, 500)
    calculate('doubao-seed-2.0-code', '火山引擎', 2000, 800)
    
    print(f'总消耗: {get_summary()[\"total\"]} tokens')
    print(f'服务商汇总: {get_provider_summary()}')
