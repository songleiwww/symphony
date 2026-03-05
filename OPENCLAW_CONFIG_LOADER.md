# OpenClaw配置加载器使用说明

## 中文说明 | Chinese Documentation

### 📦 什么是OpenClaw配置加载器？

OpenClaw配置加载器让交响（Symphony）自动从你的OpenClaw配置中读取真实的模型和API Key，无需手动维护两份配置！

---

### ✨ 主要功能

1. **自动加载** - 从 `openclaw.cherry.json` 读取配置
2. **格式转换** - 自动转换为交响的MODEL_CHAIN格式
3. **优先级保持** - 保持模型优先级顺序
4. **安全无虞** - 永远不会把真实Key提交到GitHub

---

### 🚀 快速开始

#### 方式1：直接使用加载器（推荐）

```python
from openclaw_config_loader import load_symphony_models

# 加载模型配置
MODEL_CHAIN = load_symphony_models()

# 现在MODEL_CHAIN包含了所有17个模型和真实API Key！
```

#### 方式2：使用Loader类

```python
from openclaw_config_loader import OpenClawConfigLoader

# 创建加载器
loader = OpenClawConfigLoader()

# 加载所有模型
models = loader.get_models()

# 根据优先级获取模型
model = loader.get_model_by_priority(1)  # 获取优先级1的模型

# 根据名称获取模型
model = loader.get_model_by_name("cherry_doubao_ark_code_latest")

# 打印配置摘要
loader.print_summary()
```

---

### 📊 配置的模型

加载器会自动加载以下模型：

| 提供商 | 模型数量 | 优先级范围 |
|--------|---------|-----------|
| cherry-doubao | 5 | 1-5 |
| cherry-minimax | 1 | 6 |
| cherry-nvidia | 9 | 7-15 |
| cherry-modelscope | 2 | 16-17 |

**总计**: 17个模型

---

### 🔒 安全说明

#### ⚠️ 重要规则

1. **本地使用时**：加载器会读取真实Key
2. **上传GitHub前**：config.py中的Key保持为占位符
3. **永远不要**：把openclaw_config_loader.py的输出提交到GitHub

#### ✅ 推荐工作流

```
本地开发：
    使用 load_symphony_models() → 自动读取真实Key

提交GitHub前：
    确保config.py中的Key是占位符 → 安全！
```

---

### 🛠️ 高级功能

#### 指定自定义配置路径

```python
from openclaw_config_loader import load_symphony_models

# 使用自定义配置文件
models = load_symphony_models("path/to/your/openclaw.cherry.json")
```

#### 更新config.py（仅本地使用）

```python
from openclaw_config_loader import create_updated_config

# 生成更新后的config.py内容
new_config = create_updated_config()

# 写入文件（注意：仅本地使用，不要提交！）
with open("config.py", "w", encoding="utf-8") as f:
    f.write(new_config)
```

---

### 📋 快速参考

| 函数/类 | 用途 |
|---------|------|
| `OpenClawConfigLoader()` | 创建加载器实例 |
| `loader.get_models()` | 获取所有模型列表 |
| `loader.get_model_by_priority(n)` | 获取第n个优先级的模型 |
| `loader.get_model_by_name(name)` | 根据名称获取模型 |
| `loader.print_summary()` | 打印配置摘要 |
| `load_symphony_models()` | 便捷函数，直接加载模型列表 |
| `create_updated_config()` | 生成更新后的config.py |

---

### 💡 常见问题

**Q: 加载器会修改我的OpenClaw配置吗？**
A: 不会！加载器是只读的，不会修改任何文件。

**Q: 我可以把加载器提交到GitHub吗？**
A: 可以！加载器本身不包含任何敏感信息。

**Q: 如何确保真实Key不会泄露？**
A: 只要确保config.py中的Key是占位符，就不会泄露。

---

## English Documentation

### 📦 What is OpenClaw Config Loader?

OpenClaw Config Loader lets Symphony automatically read real models and API keys from your OpenClaw config - no need to maintain two sets of configs!

---

### ✨ Key Features

1. **Auto Load** - Read config from `openclaw.cherry.json`
2. **Format Conversion** - Auto-convert to Symphony's MODEL_CHAIN format
3. **Priority Preservation** - Keep model priority order
4. **Security First** - Never commit real keys to GitHub

---

### 🚀 Quick Start

See Chinese section above for code examples (API is the same).

---

*智韵交响，共创华章*
