# 序境踩坑记录
**记录所有发现的问题及修复，防止误判**

---

## ❌ PITFALL 1: multi_agent_orchestrator.py DB路径错误

**严重程度**: 🔴 高 - 导致多脑系统完全无法启动

**问题描述**:
```python
# 错误代码 (line 16)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/symphony.db")
# 计算结果: symphony/Kernel/data/symphony.db ❌ 不存在
```

**根因**: 路径层级计算错误，需要3层dirname到达symphony根目录

**修复方案**:
```python
SYM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(SYM_ROOT, "data", "symphony.db")
# 计算结果: symphony/data/symphony.db ✅ 存在
```

**涉及文件**: `Kernel/multi_agent/multi_agent_orchestrator.py`

**症状**: `sqlite3.OperationalError: unable to open database file`

**发现时间**: 2026-04-09

---

## ❌ PITFALL 2: ProviderPool 默认db_path=None

**严重程度**: 🟡 中 - 初始化警告

**问题描述**:
```python
def __init__(self, db_path: Optional[str] = None):
    self.db_path = db_path  # None → 后续加载失败
```

**修复方案**:
```python
def __init__(self, db_path: Optional[str] = None):
    self.db_path = db_path if db_path else DEFAULT_DB_PATH
```

**涉及文件**: `providers/pool.py`

**症状**: `ProviderPool` 初始化时警告，策略无法注册

**发现时间**: 2026-04-09

---

## ❌ PITFALL 3: IntelligentStrategyScheduler 策略未自动注册

**严重程度**: 🟡 中 - 策略为空

**问题描述**: `__init__` 时未注册任何默认策略

```python
def __init__(self, config):
    self.strategies = {}  # 空字典，无策略
```

**修复方案**: 初始化时注册7个默认策略

```python
def __init__(self, config):
    self.strategies = {}
    self._register_default_strategies()  # 注册全部7个策略
```

**涉及文件**: `Kernel/intelligent_strategy_scheduler.py`

**注册策略**: random, round_robin, least_loaded, predictive, aco_routing, bco_allocation, dual_engine

**发现时间**: 2026-04-09

---

## ❌ PITFALL 4: detect_then_team.py 编码损坏

**严重程度**: 🔴 高 - 文件完全无法导入

**问题描述**: 文件包含非UTF-8字符，导致 `SyntaxError: Non-UTF-8 code`

**症状**: `invalid character '��' (U+FF0C)`

**修复方案**: 完全重写文件，使用纯ASCII

**涉及文件**: `Kernel/multi_agent/detect_then_team.py`

**发现时间**: 2026-04-09

---

## ❌ PITFALL 5: symphony_scheduler max_tokens 参数

**严重程度**: 🟢 低 - 接口不匹配

**问题描述**: 用户调用 `symphony_scheduler(prompt, max_tokens=10)` 失败

**实际签名**: `(prompt: str, model_type: str = 'text', min_context_window: int = 2048) -> str`

**涉及文件**: `symphony_scheduler.py`

**发现时间**: 2026-04-09

---

## 📋 修复文件清单

| 文件 | 修复日期 | 状态 |
|------|----------|------|
| `Kernel/multi_agent/multi_agent_orchestrator.py` | 2026-04-09 | ✅ 已修复 |
| `Kernel/multi_agent/detect_then_team.py` | 2026-04-09 | ✅ 已修复 |
| `providers/pool.py` | 2026-04-09 | ✅ 已修复 |
| `Kernel/intelligent_strategy_scheduler.py` | 2026-04-09 | ✅ 已修复 |

---

## ⚠️ 已知未修复问题

| 文件 | 问题 | 状态 |
|------|------|------|
| `Kernel/self_healing/self_healing_monitor.py` | 编码损坏 IndentationError | ⏳ 待手动修复 |
| `Kernel/evolution/self_evolution_v2.py` | 编码损坏 SyntaxError | ⏳ 待手动修复 |
| `Kernel/agent_memory/agent_memory_layer.py` | 编码损坏 | ⏳ 待手动修复 |

---

**最后更新**: 2026-04-09 01:07
