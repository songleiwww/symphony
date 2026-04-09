#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

DB_PATH = r"C:\Users\Administrator\.openclaw\skills\symphony\data\symphony_working.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Delete the model id=32
cursor.execute("DELETE FROM model_config WHERE id = 32")
conn.commit()

print("Deleted model id=32 (ep-20260329114326-l2f2s) from symphony database")

cursor.execute("SELECT COUNT(*) FROM model_config WHERE provider_name = 'volcano'")
cnt = cursor.fetchone()[0]
print(f"Total volcano models in symphony now: {cnt}")

conn.close()
