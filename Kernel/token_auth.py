#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统 v3.2.0 - Token 认证模块
提供 API Token 生成、验证、管理功能
"""
import sqlite3
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from dataclasses import dataclass


class TokenType:
    """Token类型"""
    API = "api"           # API调用Token
    USER = "user"         # 用户会话Token
    MODEL = "model"       # 模型配额Token
    ADMIN = "admin"       # 管理员Token


@dataclass
class TokenInfo:
    """Token信息"""
    token_id: str
    token_type: str
    name: str
    created_at: str
    expires_at: Optional[str]
    last_used: Optional[str]
    is_active: bool
    quota: Optional[int]  # 使用配额


class TokenAuthManager:
    """Token认证管理器"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "data", 
                "symphony.db"
            )
        else:
            self.db_path = db_path
        self._init_token_tables()
    
    def _init_token_tables(self):
        """初始化Token表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Token表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Token认证表 (
            token_id TEXT PRIMARY KEY,
            token_hash TEXT NOT NULL,
            token_type TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            last_used TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            quota INTEGER,
            usage_count INTEGER DEFAULT 0,
            metadata TEXT
        )
        ''')
        
        # Token使用日志
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Token使用日志表 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_id TEXT NOT NULL,
            used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            endpoint TEXT,
            ip_address TEXT,
            success INTEGER,
            FOREIGN KEY (token_id) REFERENCES Token认证表(token_id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _hash_token(self, token: str) -> str:
        """Hash Token"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def generate_token(
        self, 
        name: str, 
        token_type: str = TokenType.API,
        expires_days: int = 30,
        quota: Optional[int] = None
    ) -> Dict[str, str]:
        """
        生成Token
        
        Args:
            name: Token名称/用途
            token_type: Token类型
            expires_days: 过期天数 (0表示永不过期)
            quota: 使用配额限制
            
        Returns:
            {"token_id": "...", "token": "..."}
        """
        token_id = secrets.token_hex(8)
        raw_token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(raw_token)
        
        expires_at = None
        if expires_days > 0:
            expires_at = (datetime.now() + timedelta(days=expires_days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO Token认证表 
        (token_id, token_hash, token_type, name, expires_at, quota)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (token_id, token_hash, token_type, name, expires_at, quota))
        
        conn.commit()
        conn.close()
        
        return {
            "token_id": token_id,
            "token": raw_token,
            "token_type": token_type,
            "name": name,
            "expires_at": expires_at
        }
    
    def verify_token(self, raw_token: str) -> Optional[Dict]:
        """
        验证Token
        
        Args:
            raw_token: 原始Token字符串
            
        Returns:
            Token信息Dict或None
        """
        token_hash = self._hash_token(raw_token)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM Token认证表 WHERE token_hash = ? AND is_active = 1
        ''', (token_hash,))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        # 检查过期
        if row['expires_at']:
            expires = datetime.fromisoformat(row['expires_at'])
            if datetime.now() > expires:
                conn.close()
                return None
        
        # 检查配额
        if row['quota'] and row['usage_count'] >= row['quota']:
            conn.close()
            return None
        
        # 更新最后使用时间
        cursor.execute('''
        UPDATE Token认证表 
        SET last_used = CURRENT_TIMESTAMP, usage_count = usage_count + 1
        WHERE token_id = ?
        ''', (row['token_id'],))
        
        conn.commit()
        conn.close()
        
        return {
            "token_id": row['token_id'],
            "token_type": row['token_type'],
            "name": row['name'],
            "usage_count": row['usage_count'] + 1
        }
    
    def revoke_token(self, token_id: str) -> bool:
        """撤销Token"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE Token认证表 SET is_active = 0 WHERE token_id = ?
        ''', (token_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def list_tokens(self, token_type: Optional[str] = None) -> List[Dict]:
        """列出所有Token"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if token_type:
            cursor.execute('''
            SELECT token_id, token_type, name, created_at, expires_at, 
                   last_used, is_active, quota, usage_count
            FROM Token认证表 WHERE token_type = ?
            ''', (token_type,))
        else:
            cursor.execute('''
            SELECT token_id, token_type, name, created_at, expires_at,
                   last_used, is_active, quota, usage_count
            FROM Token认证表
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_usage_log(self, token_id: str, limit: int = 100) -> List[Dict]:
        """获取Token使用日志"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM Token使用日志表 
        WHERE token_id = ? 
        ORDER BY used_at DESC LIMIT ?
        ''', (token_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]


# 便捷函数
def create_api_token(name: str, expires_days: int = 30) -> Dict:
    """创建API Token"""
    manager = TokenAuthManager()
    return manager.generate_token(name, TokenType.API, expires_days)


def verify_api_token(token: str) -> Optional[Dict]:
    """验证API Token"""
    manager = TokenAuthManager()
    return manager.verify_token(token)


if __name__ == "__main__":
    # 测试
    manager = TokenAuthManager()
    
    # 生成测试Token
    result = manager.generate_token("测试API", TokenType.API, 7, 1000)
    print(f"生成Token: {result}")
    
    # 验证
    verified = manager.verify_token(result['token'])
    print(f"验证结果: {verified}")
    
    # 列出
    tokens = manager.list_tokens()
    print(f"当前Token数: {len(tokens)}")
