#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内核加载器 - 从 symphony.db 加载配置
迭代版本: 支持规则/官署/官属/模型
"""
import sqlite3
import os
from typing import Dict, List, Optional

class KernelLoader:
    """内核加载器"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            current_file = os.path.abspath(__file__)
            project_dir = os.path.dirname(os.path.dirname(current_file))
            self.db_path = os.path.join(project_dir, "data", "symphony.db")
        else:
            self.db_path = db_path
        
        self.rules: List[Dict] = []
        self.offices: List[Dict] = []
        self.roles: List[Dict] = []
        self.models: Dict[str, Dict] = []
        
    def load_all(self) -> bool:
        """加载所有配置"""
        try:
            self.load_rules()
            self.load_offices()
            self.load_roles()
            self.load_models()
            return True
        except Exception as e:
            print(f"加载失败: {e}")
            return False
    
    def load_rules(self) -> bool:
        """加载内核规则"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(内核规则表)")
        columns = [col[1] for col in cursor.fetchall()]
        cursor.execute("SELECT * FROM 内核规则表 WHERE 状态='启用' ORDER BY 优先级")
        self.rules = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        print(f"加载规则: {len(self.rules)}条")
        return True
    
    def load_offices(self) -> bool:
        """加载官署配置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(官署表)")
        columns = [col[1] for col in cursor.fetchall()]
        cursor.execute("SELECT * FROM 官署表 WHERE 状态='正常' ORDER BY 级别, 名称")
        self.offices = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        print(f"加载官署: {len(self.offices)}个")
        return True
    
    def load_roles(self) -> bool:
        """加载官属角色"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(官属角色表)")
        columns = [col[1] for col in cursor.fetchall()]
        cursor.execute("SELECT * FROM 官属角色表 WHERE 状态='正常'")
        self.roles = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        print(f"加载官属: {len(self.roles)}人")
        return True
    
    def load_models(self) -> bool:
        """加载模型配置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM 模型配置表 WHERE 状态='正常'")
        rows = cursor.fetchall()
        cursor.execute("PRAGMA table_info(模型配置表)")
        columns = [col[1] for col in cursor.fetchall()]
        self.models = [dict(zip(columns, row)) for row in rows]
        conn.close()
        print(f"加载模型: {len(self.models)}个")
        return True
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "rules": len(self.rules),
            "offices": len(self.offices),
            "roles": len(self.roles),
            "models": len(self.models)
        }
