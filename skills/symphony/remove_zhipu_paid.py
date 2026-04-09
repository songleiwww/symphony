import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from db.database import SymphonyDatabase

db = SymphonyDatabase()

# 删除智普所有收费模型
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("DELETE FROM model_config WHERE provider='zhipu' AND is_free=0")
deleted_count = cursor.rowcount
conn.commit()
conn.close()

print(f"已删除智普收费模型 {deleted_count} 个")

# 验证剩余模型
remaining_models = db.get_models_by_provider("zhipu")
print(f"剩余智普免费模型：{len(remaining_models)} 个")
print("模型列表：")
for m in remaining_models:
    print(f"  {m['model_name']} | {m['model_id']} | 免费")
