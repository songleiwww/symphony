import sqlite3
conn = sqlite3.connect(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)

for table in tables:
    cur.execute(f"PRAGMA table_info({table})")
    cols = cur.fetchall()
    print(f"\n{table}: {[c[1] for c in cols]}")
