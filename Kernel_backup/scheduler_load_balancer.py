# -*- coding: utf-8 -*-
"""
序境系统 - 智能负载均衡器
根据模型响应时间、成功率自动分配请求
"""
import sqlite3
import random
from datetime import datetime, timedelta

class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, db_path):
        self.db_path = db_path
    
    def get_model_score(self, model_id):
        """计算模型得分"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        score = 100  # 基础分
        
        # 检查故障记录
        c.execute('SELECT 失败次数 FROM 模型故障记录 WHERE 模型id=? AND 状态="active"', 
                 (str(model_id),))
        row = c.fetchone()
        if row:
            score -= row[0] * 20  # 每次失败扣20分
        
        # 检查历史响应时间（如果有统计表）
        c.execute('''SELECT AVG(响应时间) FROM 模型调用记录 
                     WHERE 模型id=? AND 调用时间 > datetime("now", "-1 hour")''', 
                 (str(model_id),))
        row = c.fetchone()
        if row and row[0]:
            avg_time = row[0]
            if avg_time < 1:  # <1秒
                score += 10
            elif avg_time > 10:  # >10秒
                score -= 10
        
        conn.close()
        return max(0, min(100, score))
    
    def select_model(self, tags=None, exclude_models=None):
        """选择最佳模型"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 基础查询
        query = 'SELECT id, 模型名称, 服务商 FROM 模型配置表 WHERE 是否启用="启用"'
        params = []
        
        if exclude_models:
            placeholders = ','.join(['?' for _ in exclude_models])
            query += f' AND id NOT IN ({placeholders})'
            params.extend([str(m) for m in exclude_models])
        
        c.execute(query, params)
        all_models = c.fetchall()
        
        if not all_models:
            conn.close()
            return None
        
        # 计算每个模型的得分
        model_scores = []
        for model in all_models:
            model_id = model[0]
            score = self.get_model_score(model_id)
            model_scores.append((model_id, model[1], model[2], score))
        
        # 按得分排序
        model_scores.sort(key=lambda x: x[3], reverse=True)
        
        conn.close()
        
        # 返回得分最高的模型
        return model_scores[0] if model_scores else None
    
    def get_provider_stats(self):
        """获取服务商统计"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT 服务商, COUNT(*) as count, 
                   (SELECT COUNT(*) FROM 模型故障记录 f 
                    JOIN 模型配置表 m ON f.模型id = m.id 
                    WHERE m.服务商 = p.服务商 AND f.状态="active") as failures
            FROM 模型配置表 p
            WHERE 是否启用="启用"
            GROUP BY 服务商
        ''')
        
        stats = c.fetchall()
        conn.close()
        
        return [(s[0], s[1], s[2] or 0) for s in stats]


if __name__ == '__main__':
    lb = LoadBalancer('C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db')
    
    # 测试选择模型
    selected = lb.select_model()
    if selected:
        print(f"推荐模型: {selected[1]} ({selected[2]}) - 得分: {selected[3]}")
    
    # 服务商统计
    print("\n服务商统计:")
    for p in lb.get_provider_stats():
        print(f"  {p[0]}: {p[1]}个模型, {p[2]}个故障")
