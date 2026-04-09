# -*- coding: utf-8 -*-
"""注册 Whisper ASR 到 symphony.db tool_registry"""
import sqlite3
import json

DB_PATH = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 检查是否已注册
cur.execute("SELECT id FROM tool_registry WHERE tool_name='whisper_asr'")
existing = cur.fetchone()

asr_config = json.dumps({
    "provider": "whisper_cli",
    "model": "tiny",
    "language": "auto",
    "model_path": None,  # 自动下载到 ~/.cache/whisper
    "available_models": ["tiny", "base", "small", "medium", "large"],
    "description": "Whisper CLI本地语音识别 - 无需API Key"
}, ensure_ascii=False)

if existing:
    cur.execute("UPDATE tool_registry SET config=?, is_enabled=1, updated_at=datetime('now') WHERE tool_name='whisper_asr'", (asr_config,))
    print("Updated existing whisper_asr entry")
else:
    cur.execute("INSERT INTO tool_registry (tool_name, config, is_enabled, created_at, updated_at) VALUES (?, ?, 1, datetime('now'), datetime('now'))", ('whisper_asr', asr_config))
    print("Inserted new whisper_asr entry")

conn.commit()

# 验证
cur.execute("SELECT tool_name, is_enabled, config FROM tool_registry WHERE tool_name='whisper_asr'")
row = cur.fetchone()
print(f"Registered: {row[0]}, enabled: {row[1]}")
print(f"Config: {row[2]}")

conn.close()
print("Done")
