# 序境 (Symphony/Xujing) - 多模型多脑协同调度引擎

**Version:** 4.5.0 Premium  
**Status:** ✅ Production Ready  
**Root Path:** `C:\Users\Administrator\.openclaw\workspace\skills\symphony`  
**Database:** `C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db`  
**Last Restoration:** 2026-04-10  

---

## 概述

**序境 (Symphony)** 是一个高级多模型多脑协同调度系统，支持 4 大主流 AI 服务商共 **613+** 个模型，实现动态负载均衡、智能优先级调度、自动失败降级、配额监控和自适应配置管理。

### 支持的服务商

| 服务商 | 模型数量 | 状态 |
|--------|---------|------|
| 阿里云百炼 | 389 | ✅ 在线 |
| MiniMax | ~100+ | ✅ 在线 |
| 智谱AI | ~100+ | ✅ 在线 |
| 英伟达 NVIDIA API | ~20+ | ✅ 在线 |

### 支持的模型类型

- `chat` - 通用文本对话
- `code` - 代码生成
- `embedding` - 文本向量嵌入
- `multimodal` - 多模态理解（文本+图片）
- `vision` / `ocr` - 视觉/文字识别
- `asr` - 语音识别
- `tts` - 语音合成
- `image` - 图像生成
- `image_edit` - 图像编辑
- `video` - 视频生成
- `classification` - 文本分类
- `rerank` - 重排序
- `translate` - 翻译

---

## 核心架构

### 目录结构

```
symphony/
├── Kernel/                    # 内核模块
│   ├── scheduler.py          # 主调度器
│   ├── router.py             # 路由决策
│   ├── priority.py           # 优先级计算
│   ├── fallback.py           # 降级处理
│   ├── quota_manager.py      # 配额管理
│   ├── adaptive_config.py    # 自适应配置
│   └── self_healing/         # ⚠️ 自修复模块（文件损坏）
├── providers/                 # 服务商对接
│   ├── pool.py               # 服务商连接池
│   ├── aliyun.py             # 阿里云百炼
│   ├── minimax.py            # MiniMax
│   ├── zhipu.py              # 智谱AI
│   └── nvidia.py             # 英伟达 API
├── db/                       # 数据库操作
│   └── database.py           # SQLite 封装
├── config/                   # 配置文件
├── rules/                    # 系统规则
├── data/                     # 数据目录
│   └── symphony.db          # 主数据库（已修正）
├── docs/                     # 文档
│   ├── ALIYUN_MODELS_API.md  # 阿里云模型API调用文档 ✨ 新增
│   ├── QUICKREF.md            # 快速参考
│   ├── SELF_TRAINING.md       # 自训练指南
│   └── TOOL_POINTERS.md       # 工具指针
└── models/                   # 模型配置缓存
```

### 核心模块

1. **ProviderPool** - 服务商连接池管理
   - 从数据库读取已启用的服务商
   - 动态负载均衡选择最轻负载的服务商
   - 支持动态注册/注销

2. **SymphonyScheduler** - 主调度器
   - 根据模型类型、优先级选择最佳模型
   - 处理请求超时、失败自动重试
   - 失败自动降级到下一可用模型

3. **QuotaManager** - 配额管理
   - 记录 token 使用量
   - 监控配额使用进度
   - 配额满自动跳过该模型

4. **AdaptiveConfig** - 自适应配置
   - 版本化配置管理
   - 自动回滚到上一可用版本
   - 运行时配置优化建议

---

## API 调用方法

### 快速开始

```python
from symphony.Kernel.scheduler import SymphonyScheduler
from symphony.providers.pool import ProviderPool

# 初始化
pool = ProviderPool()
scheduler = SymphonyScheduler(pool)

# 文本对话
response = scheduler.chat(
    messages=[{"role": "user", "content": "你好"}],
    model_type="chat"
)
print(response.output)
```

### 向量嵌入

