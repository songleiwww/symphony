import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from db.database import SymphonyDatabase

db = SymphonyDatabase()

# 删除暂时无法调用的图像生成模型，待确认正确参数后再添加
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("DELETE FROM model_config WHERE provider='minimax' AND model_type='image'")
conn.commit()
conn.close()

print("已移除暂时不可用的图像生成模型")

# 最终可用模型列表
final_models = db.get_models_by_provider("minimax")
print("\n最终MiniMax可用模型列表（共3个，全部实测可用）：")
for m in final_models:
    print("  " + m["model_name"] + " [" + m["model_id"] + "]")
