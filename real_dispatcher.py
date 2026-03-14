# -*- coding: utf-8 -*-
"""
序境交响 - 真正多模调度系统
基于 symphony.db 65模型 + 32官员 智能调度
"""
import sqlite3
import requests
import time
import json
import random

DB_PATH = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

class RealDispatcher:
    """真正的多模调度引擎"""
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.models = self._load_models()
        self.officials = self._load_officials()
        
    def _load_models(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM 模型配置表 WHERE 状态='正常'")
        models = {}
        for row in cursor.fetchall():
            models[row['模型名称']] = dict(row)
        return models
    
    def _load_officials(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM 官属角色表 WHERE 状态='正常'")
        officials = {}
        for row in cursor.fetchall():
            officials[row['id']] = dict(row)
        return officials
    
    def analyze_task(self, task):
        """智能任务分析"""
        task_lower = task.lower()
        
        if any(k in task_lower for k in ['代码', '编程', '开发', 'debug', 'bug', '函数', 'class', 'python', 'java']):
            return '代码'
        if any(k in task_lower for k in ['分析', '推理', '思考', '策略', '规划', '趋势', '预测']):
            return '推理'
        if any(k in task_lower for k in ['图', '视觉', '看', '识别']):
            return '视觉'
        if any(k in task_lower for k in ['视频', '生成视频']):
            return '视频'
        if any(k in task_lower for k in ['代理', '自动', '执行', '操作']):
            return 'Agent'
        if any(k in task_lower for k in ['诗', '写', '创作', '文案']):
            return '创意'
        return '通用'
    
    def select_model_by_type(self, task_type):
        """按任务类型选择模型"""
        # 火山引擎优先 (最稳定)
        type_preference = {
            '代码': ['Doubao-Seed-2.0-Code', 'Kimi-K2.5', 'Doubao-Seed-Code', 'ark-code-latest'],
            '推理': ['MiniMax-M2.5', 'glm-4.7', 'DeepSeek-V3.2', 'glm-z1-flash'],
            '视觉': ['glm-4v-flash', 'glm-4.1v-thinking-flash'],
            '视频': ['cogvideox-flash'],
            'Agent': ['MiniMax-M2.5', 'minimaxai/minimax-m2.1'],
            '创意': ['glm-4.7', 'MiniMax-M2.5', 'glm-4-flash'],
            '通用': ['glm-4-flash', 'glm-4.7', 'ark-code-latest', 'MiniMax-M2.5']
        }
        
        candidates = type_preference.get(task_type, type_preference['通用'])
        
        for model_name in candidates:
            if model_name in self.models:
                return model_name
        
        return 'glm-4-flash'
    
    def select_official_by_task(self, task_type):
        """按任务类型选择官员"""
        official_preference = {
            '代码': ['evolve_003', 'evolve_008'],  # 苏云渺, 林码
            '推理': ['evolve_001', 'evolve_006'],  # 沈清弦, 沈星衍
            '视觉': ['evolve_004'],  # 顾清歌
            '视频': ['evolve_004'],
            'Agent': ['evolve_002', 'evolve_005'],  # 陆念昭, 顾至尊
            '创意': ['evolve_004', 'evolve_006'],  # 顾清歌, 沈星衍
            '通用': ['evolve_002', 'evolve_005', 'evolve_001']
        }
        
        candidates = official_preference.get(task_type, official_preference['通用'])
        
        for oid in candidates:
            if oid in self.officials:
                return self.officials[oid]
        
        return self.officials.get('evolve_002')
    
    def call_api(self, model_name, messages, max_tokens=300):
        """调用真实API"""
        model_config = self.models.get(model_name)
        if not model_config:
            return None
        
        url = model_config['url']
        api_key = model_config['key']
        provider = model_config['服务商']
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model_name,
            "messages": messages,
            "max_tokens": max_tokens
        }
        
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=60)
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"API Error: {resp.status_code} - {resp.text[:50]}")
                return None
        except Exception as e:
            print(f"Request Error: {e}")
            return None
    
    def dispatch(self, task):
        """执行调度"""
        # 1. 分析任务
        task_type = self.analyze_task(task)
        
        # 2. 选择模型和官员
        model_name = self.select_model_by_type(task_type)
        official = self.select_official_by_task(task_type)
        model_config = self.models.get(model_name)
        
        # 3. 构建消息
        system_prompt = f"你是中国古代{official['官职']}{official['姓名']}。用文言文简洁回复。"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]
        
        # 4. 调用API
        start = time.time()
        result = self.call_api(model_name, messages)
        elapsed = time.time() - start
        
        if result and 'choices' in result:
            usage = result.get('usage', {})
            reply = result['choices'][0]['message']['content']
            
            return {
                'success': True,
                'task_type': task_type,
                'reply': reply,
                'model': model_name,
                'provider': model_config['服务商'],
                'model_type': model_config.get('模型类型', ''),
                'official': {
                    'id': official['id'],
                    'name': official['姓名'],
                    'title': official['官职'],
                    'office': official.get('职务', '')
                },
                'tokens': {
                    'input': usage.get('prompt_tokens', 0),
                    'output': usage.get('completion_tokens', 0),
                    'total': usage.get('total_tokens', 0)
                },
                'elapsed': round(elapsed, 2)
            }
        
        # 如果失败，尝试备用
        return {
            'success': False,
            'task_type': task_type,
            'model': model_name,
            'error': 'API call failed'
        }
    
    def get_status(self):
        return {
            'models': len(self.models),
            'officials': len(self.officials),
            'providers': list(set(m.get('服务商') for m in self.models.values()))
        }
    
    def close(self):
        self.conn.close()


# 测试
if __name__ == "__main__":
    d = RealDispatcher()
    
    print("="*70)
    print("REAL DISPATCHER TEST")
    print("="*70)
    
    tests = [
        "写一个Python函数计算阶乘",
        "分析2026年AI发展趋势",
        "今天天气怎么样",
    ]
    
    for t in tests:
        print(f"\n>>> {t}")
        r = d.dispatch(t)
        if r['success']:
            print(f"  ✅ [{r['task_type']}] {r['official']['name']} | {r['model']} | {r['tokens']['total']} tokens")
            print(f"     {r['reply'][:50]}...")
        else:
            print(f"  ❌ {r.get('error')}")
    
    print(f"\nSystem: {d.get_status()}")
    d.close()
