# 阿里云百炼 - 语音/多模态/视觉/向量模型 API 调用文档
**生成时间**: 2026-04-10
**适用范围**: 序境系统内核集成，所有调用示例可直接使用

---

## 目录

1. [语音识别 (ASR)](#语音识别-asr)
2. [语音合成 (TTS)](#语音合成-tts)
3. [多模态理解](#多模态理解)
4. [视觉理解](#视觉理解)
5. [向量嵌入](#向量嵌入)
6. [通用调用格式](#通用调用格式)
7. [错误码参考](#错误码参考)

---

## 语音识别 (ASR)

### 可用模型

| 模型ID | 说明 | 最大长度 |
|--------|------|----------|
| `paraformer-realtime-v2` | 实时语音识别 | 长音频 |
| `paraformer-v1` | 离线语音识别 | 最长30分钟 |
| `paraformer-realtime-8k-v1` | 8k 电话语音识别 | 实时 |

### 调用示例 (REST API)

```python
import requests
import json

API_KEY = "your-api-key-here"
url = "https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "paraformer-v1",
    "input": {
        "audio_url": "https://example.com/audio.wav"
    }
}

response = requests.post(url, headers=headers, json=payload, timeout=60)
result = response.json()
# 输出: {"output": {"transcript": "识别出的文本内容"}}
```

### 实时语音识别 (WebSocket)

```python
import websockets
import json

async def realtime_asr():
    url = f"wss://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription/real-time?model=paraformer-realtime-v2&token={API_KEY}"
    async with websockets.connect(url) as ws:
        # 发送音频数据分片
        # 接收结果流
```

---

## 语音合成 (TTS)

### 可用模型

| 模型ID | 说明 | 特色 |
|--------|------|------|
| `cosyvoice-v1` | CosyVoice 语音合成 | 高自然度 |
| `sambert-tts-v1` | SamBERT 语音合成 | 情感丰富 |

### 调用示例

```python
import requests
import json

API_KEY = "your-api-key-here"
url = "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/generation"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "cosyvoice-v1",
    "input": {
        "text": "你好，欢迎使用阿里云百炼",
        "voice": "longwan"  # 可选: longwan, longhua, longye, etc.
    }
}

response = requests.post(url, headers=headers, json=payload, timeout=30)
# 返回音频二进制数据
with open("output.wav", "wb") as f:
    f.write(response.content)
```

### 参数说明

| 参数 | 必须 | 说明 |
|-----|------|------|
| `model` | 是 | 模型ID |
| `input.text` | 是 | 待合成文本 |
| `input.voice` | 否 | 音色ID，默认 `longwan` |
| `input.format` | 否 | 输出格式: `wav`/`mp3`，默认 `wav` |

---

## 多模态理解

### 可用模型

| 模型ID | 说明 | 输入 |
|--------|------|------|
| `qwen-vl-plus` | 通义千问VL+ | 图片+文本问答 |
| `qwen-vl-max` | 通义千问VL Max | 图片+文本问答，更强能力 |
| `qwen-vl-chat` | 通义千问VL 对话版 | 多轮对话 |

### 调用示例 (图片问答)

```python
import requests
import json

API_KEY = "your-api-key-here"
url = "https://dashscope.aliyuncs.com/api/v1/services/multimodal/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "qwen-vl-plus",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "图片里有什么？"
                },
                {
                    "type": "image_url",
                    "image_url": "https://example.com/image.jpg"
                }
            ]
        }
    ]
}

response = requests.post(url, headers=headers, json=payload, timeout=30)
result = response.json()
# 输出: {"choices": [{"message": {"content": "分析结果"}}]}
```

### 本地图片上传方式

```python
# 使用base64编码
import base64

with open("local_image.jpg", "rb") as f:
    base64_img = base64.b64encode(f.read()).decode("utf-8")

# 在content中使用data URI格式
{
    "type": "image_url",
    "image_url": f"data:image/jpeg;base64,{base64_img}"
}
```

---

## 视觉理解

### 可用模型

| 模型ID | 任务类型 | 说明 |
|--------|---------|------|
| `detic-v1` | 开放世界检测 | 任意类别检测 |
| `ocr-general` | OCR文字识别 | 通用文字识别 |
| `ocr-structured` | 结构化OCR | 表格/卡片识别 |

### OCR 文字识别调用示例

```python
import requests
import json

API_KEY = "your-api-key-here"
url = "https://dashscope.aliyuncs.com/api/v1/services/vision/ocr/general"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "ocr-general",
    "input": {
        "image_url": "https://example.com/document.jpg"
    }
}

response = requests.post(url, headers=headers, json=payload, timeout=30)
result = response.json()
# 输出: {"output": {"text": "识别出的所有文字", "boxes": [...]}}
```

### 目标检测调用示例

```python
payload = {
    "model": "detic-v1",
    "input": {
        "image_url": "https://example.com/image.jpg",
        "categories": ["猫", "狗", "人"]
    }
}
# 返回每个检测框的位置和类别
```

---

## 向量嵌入

### 可用模型

| 模型ID | 维度 | 说明 | 适用场景 |
|--------|------|------|----------|
| `text-embedding-v1` | 1536 | 通用文本向量 | RAG、检索 |
| `text-embedding-v2` | 1536/3072 | 改进版 | 更好语义理解 |
| `text-embedding-async-v1` | 1536 | 异步批量 | 大批量处理 |

### 调用示例

```python
import requests
import json

API_KEY = "your-api-key-here"
url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 单文本
payload = {
    "model": "text-embedding-v1",
    "input": {
        "texts": ["你好，世界"]
    }
}

# 多文本批量（最多25条）
payload = {
    "model": "text-embedding-v1",
    "input": {
        "texts": ["第一段文本", "第二段文本"]
    }
}

response = requests.post(url, headers=headers, json=payload, timeout=30)
result = response.json()
# 输出: {"output": {"embeddings": [[0.1, 0.2, ...], ...]}}
```

### 输出格式

```json
{
  "output": {
    "embeddings": [
      {
        "text_index": 0,
        "embedding": [0.123, 0.456, ...]  # 1536维向量
      }
    ]
  },
  "usage": {
    "total_tokens": 8
  }
}
```

---

## 通用调用格式

### 端点汇总

| 类型 | 端点URL |
|------|---------|
| 语音识别 | `https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription` |
| 语音合成 | `https://dashscope.aliyuncs.com/api/v1/services/audio/tts/generation` |
| 多模态聊天 | `https://dashscope.aliyuncs.com/api/v1/services/multimodal/chat/completions` |
| OCR识别 | `https://dashscope.aliyuncs.com/api/v1/services/vision/ocr/general` |
| 向量嵌入 | `https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding` |

### 通用响应格式

```json
{
  "code": "",
  "message": "",
  "output": {
    // 模型特定输出
  },
  "usage": {
    "total_tokens": 0
  },
  "request_id": ""
}
```

### 认证方式

所有请求都需要在 Header 中携带：
```
Authorization: Bearer {API_KEY}
```

API_KEY 从 `symphony.db` 的 `provider_registry` 表读取

---

## 错误码参考

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| `InvalidApiKey` | API Key 无效 | 检查密钥配置 |
| `QuotaExceeded` | 配额不足 | 降级到其他模型 |
| `ModelNotEnabled` | 模型未启用 | 在阿里云控制台启用 |
| `ContentTooLarge` | 内容过大 | 分片处理 |
| `RateLimitExceeded` | 请求过快 | 等待重试 |
| `InternalError` | 服务端错误 | 重试或降级 |

---

## 序境内核集成说明

### 1. 模型类型标记

在 `symphony.db` 的 `model_config` 表中，`model_type` 字段取值：

| 类型 | 值 |
|------|-----|
| 语音识别 | `asr` |
| 语音合成 | `tts` |
| 多模态 | `multimodal` |
| 视觉 | `vision` |
| 向量嵌入 | `embedding` |

### 2. 调度优先级

序境调度器会根据 `model_type` 自动匹配对应端点：

```python
# 伪代码
if model_type == 'asr':
    endpoint = ASR_ENDPOINT
elif model_type == 'tts':
    endpoint = TTS_ENDPOINT
elif model_type == 'embedding':
    endpoint = EMBEDDING_ENDPOINT
...
```

### 3. 自动降级逻辑

- 阿里云调用失败 → 自动降级到其他服务商对应类型模型
- 配额用尽 → 自动跳过，选择下一个可用模型
- 权限错误 → 标记模型为不可用，后续跳过

---

## 测试验证

### 向量嵌入测试

```python
# 测试代码
import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
from providers.pool import ProviderPool

pool = ProviderPool(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db')
result = pool.embedding("测试文本", provider="aliyun")
print(result)  # 返回向量
```

### 多模态测试

```python
result = pool.multimodal_chat(
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "描述这张图片"},
            {"type": "image_url", "image_url": "https://example.com/image.jpg"}
        ]
    }],
    model="qwen-vl-plus",
    provider="aliyun"
)
```

---

## 更新记录

| 日期 | 更新内容 |
|------|----------|
| 2026-04-10 | 初始创建，整理语音/多模态/视觉/向量模型调用方法 |

---

**文档维护**: 序境系统内核  
**最后更新**: 2026-04-10
