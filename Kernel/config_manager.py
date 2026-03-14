# -*- coding: utf-8 -*-
"""
配置管理器 - 管理内核配置
"""
import sqlite3
from typing import Dict, List, Optional

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_rules(self) -> List[Dict]:
        """获取所有规则"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM 内核规则表 WHERE 状态='启用'")
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def update_rule(self, rule_id: str, content: str) -> bool:
        """更新规则"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE 内核规则表 SET 规则内容=? WHERE id=?", (content, rule_id))
        conn.commit()
        conn.close()
        return True
