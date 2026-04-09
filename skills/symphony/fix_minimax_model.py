import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from db.database import SymphonyDatabase

db = SymphonyDatabase()

# 删除错误的语音识别模型
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("DELETE FROM model_config WHERE provider='minimax' AND model_id='speech-02'")
conn.commit()
conn.close()

# 添加正确的语音识别模型和最新的MiniMax M2.7模型
models = [
    ("abab6.5-chat", "MiniMax abab6.5 通用对话模型", "chat", 256000, 4096, 0.01, True),
    ("abab6.5s-chat", "MiniMax abab6.5s 高速对话模型", "chat", 128000, 4096, 0.005, True),
    ("abab5.5s-chat", "MiniMax abab5.5 高性价比对话模型", "chat", 128000, 4096, 0.001, True),
    ("minimax/MiniMax-M2.7", "MiniMax M2.7 最新旗舰模型", "chat", 128000, 4096, 0.015, True),
    ("minimax-image-01", "MiniMax 图像生成模型", "image", 4096, 1024, 0.02, True),
    ("speech-01", "MiniMax 语音合成模型", "tts", 1024, 0, 0.01, True),
    ("asr-01", "MiniMax 语音识别模型", "asr", 1024, 1024, 0.01, True)
]

added = 0
for model_id, model_name, model_type, context_window, max_tokens, pricing, is_enabled in models:
    db.add_model(
        provider="minimax",
        model_id=model_id,
        model_name=model_name,
        model_type=model_type,
        context_window=context_window,
        max_tokens=max_tokens,
        pricing=pricing,
        is_free=False,
        is_enabled=is_enabled
    )
    added +=1
    print(f"已更新模型：{model_name}")

# 查询统计
all_models = db.get_models_by_provider("minimax")
print(f"\n修正完成！当前MiniMax总模型数：{len(all_models)}")
for m in all_models:
    print(f"  {m['model_name']} | {m['model_id']}")
