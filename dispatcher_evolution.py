# -*- coding: utf-8 -*-
"""
序境系统 - 调度能力自我进化
基于学习到的Self-Evolving技术改进调度系统
"""
import sqlite3
import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class AdaptiveDispatcher:
    """
    自适应调度器 - 进化版
    
    进化能力:
    1. 学习用户偏好 - 记录用户选择倾向
    2. 动态权重调整 - 根据成功率自动调整模型权重
    3. 智能路由 - 根据任务类型匹配合适模型
    4. 故障预测 - 基于历史预测模型可用性
    5. 负载感知 - 考虑模型响应速度动态调整
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.model_weights = {}  # 模型权重
        self.success_history = defaultdict(list)  # 成功历史
        self.failure_history = defaultdict(list)  # 失败历史
        self.user_preferences = {}  # 用户偏好
        self.load_weights()
    
    def load_weights(self):
        """从数据库加载权重"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            # 尝试加载模型权重表
            c.execute('SELECT 模型id, 权重, 成功次数, 失败次数 FROM 模型权重表')
            rows = c.fetchall()
            
            for r in rows:
                self.model_weights[r[0]] = {
                    'weight': r[1] if r[1] else 1.0,
                    'success_count': r[2] if r[2] else 0,
                    'failure_count': r[3] if r[3] else 0
                }
        except:
            # 表不存在，创建它
            c.execute('''
                CREATE TABLE IF NOT EXISTS 模型权重表 (
                    模型id TEXT PRIMARY KEY,
                    权重 REAL DEFAULT 1.0,
                    成功次数 INTEGER DEFAULT 0,
                    失败次数 INTEGER DEFAULT 0,
                    最后更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        
        conn.close()
    
    def save_weights(self):
        """保存权重到数据库"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        for model_id, data in self.model_weights.items():
            c.execute('''
                INSERT OR REPLACE INTO 模型权重表 (模型id, 权重, 成功次数, 失败次数, 最后更新时间)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (model_id, data.get('weight', 1.0), 
                  data.get('success_count', 0), 
                  data.get('failure_count', 0)))
        
        conn.commit()
        conn.close()
    
    def record_success(self, model_id: str, latency: float, tokens: int):
        """记录成功"""
        if model_id not in self.model_weights:
            self.model_weights[model_id] = {'weight': 1.0, 'success_count': 0, 'failure_count': 0}
        
        self.model_weights[model_id]['success_count'] += 1
        self.model_weights[model_id]['weight'] = min(10.0, self.model_weights[model_id]['weight'] * 1.05)
        
        self.success_history[model_id].append({
            'latency': latency,
            'tokens': tokens,
            'timestamp': time.time()
        })
        
        # 保留最近100条
        if len(self.success_history[model_id]) > 100:
            self.success_history[model_id] = self.success_history[model_id][-100:]
        
        self.save_weights()
    
    def record_failure(self, model_id: str, error: str):
        """记录失败"""
        if model_id not in self.model_weights:
            self.model_weights[model_id] = {'weight': 1.0, 'success_count': 0, 'failure_count': 0}
        
        self.model_weights[model_id]['failure_count'] += 1
        self.model_weights[model_id]['weight'] = max(0.1, self.model_weights[model_id]['weight'] * 0.8)
        
        self.failure_history[model_id].append({
            'error': error,
            'timestamp': time.time()
        })
        
        if len(self.failure_history[model_id]) > 100:
            self.failure_history[model_id] = self.failure_history[model_id][-100:]
        
        self.save_weights()
    
    def get_model_score(self, model: Dict) -> float:
        """计算模型综合评分"""
        model_id = model.get('id', model.get('name', ''))
        
        # 基础权重
        weight = self.model_weights.get(model_id, {}).get('weight', 1.0)
        
        # 成功率调整
        data = self.model_weights.get(model_id, {})
        success = data.get('success_count', 0)
        failure = data.get('failure_count', 0)
        total = success + failure
        
        if total > 0:
            success_rate = success / total
        else:
            success_rate = 0.5
        
        # 延迟惩罚
        latency = model.get('latency', 1.0)
        latency_score = 1.0 / (1.0 + latency)
        
        # 综合评分
        score = weight * (0.5 + success_rate * 0.3 + latency_score * 0.2)
        
        return score
    
    def select_best_models(self, online_models: List[Dict], count: int, 
                         task_type: str = None, user_id: str = None) -> List[Dict]:
        """
        智能选择最佳模型
        
        策略:
        1. 考虑模型权重
        2. 考虑成功率
        3. 考虑延迟
        4. 考虑任务类型匹配
        5. 考虑用户偏好
        """
        scored = []
        
        for model in online_models:
            score = self.get_model_score(model)
            
            # 任务类型匹配加分
            if task_type and model.get('type'):
                if task_type in str(model.get('type', '')).lower():
                    score *= 1.2
            
            # 用户偏好加分
            if user_id and user_id in self.user_preferences:
                preferred = self.user_preferences[user_id]
                if model.get('provider') in preferred.get('providers', []):
                    score *= 1.1
            
            scored.append((score, model))
        
        # 按评分排序
        scored.sort(key=lambda x: x[0], reverse=True)
        
        return [m for _, m in scored[:count]]
    
    def learn_user_preference(self, user_id: str, selected_model: str, success: bool):
        """学习用户偏好"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                'providers': [],
                'model_choices': defaultdict(int)
            }
        
        if success:
            self.user_preferences[user_id]['model_choices'][selected_model] += 1
    
    def analyze_and_evolve(self):
        """
        自我分析并进化
        分析当前调度策略的问题并调整
        """
        logger.info("=== 调度能力自我进化 ===")
        
        # 1. 分析失败模式
        for model_id, failures in self.failure_history.items():
            if len(failures) >= 3:
                recent = failures[-3:]
                errors = [f.get('error', '') for f in recent]
                
                # 如果连续失败，降低权重
                logger.info(f"模型 {model_id} 近期失败: {errors}")
        
        # 2. 分析成功模式
        for model_id, successes in self.success_history.items():
            if len(successes) >= 5:
                avg_latency = sum(s['latency'] for s in successes) / len(successes)
                logger.info(f"模型 {model_id} 平均延迟: {avg_latency:.2f}s")
        
        # 3. 调整权重策略
        for model_id, data in self.model_weights.items():
            success = data.get('success_count', 0)
            failure = data.get('failure_count', 0)
            total = success + failure
            
            if total >= 10:
                rate = success / total
                if rate > 0.8:
                    data['weight'] = min(10.0, data['weight'] * 1.1)
                elif rate < 0.3:
                    data['weight'] = max(0.1, data['weight'] * 0.7)
        
        self.save_weights()
        logger.info("进化完成")


class EvolutionDispatcher:
    """
    进化调度器 - 完整版
    整合自适应学习、故障预测、智能路由
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.adaptive = AdaptiveDispatcher(db_path)
        self.cache = {}
        self.cache_ttl = 30
    
    def _get_all_models(self) -> List[Dict]:
        """获取所有模型"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM 模型配置表')
        rows = c.fetchall()
        conn.close()
        
        models = []
        for r in rows:
            if len(r) > 6 and r[5] and r[6]:
                models.append({
                    'id': r[0],
                    'name': r[1],
                    'identifier': r[2],
                    'type': r[3],
                    'provider': r[4],
                    'api_url': r[5],
                    'api_key': r[6]
                })
        return models
    
    def check_health(self, model: Dict, timeout=3) -> Dict:
        """检测模型"""
        try:
            headers = {"Authorization": f"Bearer {model['api_key']}", "Content-Type": "application/json"}
            model_id = model.get('identifier') or 'test'
            payload = {"model": model_id, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 3}
            
            start = time.time()
            r = requests.post(model['api_url'], headers=headers, json=payload, timeout=timeout)
            elapsed = time.time() - start
            
            if r.status_code == 200:
                return {**model, 'online': True, 'latency': elapsed}
            return {**model, 'online': False}
        except:
            return {**model, 'online': False}
    
    def get_online_models(self) -> List[Dict]:
        """获取在线模型"""
        if 'online' in self.cache:
            cached_time, cached = self.cache['online']
            if time.time() - cached_time < self.cache_ttl:
                return cached
        
        models = self._get_all_models()[:15]
        
        results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.check_health, m) for m in models]
            for f in as_completed(futures):
                try:
                    r = f.result()
                    if r.get('online'):
                        results.append(r)
                except:
                    pass
        
        results.sort(key=lambda x: x['latency'])
        self.cache['online'] = (time.time(), results)
        return results
    
    def dispatch(self, prompt: str, model_count: int = 3, 
                task_type: str = None, user_id: str = None) -> Dict:
        """
        智能调度
        
        参数:
            prompt: 用户输入
            model_count: 模型数量
            task_type: 任务类型(code/reasoning/creative/general)
            user_id: 用户ID
        """
        # 1. 任务分析
        task_analysis = self._analyze_task(prompt)
        if not task_type:
            task_type = task_analysis.get('primary_type', 'general')
        
        # 2. 获取在线模型
        online = self.get_online_models()
        
        # 3. 自适应选择
        selected = self.adaptive.select_best_models(online, model_count, task_type, user_id)
        
        if not selected:
            return {'success': False, 'error': '无可用模型'}
        
        # 4. 执行
        results = []
        for model in selected:
            result = self._call_api(model, prompt)
            result['model_name'] = model['name']
            result['provider'] = model['provider']
            results.append(result)
            
            # 记录结果
            if result.get('success'):
                self.adaptive.record_success(
                    model.get('id', model['name']),
                    result.get('latency', 0),
                    result.get('tokens', 0)
                )
            else:
                self.adaptive.record_failure(
                    model.get('id', model['name']),
                    result.get('error', 'unknown')
                )
        
        # 5. 学习用户偏好
        if user_id and results:
            success_results = [r for r in results if r.get('success')]
            if success_results:
                best = success_results[0]
                self.adaptive.learn_user_preference(user_id, best['model_name'], True)
        
        return {
            'success': len([r for r in results if r.get('success')]) > 0,
            'task_type': task_type,
            'results': results,
            'selected_models': [m['name'] for m in selected]
        }
    
    def _analyze_task(self, prompt: str) -> Dict:
        """分析任务类型"""
        prompt_lower = prompt.lower()
        
        types = []
        if any(k in prompt_lower for k in ['代码', 'code', '编程', 'function', 'def ', 'class']):
            types.append('code')
        if any(k in prompt_lower for k in ['推理', 'reasoning', '逻辑', '分析']):
            types.append('reasoning')
        if any(k in prompt_lower for k in ['创作', '写', '小说', '诗歌', '故事']):
            types.append('creative')
        
        return {
            'primary_type': types[0] if types else 'general',
            'all_types': types
        }
    
    def _call_api(self, model: Dict, prompt: str) -> Dict:
        """调用API"""
        try:
            headers = {"Authorization": f"Bearer {model['api_key']}", "Content-Type": "application/json"}
            model_id = model.get('identifier') or model.get('name') or 'test'
            payload = {"model": model_id, "messages": [{"role": "user", "content": prompt}], "max_tokens": 500}
            
            start = time.time()
            r = requests.post(model['api_url'], headers=headers, json=payload, timeout=30)
            elapsed = time.time() - start
            
            if r.status_code == 200:
                data = r.json()
                content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                return {
                    'success': True,
                    'content': content,
                    'latency': elapsed,
                    'tokens': data.get('usage', {}).get('total_tokens', 0)
                }
            return {'success': False, 'error': f'HTTP {r.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def evolve(self):
        """执行自我进化"""
        self.adaptive.analyze_and_evolve()


# 测试
if __name__ == '__main__':
    db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
    dispatcher = EvolutionDispatcher(db_path)
    
    print('=== 进化调度器测试 ===\n')
    
    # 进化分析
    print('1. 执行自我进化...')
    dispatcher.evolve()
    
    # 测试调度
    print('\n2. 测试智能调度...')
    result = dispatcher.dispatch('请用一句话介绍你自己', model_count=3)
    
    print(f'   成功: {result["success"]}')
    print(f'   任务类型: {result.get("task_type", "general")}')
    print(f'   选择模型: {result["selected_models"]}')
    
    for r in result['results']:
        status = 'OK' if r.get('success') else 'FAIL'
        print(f'   - {r["model_name"]}: {status}')
