import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from db.database import SymphonyDatabase

db = SymphonyDatabase()

# 智普官方全部免费模型列表（2026公开可用）
free_models = [
    # 对话类免费模型
    ("glm-4-flash", "GLM-4 Flash 免费版", "chat", 128000, 4096, 0.0, True),
    ("glm-4-flash-search", "GLM-4 Flash 搜索版", "chat", 128000, 4096, 0.0, True),
    ("glm-3-turbo-free", "GLM-3 Turbo 免费版", "chat", 128000, 4096, 0.0, True),
    ("glm-4-long-free", "GLM-4 长文本免费体验版", "chat", 1024000, 4096, 0.0, True),
    
    # 代码类免费模型
    ("codegeex-2", "CodeGeeX2 代码模型", "code", 32000, 8192, 0.0, True),
    
    # 多模态免费模型
    ("glm-4v-flash", "GLM-4V Flash 多模态免费版", "multimodal", 8000, 2048, 0.0, True),
    
    # 角色对话免费模型
    ("charglm-3", "CharGLM-3 角色对话模型", "chat", 32000, 2048, 0.0, True),
    
    # 嵌入类免费模型
    ("embedding-2", "Embedding V2 嵌入模型", "embedding", 512, 1024, 0.0, True)
]

added = 0
for model_id, model_name, model_type, context_window, max_tokens, pricing, is_free in free_models:
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
    added +=1
    print(f"添加免费模型成功：{model_name}")

# 查询统计
all_models = db.get_models_by_provider("zhipu")
free_count = sum(1 for m in all_models if m['is_free'])
print(f"\n配置完成！")
print(f"智普总模型数：{len(all_models)}")
print(f"智普免费模型数：{free_count}")
print("所有免费模型全部已启用，可直接调度使用")
