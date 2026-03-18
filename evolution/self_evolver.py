# -*- coding: utf-8 -*-
"""
序境系统 - 自我进化框架
收集使用数据，自动优化调度策略
"""
import sqlite3
import json
from datetime import datetime, timedelta

class SelfEvolver:
    """自我进化器"""
    
    def __init__(self, db_path):
        self.db_path = db_path
    
    def record_usage(self, model_id, prompt_length, response_length, 
                   response_time, success, error_type=None):
        """记录使用数据"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 创建使用记录表
        c.execute('''
            CREATE TABLE IF NOT EXISTS 模型使用记录 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                模型id TEXT,
                输入长度 INTEGER,
                输出长度 INTEGER,
                响应时间 REAL,
                是否成功 INTEGER,
                错误类型 TEXT,
                调用时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        c.execute('''INSERT INTO 模型使用记录 
                     (模型id, 输入长度, 输出长度, 响应时间, 是否成功, 错误类型)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                 (str(model_id), prompt_length, response_length, 
                  response_time, 1 if success else 0, error_type))
        
        conn.commit()
        conn.close()
    
    def analyze_patterns(self):
        """分析使用模式"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 分析成功率
        c.execute('''
            SELECT 模型id, 
                   COUNT(*) as total,
                   SUM(是否成功) as successes,
                   AVG(响应时间) as avg_time
            FROM 模型使用记录
            WHERE 调用时间 > datetime("now", "-24 hours")
            GROUP BY 模型id
        ''')
        
        results = c.fetchall()
        
        patterns = []
        for r in results:
            model_id = r[0]
            total = r[1]
            successes = r[2] or 0
            avg_time = r[3] or 0
            
            success_rate = (successes / total * 100) if total > 0 else 0
            
            patterns.append({
                'model_id': model_id,
                'total_calls': total,
                'success_rate': success_rate,
                'avg_response_time': avg_time,
                'recommendation': self._get_recommendation(success_rate, avg_time)
            })
        
        conn.close()
        return patterns
    
    def _get_recommendation(self, success_rate, avg_time):
        """获取建议"""
        if success_rate >= 95 and avg_time < 3:
            return '优先使用'
        elif success_rate >= 80:
            return '备用选择'
        else:
            return '建议优化'
    
    def suggest_optimizations(self):
        """建议优化"""
        patterns = self.analyze_patterns()
        
        suggestions = []
        
        for p in patterns:
            if p['success_rate'] < 80:
                suggestions.append({
                    'model': p['model_id'],
                    'issue': f"成功率仅{p['success_rate']:.1f}%",
                    'action': '检查API配置或更换模型'
                })
            
            if p['avg_response_time'] > 10:
                suggestions.append({
                    'model': p['model_id'],
                    'issue': f"响应时间{p['avg_response_time']:.1f}秒",
                    'action': '考虑使用更快的模型'
                })
        
        return suggestions
    
    def generate_rules(self):
        """生成优化规则"""
        suggestions = self.suggest_optimizations()
        
        rules = []
        
        # 基于分析生成规则
        for s in suggestions:
            rule = {
                'trigger': f"模型{s['model']}表现不佳",
                'action': s['action'],
                'priority': 5
            }
            rules.append(rule)
        
        return rules


if __name__ == '__main__':
    evolver = SelfEvolver('C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db')
    
    # 测试分析
    patterns = evolver.analyze_patterns()
    print("=== 使用模式分析 ===")
    for p in patterns[:5]:
        print(f"模型{p['model_id']}: 成功率{p['success_rate']:.1f}%, "
              f"平均响应{p['avg_response_time']:.1f}s - {p['recommendation']}")
    
    # 优化建议
    print("\n=== 优化建议 ===")
    for s in evolver.suggest_optimizations():
        print(f"  {s['model']}: {s['issue']} → {s['action']}")
