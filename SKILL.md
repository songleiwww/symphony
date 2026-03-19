# 序境 (Symphony) - AI Agent调度系统

## 简介

序境是少府监的核心调度系统，负责协调AI模型进行信息搜集、学习和知识储备。基于唐朝官署制度设计，实现多模型智能调度。

---

## 目录结构

```
C:\Users\Administrator\.openclaw\workspace\skills\symphony\
├── SKILL.md                 # Skill部署说明
│
├── temp/                    # 临时文件目录 (可随时删除)
│
├── data/                    # 数据目录
│   ├── symphony.db          # 主数据库
│   ├── symphony_template.db # 数据库模板
│   └── call_log.json       # 调用日志
│
└── Kernel/                  # 内核程序
    ├── __init__.py         # 模块入口
    ├── kernel_loader.py    # 内核加载器
    ├── config_manager.py  # 配置管理器
    ├── dispatch_manager.py # 调度管理器
    ├── kernel_strategy.py # 内核策略
    ├── permission_manager.py # 权限管理
    ├── auto_init.py        # 自动初始化
    └── update_manager.py   # 更新管理
```

---

## 临时目录 (temp/)

**用途**: 存放临时文件、调试脚本、测试数据等

**特点**:
- 可随时手工删除
- 不影响核心功能
- 建议定期清理

---

## 数据库表结构

### 核心表

| 表名 | 数量 | 说明 |
|------|------|------|
| 官署表 | 6 | 6个官署 |
| 官署角色表 | 96 | 绑定模型配置 |
| 模型配置表 | 96 | 模型参数配置 |

---

## 锁定规则 (永久生效)

以下三表**禁止AI自行修改**：

- 官署表
- 官署角色表
- 模型配置表

如需修改，必须用户回答「確定」(繁体中文) 确认

---

## 默认配置

### 触发关键词
- "序境" = 呼叫陆念昭
- 任何调用序境系统的请求都由陆念昭处理

### 主对话官 (陆念昭)
- **官职**: 少府监
- **模型**: ark-code-latest
- **服务商**: 火山引擎
- **用途**: 所有用户输入的默认处理

### 备用对话官
- **苏云渺** - 工部尚书 - doubao-seed-2.0-code
