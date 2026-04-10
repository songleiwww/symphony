# 序境系统快速参考卡
> **袖珍版** — 5秒钟查找你需要的信息

---

## ⚡ 快速导入 (Copy-Paste)

```python
import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')

from Kernel import IntelligentStrategyScheduler, WisdomEmergenceEngine, EvolutionKernel
from providers.pool import ProviderPool
from strategy.dual_engine_scheduler import DualEngineScheduler, DualEngineConfig
```

---

## 📦 核心模块速查

| 需要的 | 导入语句 | 一句话说明 |
|-------|---------|-----------|
| 调度器 | `from Kernel import IntelligentStrategyScheduler` | 7种策略自动选择 |
| 智慧引擎 | `from Kernel import WisdomEmergenceEngine` | 多脑涌现 |
| 进化内核 | `from Kernel import EvolutionKernel` | 自进化核心 |
| 模型池 | `from providers.pool import ProviderPool` | 938模型统一封装 |
| 双引擎 | `from strategy.dual_engine_scheduler import DualEngineScheduler` | ACO+BCO混合 |
| 记忆层 | `from Kernel.evolution import AgentMemoryLayer` | 三层记忆 ⚠️ 文件编码损坏 |

---

## ❌ 常见错误（记住！）

| 错误写法 | 正确写法 |
|---------|---------|
| `symphony-release/` | `skills/symphony/` |
| `from failure_recovery.breaker` | `from providers.pool` (breaker已删除) |
| `from algorithms.ant_colony` | `from Kernel.intelligent_strategy_scheduler` (已整合) |
| `from Kernel.evolution import memory_system_v2` | `memory_system_v2` 不存在，已移除 |
| 固定5脑 | 多脑=自适应，1/2/3/5/7脑按需激活 |

---

## 🔧 快速调用

```python
# 1. 创建调度器
sched = IntelligentStrategyScheduler()

# 2. 获取模型池
pool = ProviderPool()

# 3. 查看状态
stats = pool.get_stats()
print(f"在线模型: {stats['online_models']}")

# 4. 双引擎调度
ds = DualEngineScheduler(DualEngineConfig(enable_aco=True, enable_bco=True))

# 5. 进化内核
kernel = EvolutionKernel()
```

---

## 📊 多脑激活规则

```
简单问答 → 1脑 (算法士)
普通任务 → 2-3脑 (算法士+秘书)
复杂任务 → 5脑 (全部能力)
超复杂   → 7脑+ (全部+扩展专家)
```

---

## 🔑 数据库路径

```
C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db
```

---

## 🛡️ 熔断器位置

**熔断器已内置于 `ProviderPool`**，不需要单独导入 `breaker.py`

```python
pool = ProviderPool()
# 自动熔断保护，无需额外配置
```

---

## 📁 目录结构速览

```
symphony/
├── Kernel/                    # 核心 (evolution_kernel, scheduler, ...)
├── providers/pool.py           # 613+模型
├── strategy/dual_engine_*.py   # 蜂蚁双引擎
├── config/                    # 配置 (tokens, db, ...)
├── rules/compliance_engine.py # 合规
├── test/integration_test.py   # 测试
├── docs/SELF_TRAINING.md      # 完整培训指南 ← 有问题看这里
└── docs/mindmap_architecture.py  # 架构图生成器
```

---

## 🚫 禁止事项

- ❌ `symphony-release/` 路径
- ❌ `symphony_db_backup/` 路径
- ❌ 修改 `backup/` 目录
- ❌ `openclaw gateway restart` (通知用户手动操作)

---

## 🆘 调试命令

```bash
# 测试导入
python -c "from Kernel import IntelligentStrategyScheduler; print('OK')"

# 运行测试
python test/integration_test.py

# 检查模型
python -c "from providers.pool import ProviderPool; p = ProviderPool(); print(p.get_stats())"
```

---

## 🔄 维护约定

**⚠️ 铁律：任何变动，立即修正！**

系统更新/模块变动后，**发现即修正**，不得拖延。

| 变动类型 | 必须修正的文档 |
|---------|--------------|
| 新增/删除文件 | SKILL.md、SELF_TRAINING.md、QUICKREF.md |
| 导入路径变化 | SKILL.md（导入语句）、SELF_TRAINING.md（API章节） |
| 新增功能 | integration_test.py（新增测试用例） |
| 架构调整 | mindmap_architecture.svg |

**修正优先级**：正确性 > 完整性 > 时效性

---

**版本**: v4.5.0 | **路径**: `skills/symphony/` | **维护**: 少府监
