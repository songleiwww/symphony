import sqlite3
c = sqlite3.connect('C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db')
print([r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()])
