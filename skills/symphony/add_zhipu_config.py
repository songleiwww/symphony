import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from db.database import SymphonyDatabase

db = SymphonyDatabase()

# 1. 添加智普服务商到密钥管理器（provider_registry表）
provider_id = db.add_provider(
    provider_code="zhipu",
    provider_name="智普AI",
    base_url="https://open.bigmodel.cn/api/paas/v4/",
    api_key="7165f8ffad664d06bac6f9be04b48e26.ovDm4h1vaajj8N3w",
    is_enabled=True
)
print(f"智普AI服务商添加成功，ID：{provider_id}")

# 2. 添加智普常用模型
models = [
    ("glm-4", "GLM-4", "chat", 128000, 4096, 0.01, False),
    ("glm-4-flash", "GLM-4 Flash", "chat", 128000, 4096, 0.0, True),
    ("glm-3-turbo", "GLM-3 Turbo", "chat", 128000, 4096, 0.001, False),
    ("glm-4v", "GLM-4V 多模态", "multimodal", 8000, 2048, 0.02, False)
]

for model_id, model_name, model_type, context_window, max_tokens, pricing, is_free in models:
    db.add_model(
        provider="zhipu",
        model_id=model_id,
        model_name=model_name,
        model_type=model_type,
        context_window=context_window,
        max_tokens=max_tokens,
        pricing=pricing,
        is_free=is_free,
        is_enabled=True
    )
    print(f"添加模型成功：{model_name} ({model_id})")

# 3. 查询验证
all_models = db.get_all_models()
print(f"\n配置完成，当前系统共有 {len(all_models)} 个可用模型：")
for m in all_models:
    status = "免费" if m["is_free"] else "付费"
    print(f"  {m['provider']} | {m['model_name']} | {status}")

print("\n密钥管理器说明：所有服务商API密钥统一存储在provider_registry表，系统调度时自动读取，无需单独配置")
