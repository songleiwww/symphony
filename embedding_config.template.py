# =============================================================================
# Symphony 向量嵌入模型配置模板
# =============================================================================

# 向量嵌入模型配置
# 使用前请将 YOUR_NVIDIA_API_KEY 替换为你的真实API Key
EMBEDDING_MODELS = [
    {
        "name": "nvidia_bge_m3",
        "provider": "nvidia",
        "model_id": "baai/bge-m3",
        "alias": "NVIDIA BGE-M3 (中文向量)",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "YOUR_NVIDIA_API_KEY",  # 替换为你的NVIDIA API Key
        "embedding_dim": 1024,
        "enabled": True,
        "type": "embedding"
    },
    {
        "name": "nvidia_nv_embed_v1",
        "provider": "nvidia",
        "model_id": "nvidia/nv-embed-v1",
        "alias": "NVIDIA NV-Embed-V1",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": "YOUR_NVIDIA_API_KEY",  # 替换为你的NVIDIA API Key
        "embedding_dim": 4096,
        "enabled": True,
        "type": "embedding"
    },
]

# 向量存储配置
VECTOR_STORE_CONFIG = {
    "enabled": True,
    "default_model": "nvidia_bge_m3",
    "storage_path": "./vector_store/",
    "index_name": "symphony_index"
}

# 使用说明：
# 1. 复制此文件内容到 config.py
# 2. 将 YOUR_NVIDIA_API_KEY 替换为你的真实API Key
# 3. 本地config.py不会被提交到GitHub
