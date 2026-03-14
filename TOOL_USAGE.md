# 🎼 序境 Symphony 2.3.0 工具调用说明

## 📖 目录

1. [快速开始](#快速开始)
2. [核心模块](#核心模块)
3. [技能系统](#技能系统)
4. [调度协调](#调度协调)
5. [进化机制](#进化机制)
6. [配置说明](#配置说明)

---

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/songleiwww/symphony.git
cd symphony

# 安装依赖
pip install -r requirements.txt
```

### 基础使用

```python
from symphony_core import SymphonyCore

# 初始化系统
symphony = SymphonyCore()

# 提交任务
task_id = symphony.submit_task(
    task={"type": "test", "data": "hello"},
    priority=2,
    timeout=30.0
)

# 处理任务
result = symphony.process_task(task_id)

# 获取状态
status = symphony.get_status()
```

---

## 🔧 核心模块

### 1. SymphonyCore（交响核心）

```python
# 初始化
core = SymphonyCore()

# 核心方法
core.submit_task(task, priority, timeout)  # 提交任务
core.process_task(task_id)                   # 处理任务
core.get_status()                           # 获取状态
```

### 2. SkillManager（技能管理）

```python
from skill_manager import SkillManager

# 创建技能管理器
sm = SkillManager()

# 注册技能
sm.register_skill("read", handler)

# 激活技能
sm.activate_skill("read")

# 升级技能
sm.upgrade_skill("read")
```

### 3. Scheduler（调度器）

```python
from scheduler import Scheduler

# 创建调度器
scheduler = Scheduler()

# 添加任务
scheduler.add_task(task, priority=2)

# 获取下一任务
next_task = scheduler.get_next()
```

---

## ⚡ 技能系统

### 技能状态

| 状态 | 说明 |
|------|------|
| READY | 就绪 |
| ACTIVE | 激活 |
| COOLDOWN | 冷却中 |
| UPGRADING | 升级中 |

### 技能生命周期

```python
# 注册技能
skill_manager.register_skill("my_skill", handler)

# 激活（使用技能）
skill_manager.activate_skill("my_skill")

# 冷却（技能冷却）
skill_manager.cooldown_skill("my_skill")

# 升级（积累经验）
skill_manager.upgrade_skill("my_skill")
```

---

## 🎯 调度协调

### 优先级

```python
from enum import Enum

class Priority(Enum):
    LOW = 1      # 低
    NORMAL = 2   # 普通
    HIGH = 3     # 高
    URGENT = 4   # 紧急
```

### 超时管理

```python
# 提交任务时设置超时
task_id = core.submit_task(
    task={"type": "process"},
    timeout=30.0  # 30秒超时
)
```

---

## 🧬 进化机制

### 被动进化

```python
# 数据驱动自适应学习
evolution.collect_data(data)
evolution.learn(feedback)
```

### 主动进化

```python
# 智能感知→决策→执行
perceived = ai.perceive(input)
decision = ai.decide(perceived)
result = ai.execute(decision)
```

---

## ⚙️ 配置说明

### 配置文件结构

```python
SYMPHONY_CONFIG = {
    "version": "2.3.0",
    "api": {...},
    "members": [...],
    "scheduler": {...},
    "skills": {...},
    "evolution": {...}
}
```

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| SYMPHONY_API_KEY | API密钥 | - |
| SYMPHONY_LOG_LEVEL | 日志级别 | INFO |
| SYMPHONY_TIMEOUT | 默认超时 | 30 |

---

## 📝 错误处理

```python
from error_handler import ErrorHandler

eh = ErrorHandler()

try:
    result = process_task(task_id)
except Exception as e:
    error = eh.handle(e, {"task_id": task_id})
    print(error)
```

---

## 🔗 相关链接

- GitHub: https://github.com/songleiwww/symphony
- 问题反馈: https://github.com/songleiwww/symphony/issues

---

**🎼 智韵交响，共创华章 - Symphony 2.3.0**
