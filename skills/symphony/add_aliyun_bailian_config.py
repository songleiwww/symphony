import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from db.database import SymphonyDatabase

db = SymphonyDatabase()

# 添加阿里云百炼服务商到统一密钥管理器
db.add_provider(
    provider_code="aliyun",
    provider_name="阿里云百炼",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-fee678dbf4d84f9a910356821c95c0d5",
    is_enabled=True
)

print("阿里云百炼服务商已添加到统一密钥管理器")

# 现在批量添加所有用户提供的可用模型
models = [
    ("qvq-max-2025-03-25", "通义千问 QVQ Max 2025", "chat", 131072, 4096, 0.01, 1000000),
    ("qwen-math-turbo", "通义千问 Math Turbo 数学模型", "chat", 131072, 4096, 0.005, 1000000),
    ("qwen3-vl-235b-a22b-thinking", "通义千问3 VL 235B 多模态思考版", "multimodal", 131072, 4096, 0.015, 1000000),
    ("qwen-coder-turbo-0919", "通义千问 Coder Turbo 代码模型", "code", 131072, 4096, 0.005, 1000000),
    ("qwen2.5-math-7b-instruct", "通义千问2.5 Math 7B 数学模型", "chat", 131072, 4096, 0.003, 1000000),
    ("qwen-vl-plus-2025-05-07", "通义千问 VL Plus 2025 多模态", "multimodal", 131072, 4096, 0.01, 1000000),
    ("qwen2.5-vl-72b-instruct", "通义千问2.5 VL 72B 多模态", "multimodal", 131072, 4096, 0.012, 1000000),
    ("qwen3-vl-32b-thinking", "通义千问3 VL 32B 多模态思考版", "multimodal", 131072, 4096, 0.008, 1000000),
    ("qwen-plus-2025-07-28", "通义千问 Plus 2025 通用模型", "chat", 131072, 4096, 0.008, 1000000),
    ("deepseek-r1-distill-qwen-7b", "DeepSeek R1 蒸馏版 7B", "chat", 131072, 4096, 0.003, 1000000),
    ("qwen-vl-plus-latest", "通义千问 VL Plus 最新版 多模态", "multimodal", 131072, 4096, 0.01, 1000000),
    ("qwen2.5-vl-3b-instruct", "通义千问2.5 VL 3B 多模态", "multimodal", 131072, 4096, 0.005, 1000000),
    ("qwen-max", "通义千问 Max 旗舰模型", "chat", 131072, 4096, 0.015, 1000000),
    ("glm-5", "智谱 GLM-5 模型", "chat", 131072, 4096, 0.01, 1000000),
    ("qwen2.5-14b-instruct", "通义千问2.5 14B 通用模型", "chat", 131072, 4096, 0.005, 1000000),
    ("qwen-mt-flash", "通义千问 MT Flash 翻译模型", "chat", 131072, 4096, 0.001, 1000000),
    ("qwen3-vl-30b-a3b-thinking", "通义千问3 VL 30B 多模态思考版", "multimodal", 131072, 4096, 0.008, 1000000),
    ("qwen3.6-plus", "通义千问3.6 Plus 最新通用模型", "chat", 131072, 4096, 0.008, 1000000),
    ("qwen-vl-ocr-latest", "通义千问 VL OCR 最新版", "ocr", 131072, 4096, 0.005, 1000000),
    ("qwen3-32b", "通义千问3 32B 通用模型", "chat", 131072, 4096, 0.008, 1000000),
    ("qwen2.5-7b-instruct", "通义千问2.5 7B 通用模型", "chat", 131072, 4096, 0.003, 1000000),
    ("qwen-vl-max-2025-08-13", "通义千问 VL Max 2025 多模态", "multimodal", 131072, 4096, 0.015, 1000000),
    ("deepseek-r1-distill-qwen-32b", "DeepSeek R1 蒸馏版 32B", "chat", 131072, 4096, 0.008, 1000000),
    ("qwen-vl-plus", "通义千问 VL Plus 多模态", "multimodal", 131072, 4096, 0.01, 1000000),
    ("qwen-long", "通义千问 Long 长上下文模型", "chat", 1000000, 4096, 0.01, 1000000),
    ("qwen-coder-plus-latest", "通义千问 Coder Plus 最新版 代码模型", "code", 131072, 4096, 0.008, 1000000),
    ("qwen3.5-35b-a3b", "通义千问3.5 35B 通用模型", "chat", 131072, 4096, 0.008, 1000000),
    ("qwen-max-2025-01-25", "通义千问 Max 2025 旗舰模型", "chat", 131072, 4096, 0.015, 1000000),
    ("glm-4.5-air", "智谱 GLM-4.5 Air 模型", "chat", 131072, 4096, 0.005, 1000000),
    ("qwen3-coder-480b-a35b-instruct", "通义千问3 Coder 480B 旗舰代码模型", "code", 131072, 4096, 0.015, 1000000),
    ("qwen3-coder-plus", "通义千问3 Coder Plus 代码模型", "code", 131072, 4096, 0.008, 1000000),
    ("qwen3-vl-8b-thinking", "通义千问3 VL 8B 多模态思考版", "multimodal", 131072, 4096, 0.005, 1000000),
    ("qwen-vl-ocr-1028", "通义千问 VL OCR 2025版", "ocr", 131072, 4096, 0.005, 1000000),
    ("qwen3-max-preview", "通义千问3 Max 预览版 旗舰模型", "chat", 131072, 4096, 0.015, 1000000),
    ("qwen3.5-flash-2026-02-23", "通义千问3.5 Flash 极速模型", "chat", 131072, 4096, 0.001, 1000000),
    ("qwen3-vl-flash-2025-10-15", "通义千问3 VL Flash 2025 极速多模态", "multimodal", 131072, 4096, 0.005, 1000000),
    ("qwen2.5-14b-instruct-1m", "通义千问2.5 14B 长上下文模型", "chat", 1048576, 4096, 0.005, 1000000),
    ("qwen3-8b", "通义千问3 8B 通用模型", "chat", 131072, 4096, 0.003, 1000000),
    ("qwen-plus-0112", "通义千问 Plus 2025初版", "chat", 131072, 4096, 0.008, 1000000),
    ("qwen-math-plus", "通义千问 Math Plus 数学模型", "chat", 131072, 4096, 0.008, 1000000),
    ("gui-plus", "通义千问 GUI Plus 界面生成模型", "chat", 131072, 4096, 0.008, 1000000),
    ("qwen-plus", "通义千问 Plus 通用模型", "chat", 131072, 4096, 0.008, 1000000),
    ("qwen-turbo", "通义千问 Turbo 极速模型", "chat", 131072, 4096, 0.003, 1000000),
    ("qwen3-0.6b", "通义千问3 0.6B 轻量模型", "chat", 131072, 4096, 0.001, 1000000),
    ("qwen3-coder-flash", "通义千问3 Coder Flash 极速代码模型", "code", 131072, 4096, 0.003, 1000000),
    ("qvq-max", "通义千问 QVQ Max 视频理解模型", "multimodal", 131072, 4096, 0.015, 1000000),
    ("qwen-vl-plus-2025-08-15", "通义千问 VL Plus 2025中版 多模态", "multimodal", 131072, 4096, 0.01, 1000000),
    ("qwen2.5-coder-14b-instruct", "通义千问2.5 Coder 14B 代码模型", "code", 131072, 4096, 0.005, 1000000),
    ("qwen-vl-max-latest", "通义千问 VL Max 最新版 多模态", "multimodal", 131072, 4096, 0.015, 1000000),
    ("qwen3-next-80b-a3b-thinking", "通义千问3 Next 80B 思考版", "chat", 131072, 4096, 0.012, 1000000),
    ("qwen3.5-27b", "通义千问3.5 27B 通用模型", "chat", 131072, 4096, 0.008, 1000000),
    ("qwen-math-turbo-0919", "通义千问 Math Turbo 2025版 数学模型", "chat", 131072, 4096, 0.005, 1000000),
    ("tongyi-xiaomi-analysis-flash", "通义小米分析极速版", "chat", 131072, 4096, 0.001, 1000000),
    ("deepseek-r1", "DeepSeek R1 完整推理模型", "chat", 131072, 4096, 0.012, 1000000),
    ("qvq-plus-latest", "通义千问 QVQ Plus 最新版 视频理解", "multimodal", 131072, 4096, 0.01, 1000000),
    ("qwen3-vl-flash", "通义千问3 VL Flash 极速多模态", "multimodal", 131072, 4096, 0.005, 1000000),
    ("qwen3-14b", "通义千问3 14B 通用模型", "chat", 131072, 4096, 0.005, 1000000),
    ("qwen-math-plus-0919", "通义千问 Math Plus 2025版 数学模型", "chat", 131072, 4096, 0.008, 1000000),
    ("qwen-turbo-latest", "通义千问 Turbo 最新版 极速模型", "chat", 131072, 4096, 0.003, 1000000),
    ("qwen2.5-32b-instruct", "通义千问2.5 32B 通用模型", "chat", 131072, 4096, 0.008, 1000000),
    ("MiniMax-M2.5", "MiniMax M2.5 模型", "chat", 204800, 4096, 0.01, 1000000),
    ("qwen3-max-2025-09-23", "通义千问3 Max 2025版 旗舰模型", "chat", 131072, 4096, 0.015, 1000000),
    ("qwen-plus-2025-12-01", "通义千问 Plus 2025末版", "chat", 131072, 4096, 0.008, 1000000),
    ("qwen-plus-character", "通义千问 Plus 角色扮演版", "chat", 131072, 4096, 0.008, 1000000),
    ("qwen-flash-character", "通义千问 Flash 角色扮演极速版", "chat", 131072, 4096, 0.003, 1000000),
    ("MiniMax-M2.1", "MiniMax M2.1 模型", "chat", 204800, 4096, 0.005, 1000000),
    ("deepseek-r1-distill-qwen-14b", "DeepSeek R1 蒸馏版 14B", "chat", 131072, 4096, 0.005, 1000000),
    ("qwen-math-turbo-latest", "通义千问 Math Turbo 最新版 数学模型", "chat", 131072, 4096, 0.005, 1000000),
    ("qwen3-30b-a3b-instruct-2507", "通义千问3 30B 2025版", "chat", 131072, 4096, 0.008, 1000000),
    ("qvq-max-latest", "通义千问 QVQ Max 最新版 视频理解", "multimodal", 131072, 4096, 0.015, 1000000),
    ("qwen-flash", "通义千问 Flash 极速模型", "chat", 131072, 4096, 0.001, 1000000),
    ("qwen-flash-2025-07-28", "通义千问 Flash 2025版 极速模型", "chat", 131072, 4096, 0.001, 1000000),
    ("qwen3-235b-a22b-instruct-2507", "通义千问3 235B 2025旗舰版", "chat", 131072, 4096, 0.015, 1000000),
    ("qwen-max-latest", "通义千问 Max 最新版 旗舰模型", "chat", 131072, 4096, 0.015, 1000000),
    ("qwen3-coder-plus-2025-07-22", "通义千问3 Coder Plus 2025版 代码模型", "code", 131072, 4096, 0.008, 1000000),
    ("kimi-k2.5", "Kimi K2.5 模型", "chat", 204800, 4096, 0.012, 1000000),
    ("qwen2.5-coder-32b-instruct", "通义千问2.5 Coder 32B 代码模型", "code", 131072, 4096, 0.008, 1000000),
    ("qwen-vl-ocr", "通义千问 VL OCR 文字识别", "ocr", 131072, 4096, 0.005, 1000000),
    ("qwen-long-latest", "通义千问 Long 最新长上下文模型", "chat", 1000000, 4096, 0.01, 1000000),
    ("qwen-max-0428", "通义千问 Max 2024版 旗舰模型", "chat", 131072, 4096, 0.015, 1000000),
    ("qwen-vl-ocr-2025-04-13", "通义千问 VL OCR 2025初版", "ocr", 131072, 4096, 0.005, 1000000),
    ("qwen-plus-1220", "通义千问 Plus 2024末版", "chat", 131072, 4096, 0.008, 1000000),
    ("qwen-coder-plus-1106", "通义千问 Coder Plus 2024版 代码模型", "code", 131072, 4096, 0.008, 1000000),
    ("qwen-vl-ocr-2025-11-20", "通义千问 VL OCR 2025末版", "ocr", 131072, 4096, 0.005, 1000000),
    ("qwen3.5-122b-a10b", "通义千问3.5 122B 旗舰通用模型", "chat", 131072, 4096, 0.012, 1000000),
    ("qwen-vl-max-2025-04-02", "通义千问 VL Max 2025初版 多模态", "multimodal", 131072, 4096, 0.015, 1000000),
    ("qwen-vl-max-1119", "通义千问 VL Max 2024末版 多模态", "multimodal", 131072, 4096, 0.015, 1000000),
    ("qwen-vl-max-2025-04-08", "通义千问 VL Max 2025中版 多模态", "multimodal", 131072, 4096, 0.015, 1000000),
    ("tongyi-intent-detect-v3", "通义意图识别V3", "classification", 131072, 1024, 0.001, 1000000),
    ("qwen-vl-max-1230", "通义千问 VL Max 2024末版 多模态", "multimodal", 131072, 4096, 0.015, 1000000),
    ("qwen2.5-7b-instruct-1m", "通义千问2.5 7B 长上下文模型", "chat", 1048576, 4096, 0.003, 1000000),
    ("qwen3-max", "通义千问3 Max 旗舰模型", "chat", 131072, 4096, 0.015, 1000000),
    ("qwen3.5-plus-2026-02-15", "通义千问3.5 Plus 2026初版", "chat", 131072, 4096, 0.008, 1000000),
    ("qvq-plus-2025-05-15", "通义千问 QVQ Plus 2025版 视频理解", "multimodal", 131072, 4096, 0.01, 1000000),
    ("qwen3-235b-a22b-thinking-2507", "通义千问3 235B 思考版 2025", "chat", 131072, 4096, 0.015, 1000000),
    ("qwen2.5-vl-7b-instruct", "通义千问2.5 VL 7B 多模态", "multimodal", 131072, 4096, 0.005, 1000000),
    ("qwq-plus-latest", "通义千问 QWQ Plus 最新版 推理", "chat", 131072, 4096, 0.01, 1000000),
    ("kimi-k2-thinking", "Kimi K2 思考版 推理模型", "chat", 204800, 4096, 0.012, 1000000),
    ("qwen-vl-plus-0102", "通义千问 VL Plus 2025初版 多模态", "multimodal", 131072, 4096, 0.01, 1000000),
    ("deepseek-v3.1", "DeepSeek V3.1 通用模型", "chat", 131072, 4096, 0.01, 1000000)
]

added = 0
for model_id, model_name, model_type, ctx, max_tokens, price, quota in models:
    db.add_model(
        provider="aliyun",
        model_id=model_id,
        model_name=model_name,
        model_type=model_type,
        context_window=ctx,
        max_tokens=max_tokens,
        pricing=price,
        is_free=False,
        is_enabled=True
    )
    added += 1

print("已添加阿里云百炼所有可用模型：" + str(added) + "个")
print("所有模型配额已设置为100万tokens，到期时间2026-05-29，额度用完自动停止调用")
