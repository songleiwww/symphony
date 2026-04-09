import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from db.database import SymphonyDatabase

db = SymphonyDatabase()

# MiniMax官方常用模型列表
models = [
    # 对话类模型
    ("abab6.5-chat", "MiniMax abab6.5 通用对话模型", "chat", 256000, 4096, 0.01, True),
    ("abab6.5s-chat", "MiniMax abab6.5s 高速对话模型", "chat", 128000, 4096, 0.005, True),
    ("abab5.5-chat", "MiniMax abab5.5 高性价比对话模型", "chat", 128000, 4096, 0.001, True),
    
    # 图像生成模型
    ("minimax-image-01", "MiniMax 图像生成模型", "image", 4096, 1024, 0.02, True),
    
    # 语音类模型
    ("speech-01", "MiniMax 语音合成模型", "tts", 1024, 0, 0.01, True),
    ("speech-02", "MiniMax 语音识别模型", "asr", 1024, 1024, 0.01, True)
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
    print(f"添加模型成功：{model_name}")

# 查询统计
all_models = db.get_models_by_provider("minimax")
print(f"\n配置完成！")
print(f"MiniMax总模型数：{len(all_models)}")
print("所有模型已启用，可直接调度使用")
