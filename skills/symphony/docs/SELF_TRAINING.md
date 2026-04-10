# 序境系统自主培训指南
> **目标**: 让宿主、其他AI模型/引擎、以及交交自己，都能正确使用序境系统

---

## 📋 目录

1. [系统概述](#1-系统概述)
2. [正确路径规范](#2-正确路径规范)
3. [模块导入规范](#3-模块导入规范)
4. [API调用模式](#4-api调用模式)
5. [多脑调度规则](#5-多脑调度规则)
6. [数据库规范](#6-数据库规范)
7. [常见错误与修复](#7-常见错误与修复)
8. [宿主操作指南](#8-宿主操作指南)

---

## 1. 系统概述

**序境系统 (Xujing) v4.5.0** 是多脑协作调度引擎：

| 指标 | 值 |
|------|-----|
| 版本 | v4.5.0 |
| 模型数量 | 613+ |
| 核心文件数 | 25+ |
| 调度算法 | ACO + BCO + 5种基础策略 |
| Benchmark | ACO 98%, BCO 96%, 77.9×加速 |

### 核心能力

- **多脑自适应**: 根据任务复杂度，动态激活 1/2/3/5/7 个能力脑
- **跨服务商调度**: 统一调度智谱AI、英伟达、硅基流动、阿里百炼
- **故障自愈**: 熔断、降级、重试三位一体
- **自进化**: 基于执行反馈持续优化调度策略

---

## 2. 正确路径规范

### ✅ 唯一正确路径

```
C:\Users\Administrator\.openclaw\workspace\skills\symphony\
```

### ❌ 禁止使用的路径

| 错误路径 | 原因 |
|---------|------|
| `symphony-release/` | 旧版本，已废弃 |
| `symphony_release/` | 下划线格式，禁止 |
| `symphony-db-backup/` | 备份目录，只读 |
| `symphony-release-backup-2026-03-29/` | 临时备份，禁止使用 |
| `symphony_db_backup/` | 同上 |

### ⚠️ 路径使用规则

1. **所有文件操作**必须使用 `skills/symphony/` 路径
2. **所有导入**必须基于 `skills/symphony/` 作为根目录
3. **禁止修改** `backup/` 目录下的任何文件
4. **禁止在** `WORKSPACE/archive/` 目录下进行开发

---

## 3. 模块导入规范

### 核心模块导入 (Python)

```python
import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')

# ✅ 正确方式
from Kernel import (
    IntelligentStrategyScheduler,  # 智能策略调度器
    WisdomEmergenceEngine,          # 智慧涌现引擎
    EvolutionKernel,                # 进化内核
    AdaptiveAlgorithmCoordinator    # 自适应算法协调器
)
from providers.pool import ProviderPool  # 服务商资源池
from strategy.dual_engine_scheduler import DualEngineScheduler, DualEngineConfig
# 注意: SelfEvolutionV2 和 AgentMemoryLayer 当前文件编码损坏
# from Kernel.evolution import SelfEvolutionV2, AgentMemoryLayer

# ❌ 错误方式
from symphony_release.Kernel import ...           # 错误路径
from failure_recovery.breaker import ...           # breaker.py 已删除
from algorithms.ant_colony import ...              # algorithms/ 已删除
```

### 可用模块清单

| 模块路径 | 类/函数 | 用途 |
|---------|--------|------|
| `Kernel` | `IntelligentStrategyScheduler` | 智能策略调度 |
| `Kernel` | `WisdomEmergenceEngine` | 智慧涌现 |
| `Kernel` | `EvolutionKernel` | 进化内核 |
| `Kernel` | `AdaptiveAlgorithmCoordinator` | 自适应协调 |
| `Kernel.evolution` | `SelfEvolutionV2` | 自进化引擎 ⚠️ 文件编码损坏 |
| `Kernel.evolution` | `AgentMemoryLayer` | 记忆层 ⚠️ 文件编码损坏 |
| `providers.pool` | `ProviderPool` | 938模型统一封装 |
| `strategy.dual_engine_scheduler` | `DualEngineScheduler` | 蜂蚁双引擎 |
| `rules.compliance_engine` | `ComplianceEngine` | 合规引擎 |

---

## 4. API调用模式

### 模式一：直接调度 (推荐)

```python
from Kernel import IntelligentStrategyScheduler

sched = IntelligentStrategyScheduler()
result = sched.schedule(task_text="你的问题", model_preference="balanced")
```

### 模式二：ProviderPool 直接调用

```python
from providers.pool import ProviderPool

pool = ProviderPool()
response = pool.chat(
    model_name="Qwen2.5-32B-Instruct",
    messages=[{"role": "user", "content": "问题"}],
    provider="zhipu"
)
```

### 模式三：双引擎调度

```python
from strategy.dual_engine_scheduler import (
    DualEngineScheduler,
    DualEngineConfig,
    ACOConfig,
    BCOConfig
)

config = DualEngineConfig(
    enable_aco=True,
    enable_bco=True,
    enable_heterogeneity=True
)
sched = DualEngineScheduler(config)
result = await sched.schedule(task, models)
```

### 模式四：多脑协作 (复杂任务)

```python
from Kernel.evolution_kernel import PentaBrainSystemV2

brain = PentaBrainSystemV2()
result = await brain.execute(
    task="复杂分析任务",
    brain_count=5,  # 动态指定脑数
    strategy="dual_engine"
)
```

---

## 5. 多脑调度规则

### 核心原则

**多脑 = 自适应 N 脑，不是固定 5 脑**

| 任务类型 | 激活脑数 | 典型组合 |
|---------|---------|---------|
| 简单问答 | 1脑 | 算法士（加权轮询） |
| 普通任务 | 2-3脑 | 算法士 + 秘书 |
| 复杂任务 | 5脑 | 算法士 + 秘书 + 战略官 + 档案官 + 测试官 |
| 超复杂任务 | 7脑+ | 全部能力 + 扩展专家 |

### 五脑能力定义

| 能力脑 | 职责 | 核心模块 |
|-------|------|---------|
| 算法士 | 调度策略选择，ACO/BCO路由 | `IntelligentStrategyScheduler` |
| 秘书 | 任务分解，进度跟踪，结果汇总 | `EvolutionKernel` |
| 战略官 | 长期规划，风险评估，决策优化 | `MilitaryStrategyAdvisor` |
| 档案官 | 记忆存储，知识检索，经验复用 | `AgentMemoryLayer` |
| 测试官 | 结果验证，质量评估，反馈收集 | `AdaptiveAlgorithmCoordinator` |

### 调度策略选择

```python
# 7种策略，系统自动选择
strategies = [
    "random",           # 随机调度
    "round_robin",      # 轮询调度
    "least_loaded",     # 最小负载
    "predictive",       # 预测调度
    "aco_routing",      # 蚁群路由
    "bco_allocation",   # 蜂群分配
    "dual_engine"       # 蚁群+蜂群混合
]
```

---

## 6. 数据库规范

### 数据库路径

```
C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db
```

### 表结构

| 表名 | 用途 |
|-----|------|
| `model_config` | 模型配置 (API密钥、参数) |
| `execution_log` | 执行日志 |
| `model_stats` | 模型统计 |
| `调度历史` | 调度记录 |

### 访问规则

- **只读操作**: 可直接查询
- **写操作**: 通过 `ProviderPool` 或 `EvolutionKernel` 的API
- **直接SQL**: 仅用于调试，禁止在生产代码中使用

---

## 7. 常见错误与修复

### 错误1: ImportError - 模块不存在

**错误信息**:
```
ModuleNotFoundError: No module named 'symphony_release.Kernel'
```

**原因**: 使用了错误的路径

**修复**:
```python
# ❌ 错误
sys.path.insert(0, '.../symphony_release')

# ✅ 正确
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
```

### 错误2: ImportError - breaker.py 不存在

**错误信息**:
```
ModuleNotFoundError: No module named 'failure_recovery.breaker'
```

**原因**: `breaker.py` 已被删除，功能整合到 `providers/pool.py`

**修复**:
```python
# ❌ 错误
from failure_recovery.breaker import CircuitBreaker

# ✅ 正确 - 使用 ProviderPool 的内置熔断
from providers.pool import ProviderPool
pool = ProviderPool()
# CircuitBreaker 已内置在 ProviderPool 中
```

### 错误3: 循环导入

**错误信息**:
```
ImportError: cannot import name 'memory_system_v2' from partially initialized module 'evolution'
```

**原因**: `evolution/__init__.py` 引用了不存在的模块

**修复**: 使用更新后的 `evolution/__init__.py`，它只导入实际存在的模块

### 错误4: WeightedEnsemble 未定义

**错误信息**:
```
NameError: name 'WeightedEnsemble' is not defined
```

**原因**: `swarm_intelligence` 不可用时缺少 fallback

**修复**: `AdaptiveAlgorithmCoordinator` 已添加 fallback 定义

### 错误5: 数据库路径错误

**错误信息**:
```
sqlite3.OperationalError: unable to open database
```

**修复**:
```python
DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
```

---

## 8. 宿主操作指南

### 启动系统

```bash
cd C:\Users\Administrator\.openclaw\workspace\skills\symphony
python -c "from Kernel import EvolutionKernel; k = EvolutionKernel(); print('序境系统就绪')"
```

### 运行测试

```bash
cd C:\Users\Administrator\.openclaw\workspace\skills\symphony
python test/integration_test.py
```

### 检查模型状态

```python
from providers.pool import ProviderPool
pool = ProviderPool()
stats = pool.get_stats()
print(f"在线模型: {stats['online_models']}")
print(f"总模型: {stats['total_models']}")
```

### 查看调度日志

```bash
# 日志目录
ls C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\
```

### 重启注意事项

- ❌ **禁止**使用 `openclaw gateway restart` / `stop`
- ✅ **必须**通知用户手动操作重启

---

## 📝 快速检查清单

使用序境系统前，请确认：

- [ ] 路径以 `skills/symphony/` 开头
- [ ] 导入了实际存在的模块
- [ ] 数据库路径正确
- [ ] 没有使用已删除的模块 (breaker.py, algorithms/, 等)
- [ ] 遵守"多脑自适应"原则（不是固定5脑）

---

---

## 🔄 维护约定

**⚠️ 铁律：任何变动，立即修正！不得拖延！**

系统更新/模块变动后，**发现即修正**，不得拖延。

| 变动类型 | 必须修正的文档 | 时限 |
|---------|--------------|------|
| 新增/删除文件 | SKILL.md、SELF_TRAINING.md、QUICKREF.md | 立即 |
| 导入路径变化 | SKILL.md、SELF_TRAINING.md | 立即 |
| 新增功能 | integration_test.py（新增测试用例） | 立即 |
| 架构调整 | mindmap_architecture.svg | 立即 |

**修正原则**：正确性第一，任何路径/导入错误都必须立即修正。

**最后更新**: 2026-04-10
**版本**: v4.5.0
**维护者**: 少府监 · 陆念昭
