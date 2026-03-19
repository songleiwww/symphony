# 序境内核说明

## 内核目录

```
Kernel/
├── __init__.py           # 模块入口
├── kernel_loader.py       # 内核加载器
├── config_manager.py     # 配置管理器
├── dispatch_manager.py   # 调度管理器
├── kernel_strategy.py    # 内核策略
├── permission_manager.py # 权限管理
├── auto_init.py          # 自动初始化
└── update_manager.py     # 更新管理
```

## 核心模块

### kernel_loader.py
从 symphony.db 加载配置：
- 规则 (内核规则表)
- 官署 (官署表)
- 官署角色 (官署角色表)
- 模型 (模型配置表)

### dispatch_manager.py
智能调度核心：
- 根据官署ID分发任务
- 绑定官署角色与模型配置
- 返回模型API调用参数

### kernel_strategy.py
策略引擎：
- 数据库验证
- 数据加载
- 内核文件生成

---

## 数据流向

```
官署表 (6)
    ↓
官署角色表 (96) ← 模型配置表_ID
    ↓
模型配置表 (96)
```

---

## 锁定规则

以下表**禁止AI自行修改**：
- 官署表
- 官署角色表
- 模型配置表

修改需用户确认「確定」(繁体)
