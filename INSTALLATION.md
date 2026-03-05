# Symphony - OpenClaw 安装配置指南 | Installation & Configuration Guide

## 中文说明 | Chinese Documentation

### 📦 项目信息
- **项目名称（中文）**: 交响
- **项目名称（英文）**: Symphony
- **GitHub仓库**: https://github.com/songleiwww/symphony
- **本地路径**: `C:\Users\Administrator\.openclaw\workspace\multi_agent_demo`

---

## 🚀 在 OpenClaw 中安装和配置

### 方式1：作为本地项目使用（推荐）

#### 步骤1：确认项目位置
项目已经在你的 OpenClaw 工作空间中：
```
C:\Users\Administrator\.openclaw\workspace\multi_agent_demo\
```

#### 步骤2：进入项目目录
```bash
cd C:\Users\Administrator\.openclaw\workspace\multi_agent_demo
```

#### 步骤3：安装依赖（可选）
```bash
pip install -r requirements.txt
```

#### 步骤4：运行项目
```bash
# 运行待办事项工具
python main.py --help
python main.py add "我的任务" --priority high
python main.py list
python main.py stats

# 运行天气查询工具
python weather_tool.py

# 测试故障处理系统
python fault_tolerance_example.py
```

---

### 方式2：作为 OpenClaw 技能安装

#### 步骤1：复制到 skills 目录
```bash
# Windows
xcopy C:\Users\Administrator\.openclaw\workspace\multi_agent_demo C:\Users\Administrator\.openclaw\workspace\skills\symphony /E /I

# 或者使用 PowerShell
Copy-Item -Path "multi_agent_demo" -Destination "skills\symphony" -Recurse
```

#### 步骤2：在 OpenClaw 中使用
在对话中直接调用：
```
使用交响帮我创建一个待办事项
用 Symphony 查一下天气
```

---

## ⚙️ 配置说明

### 模型配置（config.py）

编辑 `config.py` 文件，配置你的模型：

```python
# 天气查询API Key（需要自己申请）
API_KEY = "YOUR_API_KEY_HERE"

# 模型配置
MODEL_CHAIN = [
    {
        "name": "primary_model",
        "api_key": "YOUR_API_KEY",  # 填入你的真实Key
        "base_url": "https://api.example.com/v1",
        # ...
    }
]
```

### ⚠️ 重要安全提醒

1. **永远不要把真实的 Key 上传到 GitHub**
2. **config.py 中的 Key 应该保持为占位符**
3. **只在本地使用时才填入真实 Key**
4. **发布前务必检查所有配置文件**

---

## 📁 项目文件说明

| 文件/目录 | 说明 |
|----------|------|
| `config.py` | 模型配置文件 |
| `model_manager.py` | 模型管理器 |
| `fault_tolerance.py` | 故障处理系统 |
| `todo/` | 待办事项工具 |
| `weather_tool.py` | 天气查询工具 |
| `README.md` | 项目主文档 |
| `INSTALLATION.md` | 本文件 - 安装配置指南 |
| `OPENCLAW_USAGE.md` | OpenClaw 使用指南 |

---

## 🔄 更新项目

### 从 GitHub 拉取最新更新
```bash
cd C:\Users\Administrator\.openclaw\workspace\multi_agent_demo
git pull origin master
```

### 推送本地更新到 GitHub
```bash
cd C:\Users\Administrator\.openclaw\workspace\multi_agent_demo
git add .
git commit -m "描述你的更新"
git push origin master
```

---

---

## English Documentation

### 📦 Project Info
- **Project Name (Chinese)**: 交响
- **Project Name (English)**: Symphony
- **GitHub Repository**: https://github.com/songleiwww/symphony
- **Local Path**: `C:\Users\Administrator\.openclaw\workspace\multi_agent_demo`

---

## 🚀 Install and Configure in OpenClaw

### Method 1: Use as Local Project (Recommended)

#### Step 1: Confirm Project Location
The project is already in your OpenClaw workspace:
```
C:\Users\Administrator\.openclaw\workspace\multi_agent_demo\
```

#### Step 2: Navigate to Project Directory
```bash
cd C:\Users\Administrator\.openclaw\workspace\multi_agent_demo
```

#### Step 3: Install Dependencies (Optional)
```bash
pip install -r requirements.txt
```

#### Step 4: Run the Project
```bash
# Run Todo Tool
python main.py --help
python main.py add "My Task" --priority high
python main.py list
python main.py stats

# Run Weather Tool
python weather_tool.py

# Test Fault Tolerance System
python fault_tolerance_example.py
```

---

### Method 2: Install as OpenClaw Skill

#### Step 1: Copy to skills Directory
```bash
# Windows
xcopy C:\Users\Administrator\.openclaw\workspace\multi_agent_demo C:\Users\Administrator\.openclaw\workspace\skills\symphony /E /I

# Or using PowerShell
Copy-Item -Path "multi_agent_demo" -Destination "skills\symphony" -Recurse
```

#### Step 2: Use in OpenClaw
Call directly in conversation:
```
Use Symphony to help me create a todo
Check the weather with Symphony
```

---

## ⚙️ Configuration

### Model Configuration (config.py)

Edit `config.py` to configure your models:

```python
# Weather API Key (need to apply for your own)
API_KEY = "YOUR_API_KEY_HERE"

# Model Configuration
MODEL_CHAIN = [
    {
        "name": "primary_model",
        "api_key": "YOUR_API_KEY",  # Fill in your real key
        "base_url": "https://api.example.com/v1",
        # ...
    }
]
```

### ⚠️ Important Security Notes

1. **Never upload real keys to GitHub**
2. **Keep keys as placeholders in config.py**
3. **Only fill in real keys for local use**
4. **Always check all config files before publishing**

---

## 📁 Project Files Reference

| File/Directory | Description |
|---------------|-------------|
| `config.py` | Model configuration file |
| `model_manager.py` | Model manager |
| `fault_tolerance.py` | Fault tolerance system |
| `todo/` | Todo management tool |
| `weather_tool.py` | Weather query tool |
| `README.md` | Main project documentation |
| `INSTALLATION.md` | This file - Installation guide |
| `OPENCLAW_USAGE.md` | OpenClaw usage guide |

---

## 🔄 Update Project

### Pull Latest Updates from GitHub
```bash
cd C:\Users\Administrator\.openclaw\workspace\multi_agent_demo
git pull origin master
```

### Push Local Updates to GitHub
```bash
cd C:\Users\Administrator\.openclaw\workspace\multi_agent_demo
git add .
git commit -m "Describe your update"
git push origin master
```

---

## 🎯 Naming Convention

- **For communication (Chinese)**: 交响
- **For code/English**: Symphony
- **GitHub repository**: songleiwww/symphony

---

*智韵交响，共创华章*
