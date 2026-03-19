#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统 - 模型健康检测与熔断机制
Model Health Check & Circuit Breaker
"""
import sqlite3
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass, field

@dataclass
class ModelHealth:
    """模型健康状态"""
    model_id: int
    model_name: str
    api_identifier: str
    is_available: bool = True
    consecutive_failures: int = 0
    last_check: Optional[str] = None
    last_failure: Optional[str] = None
    cooldown_until: Optional[str] = None
    
    # 配置
    max_failures: int = 3          # 最大连续失败次数
    cooldown_seconds: int = 300     # 冷却时间5分钟

class CircuitBreaker:
    """熔断器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.health_cache: Dict[int, ModelHealth] = {}
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 创建健康检测表
        c.execute("""
            CREATE TABLE IF NOT EXISTS model_health (
                model_id INTEGER PRIMARY KEY,
                is_available INTEGER DEFAULT 1,
                consecutive_failures INTEGER DEFAULT 0,
                last_check TEXT,
                last_failure TEXT,
                cooldown_until TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_available_models(self, provider: str = None) -> list:
        """获取可用模型列表"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if provider:
            c.execute("""
                SELECT m.id, m.模型名称, m.模型标识符, h.is_available, h.consecutive_failures
                FROM 模型配置表 m
                LEFT JOIN model_health h ON m.id = h.model_id
                WHERE m.服务商 = ?
                AND (h.is_available IS NULL OR h.is_available = 1)
                ORDER BY m.id
            """, (provider,))
        else:
            c.execute("""
                SELECT m.id, m.模型名称, m.模型标识符, h.is_available, h.consecutive_failures
                FROM 模型配置表 m
                LEFT JOIN model_health h ON m.id = h.model_id
                WHERE h.is_available IS NULL OR h.is_available = 1
                ORDER BY m.id
            """)
        
        rows = c.fetchall()
        conn.close()
        
        return rows
    
    def record_failure(self, model_id: int, model_name: str, api_identifier: str):
        """记录失败"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        now = datetime.now().isoformat()
        cooldown = datetime.now() + timedelta(seconds=300)  # 5分钟冷却
        
        # 检查是否存在记录
        c.execute("SELECT consecutive_failures FROM model_health WHERE model_id = ?", (model_id,))
        row = c.fetchone()
        
        if row:
            failures = row[0] + 1
            is_available = 0 if failures >= 3 else 1
            cooldown_str = cooldown.isoformat() if failures >= 3 else None
            
            c.execute("""
                UPDATE model_health 
                SET consecutive_failures = ?, last_failure = ?, is_available = ?, cooldown_until = ?
                WHERE model_id = ?
            """, (failures, now, is_available, cooldown_str, model_id))
        else:
            c.execute("""
                INSERT INTO model_health 
                (model_id, consecutive_failures, last_failure, is_available, cooldown_until)
                VALUES (?, 1, ?, 1, NULL)
            """, (model_id, now))
        
        conn.commit()
        conn.close()
        
        print(f"⚠️ 模型 {model_id} ({model_name}) 失败+1, 共{self._get_failures(model_id)}次")
    
    def record_success(self, model_id: int):
        """记录成功，清除失败计数"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        now = datetime.now().isoformat()
        
        c.execute("""
            UPDATE model_health 
            SET consecutive_failures = 0, last_check = ?, is_available = 1, cooldown_until = NULL
            WHERE model_id = ?
        """, (now, model_id))
        
        conn.commit()
        conn.close()
        
        print(f"✅ 模型 {model_id} 恢复健康")
    
    def _get_failures(self, model_id: int) -> int:
        """获取失败次数"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT consecutive_failures FROM model_health WHERE model_id = ?", (model_id,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else 0
    
    def check_cooldown(self, model_id: int) -> bool:
        """检查是否在冷却期"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT cooldown_until FROM model_health WHERE model_id = ?", (model_id,))
        row = c.fetchone()
        conn.close()
        
        if not row or not row[0]:
            return False
        
        cooldown_until = datetime.fromisoformat(row[0])
        if datetime.now() > cooldown_until:
            # 冷却期结束，尝试恢复
            self._try_recover(model_id)
            return False
        
        return True
    
    def _try_recover(self, model_id: int):
        """尝试恢复模型"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 重置失败次数，恢复可用
        c.execute("""
            UPDATE model_health 
            SET consecutive_failures = 0, is_available = 1, cooldown_until = NULL
            WHERE model_id = ?
        """, (model_id,))
        
        conn.commit()
        conn.close()
        
        print(f"🔄 模型 {model_id} 冷却期结束，已恢复")
    
    def manual_recover(self, model_id: int):
        """手动恢复模型"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""
            UPDATE model_health 
            SET consecutive_failures = 0, is_available = 1, cooldown_until = NULL
            WHERE model_id = ?
        """, (model_id,))
        
        conn.commit()
        conn.close()
        
        print(f"✅ 模型 {model_id} 已手动恢复")
    
    def get_health_status(self) -> Dict:
        """获取健康状态汇总"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""
            SELECT m.id, m.模型名称, m.服务商, h.is_available, h.consecutive_failures, h.cooldown_until
            FROM 模型配置表 m
            LEFT JOIN model_health h ON m.id = h.model_id
            WHERE h.is_available = 0 OR h.consecutive_failures > 0
            ORDER BY h.consecutive_failures DESC
        """)
        
        rows = c.fetchall()
        conn.close()
        
        return {
            "unhealthy": [{"id": r[0], "name": r[1], "provider": r[2], "failures": r[4]} for r in rows],
            "total_unhealthy": len(rows)
        }

# 测试
if __name__ == "__main__":
    db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
    cb = CircuitBreaker(db_path)
    
    print("=== 英伟达可用模型 ===")
    models = cb.get_available_models("英伟达")
    for m in models:
        print(f"ID {m[0]}: {m[1]} = {m[2]}")
    
    print("\n=== 健康状态 ===")
    status = cb.get_health_status()
    print(f"不健康模型数: {status['total_unhealthy']}")
