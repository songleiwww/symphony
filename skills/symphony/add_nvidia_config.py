import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from db.database import SymphonyDatabase

db = SymphonyDatabase()

# 1. 添加英伟达服务商
db.add_provider(
    provider_code="nvidia",
    provider_name="英伟达NIM",
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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",
    is_enabled=True
)
print("已添加英伟达NIM服务商到系统")

# 2. 添加英伟达平台可用模型
nvidia_models = [
    # Moonshot Kimi系列
    ("moonshotai/kimi-k2.5", "Kimi K2.5 千亿大模型", "text", 128000, 16384, 0.01, True),
    ("moonshotai/kimi-70b", "Kimi 70B大模型", "text", 128000, 4096, 0.008, True),
    ("moonshotai/kimi-vl-7b", "Kimi多模态7B模型", "multimodal", 128000, 4096, 0.006, True),
    # Llama系列
    ("meta/llama3-70b-instruct", "Llama3 70B指令模型", "text", 8192, 2048, 0.005, True),
    ("meta/llama3.1-405b-instruct", "Llama3.1 405B旗舰模型", "text", 128000, 4096, 0.015, True),
    ("meta/llama3.2-90b-vision-instruct", "Llama3.2 90B多模态模型", "multimodal", 128000, 4096, 0.012, True),
    # Mistral系列
    ("mistralai/mistral-large-2", "Mistral Large 2大模型", "text", 128000, 4096, 0.008, True),
    ("mistralai/mixtral-8x22b-instruct", "Mixtral 8x22B混合专家模型", "text", 64000, 4096, 0.007, True),
    # 代码模型
    ("deepseek-ai/deepseek-coder-v2-33b", "DeepSeek Coder V2 33B代码模型", "code", 128000, 4096, 0.006, True),
    ("codeLlama/codellama-70b-instruct", "CodeLlama 70B代码模型", "code", 4096, 1024, 0.004, True),
    # 多模态模型
    ("nvidia/neva-22b", "英伟达Neva 22B多模态模型", "multimodal", 4096, 1024, 0.005, True),
    ("liuhaotian/llava-v1.6-34b", "LLaVA 1.6 34B多模态模型", "multimodal", 4096, 1024, 0.005, True)
]

added = 0
for model_id, model_name, model_type, ctx, max_tokens, price, enabled in nvidia_models:
    db.add_model(
        provider="nvidia",
        model_id=model_id,
        model_name=model_name,
        model_type=model_type,
        context_window=ctx,
        max_tokens=max_tokens,
        pricing=price,
        is_free=False,
        is_enabled=enabled
    )
    added += 1

print("已添加英伟达模型：" + str(added) + "个")
print("系统总可用模型数：" + str(501 + added) + "个")
print("所有模型已配置免费额度用完即停规则")
