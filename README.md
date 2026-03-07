# Symphony 智韵交响 🎵

> 多模型协作智能系统 | Multi-Model Collaboration Intelligence System

## 概述

Symphony（交响）是一个多模型协作智能系统，通过协调多个AI模型实现复杂任务处理。

## 特性

- 🎯 **多模型协作** - 支持16+模型并行调用
- 🔄 **智能调度** - 根据任务自动选择最优模型
- ⚡ **限流优化** - 自动检测和处理限流
- 🛡️ **错误恢复** - 完善的错误处理机制
- 📝 **记忆协调** - 与OpenClaw记忆同步
- 🧠 **人性化触发** - 主动/被动智能帮助

## 安装

```bash
git clone https://github.com/songleiwww/symphony.git
cd symphony
pip install requests
```

## 配置

编辑 `config.py` 配置你的API密钥：

```python
MODEL_CHAIN = [
    {
        "name": "your_model",
        "api_key": "YOUR_API_KEY",
        "base_url": "https://api.example.com/v1",
        "model_id": "model-id",
        "enabled": True
    }
]
```

## 使用

```python
from symphony_core import Symphony

# 初始化
s = Symphony()

# 调用
result = s.call("你好")
print(result)
```

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0.0 | 2026-03-08 | 首发版发布 |

## 许可证

MIT License

---

**品牌标语**: "智韵交响，共创华章！" 🎵
