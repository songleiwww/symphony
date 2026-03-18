"""
序境内核 - 模型管理器
实现模型自动入队功能
"""

import sqlite3
from typing import Dict, List, Optional
from contextlib import contextmanager
import logging
import time

logger = logging.getLogger(__name__)


class ModelRegistry:
    """模型注册中心 - 自动入队"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._last_check = 0
        self._check_interval = 60  # 60秒检查一次
    
    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def get_all_models(self) -> List[Dict]:
        """获取所有模型配置"""
        with self._conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM 模型配置表")
            rows = cursor.fetchall()
            result = []
            for row in rows:
                if row[6]:  # 有API密钥
                    result.append({
                        "id": row[0],
                        "model_name": row[1],
                        "model_key": row[2],
                        "provider": row[4],
                        "api_url": row[5],
                        "api_key": row[6],
                        "enabled": row[7]
                    })
            return result
    
    def get_new_models(self, last_known_ids: List[str]) -> List[Dict]:
        """获取新加入的模型"""
        all_models = self.get_all_models()
        new_models = [m for m in all_models if m["id"] not in last_known_ids]
        return new_models
    
    def check_and_enroll(self, scheduler) -> List[Dict]:
        """检查并自动入队新模型"""
        current_time = time.time()
        if current_time - self._last_check < self._check_interval:
            return []
        
        self._last_check = current_time
        
        # 获取当前调度器已注册的模型ID
        registered_ids = list(scheduler.models.keys())
        
        # 检查数据库中的模型
        all_models = self.get_all_models()
        enrolled = []
        
        for m in all_models:
            if m["id"] not in registered_ids and m.get("enabled") == "是":
                # 自动入队
                from .scheduler import ModelConfig, ModelStatus
                model = ModelConfig(
                    model_id=str(m["id"]),
                    model_name=m["model_name"],
                    provider=m["provider"],
                    api_url=m["api_url"],
                    api_key=m["api_key"]
                )
                scheduler.register_model(model)
                enrolled.append(m["model_name"])
                logger.info(f"模型自动入队: {m['model_name']}")
        
        return enrolled
    
    def get_model_health(self, model_id: str) -> Optional[Dict]:
        """获取模型健康状态"""
        with self._conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM 模型配置表 WHERE id=?", (model_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "name": row[1],
                    "enabled": row[7]
                }
            return None


# 全局注册中心
_registry: Optional[ModelRegistry] = None


def get_registry(db_path: str = "") -> ModelRegistry:
    """获取模型注册中心"""
    global _registry
    if _registry is None:
        if not db_path:
            db_path = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"
        _registry = ModelRegistry(db_path)
    return _registry
