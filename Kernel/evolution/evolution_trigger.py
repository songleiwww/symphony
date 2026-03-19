"""
进化阈值触发器模块
Evolution Threshold Trigger Module

工部尚书苏云渺 负责工程营造
功能：统计有效决策数量，当积累到阈值时触发进化，支持版本控制与回滚
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path


class EvolutionTrigger:
    """进化阈值触发器 - 统计有效决策，触发策略进化"""
    
    def __init__(self, threshold: int = 100, db_path: Optional[str] = None):
        """
        初始化进化触发器
        
        Args:
            threshold: 触发进化的阈值（默认100次）
            db_path: 数据库路径（可选，默认在evolution目录）
        """
        self.threshold = threshold
        self.counter = 0
        
        # 设置数据库路径
        if db_path is None:
            base_dir = Path(__file__).parent
            db_path = base_dir / "evolution.db"
        self.db_path = str(db_path)
        
        # 初始化数据库
        self._init_db()
        
        # 恢复之前的计数器状态
        self._load_state()
    
    def _init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建状态表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evolution_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # 创建版本记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_versions (
                version_id INTEGER PRIMARY KEY AUTOINCREMENT,
                version_name TEXT NOT NULL,
                strategy_data TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                is_active INTEGER DEFAULT 0
            )
        """)
        
        # 创建进化历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evolution_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_version INTEGER,
                to_version INTEGER,
                trigger_count INTEGER NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_state(self):
        """从数据库加载状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 加载计数器
        cursor.execute(
            "SELECT value FROM evolution_state WHERE key = 'counter'",
        )
        row = cursor.fetchone()
        if row:
            self.counter = int(row[0])
        else:
            # 初始化计数器
            cursor.execute(
                "INSERT INTO evolution_state (key, value, updated_at) VALUES (?, ?, ?)",
                ("counter", "0", datetime.now().isoformat())
            )
            conn.commit()
            self.counter = 0
        
        conn.close()
    
    def _save_state(self):
        """保存状态到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE evolution_state SET value = ?, updated_at = ? WHERE key = 'counter'",
            (str(self.counter), datetime.now().isoformat())
        )
        
        conn.commit()
        conn.close()
    
    def record_valid_decision(self) -> bool:
        """
        记录有效决策
        
        Returns:
            bool: 是否触发进化
        """
        self.counter += 1
        self._save_state()
        
        if self.counter >= self.threshold:
            return True
        return False
    
    def get_progress(self) -> dict:
        """
        获取进度信息
        
        Returns:
            dict: 包含current和threshold的进度信息
        """
        return {
            "current": self.counter,
            "threshold": self.threshold,
            "progress": round(self.counter / self.threshold * 100, 2) if self.threshold > 0 else 0
        }
    
    def reset(self):
        """重置计数器"""
        self.counter = 0
        self._save_state()
    
    def set_threshold(self, threshold: int):
        """设置新的阈值"""
        self.threshold = threshold
        self._save_state()
    
    # ==================== 版本控制功能 ====================
    
    def save_version(self, strategy_data: Dict[str, Any], version_name: str, 
                     description: str = "") -> int:
        """
        保存策略版本
        
        Args:
            strategy_data: 策略数据
            version_name: 版本名称
            description: 版本描述
        
        Returns:
            int: 版本ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 先将所有版本设为非激活
        cursor.execute("UPDATE strategy_versions SET is_active = 0")
        
        # 插入新版本
        cursor.execute(
            """INSERT INTO strategy_versions 
               (version_name, strategy_data, description, created_at, is_active) 
               VALUES (?, ?, ?, ?, 1)""",
            (version_name, json.dumps(strategy_data), description, datetime.now().isoformat())
        )
        
        version_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return version_id
    
    def get_active_version(self) -> Optional[Dict[str, Any]]:
        """
        获取当前激活的策略版本
        
        Returns:
            Optional[Dict]: 版本信息，包含version_id, strategy_data等
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT version_id, version_name, strategy_data, description, created_at 
               FROM strategy_versions WHERE is_active = 1""",
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "version_id": row[0],
                "version_name": row[1],
                "strategy_data": json.loads(row[2]),
                "description": row[3],
                "created_at": row[4]
            }
        return None
    
    def get_version(self, version_id: int) -> Optional[Dict[str, Any]]:
        """
        获取指定版本
        
        Args:
            version_id: 版本ID
        
        Returns:
            Optional[Dict]: 版本信息
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT version_id, version_name, strategy_data, description, created_at 
               FROM strategy_versions WHERE version_id = ?""",
            (version_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "version_id": row[0],
                "version_name": row[1],
                "strategy_data": json.loads(row[2]),
                "description": row[3],
                "created_at": row[4]
            }
        return None
    
    def list_versions(self) -> List[Dict[str, Any]]:
        """
        列出所有版本
        
        Returns:
            List[Dict]: 版本列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT version_id, version_name, description, created_at, is_active 
               FROM strategy_versions ORDER BY version_id DESC""",
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "version_id": row[0],
                "version_name": row[1],
                "description": row[2],
                "created_at": row[3],
                "is_active": bool(row[4])
            }
            for row in rows
        ]
    
    def rollback(self, version_id: int) -> bool:
        """
        回滚到指定版本
        
        Args:
            version_id: 目标版本ID
        
        Returns:
            bool: 是否成功回滚
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 检查版本是否存在
        cursor.execute("SELECT version_id FROM strategy_versions WHERE version_id = ?", (version_id,))
        if not cursor.fetchone():
            conn.close()
            return False
        
        # 获取当前激活版本
        cursor.execute("SELECT version_id FROM strategy_versions WHERE is_active = 1")
        from_version = cursor.fetchone()
        from_version_id = from_version[0] if from_version else None
        
        # 更新激活状态
        cursor.execute("UPDATE strategy_versions SET is_active = 0")
        cursor.execute("UPDATE strategy_versions SET is_active = 1 WHERE version_id = ?", (version_id,))
        
        # 记录进化历史
        cursor.execute(
            """INSERT INTO evolution_history (from_version, to_version, trigger_count, created_at)
               VALUES (?, ?, ?, ?)""",
            (from_version_id, version_id, self.counter, datetime.now().isoformat())
        )
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_evolution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取进化历史
        
        Args:
            limit: 返回记录数
        
        Returns:
            List[Dict]: 进化历史列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT id, from_version, to_version, trigger_count, description, created_at
               FROM evolution_history ORDER BY id DESC LIMIT ?""",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "from_version": row[1],
                "to_version": row[2],
                "trigger_count": row[3],
                "description": row[4],
                "created_at": row[5]
            }
            for row in rows
        ]
    
    def trigger_evolution(self, new_strategy: Dict[str, Any], version_name: str,
                          description: str = "") -> Dict[str, Any]:
        """
        触发进化 - 保存新版本并重置计数器
        
        Args:
            new_strategy: 新策略数据
            version_name: 版本名称
            description: 版本描述
        
        Returns:
            Dict: 进化结果
        """
        # 保存新版本
        version_id = self.save_version(new_strategy, version_name, description)
        
        # 记录进化历史
        old_version = self.get_active_version()
        old_version_id = old_version["version_id"] if old_version else None
        
        # 重置计数器
        old_counter = self.counter
        self.reset()
        
        return {
            "success": True,
            "version_id": version_id,
            "version_name": version_name,
            "trigger_count": old_counter,
            "message": f"进化触发成功！从版本 {old_version_id} 进化到版本 {version_id}"
        }


# 便捷函数
def create_trigger(threshold: int = 100, db_path: Optional[str] = None) -> EvolutionTrigger:
    """创建进化触发器实例"""
    return EvolutionTrigger(threshold=threshold, db_path=db_path)


if __name__ == "__main__":
    # 测试代码
    trigger = EvolutionTrigger(threshold=10)
    
    print("=== 进化阈值触发器测试 ===\n")
    
    # 测试记录决策
    for i in range(12):
        triggered = trigger.record_valid_decision()
        progress = trigger.get_progress()
        print(f"决策 {i+1}: 进度 {progress['current']}/{progress['threshold']} ({progress['progress']}%)")
        if triggered:
            print(f"  >>> 触发进化！")
    
    print("\n=== 保存测试版本 ===")
    test_strategy = {
        "name": "test_strategy",
        "parameters": {"learning_rate": 0.01, "batch_size": 32},
        "metrics": {"accuracy": 0.95}
    }
    result = trigger.trigger_evolution(test_strategy, "v1.0", "测试版本")
    print(result)
    
    print("\n=== 版本列表 ===")
    versions = trigger.list_versions()
    for v in versions:
        print(f"  v{v['version_id']}: {v['version_name']} (active: {v['is_active']})")
    
    print("\n=== 进度重置后 ===")
    print(trigger.get_progress())
