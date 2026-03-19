# -*- coding: utf-8 -*-
import sqlite3
conn = sqlite3.connect('C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db')
c = conn.cursor()
c.execute("UPDATE 模型配置表 SET 模型标识 = 'deepseek-ai/deepseek-r1-distill-qwen-32b' WHERE id = '12'")
c.commit()
print('Updated DeepSeek R1 model ID')
conn.close()
