#!/usr/bin/env python3
# 序境系统配置导出脚本：唯一数据源来自symphony.db，无其他配置来源
import sqlite3
import json
import os

# 唯一数据源，固定路径不可修改
DB_PATH = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"
EXPORT_PATH = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\all_config_export.json"

# 连接数据库
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 读取服务商配置
cursor.execute("SELECT * FROM provider_registry WHERE is_enabled = 1")
providers = []
for row in cursor.fetchall():
    providers.append({
        "provider_code": row[1],
        "provider_name": row[2],
        "base_url": row[3],
        "api_key": row[4],
        "is_enabled": row[5]
    })

# 读取模型配置
cursor.execute("SELECT * FROM model_config WHERE is_enabled = 1")
models = []
for row in cursor.fetchall():
    models.append({
        "id": row[0],
        "provider": row[1],
        "model_id": row[2],
        "model_name": row[3],
        "model_type": row[4],
        "context_window": row[5],
        "max_tokens": row[6],
        "pricing": row[7],
        "is_free": row[8],
        "is_enabled": row[9],
        # 强制唯一标识：provider + base_url + model_id
        "unique_id": f"{row[1]}+{[p['base_url'] for p in providers if p['provider_code'] == row[1]][0]}+{row[2]}"
    })

# 导出配置
config = {
    "info": {
        "total_providers": len(providers),
        "total_models": len(models),
        "free_models": len([m for m in models if m["is_free"] == 1]),
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "unique_data_source": DB_PATH
    },
    "providers": providers,
    "models": models
}

with open(EXPORT_PATH, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

conn.close()

print("全量配置导出完成，唯一数据源：" + DB_PATH)
print("导出路径：" + EXPORT_PATH)
print(f"总服务商：{len(providers)}个，总模型：{len(models)}个")
