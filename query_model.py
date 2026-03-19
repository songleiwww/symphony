import sqlite3

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cursor = conn.cursor()

# Use the exact table name from search result
table_name = 'ģ�����ñ�'

# Get column info
cursor.execute(f"PRAGMA table_info('{table_name}')")
cols_info = cursor.fetchall()

# Get all data - use cursor.description to get column names
cursor.execute(f"SELECT * FROM {table_name}")
rows = cursor.fetchall()
columns = [description[0] for description in cursor.description]

print(f"Columns: {columns}")
print(f"Total rows: {len(rows)}")

# Find indices
status_idx = None
online_idx = None
name_idx = None
vendor_idx = None

for i, col in enumerate(columns):
    if '状态' in col:
        status_idx = i
    if '在线' in col:
        online_idx = i
    if '名称' in col:
        name_idx = i
    if '服务商' in col:
        vendor_idx = i

print(f"\nstatus_idx: {status_idx}, online_idx: {online_idx}, name_idx: {name_idx}, vendor_idx: {vendor_idx}")

# Count statuses
status_counts = {}
for row in rows:
    if status_idx is not None:
        status = row[status_idx]
        status_counts[status] = status_counts.get(status, 0) + 1
print(f"\nStatus counts: {status_counts}")

# Show offline models
print("\n=== Offline Models ===")
offline_list = []
for row in rows:
    is_offline = False
    status = row[status_idx] if status_idx is not None else None
    online = row[online_idx] if online_idx is not None else None

    if status and '正常' not in str(status):
        is_offline = True
    if online and str(online) not in ['1', '是', 'True', 'true', '1', 'online']:
        is_offline = True

    if is_offline:
        name = row[name_idx] if name_idx is not None else 'N/A'
        vendor = row[vendor_idx] if vendor_idx is not None else 'N/A'
        offline_list.append((name, vendor, status, online))

print(f"Total offline: {len(offline_list)}")
for name, vendor, status, online in offline_list[:50]:
    print(f"  {name} | {vendor}")

if len(offline_list) > 50:
    print(f"  ... and {len(offline_list) - 50} more")

# Show online models
print("\n=== Online Models ===")
online_list = []
for row in rows:
    is_online = False
    status = row[status_idx] if status_idx is not None else None
    online = row[online_idx] if online_idx is not None else None

    if status and '正常' in str(status):
        is_online = True
    if online and str(online) in ['1', '是', 'True', 'true', '1', 'online']:
        is_online = True

    if is_online:
        name = row[name_idx] if name_idx is not None else 'N/A'
        vendor = row[vendor_idx] if vendor_idx is not None else 'N/A'
        online_list.append((name, vendor))

print(f"Total online: {len(online_list)}")
for name, vendor in online_list[:30]:
    print(f"  {name} | {vendor}")

if len(online_list) > 30:
    print(f"  ... and {len(online_list) - 30} more")

conn.close()
