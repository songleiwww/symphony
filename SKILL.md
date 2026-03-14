# Symphony Skill - 序境交响

## 概述

序境内核系统，管理AI模型调度、官属角色、官署机构。

## 核心约束

1. **现在时优先** - 只从 `symphony.db` 读取配置
2. **数据库唯一** - 不使用 `old/` 任何文件
3. **实时生效** - 数据库修改立即生效

## 数据结构

| 表 | 说明 | 数量 |
|-----|------|------|
| 官署表 | 行政机构 | 12个 |
| 官属角色表 | 人员角色 | 65人 |
| 模型配置表 | AI模型 | 65个 |
| 内核规则表 | 核心规则 | 3条 |

## 使用方法

### 1. 加载内核配置

```python
from skills.symphony.Kernel.kernel_loader import KernelLoader

kl = KernelLoader()
kl.load_all()

# 获取数据
rules = kl.rules    # 内核规则
offices = kl.offices  # 官署
roles = kl.roles    # 官属
models = kl.models  # 模型
```

### 2. 调度官属

```python
from skills.symphony.Kernel.dispatch_manager import DispatchManager

dm = DispatchManager('path/to/symphony.db')

# 调度
result = dm.dispatch('office_008', '推理模型')
```

### 3. 获取统计

```python
from skills.symphony.Kernel.kernel_strategy import KernelStrategy

ks = KernelStrategy()
ks.initialize()
stats = ks.get_stats()
```

## 工具列表

| 工具 | 文件 | 说明 |
|------|------|------|
| kernel_loader | Kernel/kernel_loader.py | 加载配置 |
| dispatch | Kernel/dispatch_manager.py | 任务调度 |
| config | Kernel/config_manager.py | 配置管理 |
| strategy | Kernel/kernel_strategy.py | 策略引擎 |

## 约束

- ❌ 禁止使用 `old/` 任何文件
- ✅ 只从 `symphony.db` 读取
- ✅ 支持完全删除后重构
