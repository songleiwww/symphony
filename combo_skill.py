#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境组合技能引擎
多模型协作闭环应用
"""
import sqlite3
import requests
import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# 路径配置
KERNEL_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(KERNEL_PATH, '..', 'data')
DB_PATH = os.path.join(DATA_PATH, 'symphony.db')


class ComboSkillEngine:
    """序境组合技能引擎"""
    
    def __init__(self):
        self.collaboration_mode = 'parallel'  # parallel/sequential/dynamic
        self.results = []
        self.fusion_method = 'confidence'  # voting/entropy/confidence
    
    def get_role_config(self, role_id: str) -> Optional[Dict]:
        """获取角色配置"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.id, r.姓名, m.API地址, m.API密钥, m.模型名称, m.服务商
            FROM 官署角色表 r
            JOIN 模型配置表 m ON r.模型配置表_ID = m.id
            WHERE r.id = ?
        ''', (role_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'api': row[2],
                'key': row[3],
                'model': row[4],
                'provider': row[5]
            }
        return None
    
    def call_model(self, config: Dict, messages: List[Dict]) -> Dict:
        """调用单个模型"""
        headers = {'Authorization': 'Bearer ' + config['key'], 'Content-Type': 'application/json'}
        payload = {'model': config['model'], 'messages': messages, 'max_tokens': 4096}
        
        try:
            resp = requests.post(config['api'], headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    'status': 'ok',
                    'model': config['model'],
                    'provider': config['provider'],
                    'response': data['choices'][0]['message']['content'],
                    'usage': data.get('usage', {}),
                    'latency': resp.elapsed.total_seconds()
                }
            else:
                return {'status': 'error', 'code': resp.status_code}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def parallel_collaboration(self, tasks: List[Dict]) -> List[Dict]:
        """并行协作 - 多模型同时处理"""
        results = []
        
        with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            futures = {}
            for i, task in enumerate(tasks):
                config = self.get_role_config(task['role_id'])
                if config:
                    future = executor.submit(self.call_model, config, task['messages'])
                    futures[future] = i
            
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    result = future.result()
                    results.append({'task_index': idx, **result})
                except Exception as e:
                    results.append({'task_index': idx, 'status': 'error', 'message': str(e)})
        
        # 按原始顺序排序
        results.sort(key=lambda x: x['task_index'])
        return results
    
    def sequential_collaboration(self, tasks: List[Dict]) -> List[Dict]:
        """序列协作 - 流水线处理"""
        results = []
        accumulated_context = []
        
        for i, task in enumerate(tasks):
            config = self.get_role_config(task['role_id'])
            if not config:
                continue
            
            # 添加前置结果作为上下文
            messages = task['messages'].copy()
            if accumulated_context:
                messages = [
                    {"role": "system", "content": f"前序模型输出: {accumulated_context[-1]}"}
                ] + messages
            
            result = self.call_model(config, messages)
            results.append({'task_index': i, **result})
            
            if result.get('status') == 'ok':
                accumulated_context.append(result.get('response', ''))
        
        return results
    
    def dynamic_collaboration(self, task: Dict, available_roles: List[str]) -> Dict:
        """动态协作 - 自适应调用"""
        # 第一步：意图识别
        intent_config = self.get_role_config(available_roles[0])
        intent_result = self.call_model(intent_config, [
            {"role": "system", "content": "分析用户意图，返回任务类型: general/code/creative/analysis"},
            {"role": "user", "content": task['messages'][-1]['content']}
        ])
        
        if intent_result.get('status') != 'ok':
            return {'status': 'error', 'message': '意图识别失败'}
        
        # 第二步：根据意图选择模型
        intent = intent_result.get('response', '').lower()
        if 'code' in intent:
            selected_role = available_roles[1] if len(available_roles) > 1 else available_roles[0]
        elif 'creative' in intent:
            selected_role = available_roles[2] if len(available_roles) > 2 else available_roles[0]
        else:
            selected_role = available_roles[0]
        
        # 第三步：执行任务
        config = self.get_role_config(selected_role)
        result = self.call_model(config, task['messages'])
        
        return {
            'status': 'ok',
            'intent': intent,
            'selected_role': selected_role,
            **result
        }
    
    def fuse_results(self, results: List[Dict], method: str = 'confidence') -> str:
        """结果融合"""
        valid_results = [r for r in results if r.get('status') == 'ok']
        
        if not valid_results:
            return "所有模型调用失败"
        
        if method == 'voting':
            # 简单投票：返回第一个结果
            return valid_results[0].get('response', '')
        
        elif method == 'entropy':
            # 熵加权：返回最详细的结果
            return max(valid_results, key=lambda x: len(x.get('response', ''))).get('response', '')
        
        else:  # confidence
            # 置信度融合：综合所有结果
            fused = "【融合结果】\n\n"
            for r in valid_results:
                fused += f"模型 {r.get('model')}:\n{r.get('response', '')}\n\n"
            return fused
    
    def execute(self, tasks: List[Dict], mode: str = 'parallel', fusion: str = 'confidence') -> Dict:
        """执行组合技能
        
        Args:
            tasks: [{'role_id': 'role-1', 'messages': [...]}]
            mode: parallel/sequential/dynamic
            fusion: voting/entropy/confidence
        """
        self.collaboration_mode = mode
        self.fusion_method = fusion
        
        print("=" * 50)
        print("🔧 序境组合技能引擎")
        print(f"模式: {mode} | 融合: {fusion}")
        print("=" * 50)
        
        start_time = time.time()
        
        # 执行协作
        if mode == 'dynamic':
            # 动态协作需要单个任务
            available_roles = [t['role_id'] for t in tasks]
            results = [self.dynamic_collaboration(tasks[0], available_roles)]
        elif mode == 'sequential':
            results = self.sequential_collaboration(tasks)
        else:
            results = self.parallel_collaboration(tasks)
        
        # 融合结果
        fused_response = self.fuse_results(results, fusion)
        
        elapsed = time.time() - start_time
        
        # 统计
        total_tokens = sum(
            r.get('usage', {}).get('total_tokens', 0) 
            for r in results if r.get('status') == 'ok'
        )
        
        print()
        print("【执行结果】")
        for r in results:
            status = "✓" if r.get('status') == 'ok' else "✗"
            model = r.get('model', 'unknown')
            tokens = r.get('usage', {}).get('total_tokens', 0)
            print(f"  {status} {model}: {tokens} tokens")
        
        print()
        print(f"总耗时: {elapsed:.2f}s")
        print(f"总Tokens: {total_tokens}")
        
        return {
            'status': 'ok',
            'mode': mode,
            'fusion': fusion,
            'individual_results': results,
            'fused_response': fused_response,
            'total_tokens': total_tokens,
            'elapsed_time': elapsed
        }


# 全局引擎实例
_combo_engine = None


def get_combo_engine() -> ComboSkillEngine:
    """获取组合技能引擎"""
    global _combo_engine
    if _combo_engine is None:
        _combo_engine = ComboSkillEngine()
    return _combo_engine
