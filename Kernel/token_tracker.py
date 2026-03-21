# -*- coding: utf-8 -*-
"""
序境系统 - Token全链路记录系统
功能：
1. 完善Token生命周期追踪
2. 成本分析与可视化
3. 实时Token监控与告警
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# 数据库路径
DB_PATH = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'


class TokenLifecycleTracker:
    """Token全生命周期追踪器"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_tables()
    
    def _ensure_tables(self):
        """确保必要的表存在"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 完善Token使用记录表 - 添加更多字段
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Token使用记录表 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT,
                session_id TEXT,
                model_name TEXT,
                provider TEXT,
                prompt_tokens INTEGER DEFAULT 0,
                completion_tokens INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                input_cost REAL DEFAULT 0,
                output_cost REAL DEFAULT 0,
                total_cost REAL DEFAULT 0,
                latency_ms REAL DEFAULT 0,
                timestamp TEXT,
                status TEXT,
                error_message TEXT,
                context_tokens INTEGER DEFAULT 0,
                reasoning_tokens INTEGER DEFAULT 0,
                tool_calls INTEGER DEFAULT 0,
                version TEXT DEFAULT 'v1.0'
            )
        """)
        
        # Token成本配置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Token成本配置表 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                model_pattern TEXT NOT NULL,
                input_price_per_1k REAL DEFAULT 0,
                output_price_per_1k REAL DEFAULT 0,
                currency TEXT DEFAULT 'CNY',
                effective_date TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Token预算与告警表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Token预算告警表 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                budget_name TEXT NOT NULL,
                budget_type TEXT DEFAULT 'daily',
                budget_limit REAL DEFAULT 0,
                current_usage REAL DEFAULT 0,
                alert_threshold REAL DEFAULT 0.8,
                alert_sent BOOLEAN DEFAULT 0,
                start_date TEXT,
                end_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Token统计汇总表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Token统计汇总表 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stat_date TEXT NOT NULL,
                provider TEXT,
                total_prompt_tokens INTEGER DEFAULT 0,
                total_completion_tokens INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                total_cost REAL DEFAULT 0,
                request_count INTEGER DEFAULT 0,
                avg_latency_ms REAL DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(stat_date, provider)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def record_usage(self, 
                     task_id: str,
                     session_id: str,
                     model_name: str,
                     provider: str,
                     prompt_tokens: int,
                     completion_tokens: int,
                     latency_ms: float = 0,
                     status: str = 'success',
                     error_message: str = None,
                     context_tokens: int = 0,
                     reasoning_tokens: int = 0,
                     tool_calls: int = 0) -> int:
        """记录一次Token使用"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 计算成本
        cost_info = self._calculate_cost(provider, model_name, prompt_tokens, completion_tokens)
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO Token使用记录表 (
                task_id, session_id, model_name, provider,
                prompt_tokens, completion_tokens, total_tokens,
                input_cost, output_cost, total_cost, latency_ms,
                timestamp, status, error_message, context_tokens,
                reasoning_tokens, tool_calls
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_id, session_id, model_name, provider,
            prompt_tokens, completion_tokens, prompt_tokens + completion_tokens,
            cost_info['input_cost'], cost_info['output_cost'], cost_info['total_cost'],
            latency_ms, timestamp, status, error_message, context_tokens,
            reasoning_tokens, tool_calls
        ))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # 检查是否需要告警
        self._check_budget_alert(provider)
        
        return record_id
    
    def _calculate_cost(self, provider: str, model_name: str, 
                       prompt_tokens: int, completion_tokens: int) -> Dict[str, float]:
        """计算Token成本"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 查找成本配置
        cursor.execute("""
            SELECT input_price_per_1k, output_price_per_1k
            FROM Token成本配置表
            WHERE provider = ? AND model_pattern = ?
            ORDER BY effective_date DESC LIMIT 1
        """, (provider, model_name))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            input_price, output_price = row
        else:
            # 默认成本 (使用常见定价)
            input_price, output_price = self._get_default_price(provider, model_name)
        
        input_cost = (prompt_tokens / 1000) * input_price
        output_cost = (completion_tokens / 1000) * output_price
        
        return {
            'input_cost': round(input_cost, 6),
            'output_cost': round(output_cost, 6),
            'total_cost': round(input_cost + output_cost, 6)
        }
    
    def _get_default_price(self, provider: str, model_name: str) -> tuple:
        """获取默认定价"""
        default_prices = {
            '火山引擎': (0.0005, 0.002),      # Doubao
            '智谱': (0.0005, 0.002),          # GLM
            '英伟达': (0.001, 0.003),          # Llama
            '硅基流动': (0.0004, 0.0015),      # Qwen
            '魔搭': (0.0003, 0.001),           # 开源模型
            'Moonshot': (0.006, 0.018),        # Moonshot
        }
        
        for p, price in default_prices.items():
            if p in provider:
                return price
        
        return (0.001, 0.003)  # 默认
    
    def _check_budget_alert(self, provider: str):
        """检查预算告警"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 获取今日使用量
        cursor.execute("""
            SELECT SUM(total_cost) FROM Token使用记录表
            WHERE provider = ? AND date(timestamp) = ?
        """, (provider, today))
        
        current_usage = cursor.fetchone()[0] or 0
        
        # 检查告警
        cursor.execute("""
            SELECT id, budget_limit, alert_threshold, alert_sent
            FROM Token预算告警表
            WHERE budget_type = 'daily' AND alert_sent = 0
            AND start_date <= ? AND end_date >= ?
        """, (today, today))
        
        for row in cursor.fetchall():
            budget_id, budget_limit, threshold, alert_sent = row
            
            if current_usage >= budget_limit * threshold:
                # 发送告警
                print(f"⚠️ 告警: {provider} 今日成本 ${current_usage:.2f} 已超过预算 {threshold*100:.0f}%")
                
                cursor.execute("""
                    UPDATE Token预算告警表 SET alert_sent = 1 WHERE id = ?
                """, (budget_id,))
        
        conn.commit()
        conn.close()
    
    def get_lifecycle_summary(self, 
                               provider: str = None,
                               start_date: str = None,
                               end_date: str = None) -> Dict[str, Any]:
        """获取生命周期汇总"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT 
                provider,
                model_name,
                COUNT(*) as request_count,
                SUM(prompt_tokens) as total_prompt,
                SUM(completion_tokens) as total_completion,
                SUM(total_tokens) as total_tokens,
                SUM(total_cost) as total_cost,
                AVG(latency_ms) as avg_latency,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN status != 'success' THEN 1 ELSE 0 END) as error_count
            FROM Token使用记录表
            WHERE 1=1
        """
        params = []
        
        if provider:
            query += " AND provider = ?"
            params.append(provider)
        
        if start_date:
            query += " AND date(timestamp) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date(timestamp) <= ?"
            params.append(end_date)
        
        query += " GROUP BY provider, model_name ORDER BY total_cost DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        summary = []
        for row in rows:
            summary.append({
                'provider': row[0],
                'model_name': row[1],
                'request_count': row[2],
                'total_prompt_tokens': row[3] or 0,
                'total_completion_tokens': row[4] or 0,
                'total_tokens': row[5] or 0,
                'total_cost': round(row[6] or 0, 4),
                'avg_latency_ms': round(row[7] or 0, 2),
                'success_count': row[8],
                'error_count': row[9],
                'success_rate': round(row[8] / (row[2] or 1) * 100, 2)
            })
        
        conn.close()
        return summary
    
    def get_daily_trend(self, days: int = 7) -> List[Dict]:
        """获取每日趋势"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        cursor.execute("""
            SELECT 
                date(timestamp) as day,
                provider,
                SUM(total_tokens) as tokens,
                SUM(total_cost) as cost,
                COUNT(*) as requests
            FROM Token使用记录表
            WHERE timestamp >= ?
            GROUP BY day, provider
            ORDER BY day DESC
        """, (start_date.isoformat(),))
        
        rows = cursor.fetchall()
        conn.close()
        
        trend = []
        for row in rows:
            trend.append({
                'date': row[0],
                'provider': row[1],
                'total_tokens': row[2],
                'total_cost': round(row[3] or 0, 4),
                'request_count': row[4]
            })
        
        return trend
    
    def get_cost_breakdown(self, start_date: str = None, end_date: str = None) -> Dict:
        """获取成本分解"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT 
                provider,
                model_name,
                SUM(input_cost) as input_cost,
                SUM(output_cost) as output_cost,
                SUM(total_cost) as total_cost
            FROM Token使用记录表
            WHERE status = 'success'
        """
        params = []
        
        if start_date:
            query += " AND date(timestamp) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date(timestamp) <= ?"
            params.append(end_date)
        
        query += " GROUP BY provider, model_name ORDER BY total_cost DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        breakdown = {
            'by_provider': {},
            'by_model': {},
            'total': 0
        }
        
        for row in rows:
            provider = row[0]
            model = row[1]
            input_cost = row[2] or 0
            output_cost = row[3] or 0
            total = row[4] or 0
            
            # 按服务商汇总
            if provider not in breakdown['by_provider']:
                breakdown['by_provider'][provider] = 0
            breakdown['by_provider'][provider] += total
            
            # 按模型汇总
            if model not in breakdown['by_model']:
                breakdown['by_model'][model] = 0
            breakdown['by_model'][model] += total
            
            breakdown['total'] += total
        
        breakdown['total'] = round(breakdown['total'], 4)
        
        conn.close()
        return breakdown
    
    def set_cost_config(self, provider: str, model_pattern: str,
                       input_price: float, output_price: float,
                       currency: str = 'CNY', notes: str = None):
        """设置成本配置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        effective_date = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute("""
            INSERT INTO Token成本配置表 (
                provider, model_pattern, input_price_per_1k, output_price_per_1k,
                currency, effective_date, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (provider, model_pattern, input_price, output_price, currency, effective_date, notes))
        
        conn.commit()
        conn.close()
    
    def set_budget(self, budget_name: str, budget_type: str, budget_limit: float,
                  alert_threshold: float = 0.8, start_date: str = None, end_date: str = None):
        """设置预算"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        start_date = start_date or today
        end_date = end_date or (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        cursor.execute("""
            INSERT INTO Token预算告警表 (
                budget_name, budget_type, budget_limit, alert_threshold,
                start_date, end_date
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (budget_name, budget_type, budget_limit, alert_threshold, start_date, end_date))
        
        conn.commit()
        conn.close()


# 全局实例
_token_tracker = TokenLifecycleTracker()


def record_token_usage(task_id: str, session_id: str, model_name: str, provider: str,
                      prompt_tokens: int, completion_tokens: int, **kwargs):
    """记录Token使用"""
    return _token_tracker.record_usage(
        task_id, session_id, model_name, provider,
        prompt_tokens, completion_tokens, **kwargs
    )


def get_token_summary(provider: str = None, start_date: str = None, end_date: str = None):
    """获取Token汇总"""
    return _token_tracker.get_lifecycle_summary(provider, start_date, end_date)


def get_token_trend(days: int = 7):
    """获取Token趋势"""
    return _token_tracker.get_daily_trend(days)


def get_cost_breakdown(start_date: str = None, end_date: str = None):
    """获取成本分解"""
    return _token_tracker.get_cost_breakdown(start_date, end_date)


def configure_token_cost(provider: str, model_pattern: str, input_price: float, output_price: float):
    """配置Token成本"""
    _token_tracker.set_cost_config(provider, model_pattern, input_price, output_price)


def create_budget(budget_name: str, budget_limit: float, budget_type: str = 'daily'):
    """创建预算"""
    _token_tracker.set_budget(budget_name, budget_type, budget_limit)


if __name__ == '__main__':
    # 测试
    print("="*60)
    print("Token全链路记录系统 - 测试")
    print("="*60)
    
    # 记录一次使用
    record_id = record_token_usage(
        task_id='test_task_001',
        session_id='test_session_001',
        model_name='ark-code-latest',
        provider='火山引擎',
        prompt_tokens=1500,
        completion_tokens=500,
        latency_ms=2500,
        status='success'
    )
    print(f"✅ 记录ID: {record_id}")
    
    # 获取汇总
    summary = get_token_summary()
    print(f"\n📊 汇总信息:")
    for s in summary[:3]:
        print(f"  {s['provider']} - {s['model_name']}: {s['total_tokens']} tokens, ${s['total_cost']}")
    
    # 成本分解
    breakdown = get_cost_breakdown()
    print(f"\n💰 成本分解:")
    print(f"  总成本: ${breakdown['total']}")
    print(f"  按服务商: {breakdown['by_provider']}")
    
    print("\n✅ 测试完成")
