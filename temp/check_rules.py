# -*- coding: utf-8 -*-
import sqlite3

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 查看序境系统总则表结构
print("=== 序境系统总则 表结构 ===\n")
c.execute("PRAGMA table_info(序境系统总则)")
for row in c.fetchall():
    print(f"{row[1]} ({row[2]})")

# 查看记录
print("\n=== 序境系统总则 记录数 ===\n")
c.execute("SELECT COUNT(*) FROM 序境系统总则")
print(f"共 {c.fetchone()[0]} 条记录")

# 查看最新几条
print("\n=== 最新记录 ===\n")
c.execute("SELECT id, 规则编号, 更新时间 FROM 序境系统总则 ORDER BY id DESC LIMIT 5")
for row in c.fetchall():
    print(f"ID: {row[0]}, 规则编号: {row[1]}, 更新时间: {row[2]}")

conn.close()
