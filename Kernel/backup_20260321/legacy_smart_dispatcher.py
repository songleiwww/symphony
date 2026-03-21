#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境智能调度器 (Phase 1: 基础调度)
"""
import sqlite3
import requests
import os
import json
from typing import Optional, List, Dict
from datetime import datetime

class SmartDispatcher:
    """智能调度器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.kernel_path = os.path.dirname(db_path).replace('\\', '/')
        
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def get_role_config(self, role_id: str) -> Optional[Dict]:
        """获取角色模型配置"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.姓名, r.官职, o.名称, m.模型名称, m.API地址, m.API密钥, m.服务商
            FROM 官署角色表 r
            JOIN 官署表 o ON r.所属官署 = o.id
            JOIN 模型配置表 m ON r.模型配置表_ID = m.id
            WHERE r.id = ?
        ''', (role_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': role_id,
                'name': row[0],
                'title': row[1],
                'office': row[2],
                'model': row[3],
                'api': row[4],
                'key': row[5],
                'provider': row[6]
            }
        return None
    
    def dispatch(self, role_id: str, messages: List[Dict], max_tokens: int = 200) -> Dict:
        """调度执行"""
        config = self.get_role_config(role_id)
        
        if not config:
            return {'status': 'error', 'message': f'Role {role_id} not found'}
        
        # 调用API
        headers = {'Authorization': 'Bearer ' + config['key'], 'Content-Type': 'application/json'}
        payload = {
            'model': config['model'],
            'messages': messages,
            'max_tokens': max_tokens
        }
        
        try:
            resp = requests.post(config['api'], headers=headers, json=payload, timeout=60)
            
            if resp.status_code == 200:
                data = resp.json()
                content = data['choices'][0]['message']['content']
                usage = data.get('usage', {})
                
                return {
                    'status': 'ok',
                    'role': config['name'],
                    'title': config['title'],
                    'model': config['model'],
                    'provider': config['provider'],
                    'api': config['api'],
                    'usage': usage,
                    'response': content
                }
            else:
                return {
                    'status': 'error',
                    'message': f'API error: {resp.status_code}',
                    'role': config['name']
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'role': config['name']
            }
    
    def failover_dispatch(self, role_id: str, messages: List[Dict], max_tokens: int = 200) -> Dict:
        """失效转移调度"""
        # 首先尝试主调度
        result = self.dispatch(role_id, messages, max_tokens)
        
        if result['status'] == 'ok':
            return result
        
        # 失效则尝试备用
        print(f"主模型失效，尝试备用...")
        return self.find_backup_and_dispatch(role_id, messages, max_tokens)
    
    def find_backup_and_dispatch(self, failed_role_id: str, messages: List[Dict], max_tokens: int) -> Dict:
        """寻找备份并调度"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 获取同官署的备用角色
        cursor.execute('''
            SELECT r.id FROM 官署角色表 r
            JOIN 官署表 o ON r.所属官署 = o.id
            WHERE r.id != ? AND r.状态 = '在职'
            LIMIT 3
        ''', (failed_role_id,))
        
        backup_roles = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # 尝试每个备用
        for backup_id in backup_roles:
            result = self.dispatch(backup_id, messages, max_tokens)
            if result['status'] == 'ok':
                result['failover'] = True
                result['original_role'] = failed_role_id
                return result
        
        return {'status': 'error', 'message': 'All backups failed'}
    
    def health_check(self, role_id: str) -> Dict:
        """健康检测"""
        config = self.get_role_config(role_id)
        if not config:
            return {'status': 'error', 'message': 'Role not found'}
        
        try:
            headers = {'Authorization': 'Bearer ' + config['key'], 'Content-Type': 'application/json'}
            payload = {'model': config['model'], 'messages': [{'role': 'user', 'content': 'hi'}], 'max_tokens': 5}
            resp = requests.post(config['api'], headers=headers, json=payload, timeout=10)
            
            if resp.status_code == 200:
                return {'status': 'ok', 'role': config['name'], 'model': config['model'], 'latency': resp.elapsed.total_seconds()}
            else:
                return {'status': 'error', 'role': config['name'], 'code': resp.status_code}
        except Exception as e:
            return {'status': 'error', 'role': config['name'], 'message': str(e)}
    
    def get_backup_chain(self, role_id: str, cross_office: bool = True) -> List[Dict]:
        """获取备份链"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get original role's office
        cursor.execute('SELECT 所属官署 FROM 官署角色表 WHERE id = ?', (role_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return []
        
        office_id = row[0]
        
        # Get backup roles from same office
        cursor.execute('''
            SELECT r.id, r.姓名, r.官职, m.模型名称, m.服务商
            FROM 官署角色表 r
            JOIN 模型配置表 m ON r.模型配置表_ID = m.id
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
                'office': office_id
            })
        
        # If no same-office backups, get from other offices
        if not backups and cross_office:
            cursor.execute('''
                SELECT r.id, r.姓名, r.官职, m.模型名称, m.服务商, o.名称
                FROM 官署角色表 r
                JOIN 模型配置表 m ON r.模型配置表_ID = m.id
                JOIN 官署表 o ON r.所属官署 = o.id
                WHERE r.id != ?
                ORDER BY r.id
                LIMIT 10
            ''', (role_id,))
            
            for row in cursor.fetchall():
                backups.append({
                    'id': row[0],
                    'name': row[1],
                    'title': row[2],
                    'model': row[3],
                    'provider': row[4],
                    'office': row[5]  # Chinese name
                })
        
        conn.close()
        return backups
    
    def record_usage(self, role_id: str, success: bool, latency: float, tokens: int):
        """记录使用情况用于自动学习"""
        log_file = os.path.join(self.kernel_path, 'usage_log.json')
        
        import json
        log = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
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
        
        # Keep last 1000 records
        log = log[-1000:]
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
    
    def save_backup_chain(self):
        """持久化备份链到文件"""
        backup_file = os.path.join(self.kernel_path, 'backup_chain.json')
        
        # Build backup chain for all roles
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM 官署角色表 ORDER BY id')
        all_roles = [row[0] for row in cursor.fetchall()]
        
        backup_data = {}
        
        for role_id in all_roles:
            backups = self.get_backup_chain(role_id, cross_office=False)
            if backups:
                backup_data[role_id] = backups
        
        conn.close()
        
        # Save to file
        import json
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        return len(backup_data)
    
    def load_backup_chain(self, role_id: str) -> List[Dict]:
        """从文件加载备份链"""
        backup_file = os.path.join(self.kernel_path, 'backup_chain.json')
        
        if not os.path.exists(backup_file):
            return self.get_backup_chain(role_id)
        
        import json
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        return backup_data.get(role_id, [])
    
    def get_optimal_role(self, task_type: str = 'general') -> str:
        """根据历史记录获取最优角色"""
        log_file = os.path.join(self.kernel_path, 'usage_log.json')
        
        if not os.path.exists(log_file):
            return 'role-1'  # Default
        
        import json
        with open(log_file, 'r', encoding='utf-8') as f:
            log = json.load(f)
        
        if not log:
            return 'role-1'
        
        # Find best performing role
        from collections import defaultdict
        stats = defaultdict(lambda: {'success': 0, 'total': 0, 'latency': 0})
        
        for entry in log:
            rid = entry['role_id']
            stats[rid]['total'] += 1
            if entry['success']:
                stats[rid]['success'] += 1
            stats[rid]['latency'] += entry.get('latency', 0)
        
        # Calculate score
        best_role = 'role-1'
        best_score = -1
        
        for rid, data in stats.items():
            if data['total'] > 0:
                success_rate = data['success'] / data['total']
                avg_latency = data['latency'] / data['total']
                score = success_rate * 100 - avg_latency  # Higher is better
                if score > best_score:
                    best_score = score
                    best_role = rid
        
        return best_role
        
        
        conn.close()
        return backups
    
    def smart_dispatch(self, role_id: str, messages: List[Dict], max_tokens: int = 200) -> Dict:
        """智能调度：自动处理失效"""
        # First try
        result = self.dispatch(role_id, messages, max_tokens)
        
        if result['status'] == 'ok':
            return result
        
        # Failed, try backups
        print(f"主模型失效，寻求备份...")
        backups = self.get_backup_chain(role_id)
        
        for backup in backups:
            print(f"尝试备份: {backup['name']}")
            result = self.dispatch(backup['id'], messages, max_tokens)
            if result['status'] == 'ok':
                result['failover'] = True
                result['original_role'] = role_id
                result['backup_role'] = backup['name']
                return result
        
        return {'status': 'error', 'message': 'All dispatch failed'} 


# 测试
if __name__ == '__main__':
    db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
    dispatcher = SmartDispatcher(db_path)
    
    # 测试调度
    result = dispatcher.dispatch('role-1', [
        {'role': 'system', 'content': '你是序境官员。'},
        {'role': 'user', 'content': '你好'}
    ])
    
    print('=== 调度测试 ===')
    print('Status:', result['status'])
    if result['status'] == 'ok':
        print('Role:', result['role'])
        print('Model:', result['model'])
        print('Provider:', result['provider'])
        print('Tokens:', result['usage'].get('total_tokens', 'N/A'))
