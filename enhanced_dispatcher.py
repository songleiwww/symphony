# -*- coding: utf-8 -*-
"""
序境交响 - 多模调度增强系统
基于 symphony.db 的 65模型 + 32官属 智能调度
"""
import sqlite3, requests, time, json
from datetime import datetime
import os

DB_PATH = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

class SymphonyDispatcher:
    """多模调度核心引擎"""
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.models = self._load_models()
        self.officials = self._load_officials()
        self._build_dispatch_index()
    
    def _load_models(self):
        """加载所有模型配置"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM 模型配置表 WHERE 状态='正常'")
        models = {}
        for row in cursor.fetchall():
            models[row['模型名称']] = dict(row)
        return models
    
    def _load_officials(self):
        """加载所有官属角色"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM 官属角色表 WHERE 状态='正常'")
        officials = {}
        for row in cursor.fetchall():
            officials[row['id']] = dict(row)
        return officials
    
    def _build_dispatch_index(self):
        """构建调度索引 - 按能力分类"""
        self.capability_index = {
            '代码': [],
            '推理': [],
            '视觉': [],
            '视频': [],
            '图像': [],
            '通用': [],
            'Agent': [],
        }
        
        for model_name, model in self.models.items():
            model_type = model.get('模型类型', '')
            if '代码' in model_type:
                self.capability_index['代码'].append(model_name)
            elif '推理' in model_type:
                self.capability_index['推理'].append(model_name)
            elif '视觉' in model_type or '视频' in model_type:
                self.capability_index['视觉'].append(model_name)
            elif '图像' in model_type:
                self.capability_index['图像'].append(model_name)
            elif 'Agent' in model_type:
                self.capability_index['Agent'].append(model_name)
            else:
                self.capability_index['通用'].append(model_name)
        
        # 按服务商分组
        self.provider_index = {}
        for model_name, model in self.models.items():
            provider = model.get('服务商', '')
            if provider not in self.provider_index:
                self.provider_index[provider] = []
            self.provider_index[provider].append(model_name)
    
    def dispatch(self, task, context=None):
        """
        智能调度核心方法
        task: 任务描述
        context: 额外上下文信息
        """
        # 1. 分析任务类型
        task_type = self._analyze_task(task)
        
        # 2. 选择合适模型
        model = self._select_model(task_type, context)
        
        # 3. 选择合适官员
        official = self._select_official(task_type, context)
        
        # 4. 执行调用
        result = self._execute_task(model, official, task)
        
        return result
    
    def _analyze_task(self, task):
        """分析任务类型"""
        task = task.lower()
        
        # 关键词匹配
        keywords = {
            '代码': ['代码', '编程', '开发', '写code', 'debug', 'bug', '修复'],
            '推理': ['分析', '推理', '思考', '策略', '规划', '决策'],
            '视觉': ['图片', '图像', '看图', '视觉', '识别'],
            '视频': ['视频', '生成视频', '剪辑'],
            'Agent': ['代理', '智能体', '自动化', '执行', '操作'],
        }
        
        for task_type, kws in keywords.items():
            for kw in kws:
                if kw in task:
                    return task_type
        
        return '通用'
    
    def _select_model(self, task_type, context=None):
        """根据任务类型选择最佳模型"""
        candidates = self.capability_index.get(task_type, self.capability_index['通用'])
        
        if not candidates:
            candidates = self.capability_index['通用']
        
        # 优先选择在线状态为"在线"的模型
        for model_name in candidates:
            if self.models[model_name].get('是否在线') == '在线':
                return model_name
        
        return candidates[0] if candidates else 'glm-4-flash'
    
    def _select_official(self, task_type, context=None):
        """根据任务类型选择合适官员"""
        # 核心官员映射
        official_map = {
            '代码': ['evolve_003', 'evolve_008'],  # 苏云渺, 林码
            '推理': ['evolve_001', 'evolve_006'],  # 沈清弦, 沈星衍
            '视觉': ['evolve_004', 'evolve_007'],  # 顾清歌, 叶轻尘
            '视频': ['evolve_004'],
            'Agent': ['evolve_002', 'evolve_005'],  # 陆念昭, 顾至尊
            '通用': ['evolve_002', 'evolve_005', 'evolve_001'],
        }
        
        candidates = official_map.get(task_type, official_map['通用'])
        
        # 返回第一个可用官员
        for oid in candidates:
            if oid in self.officials:
                return self.officials[oid]
        
        return self.officials.get('evolve_002')
    
    def _execute_task(self, model, official, task):
        """执行任务"""
        model_config = self.models.get(model)
        if not model_config:
            return {'success': False, 'error': 'Model not found'}
        
        # 获取API配置
        url = model_config['url']
        api_key = model_config['key']
        provider = model_config['服务商']
        
        # 构建请求
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        system_prompt = f"你是中国古代{official['官职']}{official['姓名']}，用文言文简洁回复。"
        
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task}
            ],
            "max_tokens": 500
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
                    'reply': result['choices'][0]['message']['content'],
                    'model': model,
                    'provider': provider,
                    'official': {
                        'id': official['id'],
                        'name': official['姓名'],
                        'title': official['官职']
                    },
                    'tokens': {
                        'input': usage.get('prompt_tokens', 0),
                        'output': usage.get('completion_tokens', 0),
                        'total': usage.get('total_tokens', 0)
                    },
                    'elapsed': elapsed
                }
            else:
                return {'success': False, 'error': f"HTTP {resp.status_code}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_status(self):
        """获取系统状态"""
        return {
            'total_models': len(self.models),
            'total_officials': len(self.officials),
            'providers': list(self.provider_index.keys()),
            'capabilities': {k: len(v) for k, v in self.capability_index.items()}
        }
    
    def close(self):
        self.conn.close()


# 测试调度
if __name__ == "__main__":
    dispatcher = SymphonyDispatcher()
    
    print("="*60)
    print("SYMPHONY DISPATCHER - Multi-Model Test")
    print("="*60)
    
    # 测试不同任务类型
    test_tasks = [
        ("写一个Python函数", "代码"),
        ("分析当前经济形势", "推理"),
        ("描述这张图片", "视觉"),
        ("帮我自动化执行这个任务", "Agent"),
        ("今天天气怎么样", "通用"),
    ]
    
    for task, expected_type in test_tasks:
        print(f"\n--- Task: {task} (预期: {expected_type}) ---")
        result = dispatcher.dispatch(task)
        
        if result['success']:
            print(f"✅ 官员: {result['official']['name']} ({result['official']['title']})")
            print(f"📡 模型: {result['model']} ({result['provider']})")
            print(f"📊 Tokens: {result['tokens']['total']} (in:{result['tokens']['input']} out:{result['tokens']['output']})")
            print(f"⏱️ 耗时: {result['elapsed']:.2f}s")
            print(f"💬 回复: {result['reply'][:80]}...")
        else:
            print(f"❌ 错误: {result.get('error')}")
    
    print("\n" + "="*60)
    print("SYSTEM STATUS")
    print("="*60)
    status = dispatcher.get_status()
    print(f"总模型数: {status['total_models']}")
    print(f"总官员数: {status['total_officials']}")
    print(f"服务商: {status['providers']}")
    print(f"能力分布: {status['capabilities']}")
    
    dispatcher.close()
