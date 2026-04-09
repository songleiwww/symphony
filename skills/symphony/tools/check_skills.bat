@echo off
python -c "import sqlite3; import json; conn = sqlite3.connect('C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'); cursor = conn.cursor(); cursor.execute('SELECT * FROM \"Skill 持久化表\"'); print('技能列表:'); [print(f'  - {row[1]} (状态：{row[4]}, 版本：{row[5]})') for row in cursor.fetchall()]; conn.close()"
pause
