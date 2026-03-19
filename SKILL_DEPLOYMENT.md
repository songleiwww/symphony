# 序境系统 Skills 部署指南

## 概述

本文档梳理序境系统内核的Skills文件及其部署需求，确保正确指向和应用。

---

## 核心Skills文件清单

### 1. 接管技能 (takeover_skill.py)
- **位置**: `Kernel/skills/takeover_skill.py`
- **功能**: 关键词触发、用户信息转换、意图分析、序境标识
- **状态**: ✅ 已部署
- **触发关键词**: 23个（中英文）

### 2. 对话接管器 (dialog_takeover.py)
- **位置**: `Kernel/dialog_takeover.py`
- **功能**: 对话拦截、自动接管响应
- **状态**: ✅ 已集成

---

## 部署结构

```
symphony/
├── SKILL.md                    # Skill部署说明
├── SKILL_DEPLOYMENT.md         # 部署指南 (本文档)
├── Kernel/
│   ├── dialog_takeover.py      # 对话接管器
│   └── skills/
│       └── takeover_skill.py   # 接管技能
```

---

## 部署检查清单

| 项目 | 路径 | 状态 |
|------|------|------|
| 接管技能 | Kernel/skills/takeover_skill.py | ✅ |
| 对话接管器 | Kernel/dialog_takeover.py | ✅ |
| 数据库 | data/symphony.db | ✅ |
| 内核加载器 | Kernel/kernel_integration.py | ✅ |

---

## 正确应用方式

### 1. 导入接管器
```python
from skills.symphony.Kernel.dialog_takeover import intercept_message
```

### 2. 触发接管
```python
result = intercept_message("接管")
if result["taken_over"]:
    print(result["response"])
```

---

*最后更新: 2026-03-19*
