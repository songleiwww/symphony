import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from db.database import SymphonyDatabase

db = SymphonyDatabase()

# 删除Plus套餐不支持的abab系列模型
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("DELETE FROM model_config WHERE provider='minimax' AND model_id LIKE 'abab%'")
deleted_count = cursor.rowcount
conn.commit()
conn.close()

print("已删除不支持的abab系列模型：" + str(deleted_count) + "个")

# 剩余可用模型
remaining = db.get_models_by_provider("minimax")
print("当前可用MiniMax模型：" + str(len(remaining)) + "个")
for m in remaining:
    print("  " + m["model_name"] + " | " + m["model_id"])
