# -*- coding: utf-8 -*-
import sqlite3
conn = sqlite3.connect(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony_working.db')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM model_config')
print('褰撳墠妯″瀷鏁伴噺:', cur.fetchone()[0])
conn.close()

