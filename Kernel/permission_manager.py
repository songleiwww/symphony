#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权限管理器 - 细粒度权限控制系统
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

class PermissionManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "data", 
                "symphony.db"
            )
        else:
            self.db_path = db_path
            
        # 初始化权限表
        self._init_permission_tables()
    
    def _init_permission_tables(self):
        """初始化权限相关数据表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 官署角色表（绑定模型）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS 官署角色表 (
            id TEXT PRIMARY KEY,
            姓名 TEXT NOT NULL,
            官职 TEXT,
            职务 TEXT,
            所属官署 TEXT,
            职责 TEXT,
            角色等级 INTEGER DEFAULT 1,
            状态 TEXT DEFAULT '正常',
            创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            官署ID TEXT,
            模型配置表_ID TEXT
        )
        ''')
        
        # 权限表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS 权限表 (
            id TEXT PRIMARY KEY,
            权限名称 TEXT NOT NULL,
            权限描述 TEXT,
            权限类型 TEXT DEFAULT '功能',
            状态 TEXT DEFAULT '正常'
        )
        ''')
        
        # 角色权限关联表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS 角色权限关联表 (
            角色ID TEXT,
            权限ID TEXT,
            授权时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            授权人 TEXT,
            PRIMARY KEY (角色ID, 权限ID),
            FOREIGN KEY (角色ID) REFERENCES 官署角色表(id),
            FOREIGN KEY (权限ID) REFERENCES 权限表(id)
        )
        ''')
        
        # 操作日志表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS 操作日志表 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            角色ID TEXT,
            操作类型 TEXT NOT NULL,
            操作内容 TEXT,
            操作时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            IP地址 TEXT,
            操作结果 TEXT DEFAULT '成功',
            FOREIGN KEY (角色ID) REFERENCES 官署角色表(id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_role(self, role_data: Dict) -> bool:
        """新增官署角色"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO 官署角色表 (
                id, 姓名, 官职, 职务, 所属官署, 职责,
                角色等级, 状态, 官署ID, 模型配置表_ID
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                role_data["id"], role_data["姓名"],
                role_data.get("官职"), role_data.get("职务"),
                role_data.get("所属官署"), role_data.get("职责"),
                role_data.get("角色等级", 1), role_data.get("状态", "正常"),
                role_data.get("官署ID"), role_data.get("模型配置表_ID")
            ))
            
            conn.commit()
            conn.close()
            
            # 记录日志
            self.log_operation(role_data["id"], "新增角色", f"新增角色：{role_data['姓名']}")
            return True
        except Exception as e:
            print(f"新增角色失败: {e}")
            return False
    
    def get_role(self, role_id: str) -> Optional[Dict]:
        """获取角色信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM 官署角色表 WHERE id = ?", (role_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        # 获取列名
        cursor.execute("PRAGMA table_info(官署角色表)")
        columns = [col[1] for col in cursor.fetchall()]
        
        conn.close()
        return dict(zip(columns, row))
    
    def update_role(self, role_id: str, update_data: Dict) -> bool:
        """更新角色信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
            params = list(update_data.values()) + [role_id]
            
            cursor.execute(f"UPDATE 官署角色表 SET {set_clause}, 更新时间 = CURRENT_TIMESTAMP WHERE id = ?", params)
            
            conn.commit()
            conn.close()
            
            self.log_operation(role_id, "更新角色", f"更新角色信息：{update_data.keys()}")
            return True
        except Exception as e:
            print(f"更新角色失败: {e}")
            return False
    
    def add_permission(self, perm_id: str, perm_name: str, perm_desc: str = "", perm_type: str = "功能") -> bool:
        """新增权限"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO 权限表 (id, 权限名称, 权限描述, 权限类型, 状态)
            VALUES (?, ?, ?, ?, '正常')
            ''', (perm_id, perm_name, perm_desc, perm_type))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"新增权限失败: {e}")
            return False
    
    def grant_permission(self, role_id: str, perm_id: str, authorizer: str = "system") -> bool:
        """为角色授权"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT OR REPLACE INTO 角色权限关联表 (角色ID, 权限ID, 授权人)
            VALUES (?, ?, ?)
            ''', (role_id, perm_id, authorizer))
            
            conn.commit()
            conn.close()
            
            self.log_operation(role_id, "授权", f"授予权限：{perm_id}")
            return True
        except Exception as e:
            print(f"授权失败: {e}")
            return False
    
    def has_permission(self, role_id: str, perm_id: str) -> bool:
        """检查角色是否有指定权限"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT 1 FROM 角色权限关联表 
        WHERE 角色ID = ? AND 权限ID = ?
        ''', (role_id, perm_id))
        
        result = cursor.fetchone() is not None
        conn.close()
        
        return result
    
    def get_role_permissions(self, role_id: str) -> List[str]:
        """获取角色所有权限"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT p.权限名称 FROM 角色权限关联表 r
        JOIN 权限表 p ON r.权限ID = p.id
        WHERE r.角色ID = ?
        ''', (role_id,))
        
        permissions = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return permissions
    
    def log_operation(self, role_id: str, op_type: str, op_content: str, ip: str = "", result: str = "成功") -> bool:
        """记录操作日志"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO 操作日志表 (角色ID, 操作类型, 操作内容, IP地址, 操作结果)
            VALUES (?, ?, ?, ?, ?)
            ''', (role_id, op_type, op_content, ip, result))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"记录日志失败: {e}")
            return False
    
    def get_operation_logs(self, role_id: str = None, limit: int = 100) -> List[Dict]:
        """获取操作日志"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if role_id:
            cursor.execute('''
            SELECT * FROM 操作日志表 WHERE 角色ID = ? 
            ORDER BY 操作时间 DESC LIMIT ?
            ''', (role_id, limit))
        else:
            cursor.execute('''
            SELECT * FROM 操作日志表 
            ORDER BY 操作时间 DESC LIMIT ?
            ''', (limit,))
        
        # 获取列名
        cursor.execute("PRAGMA table_info(操作日志表)")
        columns = [col[1] for col in cursor.fetchall()]
        
        logs = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        
        return logs

# 单例实例
_perm_manager_instance: Optional[PermissionManager] = None

def get_permission_manager() -> PermissionManager:
    """获取权限管理器单例"""
    global _perm_manager_instance
    if _perm_manager_instance is None:
        _perm_manager_instance = PermissionManager()
    return _perm_manager_instance

if __name__ == "__main__":
    # 测试权限管理器
    perm_manager = get_permission_manager()
    
    # 添加测试权限
    perm_manager.add_permission("model_call", "模型调用", "允许调用AI模型")
    perm_manager.add_permission("config_edit", "配置修改", "允许修改系统配置")
    perm_manager.add_permission("user_manage", "用户管理", "允许管理用户角色")
    
    print("✅ 权限管理器初始化完成")
