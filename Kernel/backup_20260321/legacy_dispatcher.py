#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境自动调度器
自动化调度序境角色执行任务
"""
import sqlite3
import os
import json
from typing import List, Dict, Optional

class Dispatcher:
    """序境调度器"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = os.path.join(
                os.path.dirname(__file__), "..", "data", "symphony.db"
            )
        else:
            self.db_path = db_path
    
    def get_available_roles(self) -> List[Dict]:
        """获取可用角色"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.id, r.姓名, r.官职, o.名称 as 官署, m.模型名称, m.服务商
            FROM 官署角色表 r
            JOIN 官署表 o ON r.所属官署 = o.id
            JOIN 模型配置表 m ON r.模型配置表_ID = m.id
            WHERE m.服务商 IN ('英伟达', '火山引擎')
        ''')
        roles = []
        for row in cursor.fetchall():
            roles.append({
                "id": row[0],
                "name": row[1],
                "title": row[2],
                "office": row[3],
                "model": row[4],
                "provider": row[5]
            })
        conn.close()
        return roles
    
    def select_roles_by_task(self, task: str) -> List[Dict]:
        """根据任务选择角色"""
        roles = self.get_available_roles()
        
        # 简单关键词匹配
        keywords = {
            "code": ["编程", "代码", "开发"],
            "vision": ["视觉", "图像", "图片"],
            "reasoning": ["推理", "分析", "思考"],
            "chat": ["对话", "聊天", "问答"]
        }
        
        selected = []
        for kw, keywords in keywords.items():
            if any(k in task for k in keywords):
                selected.extend([r for r in roles if kw.lower() in r["model"].lower()])
        
        # 如果没有匹配的，返回所有可用角色
        if not selected:
            selected = roles[:3]
        
        return selected[:5]  # 最多5个角色
    
    def dispatch(self, task: str) -> Dict:
        """调度执行任务"""
        roles = self.select_roles_by_task(task)
        return {
            "task": task,
            "assigned_roles": roles,
            "total": len(roles)
        }

if __name__ == "__main__":
    dispatcher = Dispatcher()
    result = dispatcher.dispatch("分析代码问题")
    print(json.dumps(result, ensure_ascii=False, indent=2))
