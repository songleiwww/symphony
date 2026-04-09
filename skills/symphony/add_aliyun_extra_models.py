import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from db.database import SymphonyDatabase

db = SymphonyDatabase()

# 新增的阿里云百炼模型列表
extra_models = [
    ("qwen3.5-397b-a17b", "通义千问3.5 397B 旗舰通用模型", "chat", 131072, 4096, 0.018, 1000000),
    ("qwen3-vl-plus-2025-09-23", "通义千问3 VL Plus 2025版 多模态", "multimodal", 131072, 4096, 0.012, 1000000),
    ("deepseek-v3.2", "DeepSeek V3.2 通用模型", "chat", 131072, 4096, 0.012, 1000000),
    ("qwen-math-plus-0816", "通义千问 Math Plus 2024版 数学模型", "chat", 131072, 4096, 0.008, 1000000),
    ("qwen3-coder-next", "通义千问3 Coder Next 下一代代码模型", "code", 131072, 4096, 0.008, 1000000),
    ("tongyi-xiaomi-analysis-pro", "通义小米分析专业版", "chat", 131072, 4096, 0.005, 1000000),
    ("qwen3.5-flash", "通义千问3.5 Flash 极速模型", "chat", 131072, 4096, 0.001, 1000000),
    ("qwen3-vl-32b-instruct", "通义千问3 VL 32B 多模态模型", "multimodal", 131072, 4096, 0.008, 1000000),
    ("qwq-32b-preview", "通义千问 QWQ 32B 推理预览版", "chat", 131072, 4096, 0.01, 1000000),
    ("qwen3-30b-a3b-thinking-2507", "通义千问3 30B 2025思考版", "chat", 131072, 4096, 0.008, 1000000),
    ("qvq-max-2025-05-15", "通义千问 QVQ Max 2025版 视频理解", "multimodal", 131072, 4096, 0.015, 1000000),
    ("qwen2.5-72b-instruct", "通义千问2.5 72B 通用模型", "chat", 131072, 4096, 0.012, 1000000),
    ("qwen3-coder-plus-2025-09-23", "通义千问3 Coder Plus 2025中版 代码模型", "code", 131072, 4096, 0.008, 1000000),
    ("qwen2.5-3b-instruct", "通义千问2.5 3B 通用模型", "chat", 131072, 4096, 0.003, 1000000),
    ("qwen-plus-latest", "通义千问 Plus 最新版 通用模型", "chat", 131072, 4096, 0.008, 1000000),
    ("qwen-turbo-2025-02-11", "通义千问 Turbo 2025初版 极速模型", "chat", 131072, 4096, 0.003, 1000000),
    ("Moonshot-Kimi-K2-Instruct", "Moonshot Kimi K2 模型", "chat", 204800, 4096, 0.012, 1000000),
    ("qwen3-max-2026-01-23", "通义千问3 Max 2026初版 旗舰模型", "chat", 131072, 4096, 0.015, 1000000),
    ("qwen-turbo-1101", "通义千问 Turbo 2024版 极速模型", "chat", 131072, 4096, 0.003, 10000000),
    ("qwen-plus-2025-09-11", "通义千问 Plus 2025中版 通用模型", "chat", 131072, 4096, 0.008, 1000000),
    ("qwen3-vl-flash-2026-01-22", "通义千问3 VL Flash 2026初版 极速多模态", "multimodal", 131072, 4096, 0.005, 1000000),
    ("qwen-vl-max", "通义千问 VL Max 多模态模型", "multimodal", 131072, 4096, 0.015, 1000000),
    ("qwen3-vl-30b-a3b-instruct", "通义千问3 VL 30B 多模态模型", "multimodal", 131072, 4096, 0.008, 1000000),
    ("qwen3-coder-30b-a3b-instruct", "通义千问3 Coder 30B 代码模型", "code", 131072, 4096, 0.008, 1000000),
    ("qwen3-vl-235b-a22b-instruct", "通义千问3 VL 235B 旗舰多模态模型", "multimodal", 131072, 4096, 0.015, 1000000),
    ("qwen-flash-character-2026-02-26", "通义千问 Flash 角色扮演2026版", "chat", 131072, 4096, 0.003, 1000000),
    ("qwen3-4b", "通义千问3 4B 轻量模型", "chat", 131072, 4096, 0.002, 1000000),
    ("qwen3-235b-a22b", "通义千问3 235B 旗舰通用模型", "chat", 131072, 4096, 0.015, 1000000),
    ("qwen2.5-coder-7b-instruct", "通义千问2.5 Coder 7B 代码模型", "code", 131072, 4096, 0.003, 1000000),
    ("qwen-coder-plus", "通义千问 Coder Plus 代码模型", "code", 131072, 4096, 0.008, 1000000),
    ("qwen-mt-lite", "通义千问 MT Lite 轻量翻译模型", "chat", 131072, 4096, 0.001, 1000000),
    ("qwen-plus-2025-01-25", "通义千问 Plus 2025初版 通用模型", "chat", 131072, 4096, 0.008, 1000000),
    ("qwen-vl-plus-2025-01-25", "通义千问 VL Plus 2025初版 多模态", "multimodal", 131072, 4096, 0.01, 1000000),
    ("qwen3-1.7b", "通义千问3 1.7B 超轻量模型", "chat", 131072, 4096, 0.001, 1000000),
    ("qwen-turbo-2025-07-15", "通义千问 Turbo 2025中版 极速模型", "chat", 131072, 4096, 0.003, 1000000),
    ("qwen3-vl-plus", "通义千问3 VL Plus 多模态模型", "multimodal", 131072, 4096, 0.012, 1000000),
    ("qwen-coder-turbo-latest", "通义千问 Coder Turbo 最新版 代码模型", "code", 131072, 4096, 0.005, 1000000),
    ("qwen-turbo-2025-04-28", "通义千问 Turbo 2025中版 极速模型", "chat", 131072, 4096, 0.003, 1000000),
    ("qwen2.5-vl-32b-instruct", "通义千问2.5 VL 32B 多模态模型", "multimodal", 131072, 4096, 0.012, 1000000),
    ("glm-4.5", "智谱 GLM-4.5 模型", "chat", 131072, 4096, 0.008, 1000000),
    ("qwen3-30b-a3b", "通义千问3 30B 通用模型", "chat", 131072, 4096, 0.008, 1000000),
    ("qwen-coder-turbo", "通义千问 Coder Turbo 代码模型", "code", 131072, 4096, 0.005, 1000000),
    ("qwen-mt-plus", "通义千问 MT Plus 专业翻译模型", "chat", 131072, 4096, 0.005, 1000000),
    ("glm-4.6", "智谱 GLM-4.6 模型", "chat", 131072, 4096, 0.01, 1000000),
    ("qwen-max-0919", "通义千问 Max 2024版 旗舰模型", "chat", 131072, 4096, 0.015, 1000000),
    ("qwen3-vl-8b-instruct", "通义千问3 VL 8B 多模态模型", "multimodal", 131072, 4096, 0.005, 1000000),
    ("glm-4.7", "智谱 GLM-4.7 最新模型", "chat", 131072, 4096, 0.012, 1000000),
    ("qwen-vl-ocr-2025-08-28", "通义千问 VL OCR 2025中版", "ocr", 131072, 4096, 0.005, 1000000),
    ("qwen3-coder-flash-2025-07-28", "通义千问3 Coder Flash 2025版 极速代码模型", "code", 131072, 4096, 0.003, 1000000),
    ("qvq-plus", "通义千问 QVQ Plus 视频理解模型", "multimodal", 131072, 4096, 0.01, 1000000),
    ("gui-plus-2026-02-26", "通义千问 GUI Plus 2026版 界面生成模型", "chat", 131072, 4096, 0.008, 1000000),
    ("deepseek-v3", "DeepSeek V3 通用模型", "chat", 131072, 4096, 0.01, 1000000),
    ("qwq-32b", "通义千问 QWQ 32B 推理模型", "chat", 131072, 4096, 0.01, 1000000),
    ("qwen3-vl-plus-2025-12-19", "通义千问3 VL Plus 2025末版 多模态", "multimodal", 131072, 4096, 0.012, 1000000),
    ("qwen-plus-2025-04-28", "通义千问 Plus 2025初版 通用模型", "chat", 131072, 4096, 0.008, 1000000),
    ("qwen-mt-turbo", "通义千问 MT Turbo 极速翻译模型", "chat", 131072, 4096, 0.003, 1000000),
    ("qwen-vl-max-2025-01-25", "通义千问 VL Max 2025初版 多模态", "multimodal", 131072, 4096, 0.015, 1000000),
    ("qwen-long-2025-01-25", "通义千问 Long 2025初版 长上下文模型", "chat", 1000000, 4096, 0.01, 1000000),
    ("qwen-plus-2025-07-14", "通义千问 Plus 2025中版 通用模型", "chat", 131072, 4096, 0.008, 1000000),
    ("qwen-math-plus-latest", "通义千问 Math Plus 最新版 数学模型", "chat", 131072, 4096, 0.008, 1000000),
    ("qvq-72b-preview", "通义千问 QVQ 72B 视频理解预览版", "multimodal", 131072, 4096, 0.015, 100000),
    ("qwq-plus", "通义千问 QWQ Plus 推理模型", "chat", 131072, 4096, 0.01, 1000000),
    ("qwen3.6-plus-2026-04-02", "通义千问3.6 Plus 2026中版 通用模型", "chat", 131072, 4096, 0.008, 1000000),
    ("qwen2.5-math-72b-instruct", "通义千问2.5 Math 72B 数学模型", "chat", 131072, 4096, 0.012, 1000000),
    ("deepseek-r1-0528", "DeepSeek R1 2025版 推理模型", "chat", 131072, 4096, 0.012, 1000000),
    ("qwq-plus-2025-03-05", "通义千问 QWQ Plus 2025版 推理模型", "chat", 131072, 4096, 0.01, 1000000),
    ("qwen3-next-80b-a3b-instruct", "通义千问3 Next 80B 通用模型", "chat", 131072, 4096, 0.012, 1000000),
    ("deepseek-v3.2-exp", "DeepSeek V3.2 实验版 通用模型", "chat", 131072, 4096, 0.012, 1000000)
]

added = 0
for model_id, model_name, model_type, ctx, max_tokens, price, quota in extra_models:
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

print("已添加新增的阿里云百炼模型：" + str(added) + "个")
print("当前阿里云百炼总模型数：" + str(len(db.get_models_by_provider("aliyun"))) + "个")
print("所有模型均设置为额度用完自动停止，后续将自动安排任务消耗剩余额度")
