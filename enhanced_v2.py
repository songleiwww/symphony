# -*- coding: utf-8 -*-
"""
序境交响 - 增强型多模调度系统
基于 symphony.db 的智能调度
"""
import sys
import sqlite3
import requests
import time
import json

DB_PATH = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

class EnhancedDispatcher:
    """增强型多模调度引擎"""
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.models = self._load_models()
        self.officials = self._load_officials()
        
    def _load_models(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM 模型配置表 WHERE 状态='正常' AND 是否在线='在线'")
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
        task = task.lower()
        
        # 任务类型识别
        if any(kw in task for kw in ['代码', '编程', '开发', '写code', 'debug', 'bug']):
            return '代码'
        if any(kw in task for kw in ['分析', '推理', '思考', '策略', '规划']):
            return '推理'
        if any(kw in task for kw in ['图片', '图像', '看图', '视觉']):
            return '视觉'
        if any(kw in task for kw in ['视频', '生成视频']):
            return '视频'
        if any(kw in task for kw in ['代理', '智能体', '自动化', '执行']):
            return 'Agent'
        return '通用'
    
    def select_model(self, task_type):
        """根据任务类型选择最佳模型"""
        type_model_map = {
            '代码': ['Doubao-Seed-2.0-Code', 'Kimi-K2.5', 'Doubao-Seed-Code'],
            '推理': ['glm-z1-flash', 'MiniMax-M2.5', 'DeepSeek-V3.2', 'glm-4.7'],
            '视觉': ['glm-4v-flash', 'glm-4.1v-thinking-flash'],
            '视频': ['cogvideox-flash'],
            'Agent': ['MiniMax-M2.5', 'minimaxai/minimax-m2.1'],
            '通用': ['glm-4-flash', 'glm-4.7', 'ark-code-latest', 'MiniMax-M2.5']
        }
        
        candidates = type_model_map.get(task_type, type_model_map['通用'])
        
        for model_name in candidates:
            if model_name in self.models:
                return model_name
        
        return 'glm-4-flash'
    
    def select_official(self, task_type, context=None):
        """选择合适的官员"""
        type_official_map = {
            '代码': ['evolve_003', 'evolve_008'],  # 苏云渺(工部尚书), 林码(营造司正)
            '推理': ['evolve_001', 'evolve_006'],  # 沈清弦(枢密使), 沈星衍(智囊博士)
            '视觉': ['evolve_004'],  # 顾清歌(翰林学士)
            '视频': ['evolve_004'],
            'Agent': ['evolve_002', 'evolve_005'],  # 陆念昭(少府监), 顾至尊(首辅大学士)
            '通用': ['evolve_002', 'evolve_005', 'evolve_001']
        }
        
        candidates = type_official_map.get(task_type, type_official_map['通用'])
        
        for oid in candidates:
            if oid in self.officials:
                return self.officials[oid]
        
        return self.officials.get('evolve_002')
    
    def dispatch(self, task, context=None):
        """执行智能调度"""
        # 1. 分析任务
        task_type = self.analyze_task(task)
        
        # 2. 选择模型和官员
        model_name = self.select_model(task_type)
        official = self.select_official(task_type, context)
        
        model_config = self.models.get(model_name)
        
        if not model_config:
            return {'success': False, 'error': 'Model not found'}
        
        # 3. 构建请求
        url = model_config['url']
        api_key = model_config['key']
        provider = model_config['服务商']
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        system_prompt = f"你是中国古代{official['官职']}{official['姓名']}，用文言文简洁回复。"
        
        data = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task}
            ],
            "max_tokens": 300
        }
        
        start_time = time.time()
        
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=60)
            elapsed = time.time() - start_time
            
            if resp.status_code == 200:
                result = resp.json()
                usage = result.get('usage', {})
                
                return {
                    'success': True,
                    'task_type': task_type,
                    'reply': result['choices'][0]['message']['content'],
                    'model': model_name,
                    'provider': provider,
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
            else:
                return {'success': False, 'error': f"HTTP {resp.status_code}", 'detail': resp.text[:100]}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_capabilities(self):
        """获取系统能力"""
        return {
            'total_models': len(self.models),
            'total_officials': len(self.officials),
            'models_by_provider': self._count_by_provider(),
            'models_by_type': self._count_by_type()
        }
    
    def _count_by_provider(self):
        counts = {}
        for m in self.models.values():
            p = m.get('服务商', 'Unknown')
            counts[p] = counts.get(p, 0) + 1
        return counts
    
    def _count_by_type(self):
        counts = {}
        for m in self.models.values():
            t = m.get('模型类型', 'Unknown')
            counts[t] = counts.get(t, 0) + 1
        return counts
    
    def close(self):
        self.conn.close()


# 测试
if __name__ == "__main__":
    dispatcher = EnhancedDispatcher()
    
    print("="*70)
    print("ENHANCED DISPATCHER - Multi-Model Test")
    print("="*70)
    
    # 测试用例
    tests = [
        ("写一个Python函数计算斐波那契", "代码"),
        ("分析2026年AI发展趋势", "推理"),
        ("今天天气怎么样", "通用"),
        ("帮我写首诗", "创意"),
    ]
    
    for task, expected in tests:
        print(f"\n[{expected}] {task}")
        result = dispatcher.dispatch(task)
        
        if result['success']:
            print(f"  ✅ 官员: {result['official']['name']} | {result['official']['title']}")
            print(f"  📡 模型: {result['model']} ({result['provider']})")
            print(f"  📊 Tokens: {result['tokens']['total']} | ⏱️ {result['elapsed']}s")
            print(f"  💬 {result['reply'][:60]}...")
        else:
            print(f"  ❌ {result.get('error')}")
    
    print("\n" + "="*70)
    print("SYSTEM CAPABILITIES")
    print("="*70)
    caps = dispatcher.get_capabilities()
    print(f"总模型: {caps['total_models']} | 总官员: {caps['total_officials']}")
    print(f"按服务商: {caps['models_by_provider']}")
    print(f"按类型: {caps['models_by_type']}")
    
    dispatcher.close()
