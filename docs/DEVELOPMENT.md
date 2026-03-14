# 📖 序境交响 - 开发文档

## 系统架构

```
symphony/
├── Kernel/           # 内核核心 (必需)
│   ├── kernel_loader.py
│   ├── dispatch_manager.py
│   ├── config_manager.py
│   └── kernel_strategy.py
│
├── data/            # 数据存储 (必需)
│   ├── symphony_template.db  # 模板
│   └── symphony.db            # 本地
│
├── core/            # 核心引擎 (可选)
│   ├── symphony_api.py
│   ├── model_call_manager.py
│   └── scheduler.py
│
├── scripts/         # 工具脚本
│   ├── init_api_keys.py
│   └── update_keys.py
│
└── docs/           # 文档
```

---

## 核心概念

### 1. 官署 (Office)

行政机构，共12个:

| ID | 名称 | 级别 |
|----|------|------|
| office_001 | 中书省 | 1级 |
| office_002 | 门下省 | 1级 |
| office_003 | 尚书省 | 1级 |
| office_004 | 枢密院 | 1级 |
| office_005 | 翰林院 | 2级 |
| office_006 | 工部 | 2级 |
| office_007 | 军器监 | 2级 |
| office_008 | 少府监 | 1级 |
| office_009 | 礼部 | 2级 |
| office_010 | 司天监 | 3级 |
| office_011 | 太医院 | 3级 |
| office_012 | 大理寺 | 2级 |

### 2. 官属 (Role)

人员角色，绑定官署和模型。

### 3. 模型 (Model)

AI模型，绑定服务商。

---

## 使用示例

### 初始化

```python
from skills.symphony.Kernel.kernel_loader import KernelLoader

kl = KernelLoader()
kl.load_all()

print(f"规则: {len(kl.rules)}")
print(f"官署: {len(kl.offices)}")
print(f"官属: {len(kl.roles)}")
```

### 调度

```python
from skills.symphony.Kernel.dispatch_manager import DispatchManager

dm = DispatchManager('data/symphony.db')
result = dm.dispatch('office_008', '推理模型')
```

---

## 内核规则

1. **现在时优先**: 只从symphony.db读取
2. **数据库唯一**: 不使用old/文件
3. **实时生效**: 修改立即生效
