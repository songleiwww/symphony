import sqlite3
conn = sqlite3.connect(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db')
c = conn.cursor()

# Get all tables
c.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [r[0] for r in c.fetchall()]
print('Tables:', tables)

# Search for bailian in provider_registry
c.execute('SELECT * FROM provider_registry')
for row in c.fetchall():
    print('Provider:', row)

# Check model_config for aliyun
c.execute('SELECT id, model_name, api_address, api_key FROM model_config WHERE provider LIKE "%aliyun%" OR provider LIKE "%bailian%" LIMIT 10')
for row in c.fetchall():
    print('Model:', row[0], row[1], row[2], row[3][:20]+'...' if row[3] else None)

conn.close()
