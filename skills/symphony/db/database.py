# -*- coding: utf-8 -*-
"""
Symphony Database Core
Pure English structure, no Chinese characters to avoid encoding issues
"""

import sqlite3
import os
from typing import Optional, List, Dict, Any
from datetime import datetime

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'symphony.db')

class SymphonyDatabase:
    """Symphony system database management class"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_dir()
    
    def _init_dir(self) -> None:
        """Ensure database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self) -> None:
        """Initialize database, create all required tables (pure English structure)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Drop existing tables to replace with clean structure
        cursor.execute('DROP TABLE IF EXISTS model_config')
        cursor.execute('DROP TABLE IF EXISTS provider_registry')
        cursor.execute('DROP TABLE IF EXISTS task_history')
        cursor.execute('DROP TABLE IF EXISTS node_registry')
        
        # 1. model_config table: store all model configuration
        cursor.execute('''
            CREATE TABLE model_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                model_id TEXT NOT NULL,
                model_name TEXT,
                model_type TEXT,
                context_window INTEGER,
                max_tokens INTEGER,
                pricing REAL,
                is_free BOOLEAN DEFAULT 1,
                is_enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(provider, model_id)
            );
        ''')
        
        # 2. provider_registry table: store provider information
        cursor.execute('''
            CREATE TABLE provider_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_code TEXT NOT NULL UNIQUE,
                provider_name TEXT NOT NULL,
                base_url TEXT,
                api_key TEXT,
                is_enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        # 3. task_history table: store task scheduling history
        cursor.execute('''
            CREATE TABLE task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL UNIQUE,
                provider TEXT NOT NULL,
                model_id TEXT NOT NULL,
                task_type TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                status TEXT,
                tokens_used INTEGER,
                cost REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        # 4. node_registry table: ACO node registry
        cursor.execute('''
            CREATE TABLE node_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id TEXT NOT NULL UNIQUE,
                provider TEXT NOT NULL,
                model_id TEXT NOT NULL,
                pheromone REAL DEFAULT 1.0,
                capability TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        conn.commit()
        conn.close()
        print(f"Database initialized successfully, path: {self.db_path}")
    
    def check_table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def add_model(self, provider: str, model_id: str, model_name: str = None, 
                 model_type: str = None, context_window: int = None, 
                 max_tokens: int = None, pricing: float = None, 
                 is_free: bool = True, is_enabled: bool = True) -> int:
        """Add a new model to config"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO model_config 
                (provider, model_id, model_name, model_type, context_window, 
                 max_tokens, pricing, is_free, is_enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (provider, model_id, model_name, model_type, context_window,
                  max_tokens, pricing, 1 if is_free else 0, 1 if is_enabled else 0))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Model already exists, update it
            cursor.execute('''
                UPDATE model_config SET 
                model_name=?, model_type=?, context_window=?, max_tokens=?,
                pricing=?, is_free=?, is_enabled=?, updated_at=CURRENT_TIMESTAMP
                WHERE provider=? AND model_id=?
            ''', (model_name, model_type, context_window, max_tokens,
                  pricing, 1 if is_free else 0, 1 if is_enabled else 0,
                  provider, model_id))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_all_models(self, enabled_only: bool = True) -> List[Dict]:
        """Get all models from config"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if enabled_only:
            cursor.execute("SELECT * FROM model_config WHERE is_enabled=1")
        else:
            cursor.execute("SELECT * FROM model_config")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_models_by_provider(self, provider: str, enabled_only: bool = True) -> List[Dict]:
        """Get all models for a specific provider"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if enabled_only:
            cursor.execute("SELECT * FROM model_config WHERE provider=? AND is_enabled=1", (provider,))
        else:
            cursor.execute("SELECT * FROM model_config WHERE provider=?", (provider,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def add_provider(self, provider_code: str, provider_name: str, base_url: str = None, 
                   api_key: str = None, is_enabled: bool = True) -> int:
        """Add a new provider to registry (unified key manager)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO provider_registry
                (provider_code, provider_name, base_url, api_key, is_enabled)
                VALUES (?, ?, ?, ?, ?)
            ''', (provider_code, provider_name, base_url, api_key, 1 if is_enabled else 0))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Provider already exists, update it
            cursor.execute('''
                UPDATE provider_registry SET
                provider_name=?, base_url=?, api_key=?, is_enabled=?, updated_at=CURRENT_TIMESTAMP
                WHERE provider_code=?
            ''', (provider_name, base_url, api_key, 1 if is_enabled else 0, provider_code))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

# Auto init database when module is imported
if __name__ == "__main__":
    db = SymphonyDatabase()
    db.init_database()
