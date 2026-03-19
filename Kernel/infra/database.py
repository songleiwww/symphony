"""
序境内核 - 基础设施层
"""

import sqlite3
from typing import Dict, List, Optional
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class ModelRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def get_all_enabled(self) -> List[Dict]:
        """获取所有启用的模型"""
        with self._conn() as conn:
            cursor = conn.cursor()
            # 列索引: 0=id, 1=模型名称, 4=服务商, 5=API地址, 6=API密钥
            cursor.execute("SELECT * FROM 模型配置表")
            rows = cursor.fetchall()
            result = []
            for row in rows:
                # 跳过没有API密钥的模型
                if row[6]:  # API密钥
                    result.append({
                        "id": row[0],
                        "model_name": row[1],
                        "provider": row[4],
                        "api_url": row[5],
                        "api_key": row[6]
                    })
            return result
    
    def get_by_provider(self, provider: str) -> List[Dict]:
        """按服务商获取"""
        with self._conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM 模型配置表")
            rows = cursor.fetchall()
            result = []
            for row in rows:
                if row[4] == provider and row[6]:
                    result.append({
                        "id": row[0],
                        "model_name": row[1],
                        "provider": row[4],
                        "api_url": row[5],
                        "api_key": row[6]
                    })
            return result
    
    def get_by_id(self, model_id: str) -> Optional[Dict]:
        """按ID获取"""
        with self._conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM 模型配置表 WHERE id=?", (model_id,))
            row = cursor.fetchone()
            if row and row[6]:
                return {
                    "id": row[0],
                    "model_name": row[1],
                    "provider": row[4],
                    "api_url": row[5],
                    "api_key": row[6]
                }
            return None
    
    def update_status(self, model_id: str, status: str):
        """更新状态"""
        with self._conn() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE 模型配置表 SET 是否启用=? WHERE id=?", (status, model_id))
            conn.commit()
