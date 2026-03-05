# Symphony - OpenClaw 使用指南 | OpenClaw Usage Guide

## 中文说明 | Chinese Documentation

### 📦 项目信息
- **项目名称**: Symphony（交响）
- **GitHub仓库**: https://github.com/songleiwww/symphony-multi-agent
- **项目路径**: `C:\Users\Administrator\.openclaw\workspace\multi_agent_demo`

---

### 🚀 在OpenClaw中使用 Symphony

#### 方式1：作为本地项目使用

1. **进入项目目录**
```bash
cd C:\Users\Administrator\.openclaw\workspace\multi_agent_demo
```

2. **运行待办事项工具**
```bash
python main.py --help
python main.py add "我的任务" --priority high
python main.py list
python main.py stats
```

3. **运行天气查询工具**
```bash
python weather_tool.py
```

4. **测试故障处理系统**
```bash
python fault_tolerance_example.py
```

#### 方式2：作为OpenClaw技能集成

1. **将项目复制到skills目录**
```bash
# （可选）将项目作为技能安装
xcopy multi_agent_demo skills\symphony /E /I
```

2. **在OpenClaw中调用**
```
# 在对话中直接使用项目功能
使用 Symphony 帮我创建一个待办事项
```

---

### 📚 项目文件说明

| 文件 | 说明 |
|------|------|
| `config.py` | 模型配置文件（17个模型） |
| `model_manager.py` | 模型管理器 |
| `fault_tolerance.py` | 故障处理系统 |
| `todo/` | 待办事项工具 |
| `weather_tool.py` | 天气查询工具 |
| `README.md` | 项目主文档 |
| `OPENCLAW_USAGE.md` | 本文件 - OpenClaw使用指南 |

---

### ⚠️ 重要提醒

1. **不要上传真实的Key到GitHub**
   - `config.py` 中的Key应该保持为占位符
   - 本地使用时再填入真实Key

2. **项目更新**
   - 所有更新都推送到：https://github.com/songleiwww/symphony-multi-agent
   - 推送前务必检查敏感信息

---

---

## English Documentation

### 📦 Project Info
- **Project Name**: Symphony
- **GitHub Repository**: https://github.com/songleiwww/symphony-multi-agent
- **Project Path**: `C:\Users\Administrator\.openclaw\workspace\multi_agent_demo`

---

### 🚀 Using Symphony in OpenClaw

#### Method 1: Use as a Local Project

1. **Navigate to project directory**
```bash
cd C:\Users\Administrator\.openclaw\workspace\multi_agent_demo
```

2. **Run Todo Tool**
```bash
python main.py --help
python main.py add "My Task" --priority high
python main.py list
python main.py stats
```

3. **Run Weather Tool**
```bash
python weather_tool.py
```

4. **Test Fault Tolerance System**
```bash
python fault_tolerance_example.py
```

#### Method 2: Integrate as OpenClaw Skill

1. **Copy project to skills directory**
```bash
# (Optional) Install as a skill
xcopy multi_agent_demo skills\symphony /E /I
```

2. **Call from OpenClaw**
```
# Use project features directly in conversation
Use Symphony to help me create a todo
```

---

### 📚 Project Files Reference

| File | Description |
|------|-------------|
| `config.py` | Model configuration (17 models) |
| `model_manager.py` | Model manager |
| `fault_tolerance.py` | Fault tolerance system |
| `todo/` | Todo management tool |
| `weather_tool.py` | Weather query tool |
| `README.md` | Main project documentation |
| `OPENCLAW_USAGE.md` | This file - OpenClaw usage guide |

---

### ⚠️ Important Notes

1. **Never upload real keys to GitHub**
   - Keep keys as placeholders in `config.py`
   - Only fill in real keys for local use

2. **Project Updates**
   - All updates pushed to: https://github.com/songleiwww/symphony-multi-agent
   - Always check for sensitive info before pushing

---

---

## 永久记忆 | Permanent Memory

**项目-仓库对应关系**:
- 项目名称: Symphony（交响）
- 本地路径: `C:\Users\Administrator\.openclaw\workspace\multi_agent_demo`
- GitHub仓库: https://github.com/songleiwww/symphony-multi-agent
- 用途: 多模型协作系统演示

**安全规则**:
- ❌ 禁止上传真实Key、密码、Token到GitHub
- ✅ 发布前必须检查所有配置文件
- ✅ 保持 `config.py` 中的Key为占位符

**品牌标语**: 智韵交响，共创华章 | Symphony - Where AI Models Collaborate
