# -*- coding: utf-8 -*-
"""
序境系统数据库读取工具 - 修复版
解决子Agent读取数据库中文乱码问题

关键发现：不要设置text_factory！默认就是正确的UTF-8！
"""

import sqlite3

def get_db_connection(db_path=None):
    """获取数据库连接 - 不要设置text_factory！"""
    if db_path is None:
        db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
    
    conn = sqlite3.connect(db_path)
    # 关键：不要设置text_factory，默认就是正确的！
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

# 测试
if __name__ == '__main__':
    print('=== 序境系统总则 (前5条) ===')
    rules = read_rules()
    for r in rules[:5]:
        print(f'{r[0]}: {r[1]} - {r[2]}')
    
    print(f'\n总规则数: {len(rules)}')
