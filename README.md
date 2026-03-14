# 🎼 序境交响 Symphony

> **⚠️ 重要声明**: 这是一个AI模型调度框架，使用前请配置自己的API Key

[![Version](https://img.shields.io/badge/version-2.0.0-blue)](https://github.com)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## ⚡ 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/symphony.git
cd symphony
```

### 2. 配置API Key

编辑 `data/symphony_template.db` 或创建 `data/symphony.db` 并配置:

```bash
# 使用脚本初始化
python scripts/init_api_keys.py
```

或手动修改数据库中的API Key字段。

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行

```python
from skills.symphony.Kernel.kernel_loader import KernelLoader

kl = KernelLoader()
kl.load_all()
print(f"加载完成: {kl.rules}")
```

---

## 📋 版本信息

| 版本 | 日期 | 说明 |
|------|------|------|
| 2.0.0 | 2026-03-14 | 正式版 - 模块化重构 |

---

## ⚠️ 使用约束

1. **现在时优先** - 只从 `symphony.db` 读取配置
2. **数据库唯一** - 不使用 `old/` 任何文件
3. **自行配置** - 使用前必须配置自己的API Key

---

## 📁 目录结构

```
symphony/
├── Kernel/              # ⭐ 内核核心
│   ├── kernel_loader.py  # 加载器
│   ├── dispatch_manager.py # 调度器
│   └── ...
├── data/                # ⭐ 数据存储
│   ├── symphony_template.db # 模板(不含Key)
│   └── README.md        # 数据说明
├── core/                # 可选 - 核心引擎
├── docs/                # 文档
├── scripts/             # 脚本工具
└── SKILL.md            # Skill说明
```

---

## 🔧 配置说明

### API Key配置

1. 复制模板数据库:
   ```bash
   cp data/symphony_template.db data/symphony.db
   ```

2. 使用SQLite工具修改:
   ```sql
   UPDATE 模型配置表 SET key = '你的API密钥';
   ```

3. 或使用Python脚本:
   ```python
   from skills.symphony.scripts.update_keys import update_api_keys
   
   update_api_keys({
       '火山引擎': 'your_volcano_key',
       '硅基流动': 'your_silicon_key',
       ...
   })
   ```

### 支持的服务商

| 服务商 | 状态 | 说明 |
|--------|------|------|
| 火山引擎 | ✅ 可用 | 需配置API Key |
| 硅基流动 | ✅ 可用 | 需配置API Key |
| 英伟达 | ✅ 可用 | 需配置API Key |
| 魔搭 | ✅ 可用 | 需配置API Key |
| 智谱 | ⚠️ 需测试 | 需配置API Key |
| OpenRouter | ⚠️ 需测试 | 需配置API Key |
| 魔力方舟 | ⚠️ 需测试 | 需配置API Key |

---

## 📖 文档

- [SKILL.md](SKILL.md) - Skill使用指南
- [data/README.md](data/README.md) - 数据说明
- [Kernel/README.md](Kernel/README.md) - 内核说明

---

## 🔄 迭代指南

用户/开发者可完全删除所有文件进行迭代:

1. 删除 `Kernel/`, `core/`, `data/` 等目录
2. 从GitHub重新克隆
3. 配置自己的API Key
4. 系统会自动从数据库重构

---

## 📝 License

MIT License

---

**⚠️ 注意**: 本项目不包含实际API Key，使用前请配置自己的密钥。
