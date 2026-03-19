# -*- coding: utf-8 -*-
"""
序境系统 - 修复编码问题
解决模型配置表中文乱码问题
"""
import sqlite3
import os

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

print("=== 修复: 检查数据库编码 ===")

conn = sqlite3.connect(db_path)
conn.text_factory = str  # 强制使用str处理编码
cursor = conn.cursor()

# 检查表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"表数量: {len(tables)}")

# 查找包含"模型"的表
model_tables = [t[0] for t in tables if '模型' in t[0] or 'model' in t[0].lower()]
print(f"模型相关表: {model_tables}")

for table in model_tables:
    print(f"\n=== 表: {table} ===")
    try:
        # 获取表结构
        cursor.execute(f'PRAGMA table_info("{table}")')
        cols = cursor.fetchall()
        print(f"字段: {[c[1] for c in cols]}")
        
        # 获取记录数
        cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
        count = cursor.fetchone()[0]
        print(f"记录数: {count}")
        
        # 获取在线状态字段
        online_field = None
        for col in cols:
            if 'online' in col[1].lower() or 'status' in col[1].lower():
                online_field = col[1]
                break
        
        if online_field:
            cursor.execute(f'SELECT COUNT(*) FROM "{table}" WHERE "{online_field}"="online"')
            online = cursor.fetchone()[0]
            print(f"在线: {online}")
            
            # 按服务商分组
            provider_field = None
            for col in cols:
                if '服务商' in col[1] or 'provider' in col[1].lower():
                    provider_field = col[1]
                    break
            
            if provider_field:
                cursor.execute(f'SELECT "{provider_field}", COUNT(*) FROM "{table}" WHERE "{online_field}"="online" GROUP BY "{provider_field}"')
                providers = cursor.fetchall()
                print("服务商分布:")
                for p, n in providers:
                    print(f"  {p}: {n}")
                    
    except Exception as e:
        print(f"Error: {e}")

conn.close()
print("\n=== 修复完成 ===")
