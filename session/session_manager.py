# -*- coding: utf-8 -*-
"""
序境系统 - 多模型反馈会话管理系统
实现任务执行后的反馈会话对话功能
"""
import sqlite3
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class SessionManager:
    """会话管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_tables()
    
    def _init_tables(self):
        """初始化数据表"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 任务会话表
        c.execute('''
            CREATE TABLE IF NOT EXISTS 任务会话表 (
                会话id TEXT PRIMARY KEY,
                用户id TEXT,
                创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                状态 TEXT DEFAULT 'pending',
                总模型数 INTEGER DEFAULT 0,
                成功数 INTEGER DEFAULT 0,
                失败数 INTEGER DEFAULT 0,
                上下文 TEXT
            )
        ''')
        
        # 模型执行结果表
        c.execute('''
            CREATE TABLE IF NOT EXISTS 模型执行结果表 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                会话id TEXT,
                模型id TEXT,
                模型名称 TEXT,
                提示词 TEXT,
                响应内容 TEXT,
                延迟 REAL,
                tokens INTEGER,
                状态 TEXT,
                错误信息 TEXT,
                执行时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(会话id) REFERENCES 任务会话表(会话id)
            )
        ''')
        
        # 对话轮次表
        c.execute('''
            CREATE TABLE IF NOT EXISTS 对话轮次表 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                会话id TEXT,
                轮次序号 INTEGER,
                用户输入 TEXT,
                聚合响应 TEXT,
                执行时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(会话id) REFERENCES 任务会话表(会话id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_session(self, user_id: str, total_models: int = 1) -> str:
        """创建新会话"""
        session_id = f"session_{int(time.time() * 1000)}"
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO 任务会话表 (会话id, 用户id, 状态, 总模型数)
            VALUES (?, ?, ?, ?)
        ''', (session_id, user_id, TaskStatus.PENDING.value, total_models))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def update_session_status(self, session_id: str, status: TaskStatus, 
                            success_count: int = 0, failed_count: int = 0):
        """更新会话状态"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            UPDATE 任务会话表 
            SET 状态=?, 成功数=?, 失败数=?
            WHERE 会话id=?
        ''', (status.value, success_count, failed_count, session_id))
        
        conn.commit()
        conn.close()
    
    def record_model_result(self, session_id: str, model_id: str, model_name: str,
                          prompt: str, response: str, latency: float, 
                          tokens: int, status: str, error: str = None):
        """记录模型执行结果"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO 模型执行结果表 
            (会话id, 模型id, 模型名称, 提示词, 响应内容, 延迟, tokens, 状态, 错误信息)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, model_id, model_name, prompt, response, latency, 
              tokens, status, error))
        
        conn.commit()
        conn.close()
    
    def record_conversation_turn(self, session_id: str, user_input: str, 
                                 aggregated_response: str) -> int:
        """记录对话轮次"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 获取当前轮次序号
        c.execute('SELECT MAX(轮次序号) FROM 对话轮次表 WHERE 会话id=?', (session_id,))
        max_turn = c.fetchone()[0] or 0
        turn_number = max_turn + 1
        
        c.execute('''
            INSERT INTO 对话轮次表 (会话id, 轮次序号, 用户输入, 聚合响应)
            VALUES (?, ?, ?, ?)
        ''', (session_id, turn_number, user_input, aggregated_response))
        
        conn.commit()
        conn.close()
        
        return turn_number
    
    def get_session_status(self, session_id: str) -> Optional[Dict]:
        """获取会话状态"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT 会话id, 用户id, 状态, 总模型数, 成功数, 失败数, 创建时间
            FROM 任务会话表 WHERE 会话id=?
        ''', (session_id,))
        
        row = c.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'session_id': row[0],
            'user_id': row[1],
            'status': row[2],
            'total_models': row[3],
            'success_count': row[4],
            'failed_count': row[5],
            'created_at': row[6]
        }
    
    def get_model_results(self, session_id: str) -> List[Dict]:
        """获取会话中所有模型执行结果"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT 模型id, 模型名称, 延迟, tokens, 状态, 错误信息, 执行时间
            FROM 模型执行结果表 
            WHERE 会话id=?
            ORDER BY 执行时间
        ''', (session_id,))
        
        rows = c.fetchall()
        conn.close()
        
        results = []
        for r in rows:
            results.append({
                'model_id': r[0],
                'model_name': r[1],
                'latency': r[2],
                'tokens': r[3],
                'status': r[4],
                'error': r[5],
                'executed_at': r[6]
            })
        
        return results
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """获取会话对话历史"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT 轮次序号, 用户输入, 聚合响应, 执行时间
            FROM 对话轮次表
            WHERE 会话id=?
            ORDER BY 轮次序号
        ''', (session_id,))
        
        rows = c.fetchall()
        conn.close()
        
        history = []
        for r in rows:
            history.append({
                'turn': r[0],
                'user_input': r[1],
                'response': r[2],
                'timestamp': r[3]
            })
        
        return history
    
    def get_full_session_data(self, session_id: str) -> Dict:
        """获取完整会话数据"""
        session = self.get_session_status(session_id)
        if not session:
            return {}
        
        results = self.get_model_results(session_id)
        history = self.get_conversation_history(session_id)
        
        return {
            'session': session,
            'model_results': results,
            'conversation_history': history
        }


class ResultAggregator:
    """结果聚合器"""
    
    @staticmethod
    def aggregate_responses(results: List[Dict]) -> str:
        """聚合多个模型的响应"""
        if not results:
            return ""
        
        # 只取成功的响应
        successful = [r for r in results if r.get('status') == 'success']
        
        if not successful:
            return "所有模型执行均失败"
        
        # 如果只有一个，直接返回
        if len(successful) == 1:
            return successful[0].get('response', '')
        
        # 多个结果，拼接展示
        aggregated = "【多模型响应汇总】\n\n"
        
        for i, r in enumerate(successful, 1):
            model_name = r.get('model_name', 'Unknown')
            response = r.get('response', '')
            latency = r.get('latency', 0)
            
            aggregated += f"--- 模型{i}: {model_name} (延迟:{latency:.2f}s) ---\n"
            aggregated += f"{response}\n\n"
        
        return aggregated.strip()
    
    @staticmethod
    def get_execution_summary(results: List[Dict]) -> Dict:
        """获取执行摘要"""
        total = len(results)
        success = len([r for r in results if r.get('status') == 'success'])
        failed = len([r for r in results if r.get('status') == 'failed'])
        
        avg_latency = 0
        total_tokens = 0
        
        for r in results:
            if r.get('latency'):
                avg_latency += r.get('latency', 0)
            if r.get('tokens'):
                total_tokens += r.get('tokens', 0)
        
        if total > 0:
            avg_latency /= total
        
        return {
            'total_models': total,
            'success_count': success,
            'failed_count': failed,
            'success_rate': f"{(success/total*100):.1f}%",
            'avg_latency': f"{avg_latency:.2f}s",
            'total_tokens': total_tokens
        }


# 测试
if __name__ == '__main__':
    db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
    manager = SessionManager(db_path)
    
    # 创建测试会话
    session_id = manager.create_session("test_user", total_models=3)
    print(f"创建会话: {session_id}")
    
    # 记录模型结果
    manager.record_model_result(
        session_id=session_id,
        model_id="1",
        model_name="Llama 3.2",
        prompt="你好",
        response="Hello!",
        latency=1.2,
        tokens=50,
        status="success"
    )
    
    manager.record_model_result(
        session_id=session_id,
        model_id="2", 
        model_name="Mistral",
        prompt="你好",
        response="Hi there!",
        latency=0.8,
        tokens=45,
        status="success"
    )
    
    # 更新会话状态
    manager.update_session_status(session_id, TaskStatus.COMPLETED, success_count=2, failed_count=0)
    
    # 记录对话
    turn = manager.record_conversation_turn(session_id, "你好", "Hello! Hi there!")
    print(f"对话轮次: {turn}")
    
    # 获取完整数据
    data = manager.get_full_session_data(session_id)
    print("\n=== 完整会话数据 ===")
    print(f"状态: {data['session']['status']}")
    print(f"模型结果: {len(data['model_results'])}")
    print(f"对话历史: {len(data['conversation_history'])}")
    
    # 结果聚合测试
    aggregator = ResultAggregator()
    summary = aggregator.get_execution_summary(data['model_results'])
    print(f"\n执行摘要: {summary}")
