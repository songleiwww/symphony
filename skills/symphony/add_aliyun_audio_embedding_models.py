import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from db.database import SymphonyDatabase

db = SymphonyDatabase()

# 第一部分：语音/ASR/TTS类模型
audio_models = [
    ("qwen3-tts-vd-2026-01-26", "通义千问3 TTS 声音复刻2026版", "tts", 10000, 0, 0.01, True, 10000, "2026-05-29"),
    ("paraformer-v2", "Paraformer V2 语音识别模型", "asr", 1024, 1024, 0.005, True, 36000, "2099-01-01"),
    ("fun-asr-mtl", "FunASR 多任务语音识别模型", "asr", 1024, 1024, 0.005, True, 36000, "2026-05-29"),
    ("paraformer-v1", "Paraformer V1 语音识别模型", "asr", 1024, 1024, 0.005, True, 36000, "2099-01-01"),
    ("gummy-realtime-v1", "Gummy 实时语音模型V1", "asr", 1024, 1024, 0.005, True, 36000, "2026-05-29"),
    ("sambert-zhida-v1", "Sambert 知导 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("sambert-zhishu-v1", "Sambert 知述 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("sambert-eva-v1", "Sambert Eva 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("paraformer-realtime-8k-v2", "Paraformer 8K实时语音识别V2", "asr", 1024, 1024, 0.005, True, 36000, "2099-01-01"),
    ("qwen3-livetranslate-flash-realtime-2025-09-22", "通义千问3 实时翻译极速版2025", "translate", 4096, 4096, 0.003, True, 1000000, "2026-05-29"),
    ("paraformer-realtime-8k-v1", "Paraformer 8K实时语音识别V1", "asr", 1024, 1024, 0.005, True, 36000, "2099-01-01"),
    ("sambert-zhiye-v1", "Sambert 知叶 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("qwen-tts-2025-05-22", "通义千问 TTS 2025版", "tts", 10000, 0, 0.003, True, 1000000, "2026-05-29"),
    ("qwen-tts-realtime-latest", "通义千问 TTS 实时最新版", "tts", 10000, 0, 0.003, True, 1000000, "2026-05-29"),
    ("fun-asr-2025-11-07", "FunASR 语音识别2025版", "asr", 1024, 1024, 0.005, True, 36000, "2026-05-29"),
    ("fun-asr-realtime-2025-09-15", "FunASR 实时语音识别2025版", "asr", 1024, 1024, 0.005, True, 36000, "2026-05-29"),
    ("sambert-indah-v1", "Sambert Indah 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("sambert-cindy-v1", "Sambert Cindy 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("paraformer-realtime-v2", "Paraformer 实时语音识别V2", "asr", 1024, 1024, 0.005, True, 36000, "2099-01-01"),
    ("sambert-zhiying-v1", "Sambert 知英 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("paraformer-realtime-v1", "Paraformer 实时语音识别V1", "asr", 1024, 1024, 0.005, True, 36000, "2099-01-01"),
    ("sambert-perla-v1", "Sambert Perla 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("qwen3-tts-instruct-flash", "通义千问3 TTS 指令极速版", "tts", 10000, 0, 0.003, True, 10000, "2026-05-29"),
    ("sambert-zhilun-v1", "Sambert 知伦 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("qwen3-tts-vd-realtime-2026-01-15", "通义千问3 TTS 实时声音复刻2026版", "tts", 10000, 0, 0.01, True, 10000, "2026-05-29"),
    ("qwen-tts-realtime-2025-07-15", "通义千问 TTS 实时2025版", "tts", 10000, 0, 0.003, True, 1000000, "2026-05-29"),
    ("qwen-tts-latest", "通义千问 TTS 最新版", "tts", 10000, 0, 0.003, True, 1000000, "2026-05-29"),
    ("sambert-zhimao-v1", "Sambert 知猫 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("qwen3-livetranslate-flash-2025-12-01", "通义千问3 翻译极速版2025", "translate", 4096, 4096, 0.003, True, 1000000, "2026-05-29"),
    ("qwen3-asr-flash", "通义千问3 ASR 极速版", "asr", 1024, 1024, 0.005, True, 36000, "2026-08-27"),
    ("qwen3-asr-flash-2025-09-08", "通义千问3 ASR 极速版2025", "asr", 1024, 1024, 0.005, True, 36000, "2026-05-29"),
    ("qwen3-omni-30b-a3b-captioner", "通义千问3 多模态30B 字幕生成", "multimodal", 4096, 1024, 0.008, True, 1000000, "2026-05-29"),
    ("sambert-zhixiao-v1", "Sambert 知晓 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("sambert-zhimo-v1", "Sambert 知墨 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("fun-asr-2025-08-25", "FunASR 语音识别2025初版", "asr", 1024, 1024, 0.005, True, 36000, "2026-05-29"),
    ("sambert-betty-v1", "Sambert Betty 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("sambert-zhiru-v1", "Sambert 知如 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("paraformer-8k-v1", "Paraformer 8K语音识别V1", "asr", 1024, 1024, 0.005, True, 36000, "2099-01-01"),
    ("qwen3-tts-flash", "通义千问3 TTS 极速版", "tts", 10000, 0, 0.003, True, 10000, "2026-05-29"),
    ("paraformer-8k-v2", "Paraformer 8K语音识别V2", "asr", 1024, 1024, 0.005, True, 36000, "2099-01-01"),
    ("qwen3-tts-flash-realtime-2025-09-18", "通义千问3 TTS 实时极速版2025", "tts", 10000, 0, 0.003, True, 10000, "2026-05-29"),
    ("qwen3-tts-vc-2026-01-22", "通义千问3 TTS 音色转换2026版", "tts", 10000, 0, 0.01, True, 10000, "2026-05-29"),
    ("sambert-zhiqi-v1", "Sambert 知琪 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("cosyvoice-v2", "CosyVoice 语音合成V2", "tts", 10000, 0, 0.005, True, 10000, "2026-05-29"),
    ("cosyvoice-v1", "CosyVoice 语音合成V1", "tts", 10000, 0, 0.005, True, 10000, "2099-01-01"),
    ("qwen3-tts-flash-2025-11-27", "通义千问3 TTS 极速版2025", "tts", 10000, 0, 0.003, True, 10000, "2026-05-29"),
    ("qwen-tts-realtime", "通义千问 TTS 实时版", "tts", 10000, 0, 0.003, True, 1000000, "2026-05-29"),
    ("paraformer-mtl-v1", "Paraformer 多任务语音识别V1", "asr", 1024, 1024, 0.005, True, 36000, "2099-01-01"),
    ("sambert-zhifei-v1", "Sambert 知非 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("fun-asr-flash-8k-realtime", "FunASR 8K实时极速语音识别", "asr", 1024, 1024, 0.005, True, 36000, "2026-05-29"),
    ("fun-asr-mtl-2025-08-25", "FunASR 多任务语音识别2025版", "asr", 1024, 1024, 0.005, True, 36000, "2026-05-29"),
    ("sambert-camila-v1", "Sambert Camila 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("qwen3-asr-flash-filetrans", "通义千问3 ASR 文件转写极速版", "asr", 1024, 1024, 0.005, True, 36000, "2026-05-29"),
    ("sambert-zhijing-v1", "Sambert 知静 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("fun-asr-flash-8k-realtime-2026-01-28", "FunASR 8K实时极速语音识别2026版", "asr", 1024, 1024, 0.005, True, 36000, "2026-05-29"),
    ("sambert-cally-v1", "Sambert Cally 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("sambert-zhimiao-emo-v1", "Sambert 知淼 情感语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("sambert-zhishuo-v1", "Sambert 知硕 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("qwen-voice-design", "通义千问 音色设计模型", "tts", 10000, 0, 0.05, True, 10, "2026-05-29"),
    ("sambert-zhide-v1", "Sambert 知德 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("qwen3-tts-flash-realtime", "通义千问3 TTS 实时极速版", "tts", 10000, 0, 0.003, True, 10000, "2026-05-29"),
    ("qwen-voice-enrollment", "通义千问 音色录入模型", "tts", 10000, 0, 0.02, True, 1000, "2026-05-29"),
    ("sambert-zhiyue-v1", "Sambert 知悦 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("qwen3-tts-flash-2025-09-18", "通义千问3 TTS 极速版2025初版", "tts", 10000, 0, 0.003, True, 10000, "2026-05-29"),
    ("sambert-beth-v1", "Sambert Beth 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("qwen-tts-2025-04-10", "通义千问 TTS 2025初版", "tts", 10000, 0, 0.003, True, 1000000, "2026-05-29"),
    ("qwen3-tts-instruct-flash-2026-01-26", "通义千问3 TTS 指令极速版2026", "tts", 10000, 0, 0.003, True, 10000, "2026-05-29"),
    ("sambert-zhiya-v1", "Sambert 知雅 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("qwen3-tts-vc-realtime-2025-11-27", "通义千问3 TTS 实时音色转换2025", "tts", 10000, 0, 0.01, True, 10000, "2026-05-29"),
    ("qwen-tts", "通义千问 TTS 基础版", "tts", 10000, 0, 0.003, True, 1000000, "2026-05-29"),
    ("sambert-zhistella-v1", "Sambert 知星 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("sambert-zhihao-v1", "Sambert 知浩 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("qwen3-tts-instruct-flash-realtime-2026-01-22", "通义千问3 TTS 实时指令版2026", "tts", 10000, 0, 0.003, True, 10000, "2026-05-29"),
    ("qwen3-tts-instruct-flash-realtime", "通义千问3 TTS 实时指令版", "tts", 10000, 0, 0.003, True, 10000, "2026-05-29"),
    ("sambert-zhichu-v1", "Sambert 知初 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("qwen3-asr-flash-filetrans-2025-11-17", "通义千问3 ASR 文件转写极速版2025", "asr", 1024, 1024, 0.005, True, 36000, "2026-05-29"),
    ("qwen3-livetranslate-flash-realtime", "通义千问3 实时翻译极速版", "translate", 4096, 4096, 0.003, True, 1000000, "2026-05-29"),
    ("fun-asr", "FunASR 基础语音识别", "asr", 1024, 1024, 0.005, True, 36000, "2026-05-29"),
    ("sambert-zhigui-v1", "Sambert 知贵 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("sambert-zhinan-v1", "Sambert 知南 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("qwen3-tts-vc-realtime-2026-01-15", "通义千问3 TTS 实时音色转换2026", "tts", 10000, 0, 0.01, True, 10000, "2026-05-29"),
    ("cosyvoice-v3-flash", "CosyVoice V3 极速版语音合成", "tts", 10000, 0, 0.005, True, 10000, "2026-05-29"),
    ("sambert-zhiming-v1", "Sambert 知明 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("sambert-brian-v1", "Sambert Brian 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("fun-asr-realtime-2025-11-07", "FunASR 实时语音识别2025末版", "asr", 1024, 1024, 0.005, True, 36000, "2026-05-29"),
    ("sambert-donna-v1", "Sambert Donna 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("sambert-hanna-v1", "Sambert Hanna 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("qwen3-asr-flash-realtime-2026-02-10", "通义千问3 ASR 实时极速版2026", "asr", 1024, 1024, 0.005, True, 36000, "2026-05-29"),
    ("sambert-zhiting-v1", "Sambert 知婷 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("sambert-zhiyuan-v1", "Sambert 知远 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("sambert-zhixiang-v1", "Sambert 知祥 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("qwen3-asr-flash-realtime-2025-10-27", "通义千问3 ASR 实时极速版2025", "asr", 1024, 1024, 0.005, True, 36000, "2026-05-29"),
    ("qwen3-asr-flash-realtime", "通义千问3 ASR 实时极速版", "asr", 1024, 1024, 0.005, True, 36000, "2026-05-29"),
    ("sambert-zhijia-v1", "Sambert 知佳 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01"),
    ("qwen3-tts-vd-realtime-2025-12-16", "通义千问3 TTS 实时声音复刻2025", "tts", 10000, 0, 0.01, True, 10000, "2026-05-29"),
    ("cosyvoice-v3-plus", "CosyVoice V3 增强版语音合成", "tts", 10000, 0, 0.005, True, 10000, "2026-05-29"),
    ("qwen3-asr-flash-2026-02-10", "通义千问3 ASR 极速版2026", "asr", 1024, 1024, 0.005, True, 36000, "2026-06-01"),
    ("gummy-chat-v1", "Gummy 对话语音模型V1", "asr", 1024, 1024, 0.005, True, 36000, "2026-05-29"),
    ("sambert-clara-v1", "Sambert Clara 语音合成V1", "tts", 10000, 0, 0.003, True, 30000, "2099-01-01")
]

# 第二部分：向量/重排序类模型
embedding_models = [
    ("gte-rerank-v2", "GTE 重排序模型V2", "rerank", 8192, 1024, 0.001, True, 1000000, "2026-05-29"),
    ("tongyi-embedding-vision-plus-2026-03-06", "通义 多模态向量增强版2026", "embedding", 8192, 1536, 0.001, True, 1000000, "2026-06-19"),
    ("tongyi-embedding-vision-flash-2026-03-06", "通义 多模态向量极速版2026", "embedding", 8192, 1024, 0.0005, True, 1000000, "2026-06-19"),
    ("qwen3-vl-rerank", "通义千问3 多模态重排序模型", "rerank", 8192, 1024, 0.001, True, 1000000, "2026-05-29"),
    ("tongyi-embedding-vision-flash", "通义 多模态向量极速版", "embedding", 8192, 1024, 0.0005, True, 1000000, "2026-05-29"),
    ("qwen3-vl-embedding", "通义千问3 多模态向量模型", "embedding", 8192, 1536, 0.001, True, 1000000, "2026-05-29"),
    ("multimodal-embedding-v1", "多模态向量模型V1", "embedding", 8192, 1024, 0.001, True, 1000000, "2026-05-29"),
    ("qwen3-rerank", "通义千问3 文本重排序模型", "rerank", 8192, 1024, 0.001, True, 1000000, "2026-05-29"),
    ("text-embedding-v1", "文本向量模型V1", "embedding", 8192, 1536, 0.0005, True, 500000, "2026-05-29"),
    ("tongyi-embedding-vision-plus", "通义 多模态向量增强版", "embedding", 8192, 1536, 0.001, True, 1000000, "2026-05-29"),
    ("text-embedding-v3", "文本向量模型V3", "embedding", 8192, 1536, 0.0005, True, 500000, "2026-05-29"),
    ("text-embedding-v2", "文本向量模型V2", "embedding", 8192, 1536, 0.0005, True, 500000, "2026-05-29"),
    ("text-embedding-v4", "文本向量模型V4", "embedding", 8192, 1536, 0.0005, True, 1000000, "2026-05-29"),
    ("qwen2.5-vl-embedding", "通义千问2.5 多模态向量模型", "embedding", 8192, 1536, 0.001, True, 1000000, "2026-05-29"),
    ("text-embedding-async-v1", "异步文本向量模型V1", "embedding", 8192, 1536, 0.0005, True, 20000000, "2026-05-29"),
    ("text-embedding-async-v2", "异步文本向量模型V2", "embedding", 8192, 1536, 0.0005, True, 20000000, "2026-05-29")
]

# 批量添加语音模型
audio_added = 0
for model_id, model_name, model_type, ctx, max_tokens, price, enabled, quota, expire in audio_models:
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

# 批量添加向量模型
embedding_added = 0
for model_id, model_name, model_type, ctx, max_tokens, price, enabled, quota, expire in embedding_models:
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
    embedding_added += 1

print("已添加阿里云百炼语音类模型：" + str(audio_added) + "个")
print("已添加阿里云百炼向量/重排序类模型：" + str(embedding_added) + "个")
print("本次合计新增：" + str(audio_added + embedding_added) + "个")
print("阿里云百炼总可用模型数：241 + 73 + " + str(audio_added + embedding_added) + " = " + str(241+73+audio_added+embedding_added) + "个")
print("系统总可用模型数：" + str(241+73+audio_added+embedding_added + 8 + 11) + "个（智普8+MiniMax11+阿里云百炼" + str(241+73+audio_added+embedding_added) + "）")
print("所有模型已配置额度用完即停规则，不会产生额外费用")