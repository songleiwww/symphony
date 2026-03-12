# 🎼 序境系统 v1.1.0 中文说明书

## 系统简介

序境系统（Symphony）是业界领先的多模型协作调度系统，旨在实现多AI模型的智能协作与高效调度。该系统支持火山引擎、智谱AI、魔搭（ModelScope）、NVIDIA等多个主流AI服务提供商，能够根据任务需求自动选择最优模型，并具备完善的容错、限流处理和记忆机制。

### 核心特性

- **多模型调度**：支持4大主流AI服务提供商，火山引擎支持豆包全系列模型
- **智能路由**：根据任务类型自动匹配合适的模型
- **容错机制**：故障自动重试、降级处理，确保服务连续性
- **限流管理**：智能API限流检测与自动恢复
- **记忆系统**：长期记忆与每日日志，支持上下文连续性

---

## 功能列表

### 1. 模型调度中心
- 并行/顺序/链式多种调度策略
- 动态模型选择与负载均衡
- API限流自动检测与恢复

### 2. 协作会议系统
- 多人多模型讨论会议
- 自动汇总各方观点
- 决策建议生成

### 3. 记忆管理系统
- 长期记忆持久化（MEMORY.md）
- 每日工作日志（memory/YYYY-MM-DD.md）
- 基因故事与品牌故事

### 4. 进化优化系统
- 基于使用反馈的系统进化
- 性能监控与报告生成
- 自动化测试与验证

### 5. 故障处理系统
- 多层级容错机制
- 备用模型自动切换
- 网络异常自动恢复

---

## 快速开始

### 环境要求

- Python 3.8+
- 网络访问API服务

### 安装步骤

```bash
# 克隆项目
git clone https://github.com/songleiwww/symphony.git
cd symphony

# 安装依赖
pip install -r requirements.txt
```

### 基础使用

```python
from sf_complete_system import SymphonySystem

# 初始化系统
symphony = SymphonySystem()

# 调用单模型
result = symphony.call_model("你好，请介绍一下自己")

# 调用多模型协作
results = symphony.call_multi_models(["问题1", "问题2", "问题3"])
```

---

## 配置文件说明

### 主要配置文件：`config.py`

#### 1. 火山引擎配置（DOUBAO_CONFIG）

| 参数 | 说明 | 示例值 |
|------|------|--------|
| api_key | API密钥 | 3b922877-3fbe-45d1-a298-53f2231c5224 |
| base_url | API地址 | https://ark.cn-beijing.volces.com/api/coding/v3 |
| rate_limit.max_requests_per_minute | 每分钟请求上限 | 60 |

**支持的模型：**
- ark-code-latest（豆包默认引擎）
- Doubao-Seed-2.0-pro（旗舰推理模型）
- Doubao-Seed-2.0-Code（代码模型）
- MiniMax-M2.5（通用模型）
- Kimi-K2.5（代码模型）
- GLM-4.7（智谱模型）

#### 2. 智谱配置（ZHIPU_CONFIG）

| 参数 | 说明 | 示例值 |
|------|------|--------|
| api_key | API密钥 | 16cf0a4a... |
| base_url | API地址 | https://open.bigmodel.cn/api/paas/v4 |

**支持的模型：**
- glm-4-flash（通用）
- glm-z1-flash（推理）
- glm-4v-flash（视觉）

#### 3. 魔搭配置（MODELSCOPE_CONFIG）

| 参数 | 说明 | 示例值 |
|------|------|--------|
| api_key | API密钥 | ms-eac6f154-... |
| base_url | API地址 | https://api-inference.modelscope.cn/v1 |

**限制：** 每日2000次调用，单模型≤500次/天

#### 4. 人员绑定配置（PERSON_ROSTER）

将团队成员与模型进行绑定，实现个性化调度：

```python
PERSON_ROSTER = {
    "沈清弦": {"model": "ark-code-latest", "priority": 1},
    "苏云渺": {"model": "ark-code-latest", "priority": 1},
    # ...
}
```

---

## 常见问题

### Q1: 如何添加新的模型提供商？

在`config.py`中新增配置块，参考现有格式：

```python
NEW_PROVIDER_CONFIG = {
    "api_key": "your-api-key",
    "base_url": "https://api.provider.com/v1",
    "provider": "provider-name",
    "models": [...]
}
```

### Q2: 遇到API限流怎么办？

系统内置限流处理机制：
1. 自动降级到备用模型
2. 等待恢复后重试
3. 记录限流事件供分析

### Q3: 如何查看系统日志？

```bash
# 查看实时日志
python -m sf_complete_system --log-level DEBUG
```

### Q4: 记忆系统如何工作？

- **MEMORY.md**：长期记忆文件，记录重要信息
- **memory/YYYY-MM-DD.md**：每日工作日志
- 系统会自动同步上下文到记忆系统

### Q5: 如何进行多模型协作？

```python
from symphony_meeting import Meeting

# 创建讨论会议
meeting = Meeting(topic="问题讨论", participants=["model1", "model2"])
result = meeting.discuss("需要讨论的问题")
```

---

## 目录结构

```
symphony/
├── config.py              # 主配置文件
├── sf_complete_system.py # 核心系统
├── sf_adaptive_system_v2.py # 自适应系统
├── symphony_meeting.py    # 会议系统
├── memory_system.py       # 记忆系统
├── fault_tolerance.py     # 容错系统
├── rate_limit_handler.py  # 限流处理
├── model_manager.py       # 模型管理
├── examples/              # 使用示例
├── docs/                  # 文档
└── outputs/               # 输出结果
```

---

## 技术支持

- GitHub: https://github.com/songleiwww/symphony
- 邮箱: songlei_www@qq.com
- 版本: v1.1.0 (Evolution Release)

---

**🎼 智韵交响，共创华章**
