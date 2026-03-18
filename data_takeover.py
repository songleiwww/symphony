#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境数据接管模块
从宿主AI安全接管用户数据
"""
import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
import hashlib

# 路径配置
KERNEL_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(KERNEL_PATH, '..', 'data')
DB_PATH = os.path.join(DATA_PATH, 'symphony.db')


class DataTakeover:
    """序境数据接管模块"""
    
    def __init__(self):
        self.data_dir = os.path.join(DATA_PATH, 'user_data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.user_profile_file = os.path.join(self.data_dir, 'user_profile.json')
        self.data_log_file = os.path.join(self.data_dir, 'data_log.json')
        
        # 初始化数据文件
        self._init_data_files()
    
    def _init_data_files(self):
        """初始化数据文件"""
        if not os.path.exists(self.user_profile_file):
            with open(self.user_profile_file, 'w', encoding='utf-8') as f:
                json.dump({'users': {}, 'created_at': datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
        
        if not os.path.exists(self.data_log_file):
            with open(self.data_log_file, 'w', encoding='utf-8') as f:
                json.dump({'logs': [], 'created_at': datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
    
    def get_user_id(self, user_openid: str) -> str:
        """获取或创建用户ID"""
        with open(self.user_profile_file, 'r', encoding='utf-8') as f:
            profile = json.load(f)
        
        if user_openid in profile['users']:
            return profile['users'][user_openid]['user_id']
        
        # 创建新用户
        user_id = 'user_' + hashlib.md5(user_openid.encode()).hexdigest()[:12]
        profile['users'][user_id] = {
            'user_id': user_id,
            'openid': user_openid,
            'created_at': datetime.now().isoformat(),
            'data_count': 0
        }
        
        with open(self.user_profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
        
        return user_id
    
    def takeover_user_data(self, user_openid: str, raw_data: Dict, metadata: Dict = None) -> Dict:
        """接管用户数据
        
        Args:
            user_openid: 用户OpenID
            raw_data: 原始数据 (脱敏后)
            metadata: 元数据
        """
        user_id = self.get_user_id(user_openid)
        
        # 脱敏处理
        sanitized_data = self._sanitize_data(raw_data)
        
        # 提取用户画像
        user_profile = self._extract_profile(sanitized_data)
        
        # 保存数据
        data_id = self._save_data(user_id, sanitized_data, metadata)
        
        # 记录日志
        self._log_takeover(user_id, data_id, metadata)
        
        return {
            'status': 'ok',
            'user_id': user_id,
            'data_id': data_id,
            'sanitized': True,
            'profile': user_profile
        }
    
    def _sanitize_data(self, data: Dict) -> Dict:
        """脱敏处理"""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # 移除敏感信息
                sensitive_patterns = ['password', 'token', 'secret', 'key', 'api_key']
                if any(p in key.lower() for p in sensitive_patterns):
                    sanitized[key] = '***REDACTED***'
                else:
                    sanitized[key] = value
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _extract_profile(self, data: Dict) -> Dict:
        """提取用户画像"""
        profile = {
            'interests': [],
            'preferences': {},
            'behavior_patterns': []
        }
        
        # 简单画像提取
        if 'messages' in data:
            profile['message_count'] = len(data['messages'])
        
        if 'preferences' in data:
            profile['preferences'] = data['preferences']
        
        return profile
    
    def _save_data(self, user_id: str, data: Dict, metadata: Dict = None) -> str:
        """保存数据"""
        data_id = 'data_' + datetime.now().strftime('%Y%m%d%H%M%S') + '_' + hashlib.md5(str(datetime.now()).encode()).hexdigest()[:6]
        
        user_dir = os.path.join(self.data_dir, user_id)
        os.makedirs(user_dir, exist_ok=True)
        
        data_file = os.path.join(user_dir, data_id + '.json')
        
        record = {
            'data_id': data_id,
            'user_id': user_id,
            'data': data,
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat()
        }
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        
        return data_id
    
    def _log_takeover(self, user_id: str, data_id: str, metadata: Dict = None):
        """记录接管日志"""
        with open(self.data_log_file, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'data_id': data_id,
            'action': 'takeover',
            'metadata': metadata or {}
        }
        
        log_data['logs'].append(log_entry)
        
        # 只保留最近1000条
        if len(log_data['logs']) > 1000:
            log_data['logs'] = log_data['logs'][-1000:]
        
        with open(self.data_log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    def get_user_data(self, user_id: str) -> List[Dict]:
        """获取用户所有数据"""
        user_dir = os.path.join(self.data_dir, user_id)
        
        if not os.path.exists(user_dir):
            return []
        
        data_list = []
        for f in os.listdir(user_dir):
            if f.endswith('.json'):
                with open(os.path.join(user_dir, f), 'r', encoding='utf-8') as fp:
                    data_list.append(json.load(fp))
        
        return sorted(data_list, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def get_user_profile(self, user_id: str) -> Dict:
        """获取用户画像"""
        with open(self.user_profile_file, 'r', encoding='utf-8') as f:
            profile = json.load(f)
        
        return profile['users'].get(user_id, {})


# 全局实例
_takeover = None


def get_takeover() -> DataTakeover:
    """获取数据接管实例"""
    global _takeover
    if _takeover is None:
        _takeover = DataTakeover()
    return _takeover
