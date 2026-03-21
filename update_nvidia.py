# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 英伟达可用模型列表（从官网获取）
nvidia_models = [
    ("meta/llama-3.2-1b-instruct", "Llama 3.2 1B"),
    ("meta/llama-3.2-3b-instruct", "Llama 3.2 3B"),
    ("meta/llama-3.3-70b-instruct", "Llama 3.3 70B"),
    ("deepseek-ai/deepseek-v3.2", "DeepSeek V3.2"),
    ("deepseek-ai/deepseek-r1-distill-qwen-32b", "DeepSeek R1 Distill Qwen 32B"),
    ("google/gemma-2-9b-it", "Gemma 2 9B"),
    ("microsoft/phi-4-mini-instruct", "Phi-4 Mini"),
    ("mistralai/mistral-large", "Mistral Large"),
    ("moonshotai/kimi-k2-instruct", "Kimi K2"),
]

# 获取英伟达API Key
c.execute("SELECT API密钥, API地址 FROM 模型配置表 WHERE 服务商='英伟达' LIMIT 1")
row = c.fetchone()
api_key = row[0] if row else None
api_url = row[1] if row else "https://integrate.api.nvidia.com/v1"

print(f"API Key: {api_key[:30]}...")
print(f"API URL: {api_url}")

# 删除旧的英伟达模型
c.execute("DELETE FROM 模型配置表 WHERE 服务商='英伟达'")
print(f"删除了旧模型")

# 添加新模型
for model_id, model_name in nvidia_models:
    c.execute("""INSERT INTO 模型配置表 
        (模型名称, 模型标识符, 服务商, API地址, API密钥, 在线状态, 模型类型)
        VALUES (?, ?, '英伟达', ?, ?, 'online', '通义对话')""",
        (model_name, model_id, api_url, api_key))
    print(f"添加: {model_name}")

conn.commit()
print(f"\n共添加 {len(nvidia_models)} 个英伟达模型")

# 验证
c.execute("SELECT COUNT(*) FROM 模型配置表 WHERE 服务商='英伟达'")
print(f"英伟达模型总数: {c.fetchone()[0]}")

conn.close()
