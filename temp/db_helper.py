# -*- coding: utf-8 -*-
"""
序境系统数据库读取工具
解决子Agent读取数据库中文乱码问题
"""

import sqlite3

def get_db_connection(db_path=None):
    """获取数据库连接，正确处理中文编码"""
    if db_path is None:
        db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
    
    conn = sqlite3.connect(db_path)
    # 关键：设置text_factory处理编码
    conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
    return conn

def read_rules():
    """读取序境系统总则"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM "序境系统总则" ORDER BY id')
    rules = cur.fetchall()
    conn.close()
    return rules

def read_model_config():
    """读取模型配置表"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM "模型配置表"')
    models = cur.fetchall()
    conn.close()
    return models

def read_roles():
    """读取官署角色表"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM "官署角色表"')
    roles = cur.fetchall()
    conn.close()
    return roles

# 测试
if __name__ == '__main__':
    print('=== 序境系统总则 (前5条) ===')
    rules = read_rules()
    for r in rules[:5]:
        print(f'{r[0]}: {r[1]} - {r[2]}')
    
    print(f'\n总规则数: {len(rules)}')
