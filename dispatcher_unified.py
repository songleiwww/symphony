# -*- coding: utf-8 -*-
"""
序境系统 - 统一调度器 (整改版v3)
修复数据库查询编码问题
"""
import sqlite3
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

class UnifiedDispatcher:
    """统一调度器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def _get_all_models(self) -> List[Dict]:
        """获取所有模型"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM 模型配置表')
        rows = c.fetchall()
        conn.close()
        
        models = []
        for r in rows:
            # 列: 0=id,1=名称,2=标识,3=类型,4=服务商,5=API地址,6=API密钥,7=是否启用
            if len(r) > 6 and r[5] and r[6]:  # 有API配置
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
    
    def check_health(self, model: Dict, timeout=5) -> Dict:
        """检测单个模型"""
        try:
            headers = {"Authorization": f"Bearer {model['api_key']}", "Content-Type": "application/json"}
            model_id = model.get('identifier') or 'meta/llama-3.2-1b-instruct'
            payload = {"model": model_id, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 3}
            
            start = time.time()
            r = requests.post(model['api_url'], headers=headers, json=payload, timeout=timeout)
            elapsed = time.time() - start
            
            if r.status_code == 200:
                return {'id': model['id'], 'online': True, 'latency': elapsed, **model}
            return {'id': model['id'], 'online': False}
        except:
            return {'id': model['id'], 'online': False}
    
    def get_online_models(self, max_check=10) -> List[Dict]:
        """获取在线模型"""
        models = self._get_all_models()[:max_check]
        
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.check_health, m) for m in models]
            for f in as_completed(futures):
                try:
                    r = f.result()
                    if r.get('online'):
                        results.append(r)
                except:
                    pass
        
        results.sort(key=lambda x: x['latency'])
        return results
    
    def dispatch(self, prompt: str, max_retries=3) -> Dict:
        """调度"""
        online = self.get_online_models()
        
        if not online:
            return {'success': False, 'error': '无可用模型', 'code': 503}
        
        for model in online[:max_retries]:
            result = self._call_api(model, prompt)
            if result.get('success'):
                result['model'] = model['name']
                result['provider'] = model['provider']
                return result
        
        return {'success': False, 'error': '所有模型均失败', 'code': 500}
    
    def _call_api(self, model: Dict, prompt: str) -> Dict:
        """调用API"""
        try:
            headers = {"Authorization": f"Bearer {model['api_key']}", "Content-Type": "application/json"}
            model_id = model.get('identifier') or model.get('name') or 'meta/llama-3.2-1b-instruct'
            payload = {"model": model_id, "messages": [{"role": "user", "content": prompt}], "max_tokens": 500}
            
            start = time.time()
            r = requests.post(model['api_url'], headers=headers, json=payload, timeout=30)
            elapsed = time.time() - start
            
            if r.status_code == 200:
                data = r.json()
                content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                return {'success': True, 'content': content, 'code': 200, 'latency': elapsed}
            
            return {'success': False, 'error': f'HTTP {r.status_code}', 'code': r.status_code}
        except Exception as e:
            return {'success': False, 'error': str(e), 'code': 500}


if __name__ == '__main__':
    d = UnifiedDispatcher('C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db')
    
    print('=== 统一调度器测试 ===')
    
    # 获取模型
    models = d._get_all_models()
    print(f'总模型数: {len(models)}')
    
    # 健康检测
    print('\n模型在线检测:')
    online = d.get_online_models()
    print(f'在线: {len(online)}')
    for m in online[:3]:
        print(f'  - {m["name"]}: {m["latency"]:.2f}s')
    
    # 调度测试
    if online:
        print('\n调度测试:')
        r = d.dispatch('你好，请用一句话介绍自己')
        if r.get('success'):
            print(f'成功! 模型:{r.get("model")}')
            print(f'内容: {r.get("content", "")[:100]}...')
        else:
            print(f'失败: {r.get("error")}')
