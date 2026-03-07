#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v1.0.0 - User Guide Generator
"""
import sys
import json
import time
import requests
import threading
from datetime import datetime
from config import MODEL_CHAIN

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


print("=" * 70)
print("Symphony v1.0.0 - User Guide")
print("=" * 70)

# 生成用户指南
user_guide = '''
# 🎼 Symphony v1.0.0 用户使用指南

---

## 一、安装后快速开始

### 1. 配置API Key

编辑 `config.py` 文件，填入你的API Key：

```python
MODEL_CHAIN = [
    {
        "name": "zhipu_glm4_flash",
        "model_id": "glm-4-flash",
        "api_key": "你的智谱API Key",  # <--- 在这里填入
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "provider": "zhipu",
        "enabled": True,
        "priority": 1
    }
]
```

### 2. 运行Symphony

```bash
python symphony.py
```

---

## 二、基础使用

### 方式1：命令行调用

```python
from symphony import Symphony

# 初始化
s = Symphony(config)

# 调用模型
result = s.call("你好，请介绍一下自己")
print(result)
```

### 方式2：多模型协作

```python
# 并行调用多个模型
results = s.parallel_call([
    "作为产品经理，分析用户需求",
    "作为架构师，设计系统架构",
    "作为开发工程师，编写代码"
])

for r in results:
    print(r)
```

---

## 三、核心功能

### 1. 多模型并行调用

```python
# 同时调用6个不同模型
results = symphony.parallel_call(prompts)
```

### 2. 模型类型选择

```python
# 文本模型
model = symphony.get_model("text")

# 视觉模型
model = symphony.get_model("vision")

# 图像生成
model = symphony.get_model("image_gen")
```

### 3. 被动触发

```python
# 配置触发词
TRIGGERS = {
    "P0": ["交响", "symphony"],
    "P1": ["开发", "研发"],
    "P2": ["优化", "改进"]
}
```

---

## 四、配置说明

### model_index 对应表

| 索引 | 模型名称 | 类型 |
|------|----------|------|
| 0 | 智谱GLM-4-Flash | 文本 |
| 1 | 智谱GLM-Z1-Flash | 推理 |
| 2 | 智谱GLM-4V-Flash | 视觉 |
| 3 | 智谱GLM-4.1V-Thinking | 视觉推理 |
| 4 | 智谱CogView-3-Flash | 图像生成 |
| 5 | 智谱CogVideoX-Flash | 视频生成 |
| 6 | ModelScope GLM-4.7 | 文本 |
| 7 | ModelScope Z-Image-Turbo | 图像生成 |
| 8 | ModelScope DeepSeek-V3.2 | 文本 |
| 9+ | 其他模型 | 文本/推理 |

---

## 五、常见问题

### Q1: 提示API Key错误怎么办？
A: 检查config.py中的api_key是否正确，是否包含空格或特殊字符。

### Q2: 提示HTTP 429怎么办？
A: API调用超限，稍后再试或更换模型。

### Q3: 如何添加更多模型？
A: 在MODEL_CHAIN数组中添加新的模型配置。

### Q4: 支持哪些API提供商？
A: 目前支持智谱(zhipu)和ModelScope。

---

## 六、代码示例

### 示例1：简单对话

```python
import requests

# 配置
API_KEY = "your_api_key"
URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# 调用
headers = {"Authorization": f"Bearer {API_KEY}"}
data = {
    "model": "glm-4-flash",
    "messages": [{"role": "user", "content": "你好"}]
}

response = requests.post(URL, headers=headers, json=data)
print(response.json())
```

### 示例2：多模型协作

```python
import threading

def call_model(model_config, prompt):
    # 并行调用不同模型
    pass

# 创建线程
threads = []
for prompt, config in zip(prompts, models):
    t = threading.Thread(target=call_model, args=(config, prompt))
    threads.append(t)
    t.start()

# 等待结果
for t in threads:
    t.join()
```

---

## 七、版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0-beta | 2026-03-07 | 首次公测 |

---

## 八、获取帮助

- GitHub: https://github.com/songleiwww/symphony
- 问题反馈: https://github.com/songleiwww/symphony/issues

---

**品牌标语**: "智韵交响，共创华章！"
'''

# 保存用户指南
with open("USER_GUIDE.md", "w", encoding="utf-8") as f:
    f.write(user_guide)

print("\n已生成用户指南: USER_GUIDE.md")
print("\n" + "=" * 70)
print("User Guide Content Preview")
print("=" * 70)

sections = [
    "一、安装后快速开始",
    "二、基础使用", 
    "三、核心功能",
    "四、配置说明",
    "五、常见问题",
    "六、代码示例"
]

for s in sections:
    print("  ✓ {}".format(s))

print("\n完整内容请查看: USER_GUIDE.md")
print("\nSymphony - 智韵交响，共创华章！")
