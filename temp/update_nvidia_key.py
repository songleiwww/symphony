import sqlite3
conn = sqlite3.connect('C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db')
conn.text_factory = str
c = conn.cursor()

# Find the model config table
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
model_table = None
for t in tables:
    if '模型' in t and '配置' in t:
        model_table = t
        break

# New API key
new_key = "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"

# Get count first
c.execute(f"SELECT COUNT(*) FROM '{model_table}' WHERE 服务商 = '英伟达'")
count = c.fetchone()[0]
print(f"Found {count} NVIDIA models")

# Update all NVIDIA models
c.execute(f"UPDATE '{model_table}' SET API密钥 = ? WHERE 服务商 = '英伟达'", (new_key,))

print(f"Updated NVIDIA models with new API key")

# Verify
c.execute(f"SELECT id, 模型名称, API密钥 FROM '{model_table}' WHERE 服务商 = '英伟达' LIMIT 3")
for row in c.fetchall():
    print(f"  ID {row[0]}: {row[1][:20]} - {row[2][:30]}...")

conn.commit()
conn.close()
print("\nDone!")
