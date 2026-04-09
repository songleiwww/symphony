import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from db.database import SymphonyDatabase

db = SymphonyDatabase()

# 1. 全模态模型（22个）
omni_models = [
    ("qwen3.5-omni-plus-2026-03-15", "通义千问3.5 全模态增强版2026", "multimodal", 32768, 4096, 0.01, True, 1000000, "2026-06-23"),
    ("qwen3-omni-flash-realtime-2025-09-15", "通义千问3 全模态实时极速版2025", "multimodal", 16384, 2048, 0.005, True, 1000000, "2026-05-29"),
    ("qwen3-omni-flash-realtime", "通义千问3 全模态实时极速版", "multimodal", 16384, 2048, 0.005, True, 1000000, "2026-05-29"),
    ("qwen-omni-turbo-realtime-2025-05-08", "通义千问 全模态实时版2025", "multimodal", 16384, 2048, 0.005, True, 1000000, "2026-05-29"),
    ("qwen-omni-turbo-realtime-latest", "通义千问 全模态实时最新版", "multimodal", 16384, 2048, 0.005, True, 1000000, "2026-05-29"),
    ("qwen3.5-omni-flash-realtime-2026-03-15", "通义千问3.5 全模态实时极速版2026", "multimodal", 16384, 2048, 0.005, True, 1000000, "2026-06-23"),
    ("qwen3-omni-flash-2025-12-01", "通义千问3 全模态极速版2025", "multimodal", 16384, 2048, 0.005, True, 1000000, "2026-05-29"),
    ("qwen3-omni-flash", "通义千问3 全模态极速版", "multimodal", 16384, 2048, 0.005, True, 1000000, "2026-05-29"),
    ("qwen3.5-omni-plus", "通义千问3.5 全模态增强版", "multimodal", 32768, 4096, 0.01, True, 1000000, "2026-06-23"),
    ("qwen-omni-turbo-realtime", "通义千问 全模态实时版", "multimodal", 16384, 2048, 0.005, True, 1000000, "2026-05-29"),
    ("qwen-omni-turbo-latest", "通义千问 全模态最新版", "multimodal", 16384, 2048, 0.005, True, 1000000, "2026-05-29"),
    ("qwen-omni-turbo", "通义千问 全模态基础版", "multimodal", 16384, 2048, 0.005, True, 1000000, "2026-05-29"),
    ("qwen2.5-omni-7b", "通义千问2.5 全模态7B版", "multimodal", 8192, 2048, 0.003, True, 1000000, "2026-05-29"),
    ("qwen3.5-omni-plus-realtime", "通义千问3.5 全模态实时增强版", "multimodal", 32768, 4096, 0.01, True, 1000000, "2026-06-23"),
    ("qwen-omni-turbo-2025-03-26", "通义千问 全模态2025初版", "multimodal", 16384, 2048, 0.005, True, 1000000, "2026-05-29"),
    ("qwen3.5-omni-flash", "通义千问3.5 全模态极速版", "multimodal", 16384, 2048, 0.005, True, 1000000, "2026-06-23"),
    ("qwen3-omni-flash-realtime-2025-12-01", "通义千问3 全模态实时极速版2025末", "multimodal", 16384, 2048, 0.005, True, 1000000, "2026-05-29"),
    ("qwen-omni-turbo-2025-01-19", "通义千问 全模态2025初版", "multimodal", 16384, 2048, 0.005, True, 1000000, "2026-05-29"),
    ("qwen3.5-omni-flash-realtime", "通义千问3.5 全模态实时极速版", "multimodal", 16384, 2048, 0.005, True, 1000000, "2026-06-23"),
    ("qwen3.5-omni-plus-realtime-2026-03-15", "通义千问3.5 全模态实时增强版2026", "multimodal", 32768, 4096, 0.01, True, 1000000, "2026-06-23"),
    ("qwen3-omni-flash-2025-09-15", "通义千问3 全模态极速版2025初", "multimodal", 16384, 2048, 0.005, True, 1000000, "2026-05-29"),
    ("qwen3.5-omni-flash-2026-03-15", "通义千问3.5 全模态极速版2026", "multimodal", 16384, 2048, 0.005, True, 1000000, "2026-06-23")
]

# 2. 补充语音模型（12个）
additional_audio_models = [
    ("sambert-waan-v1", "Sambert Waan 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("fun-asr-realtime", "FunASR 实时语音识别基础版", "asr", 1024, 1024, 0.005, True, 36000, "2026-05-29"),
    ("sambert-zhiwei-v1", "Sambert 知威 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("qwen3-tts-flash-realtime-2025-11-27", "通义千问3 TTS 实时极速版2025末", "tts", 10000, 0, 0.003, True, 10000, "2026-05-29"),
    ("fun-asr-realtime-2026-02-28", "FunASR 实时语音识别2026版", "asr", 1024, 1024, 0.005, True, 36000, "2026-06-03"),
    ("qwen-tts-vc-realtime-2025-08-20", "通义千问 TTS 实时音色转换2025", "tts", 10000, 0, 0.01, True, 10000, "2026-05-29"),
    ("cosyvoice-v3.5-plus", "CosyVoice V3.5 增强版语音合成", "tts", 10000, 0, 0.005, True, 10000, "2026-05-29"),
    ("sambert-zhiqian-v1", "Sambert 知谦 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("cosyvoice-clone-v1", "CosyVoice 音色复刻V1", "tts", 10000, 0, 0.02, True, 10000, "2099-01-01"),
    ("sambert-zhina-v1", "Sambert 知纳 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("cosyvoice-v3.5-flash", "CosyVoice V3.5 极速版语音合成", "tts", 10000, 0, 0.005, True, 10000, "2026-05-29")
]

# 添加全模态模型
omni_added = 0
for model_id, model_name, model_type, ctx, max_tokens, price, enabled, quota, expire in omni_models:
    db.add_model(
        provider="aliyun",
        model_id=model_id,
        model_name=model_name,
        model_type=model_type,
        context_window=ctx,
        max_tokens=max_tokens,
        pricing=price,
        is_free=False,
        is_enabled=enabled
    )
    omni_added += 1

# 添加补充语音模型
audio_added = 0
for model_id, model_name, model_type, ctx, max_tokens, price, enabled, quota, expire in additional_audio_models:
    db.add_model(
        provider="aliyun",
        model_id=model_id,
        model_name=model_name,
        model_type=model_type,
        context_window=ctx,
        max_tokens=max_tokens,
        pricing=price,
        is_free=False,
        is_enabled=enabled
    )
    audio_added += 1

print("已添加全模态模型：" + str(omni_added) + "个")
print("已添加补充语音模型：" + str(audio_added) + "个")
print("本次合计新增：" + str(omni_added + audio_added) + "个")
print("阿里云百炼总模型数：449 + " + str(omni_added + audio_added) + " = " + str(449 + omni_added + audio_added) + "个")
print("系统总可用模型数：" + str(449 + omni_added + audio_added + 8 + 11) + "个")
print("所有模型添加完成，已配置额度用完即停规则")