```python
embeddings = scheduler.embed(
    texts=["你的文本1", "你的文本2"]
)
# 返回: [vector1, vector2]
```

### 多模态图片问答

```python
response = scheduler.multimodal_chat(
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "描述这张图片"},
            {"type": "image_url", "image_url": "https://example.com/image.jpg"}
        ]
    }]
)
```

### 语音识别 (ASR)

```python
result = scheduler.asr(
    audio_url="https://example.com/audio.wav",
    model="paraformer-v1"
)
# 返回识别文本
```

### 语音合成 (TTS)

```python
audio_data = scheduler.tts(
    text="你好，世界",
    voice="longwan"
)
# 返回音频二进制
```

完整 API 文档参见: [docs/ALIYUN_MODELS_API.md](./docs/ALIYUN_MODELS_API.md)

---

## 数据库结构

主数据库: `data/symphony.db` (**已从 symphony_working.db 修正**)

| 表名 | 用途 |
|------|------|
| `provider_registry` | 服务商注册信息（API Key、URL）|
| `model_config` | 所有模型配置（ID、类型、上下文窗口、价格）|
| `model_quotas` | 配额使用记录 |
| `model_preferences` | 用户偏好配置 |
| `task_history` | 任务历史记录 |
| `Token使用记录` | Token 消费明细 |
| `node_registry` | 计算节点注册 |
| `tool_registry` | 工具注册 |
| `adaptive_config` | 自适应配置 |
| `config_versions` | 配置版本历史 |

---

## 核心特性

| 特性 | 说明 |
|------|------|
| ✅ **动态负载均衡** | 自动选择负载最低的服务商 |
| ✅ **自动失败降级** | 调用失败自动重试 → 不行就换模型 |
| ✅ **配额感知调度** | 配额用尽自动跳过，不会浪费请求 |
| ✅ **类型感知路由** | 根据任务类型自动匹配对应模型 |
| ✅ **自适应配置版本** | 支持配置回滚，永不宕机 |
| ✅ **多服务商支持** | 一次配置，百家模型可用 |
| ✅ **SQLite 持久化** | 所有配置存在数据库，易于备份迁移 |

---

## 恢复状态 (2026-04-10)

### ✅ 已恢复正常

- [x] 所有核心模块代码可读可运行
- [x] 数据库路径修正 (`symphony.db` ✅ 存在)
- [x] 版本号更新 (v4.5.0)
- [x] 模型计数更新 (613+)
- [x] 阿里云各类型模型API文档整理完成并测试
- [x] 文档错误修正完成

### ⚠️ 损坏模块

以下非核心模块文件编码损坏，不影响核心调度功能:

- `Kernel/SelfEvolutionV2.py` - 自进化模块（非核心）
- `Kernel/AgentMemoryLayer.py` - 增强记忆层（非核心）
- `Kernel/self_healing/SelfHealingMonitor.py` - 自监控模块（非核心）

如需修复，需要重新获取原始文件。

---

## 配置约束 (OpenClaw 集成)

在 OpenClaw 环境中运行时，需遵守:

1. **禁止自动修改 `openclaw.json`** - 配置已固化
2. **禁止自动重启网关** - 任何重启必须由用户手动执行

---

## 文档索引

- [快速参考](./docs/QUICKREF.md)
- [自训练指南](./docs/SELF_TRAINING.md)
- [阿里云模型 API 调用文档](./docs/ALIYUN_MODELS_API.md)
- [模型配置指南](./model_config_guide.md)
- [常见陷阱](./PITFALLS.md)
- [恢复状态报告](./RESTORATION_STATUS.md)

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v4.5.0 | 2026 | 当前版本，613+ 模型，修复路径，文档更新 |
| v4.3.0 | 2025 | 之前版本，938+ 模型 |

---

## 作者

序境 (Symphony/Xujing) - 宋磊  
**本 Skill 维护:** 序境内核团队

---

## 许可证

Premium Edition - 仅限授权使用
