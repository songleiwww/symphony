# -*- coding: utf-8 -*-
"""
序境系统 - 多服务商并行调度器
支持任意规则调度、在线自动入队、任务复杂度分析
"""
import sqlite3
import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
from collections import defaultdict

class TaskComplexityAnalyzer:
    """
    任务复杂度分析器
    
    分析维度:
    - 文本长度
    - 语言类型
    - 任务类型(代码/对话/推理/创作)
    - 特殊需求(数学/翻译/总结)
    """
    
    def __init__(self):
        # 关键词匹配
        self.code_keywords = ['代码', 'code', '编程', 'function', 'class', 'def ', '算法']
        self.reasoning_keywords = ['推理', 'reasoning', '逻辑', '分析', '证明', '计算']
        self.translation_keywords = ['翻译', 'translate', '英文', '中文', '日语']
        self.creative_keywords = ['创作', '写', '小说', '诗歌', '故事', '创意']
        self.math_keywords = ['数学', 'math', '计算', '公式', '方程', '积分', '微分']
    
    def analyze(self, prompt: str) -> Dict:
        """分析任务复杂度"""
        prompt_lower = prompt.lower()
        
        # 基础指标
        length = len(prompt)
        char_count = len(prompt)  # 字符数
        
        # 语言检测
        cn_count = sum(1 for c in prompt if '\u4e00' <= c <= '\u9fff')
        en_count = sum(1 for c in prompt if c.isascii())
        
        if cn_count > en_count:
            language = 'cn'
        else:
            language = 'en'
        
        # 任务类型检测
        task_types = []
        if any(k in prompt_lower for k in self.code_keywords):
            task_types.append('code')
        if any(k in prompt_lower for k in self.reasoning_keywords):
            task_types.append('reasoning')
        if any(k in prompt_lower for k in self.translation_keywords):
            task_types.append('translation')
        if any(k in prompt_lower for k in self.creative_keywords):
            task_types.append('creative')
        if any(k in prompt_lower for k in self.math_keywords):
            task_types.append('math')
        
        if not task_types:
            task_types.append('general')
        
        # 复杂度评分 (1-10)
        complexity = 1
        
        # 长度复杂度
        if length > 1000:
            complexity += 3
        elif length > 500:
            complexity += 2
        elif length > 200:
            complexity += 1
        
        # 任务类型复杂度
        if 'code' in task_types:
            complexity += 2
        if 'reasoning' in task_types:
            complexity += 2
        if 'math' in task_types:
            complexity += 3
        
        complexity = min(complexity, 10)
        
        return {
            'length': length,
            'language': language,
            'task_types': task_types,
            'complexity': complexity,
            'complexity_label': self._get_complexity_label(complexity)
        }
    
    def _get_complexity_label(self, complexity: int) -> str:
        if complexity <= 3:
            return '简单'
        elif complexity <= 6:
            return '中等'
        elif complexity <= 8:
            return '复杂'
        else:
            return '超复杂'
    
    def recommend_model_count(self, complexity: int) -> int:
        """根据复杂度推荐模型数量"""
        if complexity <= 3:
            return 1
        elif complexity <= 6:
            return 2
        elif complexity <= 8:
            return 3
        else:
            return 4


