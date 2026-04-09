import sqlite3
conn = sqlite3.connect(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db')
cur = conn.cursor()

print("=== tool_registry ===")
cur.execute("SELECT * FROM tool_registry")
for row in cur.fetchall():
    print(row)

print("\n=== adaptive_config ===")
cur.execute("SELECT key, value, var_type FROM adaptive_config")
for row in cur.fetchall():
    print(row)

print("\n=== model_quotas ===")
cur.execute("SELECT * FROM model_quotas LIMIT 10")
for row in cur.fetchall():
    print(row)
