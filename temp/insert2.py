# -*- coding: utf-8 -*-
import sqlite3

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
NEW_KEY = "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"

available = ['abacusai/dracarys-llama-3.1-70b-instruct', 'ai21labs/jamba-1.5-mini-instruct', 'baichuan-inc/baichuan2-13b-chat', 'bytedance/seed-oss-36b-instruct', 'deepseek-ai/deepseek-r1-distill-llama-8b', 'deepseek-ai/deepseek-v3.1', 'deepseek-ai/deepseek-v3.1-terminus', 'deepseek-ai/deepseek-v3.2', 'google/gemma-2-27b-it', 'google/gemma-2-2b-it', 'google/gemma-2-9b-it', 'google/gemma-3-1b-it', 'google/gemma-3-27b-it', 'google/gemma-3n-e2b-it', 'google/gemma-3n-e4b-it', 'google/gemma-7b', 'google/shieldgemma-9b', 'gotocompany/gemma-2-9b-cpt-sahabatai-instruct', 'ibm/granite-guardian-3.0-8b', 'igenius/italia_10b_instruct_16k', 'institute-of-science-tokyo/llama-3.1-swallow-70b-instruct-v0.1', 'institute-of-science-tokyo/llama-3.1-swallow-8b-instruct-v0.1', 'marin/marin-8b-instruct', 'mediatek/breeze-7b-instruct', 'meta/llama-3.1-405b-instruct', 'meta/llama-3.1-70b-instruct', 'meta/llama-3.1-8b-instruct', 'meta/llama-3.2-3b-instruct', 'meta/llama-3.2-90b-vision-instruct', 'meta/llama-3.3-70b-instruct', 'meta/llama-4-maverick-17b-128e-instruct', 'meta/llama-guard-4-12b', 'meta/llama3-70b-instruct', 'meta/llama3-8b-instruct', 'microsoft/phi-3-medium-128k-instruct', 'microsoft/phi-3-medium-4k-instruct', 'microsoft/phi-3-mini-4k-instruct', 'microsoft/phi-3-small-128k-instruct', 'microsoft/phi-3-small-8k-instruct', 'microsoft/phi-3.5-mini-instruct', 'microsoft/phi-3.5-vision-instruct', 'microsoft/phi-4-mini-flash-reasoning', 'microsoft/phi-4-multimodal-instruct', 'minimaxai/minimax-m2.5', 'mistralai/devstral-2-123b-instruct-2512', 'mistralai/magistral-small-2506', 'mistralai/mamba-codestral-7b-v0.1', 'mistralai/mathstral-7b-v0.1', 'mistralai/ministral-14b-instruct-2512', 'mistralai/mistral-7b-instruct-v0.2', 'mistralai/mistral-7b-instruct-v0.3', 'mistralai/mistral-medium-3-instruct', 'mistralai/mistral-nemotron', 'mistralai/mistral-small-24b-instruct', 'mistralai/mistral-small-3.1-24b-instruct-2503', 'mistralai/mistral-small-4-119b-2603', 'mistralai/mixtral-8x22b-instruct-v0.1', 'mistralai/mixtral-8x7b-instruct-v0.1', 'moonshotai/kimi-k2-instruct', 'moonshotai/kimi-k2-instruct-0905', 'moonshotai/kimi-k2-thinking', 'moonshotai/kimi-k2.5', 'nvidia/gliner-pii', 'nvidia/llama-3.1-nemoguard-8b-content-safety', 'nvidia/llama-3.1-nemoguard-8b-topic-control', 'nvidia/llama-3.1-nemotron-70b-reward', 'nvidia/llama-3.1-nemotron-nano-vl-8b-v1', 'nvidia/llama-3.1-nemotron-safety-guard-8b-v3', 'nvidia/llama-3.3-nemotron-super-49b-v1', 'nvidia/llama-3.3-nemotron-super-49b-v1.5', 'nvidia/llama3-chatqa-1.5-8b', 'nvidia/nemotron-3-nano-30b-a3b', 'nvidia/nemotron-3-super-120b-a12b', 'nvidia/nemotron-4-mini-hindi-4b-instruct', 'nvidia/nemotron-content-safety-reasoning-4b', 'nvidia/nemotron-mini-4b-instruct', 'nvidia/nemotron-nano-12b-v2-vl', 'nvidia/nvidia-nemotron-nano-9b-v2', 'nvidia/riva-translate-4b-instruct-v1.1', 'openai/gpt-oss-120b', 'openai/gpt-oss-20b', 'opengpt-x/teuken-7b-instruct-commercial-v0.4', 'qwen/qwen2-7b-instruct', 'qwen/qwen2.5-7b-instruct', 'qwen/qwen2.5-coder-32b-instruct', 'qwen/qwen2.5-coder-7b-instruct', 'qwen/qwen3-next-80b-a3b-instruct', 'qwen/qwen3-next-80b-a3b-thinking', 'qwen/qwen3.5-122b-a10b', 'qwen/qwen3.5-397b-a17b', 'qwen/qwq-32b', 'rakuten/rakutenai-7b-chat', 'rakuten/rakutenai-7b-instruct', 'sarvamai/sarvam-m', 'speakleash/bielik-11b-v2.3-instruct', 'speakleash/bielik-11b-v2.6-instruct', 'stepfun-ai/step-3.5-flash', 'stockmark/stockmark-2-100b-instruct', 'thudm/chatglm3-6b', 'tiiuae/falcon3-7b-instruct', 'tokyotech-llm/llama-3-swallow-70b-instruct-v0.1', 'upstage/solar-10.7b-instruct', 'utter-project/eurollm-9b-instruct', 'yentinglin/llama-3-taiwan-70b-instruct', 'z-ai/glm4.7']

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Delete old nvidia
c.execute('DELETE FROM 模型配置表 WHERE 服务商 = "英伟达"')
print(f"Deleted: {c.rowcount}")

# Insert using raw SQL with positional values
for m in available:
    parts = m.split("/")
    name = parts[-1] if len(parts) > 1 else m
    
    c.execute(f'''INSERT INTO 模型配置表 VALUES (NULL, ?, ?, "对话", "英伟达", "https://integrate.api.nvidia.com/v1/chat/completions", ?, "是", "通用对话", NULL, NULL, "否", "否", "online")''',
              (name, m, NEW_KEY))

conn.commit()

# Verify
c.execute('SELECT COUNT(*) FROM 模型配置表 WHERE 服务商 = "英伟达"')
print(f"Inserted: {c.fetchone()[0]}")

conn.close()
print("Done!")
