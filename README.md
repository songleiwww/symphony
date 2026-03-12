# 🎼 序境系统 v1.0.0 正式版

## 系统简介

序境系统（Symphony）是业界领先的多模型协作调度系统，旨在实现多AI模型的智能协作与高效调度。该系统支持火山引擎、智谱AI、魔搭（ModelScope）、NVIDIA等多个主流AI服务提供商，能够根据任务需求自动选择最优模型，并具备完善的容错、限流处理和记忆机制。

### 核心特性

- **多模型调度**：支持4大主流AI服务提供商，火山引擎支持豆包全系列模型
- **智能路由**：根据任务类型自动匹配合适的模型
- **容错机制**：故障自动重试，降级处理，确保服务连续性
- **限流管理**：智能API限流检测与自动恢复
- **记忆系统**：长期记忆与每日日志，支持上下文连续性
- **少府监花名册**：完整的人员管理系统，9人团队协作

---

## 安装方式

### PyPI 安装（推荐）

```bash
pip install symphony-ai==1.0.1
```

### GitHub 安装

```bash
# 克隆项目
git clone https://github.com/songleiwww/symphony.git
cd symphony

# 安装依赖
pip install -r requirements.txt
```

---

## 快速开始

### 环境要求

- Python 3.9+
- 网络访问API服务

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

## 少府监团队

序境系统拥有完整的9人团队，模拟古代官署运作：

| ID | 姓名 | 官职 | 部门 | 专长 |
|----|------|------|------|------|
| sf-001 | 萧云飞 | 文案助手 | 内容部 | 文案润色 |
| sf-002 | 柳沉鱼 | 分析顾问 | 分析部 | 数据分析 |
| sf-003 | 慕容惊鸿 | 首席策略师 | 战略部 | 深度推理 |
| sf-004 | 苏瑾年 | 对话专家 | 客服部 | 中文对话 |
| sf-005 | 洛紫烟 | 文书博士 | 文档部 | 长文本处理 |
| sf-006 | 顾寒江 | 代码工程师 | 技术部 | 代码生成 |
| sf-007 | 沈星衍 | 推理大师 | 研究部 | 逻辑推理 |
| sf-008 | 叶轻舟 | 效率先锋 | 执行部 | 快速响应 |
| sf-009 | 程九章 | 高级研究员 | 研究部 | 深度研究 |

---

## 配置文件说明

### 主要配置文件：`config.py`

#### 1. 火山引擎配置（DOUBAO_CONFIG）

| 参数 | 说明 | 示例值 |
|------|------|--------|
| api_key | API密钥 | 3b922877-3fbe-45d1-a298-53f2231c5224 |
| base_url | API地址 | https://ark.cn-beijing.volces.com/api/coding/v3 |

**支持的模型：**
- ark-code-latest（豆包默认引擎）
- Doubao-Seed-2.0-pro（旗舰推理模型）
- Doubao-Seed-2.0-Code（代码模型）

---

## 下载地址

| 平台 | 地址 |
|------|------|
| GitHub Release | https://github.com/songleiwww/symphony/releases/tag/v1.0.0 |
| PyPI | https://pypi.org/project/symphony-ai/1.0.1/ |
| Gitee | https://gitee.com/wwwsonglei/symphony |

---

## 技术支持

- GitHub: https://github.com/songleiwww/symphony
- 邮箱: songlei_www@qq.com
- 版本: v1.0.0 (正式版)

---

**🎼 智韵交响，共创华章**
