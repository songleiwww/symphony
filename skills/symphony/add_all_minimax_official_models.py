import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from db.database import SymphonyDatabase

db = SymphonyDatabase()

# 删除现有MiniMax模型，重新添加所有官方模型
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("DELETE FROM model_config WHERE provider='minimax'")
conn.commit()
conn.close()

# 官方文本模型列表
text_models = [
    ("MiniMax-M2.7", "MiniMax M2.7 旗舰模型", "chat", 204800, 4096, 0.015, True),
    ("MiniMax-M2.7-highspeed", "MiniMax M2.7 极速版", "chat", 204800, 4096, 0.015, True),
    ("MiniMax-M2.5", "MiniMax M2.5 高性能模型", "chat", 204800, 4096, 0.01, True),
    ("MiniMax-M2.5-highspeed", "MiniMax M2.5 极速版", "chat", 204800, 4096, 0.01, True),
    ("MiniMax-M2.1", "MiniMax M2.1 编程模型", "chat", 204800, 4096, 0.005, True),
    ("MiniMax-M2.1-highspeed", "MiniMax M2.1 极速编程版", "chat", 204800, 4096, 0.005, True),
    ("MiniMax-M2", "MiniMax M2 高效编码模型", "chat", 204800, 4096, 0.003, True)
]

# 官方语音合成模型列表
tts_models = [
    ("speech-2.8-hd", "Speech 2.8 HD 高清语音合成", "tts", 10000, 0, 0.01, True),
    ("speech-2.8-turbo", "Speech 2.8 Turbo 极速语音合成", "tts", 10000, 0, 0.008, True),
    ("speech-2.6-hd", "Speech 2.6 HD 高清语音合成", "tts", 10000, 0, 0.007, True),
    ("speech-2.6-turbo", "Speech 2.6 Turbo 极速语音合成", "tts", 10000, 0, 0.006, True),
    ("speech-02-hd", "Speech 02 HD 高清语音合成", "tts", 10000, 0, 0.005, True),
    ("speech-02-turbo", "Speech 02 Turbo 极速语音合成", "tts", 10000, 0, 0.004, True)
]

# 其他模型
other_models = [
    ("asr-01", "ASR 01 语音识别模型", "asr", 1024, 1024, 0.01, True),
    ("image-01", "Image 01 图像生成模型", "image", 4096, 1024, 0.02, True),
    ("image-01-live", "Image 01 Live 多风格图像生成", "image", 4096, 1024, 0.025, True)
]

all_models = text_models + tts_models + other_models
added = 0
for model_id, model_name, model_type, ctx, max_tokens, price, enabled in all_models:
    db.add_model(
        provider="minimax",
        model_id=model_id,
        model_name=model_name,
        model_type=model_type,
        context_window=ctx,
        max_tokens=max_tokens,
        pricing=price,
        is_free=False,
        is_enabled=enabled
    )
    added +=1

print("已添加所有官方MiniMax模型：" + str(added) + "个")
print("现在开始逐一测试可用性...")
