#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境内核调度器
统一调度入口，根据任务自动选择合适人员
"""
import sqlite3
import requests
import os
import json
from typing import Optional, List, Dict
from datetime import datetime

# 路径配置
KERNEL_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(KERNEL_PATH, '..', 'data')
DB_PATH = os.path.join(DATA_PATH, 'symphony.db')


class XujingScheduler:
    """序境内核调度器"""
    
    def __init__(self):
        self.rules = self.load_rules()
        self.usage_log = os.path.join(DATA_PATH, 'usage_log.json')
    
    def load_rules(self) -> dict:
        """加载规则"""
        rules_file = os.path.join(DATA_PATH, 'rules.json')
        if os.path.exists(rules_file):
            with open(rules_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def get_db_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(DB_PATH)
    
    def get_role_config(self, role_id: str) -> Optional[Dict]:
        """获取角色配置"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.id, r.姓名, r.官职, m.API地址, m.API密钥, m.模型名称, m.服务商, o.名称
            FROM 官署角色表 r
            JOIN 模型配置表 m ON r.模型配置表_ID = m.id
            JOIN 官署表 o ON r.所属官署 = o.id
            WHERE r.id = ?
        ''', (role_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'title': row[2],
                'api': row[3],
                'key': row[4],
                'model': row[5],
                'provider': row[6],
                'office': row[7]
            }
        return None
    
    def get_backup_chain(self, role_id: str) -> List[Dict]:
        """获取备份链"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT 所属官署 FROM 官署角色表 WHERE id = ?', (role_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return []
        
        office_id = row[0]
        
        cursor.execute('''
            SELECT r.id, r.姓名, r.官职, m.模型名称, m.服务商, o.名称
            FROM 官署角色表 r
            JOIN 模型配置表 m ON r.模型配置表_ID = m.id
            JOIN 官署表 o ON r.所属官署 = o.id
            WHERE r.所属官署 = ? AND r.id != ?
            ORDER BY r.id
        ''', (office_id, role_id))
        
        backups = []
        for row in cursor.fetchall():
            backups.append({
                'id': row[0],
                'name': row[1],
                'title': row[2],
                'model': row[3],
                'provider': row[4],
                'office': row[5]
            })
        
        conn.close()
        return backups
    
    def select_best_role(self, task_type: str = 'general') -> str:
        """根据任务类型选择最佳角色"""
        role_mapping = {
            'general': 'role-1',      # 陆念昭
            'code': 'role-56',         # 顾清歌
            'strategy': 'role-2',      # 沈清弦
            'creative': 'role-3',      # 顾至尊
            'analysis': 'role-4',      # 苏云渺
        }
        
        return role_mapping.get(task_type, 'role-1')
    
    def dispatch(self, role_id: str, messages: List[Dict], max_tokens: int = 4096) -> Dict:
        """调度执行"""
        config = self.get_role_config(role_id)
        if not config:
            return {'status': 'error', 'message': f'Role {role_id} not found'}
        
        headers = {'Authorization': 'Bearer ' + config['key'], 'Content-Type': 'application/json'}
        payload = {'model': config['model'], 'messages': messages, 'max_tokens': max_tokens}
        
        try:
            resp = requests.post(config['api'], headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                content = data['choices'][0]['message']['content']
                usage = data.get('usage', {})
                
                self.record_usage(role_id, True, resp.elapsed.total_seconds(), usage.get('total_tokens', 0))
                
                return {
                    'status': 'ok',
                    'role': config['name'],
                    'title': config['title'],
                    'model': config['model'],
                    'provider': config['provider'],
                    'office': config['office'],
                    'latency': resp.elapsed.total_seconds(),
                    'usage': usage,
                    'response': content
                }
            else:
                return self.failover_dispatch(role_id, messages, max_tokens)
        except Exception as e:
            return self.failover_dispatch(role_id, messages, max_tokens)
    
    def failover_dispatch(self, role_id: str, messages: List[Dict], max_tokens: int = 4096) -> Dict:
        """失效转移调度"""
        backups = self.get_backup_chain(role_id)
        
        for backup in backups:
            result = self.dispatch(backup['id'], messages, max_tokens)
            if result['status'] == 'ok':
                result['failover'] = True
                result['original_role'] = role_id
                result['backup_role'] = backup['name']
                return result
        
        return {'status': 'error', 'message': 'All backups failed'}
    
    def smart_dispatch(self, task: str, messages: List[Dict], task_type: str = 'general') -> Dict:
        """智能调度 - 自动选择最佳角色"""
        role_id = self.select_best_role(task_type)
        return self.dispatch(role_id, messages)
    
    def record_usage(self, role_id: str, success: bool, latency: float, tokens: int):
        """记录使用情况"""
        log = []
        if os.path.exists(self.usage_log):
            try:
                with open(self.usage_log, 'r', encoding='utf-8') as f:
                    log = json.load(f)
            except:
                pass
        
        log.append({
            'role_id': role_id,
            'success': success,
            'latency': latency,
            'tokens': tokens,
            'timestamp': str(datetime.now())
        })
        
        log = log[-1000:]
        
        with open(self.usage_log, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
    
    def get_status(self) -> Dict:
        """获取调度器状态"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM 官署角色表')
        total_roles = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM 模型配置表')
        total_models = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'status': 'ok',
            'total_roles': total_roles,
            'total_models': total_models,
            'version': '1.0'
        }


# 全局调度器实例
_scheduler = None


def get_scheduler() -> XujingScheduler:
    """获取调度器实例"""
    global _scheduler
    if _scheduler is None:
        _scheduler = XujingScheduler()
    return _scheduler
