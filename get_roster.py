# -*- coding: utf-8 -*-
"""获取所有官属列表"""
import sqlite3
conn = sqlite3.connect('data/symphony.db')
cursor = conn.cursor()
cursor.execute('SELECT id, 官名, 职, 专长, 模型名称, 模型服务商, 角色等级 FROM 官属角色表 ORDER BY 角色等级, 职')
rows = cursor.fetchall()
print(f'Total officials: {len(rows)}')
for r in rows:
    print(f'{r[0]}|{r[1]}|{r[2]}|{r[3]}|{r[4]}|{r[5]}|{r[6]}')
conn.close()
