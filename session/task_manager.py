# -*- coding: utf-8 -*-
"""
序境系统 - 任务管理器
整合多模型调度与反馈会话系统
"""
import sqlite3
import requests
import time
import json
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from session.session_manager import SessionManager, TaskStatus, ResultAggregator
from dispatcher_unified import UnifiedDispatcher

class TaskManager:
    """
    任务管理器 - 多模型任务执行与反馈系统
    
    功能:
    1. 创建任务会话
    2. 多模型并行执行
    3. 实时反馈执行进度
    4. 结果聚合与汇总
    5. 支持多轮对话
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.session_manager = SessionManager(db_path)
        self.dispatcher = UnifiedDispatcher(db_path)
    
    def execute_task(self, user_id: str, prompt: str, model_count: int = 3) -> Dict:
        """
        执行多模型任务
        
        参数:
            user_id: 用户ID
            prompt: 用户输入
            model_count: 使用模型数量
        
        返回:
            包含执行结果的字典
        """
        # 1. 获取在线模型
        online_models = self.dispatcher.get_online_models(max_check=model_count)
        
        if not online_models:
            return {
                'success': False,
                'error': '无可用模型'
            }
        
        # 2. 创建任务会话
        session_id = self.session_manager.create_session(user_id, total_models=len(online_models))
        self.session_manager.update_session_status(session_id, TaskStatus.RUNNING)
        
        # 3. 并行执行多模型
        results = self._execute_models_parallel(online_models[:model_count], prompt)
        
        # 4. 记录结果
        success_count = 0
        failed_count = 0
        
        for result in results:
            self.session_manager.record_model_result(
                session_id=session_id,
                model_id=result.get('model_id', ''),
                model_name=result.get('model', ''),
                prompt=prompt,
                response=result.get('content', ''),
                latency=result.get('latency', 0),
                tokens=result.get('tokens', 0),
                status='success' if result.get('success') else 'failed',
                error=result.get('error')
            )
            
            if result.get('success'):
                success_count += 1
            else:
                failed_count += 1
        
        # 5. 聚合响应
        aggregated = ResultAggregator.aggregate_responses(results)
        
        # 6. 记录对话轮次
        turn = self.session_manager.record_conversation_turn(
            session_id, prompt, aggregated
        )
        
        # 7. 更新会话状态
        status = TaskStatus.COMPLETED if success_count > 0 else TaskStatus.FAILED
        self.session_manager.update_session_status(
            session_id, status, success_count, failed_count
        )
        
        # 8. 获取执行摘要
        summary = ResultAggregator.get_execution_summary(results)
        
        return {
            'success': success_count > 0,
            'session_id': session_id,
            'turn': turn,
            'response': aggregated,
            'model_results': results,
            'summary': summary
        }
    
    def _execute_models_parallel(self, models: List[Dict], prompt: str) -> List[Dict]:
        """并行执行多个模型"""
        results = []
        
        def call_model(model):
            return self.dispatcher._call_api(model, prompt)
        
        with ThreadPoolExecutor(max_workers=len(models)) as executor:
            futures = {executor.submit(call_model, m): m for m in models}
            
            for future in as_completed(futures):
                model = futures[future]
                try:
                    result = future.result()
                    result['model_id'] = model.get('id')
                    result['model'] = model.get('name')
                    results.append(result)
                except Exception as e:
                    results.append({
                        'success': False,
                        'model_id': model.get('id'),
                        'model': model.get('name'),
                        'error': str(e)
                    })
        
        return results
    
    def continue_conversation(self, session_id: str, user_input: str) -> Dict:
        """
        继续多轮对话
        
        参数:
            session_id: 会话ID
            user_input: 用户新输入
        
        返回:
            对话结果
        """
        # 检查会话是否存在
        session = self.session_manager.get_session_status(session_id)
        if not session:
            return {'success': False, 'error': '会话不存在'}
        
        # 获取对话历史作为上下文
        history = self.session_manager.get_conversation_history(session_id)
        
        # 构建上下文提示
        context_prompt = self._build_context_prompt(history, user_input)
        
        # 执行任务
        result = self.execute_task(session['user_id'], context_prompt, model_count=2)
        
        if result.get('success'):
            # 记录新轮次
            self.session_manager.record_conversation_turn(
                session_id, user_input, result['response']
            )
        
        return result
    
    def _build_context_prompt(self, history: List[Dict], current_input: str) -> str:
        """构建带上下文的提示"""
        prompt = "以下是之前的对话历史：\n\n"
        
        for h in history[-3:]:  # 只取最近3轮
            prompt += f"用户: {h['user_input']}\n"
            prompt += f"助手: {h['response'][:200]}...\n\n"
        
        prompt += f"用户最新问题: {current_input}\n"
        prompt += "请根据上下文回答。"
        
        return prompt
    
    def get_task_status(self, session_id: str) -> Dict:
        """获取任务状态"""
        return self.session_manager.get_full_session_data(session_id)
    
    def list_user_sessions(self, user_id: str, limit: int = 10) -> List[Dict]:
        """列出用户的所有会话"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT 会话id, 状态, 总模型数, 成功数, 失败数, 创建时间
            FROM 任务会话表
            WHERE 用户id=?
            ORDER BY 创建时间 DESC
            LIMIT ?
        ''', (user_id, limit))
        
        rows = c.fetchall()
        conn.close()
        
        sessions = []
        for r in rows:
            sessions.append({
                'session_id': r[0],
                'status': r[1],
                'total_models': r[2],
                'success_count': r[3],
                'failed_count': r[4],
                'created_at': r[5]
            })
        
        return sessions


# 测试
if __name__ == '__main__':
    db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
    manager = TaskManager(db_path)
    
    print("=== 多模型任务执行测试 ===\n")
    
    # 执行任务
    print("1. 执行多模型任务...")
    result = manager.execute_task("test_user", "请用一句话介绍你自己", model_count=3)
    
    if result.get('success'):
        print(f"   会话ID: {result['session_id']}")
        print(f"   执行轮次: {result['turn']}")
        print(f"   响应: {result['response'][:150]}...")
        print(f"   摘要: {result['summary']}")
        
        # 获取状态
        print("\n2. 获取任务状态...")
        status = manager.get_task_status(result['session_id'])
        print(f"   状态: {status['session']['status']}")
        print(f"   模型数: {len(status['model_results'])}")
        
        # 继续对话
        print("\n3. 继续对话...")
        cont = manager.continue_conversation(result['session_id'], "你是做什么的?")
        if cont.get('success'):
            print(f"   响应: {cont['response'][:100]}...")
    else:
        print(f"   失败: {result.get('error')}")
