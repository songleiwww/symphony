# 交响（Symphony）模型配置说明

## 中文说明 | Chinese Documentation

### 📊 可用模型总览

交响（Symphony）配置了 **17个模型**，来自 **4个提供商**：

| 提供商 | 模型数量 | 优先级范围 | 说明 |
|--------|---------|-----------|------|
| **cherry-doubao** | 5个 | 1-5 | 豆包模型（默认首选） |
| **cherry-minimax** | 1个 | 6 | MiniMax模型 |
| **cherry-nvidia** | 10个 | 7-15 | NVIDIA模型 |
| **cherry-modelscope** | 2个 | 16-17 | ModelScope模型 |

---

### 🎯 详细模型列表

#### 1️⃣ cherry-doubao（5个模型）

| 优先级 | 名称 | 别名 | 模型ID | 上下文 |
|-------|------|------|--------|--------|
| 1 | doubao_ark_code | Doubao Ark Code | ark-code-latest | 128K |
| 2 | doubao_deepseek_v32 | DeepSeek V3.2 | deepseek-v3.2 | 128K |
| 3 | doubao_seed_code | Doubao Seed Code | doubao-seed-2.0-code | 128K |
| 4 | doubao_glm_47 | GLM 4.7 | glm-4.7 | 128K |
| 5 | doubao_kimi_k25 | Kimi K2.5 | kimi-k2.5 | 128K |

**API配置**:
- Base URL: `https://ark.cn-beijing.volces.com/api/coding/v3`
- API类型: OpenAI Completions
- 配置Key: `YOUR_CHERRY_DOUBAO_API_KEY`

---

#### 2️⃣ cherry-minimax（1个模型）

| 优先级 | 名称 | 别名 | 模型ID | 上下文 |
|-------|------|------|--------|--------|
| 6 | minimax_m25 | MiniMax M2.5 | MiniMax-M2.5 | 128K |

**API配置**:
- Base URL: `https://api.minimaxi.com/anthropic`
- API类型: Anthropic Messages
- 配置Key: `YOUR_CHERRY_MINIMAX_API_KEY`

---

#### 3️⃣ cherry-nvidia（10个模型）

| 优先级 | 名称 | 别名 | 模型ID | 上下文 |
|-------|------|------|--------|--------|
| 7 | nvidia_llama_31_405b | Llama 3.1 405B | meta/llama-3.1-405b-instruct | 128K |
| 8 | nvidia_deepseek_v32 | DeepSeek V3.2 (NVIDIA) | deepseek-ai/deepseek-v3.2 | 128K |
| 9 | nvidia_kimi_k25 | Kimi K2.5 (NVIDIA) | moonshotai/kimi-k2.5 | 128K |
| 10 | nvidia_glm_47 | GLM 4.7 (NVIDIA) | z-ai/glm4.7 | 128K |
| 11 | nvidia_qwen3_coder | Qwen3 Coder 480B | qwen/qwen3-coder-480b-a35b-instruct | 128K |
| 12 | nvidia_qwen35_397b | Qwen3.5 397B | qwen/qwen3.5-397b-a17b | 128K |
| 13 | nvidia_minimax_m25 | MiniMax M2.5 (NVIDIA) | minimaxai/minimax-m2.5 | 128K |
| 14 | nvidia_glm5 | GLM 5 | z-ai/glm5 | 128K |
| 15 | nvidia_gpt_oss_20b | GPT OSS 20B | openai/gpt-oss-20b | 128K |

**API配置**:
- Base URL: `https://integrate.api.nvidia.com/v1`
- API类型: OpenAI Completions
- 配置Key: `YOUR_CHERRY_NVIDIA_API_KEY`

---

#### 4️⃣ cherry-modelscope（2个模型）

| 优先级 | 名称 | 别名 | 模型ID | 上下文 |
|-------|------|------|--------|--------|
| 16 | modelscope_deepseek_r1 | DeepSeek R1 | deepseek-ai/DeepSeek-R1-0528 | 128K |
| 17 | modelscope_qwen3_235b | Qwen3 235B | Qwen/Qwen3-235B-A22B-Instruct-2507 | 128K |

**API配置**:
- Base URL: `https://api-inference.modelscope.cn`
- API类型: Anthropic Messages
- 配置Key: `YOUR_CHERRY_MODELSCOPE_API_KEY`

---

### ⚙️ 配置API Key

#### 步骤1：获取真实Key
从你的OpenClaw配置文件中复制Key：
```
C:\Users\Administrator\.openclaw\openclaw.cherry.json
```

#### 步骤2：编辑 config.py
```python
# 替换占位符为真实Key
# cherry-doubao
"api_key": "3b922877-3fbe-45d1-a298-53f2231c5224",

# cherry-minimax
"api_key": "sk-cp-c_GUV0dBahIRIeYgEvbXK8YAPlZBTNwN_6FcETIELPo_zrGAXtwscyVLNs_FKh9aQZECdOwdm2UqsKy85D8KlmkR7EGro-tiTADoYapVwiA7xu9NYcnidak",

# cherry-nvidia
"api_key": "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",

# cherry-modelscope
"api_key": "ms-eac6f154-3502-4721-a168-ce7caeaf1033",
```

#### ⚠️ 重要安全提醒
1. **本地使用时**：填入真实Key
2. **上传GitHub前**：改回占位符
3. **永远不要**：把真实Key提交到GitHub

---

### 🔄 故障转移机制

交响会按优先级自动尝试模型：

```
优先级 1 (Doubao Ark Code)
    ↓ 失败
优先级 2 (DeepSeek V3.2)
    ↓ 失败
优先级 3 (Doubao Seed Code)
    ↓ ...
...
    ↓ 失败
优先级 17 (Qwen3 235B)
```

所有模型都失败时，会触发故障处理系统。

---

### 📊 模型统计

| 指标 | 数值 |
|------|------|
| **总模型数** | 17个 |
| **提供商数** | 4个 |
| **上下文窗口** | 128K（所有模型）|
| **默认首选** | Doubao Ark Code |
| **最后备选** | Qwen3 235B |

---

## English Documentation

### 📊 Available Models Overview

Symphony is configured with **17 models** from **4 providers**:

| Provider | Count | Priority Range | Description |
|----------|-------|---------------|-------------|
| **cherry-doubao** | 5 | 1-5 | Doubao models (default primary) |
| **cherry-minimax** | 1 | 6 | MiniMax models |
| **cherry-nvidia** | 10 | 7-15 | NVIDIA models |
| **cherry-modelscope** | 2 | 16-17 | ModelScope models |

---

### ⚙️ Configure API Keys

#### Step 1: Get real keys
Copy from your OpenClaw config:
```
C:\Users\Administrator\.openclaw\openclaw.cherry.json
```

#### Step 2: Edit config.py
Replace placeholders with real keys (see Chinese section above for details).

#### ⚠️ Important Security Notes
1. **Local use**: Fill in real keys
2. **Before GitHub upload**: Change back to placeholders
3. **Never**: Commit real keys to GitHub

---

### 🔄 Failover Mechanism

Symphony automatically tries models in priority order (see Chinese section for diagram).

---

*智韵交响，共创华章*