class MultiProviderDispatcher:
    """
    多服务商并行调度器
    
    特性:
    1. 多服务商同时选调
    2. 任意规则排序(延迟/随机/服务商权重)
    3. 在线模型自动入队
    4. 任务复杂度分析
    5. 并行执行
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.complexity_analyzer = TaskComplexityAnalyzer()
        self.cache = {}
        self.cache_ttl = 30
    
    def _get_all_models_by_provider(self) -> Dict[str, List[Dict]]:
        """按服务商分组获取所有模型"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM 模型配置表')
        rows = c.fetchall()
        conn.close()
        
        providers = defaultdict(list)
        
        for r in rows:
            if len(r) > 6 and r[5] and r[6]:  # 有API配置
                # 解析服务商
                provider = r[4] if r[4] else 'unknown'
                
                providers[provider].append({
                    'id': r[0],
                    'name': r[1],
                    'identifier': r[2],
                    'type': r[3],
                    'provider': provider,
                    'api_url': r[5],
                    'api_key': r[6]
                })
        
        return dict(providers)
    
    def check_model_health(self, model: Dict, timeout=3) -> Dict:
        """检测模型在线状态"""
        try:
            start = time.time()
            headers = {"Authorization": f"Bearer {model['api_key']}", "Content-Type": "application/json"}
            model_id = model.get('identifier') or 'test'
            payload = {"model": model_id, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 3}
            
            r = requests.post(model['api_url'], headers=headers, json=payload, timeout=timeout)
            elapsed = time.time() - start
            
            if r.status_code == 200:
                return {**model, 'online': True, 'latency': elapsed}
            return {**model, 'online': False}
        except:
            return {**model, 'online': False}
    
    def get_online_models(self, max_per_provider: int = 3) -> Dict[str, List[Dict]]:
        """获取各服务商在线模型"""
        # 检查缓存
        cache_key = 'online_models'
        if cache_key in self.cache:
            cached_time, cached = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return cached
        
        # 按服务商分组获取模型
        providers = self._get_all_models_by_provider()
        
        online_by_provider = defaultdict(list)
        
        # 并行检测所有模型
        all_models = []
        for provider, models in providers.items():
            for m in models[:max_per_provider]:
                all_models.append((provider, m))
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self.check_model_health, m): p for p, m in all_models}
            
            for future in as_completed(futures):
                provider = futures[future]
                try:
                    result = future.result()
                    if result.get('online'):
                        online_by_provider[provider].append(result)
                except:
                    pass
        
        # 每个服务商内部按延迟排序
        for provider in online_by_provider:
            online_by_provider[provider].sort(key=lambda x: x['latency'])
        
        result = dict(online_by_provider)
        
        # 缓存
        self.cache[cache_key] = (time.time(), result)
        
        return result
    
    def dispatch_parallel(self, prompt: str, 
                         max_models: int = 4,
                         strategy: str = 'balanced',
                         providers: List[str] = None) -> Dict:
        """
        并行调度多服务商模型
        
        参数:
            prompt: 用户输入
            max_models: 最大模型数
            strategy: 调度策略
                - balanced: 各服务商均衡选调
                - fastest: 优先低延迟
                - random: 随机选调
                - priority: 按服务商权重
            providers: 指定服务商列表，None表示全部
        
        返回:
            执行结果
        """
        # 1. 任务复杂度分析
        complexity = self.complexity_analyzer.analyze(prompt)
        recommended_count = self.complexity_analyzer.recommend_model_count(complexity['complexity'])
        
        # 2. 获取在线模型
        online = self.get_online_models()
        
        # 3. 根据策略选择模型
        selected = self._select_models(
            online, 
            max_models=max_models,
            strategy=strategy,
            providers=providers
        )
        
        if not selected:
            return {
                'success': False,
                'error': '无可用模型',
                'complexity': complexity
            }
        
        # 4. 并行执行
        results = self._execute_parallel(selected, prompt)
        
        # 5. 整理结果
        success_results = [r for r in results if r.get('success')]
        
        return {
            'success': len(success_results) > 0,
            'complexity': complexity,
            'recommended_count': recommended_count,
            'selected_models': [m['name'] for m in selected],
            'results': results,
            'success_count': len(success_results),
            'total': len(results)
        }
    
    def _select_models(self, online: Dict[str, List[Dict]], 
                      max_models: int, 
                      strategy: str,
                      providers: List[str] = None) -> List[Dict]:
        """根据策略选择模型"""
        selected = []
        
        # 过滤指定服务商
        if providers:
            online = {k: v for k, v in online.items() if k in providers}
        
        if strategy == 'balanced':
            # 均衡选调: 每个服务商轮着选
            all_providers = list(online.keys())
            random.shuffle(all_providers)
            
            idx = 0
            while len(selected) < max_models and idx < len(all_providers) * 2:
                provider = all_providers[idx % len(all_providers)]
                models = online[provider]
                
                if models:
                    selected.append(models[idx // len(all_providers)])
                
                idx += 1
        
        elif strategy == 'fastest':
            # 全部按延迟排序
            all_models = []
            for models in online.values():
                all_models.extend(models)
            all_models.sort(key=lambda x: x['latency'])
            selected = all_models[:max_models]
        
        elif strategy == 'random':
            # 随机选调
            all_models = []
            for models in online.values():
                all_models.extend(models)
            random.shuffle(all_models)
            selected = all_models[:max_models]
        
        elif strategy == 'priority':
            # 优先级选调(服务商权重)
            provider_priority = {
                'NVIDIA': 1,
                '火山引擎': 2,
                '硅基流动': 3,
                '魔搭': 4,
                '智谱': 5,
                'OpenRouter': 6
            }
            
            all_models = []
            for models in online.values():
                for m in models:
                    priority = provider_priority.get(m['provider'], 10)
                    all_models.append((priority, m))
            
            all_models.sort(key=lambda x: x[0])
            selected = [m for _, m in all_models[:max_models]]
        
        else:
            # 默认: 取每个服务商第一个
            for models in online.values():
                if models and len(selected) < max_models:
                    selected.append(models[0])
        
        return selected
    
    def _execute_parallel(self, models: List[Dict], prompt: str) -> List[Dict]:
        """并行执行"""
        results = []
        
        def call_model(model):
            return self._call_api(model, prompt)
        
        with ThreadPoolExecutor(max_workers=len(models)) as executor:
            futures = {executor.submit(call_model, m): m for m in models}
            
            for future in as_completed(futures):
                model = futures[future]
                try:
                    result = future.result()
                    result['model_name'] = model.get('name')
                    result['provider'] = model.get('provider')
                    results.append(result)
                except Exception as e:
                    results.append({
                        'success': False,
                        'error': str(e),
                        'model_name': model.get('name'),
                        'provider': model.get('provider')
                    })
        
        return results
    
    def _call_api(self, model: Dict, prompt: str) -> Dict:
        """调用模型API"""
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


# 测试
if __name__ == '__main__':
    db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
    dispatcher = MultiProviderDispatcher(db_path)
    
    print("=== 多服务商并行调度器测试 ===\n")
    
    # 测试任务复杂度分析
    print("1. 任务复杂度分析:")
    
    test_prompts = [
        "你好，请介绍一下你自己",  # 简单
        "写一个Python函数计算斐波那契数列",  # 代码
        "请分析一下如果AI继续发展下去，未来10年人类社会会发生什么变化？请从经济、科技、社会等多个角度详细分析",  # 复杂
    ]
    
    analyzer = TaskComplexityAnalyzer()
    for p in test_prompts:
        result = analyzer.analyze(p)
        print(f"\n提示: {p[:30]}...")
        print(f"  复杂度: {result['complexity']} ({result['complexity_label']})")
        print(f"  语言: {result['language']}")
        print(f"  类型: {result['task_types']}")
        print(f"  推荐模型数: {analyzer.recommend_model_count(result['complexity'])}")
    
    # 测试并行调度
    print("\n\n2. 并行调度测试:")
    result = dispatcher.dispatch_parallel("你好，请用一句话介绍自己", max_models=3, strategy='balanced')
    
    print(f"  复杂度: {result['complexity']['complexity_label']}")
    print(f"  选择模型: {result['selected_models']}")
    print(f"  成功/总数: {result['success_count']}/{result['total']}")
    
    for r in result['results']:
        status = "OK" if r.get('success') else "FAIL"
        print(f"    {r.get('model_name')}: {status}")
