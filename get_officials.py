# -*- coding: utf-8 -*-
import sqlite3
conn = sqlite3.connect(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db')
cursor = conn.cursor()
cursor.execute("SELECT id, 姓名, 官职, 模型名称, 模型服务商 FROM 官属角色表 WHERE 状态='正常' OR 状态 IS NULL")
rows = cursor.fetchall()
print('Total:', len(rows))
for r in rows[:20]:
    print(f'{r[0]}|{r[1]}|{r[2]}|{r[3]}|{r[4]}')
conn.close()
