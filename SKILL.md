---
name: symphony
version: 0.8.5
description: >
  Symphony（交响）多模型协作系统：完整的多模型协作开发平台，展示从需求分析到最终交付的全流程AI协作。品牌标语："智韵交响，共创华章"。
author: songleiwww
keywords: [symphony, 交响, multi-agent, 多模型协作, real model, 真实模型调用, entertainment mode, 娱乐模式, conductor, 指挥家]
---

# 🎼 Symphony（交响）多模型协作系统

> **智韵交响，共创华章**
>
> 一个完整的多模型协作开发平台，展示从需求分析到最终交付的全流程AI协作。

---

## 📋 项目信息

| 项目 | 说明 |
|------|------|
| **项目名称（中文沟通用）** | 交响 |
| **项目名称（英文/代码用）** | Symphony |
| **本地路径** | `C:\Users\Administrator\.openclaw\workspace\multi_agent_demo` |
| **GitHub仓库** | https://github.com/songleiwww/symphony |
| **品牌标语** | "智韵交响，共创华章" |

---

## 🎯 核心功能

### 🤖 多模型协作
- **完整的开发流程** - 从需求分析到最终交付的5步协作流程
- **可追溯的决策历史** - 每个步骤都有详细的输入输出记录
- **模块化设计** - 清晰的职责分离，易于扩展
- **知识沉淀** - 完整的文档体系，便于学习和回顾

### 🌤️ 天气查询工具（演示项目）
- 🌍 支持全球城市查询（中文/英文）
- 🌡️ 实时温度、体感温度
- 💨 风速、风向信息
- 💧 湿度、气压、能见度
- ☀️ 天气状况描述
- 🎨 美观的命令行界面
- 🔄 自动重试机制
- ⚡ 快速响应

### 📚 完整文档
- 用户使用指南
- 开发文档
- 架构设计文档
- 测试报告
- 协作流程记录

---

## 🚀 快速开始

### 前置要求

- Python 3.7 或更高版本
- pip 包管理器
- WeatherAPI.com API Key（免费）

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/songleiwww/symphony.git
cd symphony
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **获取API Key**
   - 访问 [WeatherAPI.com](https://www.weatherapi.com/)
   - 注册免费账户
   - 在 Dashboard 获取 API Key

4. **配置API Key**
```bash
# 编辑 config.py 文件，填入你的API Key
API_KEY = "你的API_KEY"
```

5. **运行程序**
```bash
python weather_tool.py
```

---

## 🎮 娱乐模式（Entertainment Mode）

### 核心约定（2026-03-05确立）
- ✅ 不开发核心文件
- ✅ 不进行版本迭代
- ✅ 若发现Bug，修复测试后GitHub更新

### 游戏列表（v072-v085）
| 版本 | 游戏主题 | 参与模型数 |
|------|---------|-----------|
| v072 | 创意故事接龙 | 3位 |
| v073 | AI角色扮演派对 | 6位 |
| v074 | "星光熠熠"角色命名大赛 | 6位 |
| v075 | 游戏状态检查 | - |
| v076 | 真实模型调用游戏 | 6位 |
| v077 | 真实模型调用详细证据 | - |
| v078 | 简单真实模型测试 | - |
| v079 | 真实模型调用游戏（非模拟） | 6位 |
| v080 | AI模型奥运会（加入英伟达） | 9位 |
| v081 | "Token之谜"解答会 | 9位 |
| v082 | "智慧闪电战"（不商量） | 9位 |
| v083 | "头脑风暴议事会"（必须商量） | 9位 |
| v084 | "AI联合国大会" | 17位 |
| v085 | "智韵交响·星光盛典" | 17位 |

---

## 📁 项目文件

### 核心文件
| 文件 | 说明 |
|------|------|
| `symphony_core.py` | 交响核心（记忆系统集成） |
| `real_model_caller.py` | 真实模型调用器（v0.6.0开发） |
| `model_manager.py` | 模型管理器 |
| `config.py` | 17个模型配置 |

---

## 🔧 OpenClaw模型调用方式

### 常用命令
```bash
openclaw models list        # 列出所有可用模型
openclaw models set <model> # 设置默认模型
openclaw models status      # 查看模型状态
```

### 当前可用模型
| 模型 | 别名 | 说明 |
|------|------|------|
| `cherry-doubao/ark-code-latest` | Doubao Ark Code | 默认模型 |
| `cherry-minimax/MiniMax-M2.5` | MiniMax M2.5 | 回退#1 |
| `cherry-doubao/deepseek-v3.2` | DeepSeek V3.2 | 回退#2 |
| `cherry-doubao/doubao-seed-2.0-code` | Doubao Seed Code | 回退#3 |
| `cherry-doubao/glm-4.7` | GLM 4.7 | 回退#4 |
| `cherry-doubao/kimi-k2.5` | Kimi K2.5 | 回退#5 |

---

## 🎯 触发约定

- 消息开头两个字是"**交响**" → 启动交响模式
- 文案里有"**交响**"两个字 → 启动交响模式

---

**品牌标语**: "智韵交响，共创华章" 🎵