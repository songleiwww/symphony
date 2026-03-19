# -*- coding: utf-8 -*-
"""
序境系统 - 在线检测模块v3
使用列索引避免编码问题
"""
import requests
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

class ModelHealthChecker:
    """模型在线健康检测器"""
    
    def __init__(self, db_path, timeout=5):
        self.db_path = db_path
        self.timeout = timeout
        self.test_prompt = "hi"
    
    def check_single_model(self, model_info):
        """检测单个模型"""
        model_id, api_url, api_key = model_info
        
        if not api_url or not api_key:
            return {'model_id': model_id, 'status': 'no_api', 'latency': 0}
        
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": "test", "messages": [{"role": "user", "content": self.test_prompt}], "max_tokens": 5}
        
        for endpoint in [api_url, api_url.replace('/chat/completions', '/completions')]:
            try:
                start = time.time()
                r = requests.post(endpoint, headers=headers, json=payload, timeout=self.timeout)
                elapsed = time.time() - start
                if r.status_code in [200, 201]:
                    return {'model_id': model_id, 'status': 'online', 'latency': elapsed}
            except: continue
        
        return {'model_id': model_id, 'status': 'offline', 'latency': self.timeout}
    
    def get_enabled_models(self):
        """获取启用的模型"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM 模型配置表')
        rows = c.fetchall()
        conn.close()
        
        # 列索引: 0=id, 5=API地址, 6=API密钥, 7=是否启用
        enabled = [r for r in rows if len(r) > 7 and r[7] and '启用' in str(r[7])]
        return [(r[0], r[5], r[6]) for r in enabled if r[5] and r[6]]
    
    def check_all_models(self, max_workers=5):
        """批量检测"""
        models = self.get_enabled_models()[:10]  # 只检测前10个
        
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.check_single_model, m): m for m in models}
            for future in as_completed(futures):
                try: results.append(future.result())
                except: pass
        return results
    
    def get_online_models(self):
        """获取在线模型"""
        results = self.check_all_models()
        online = [r for r in results if r['status'] == 'online']
        online.sort(key=lambda x: x['latency'])
        return {'total': len(results), 'online': len(online), 'models': online}


if __name__ == '__main__':
    checker = ModelHealthChecker('C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db')
    health = checker.get_online_models()
    print(f'检测: {health[\"total\"]} | 在线: {health[\"online\"]}')
    for m in health['models'][:5]:
        print(f'  模型{m[\"model_id\"]}: {m[\"latency\"]:.2f}s')
