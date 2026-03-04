# 待办事项管理工具 - 架构设计文档

## 1. 系统架构

### 1.1 整体架构
采用模块化设计，分为三层：
- **表现层**: 命令行接口（CLI）
- **业务逻辑层**: 任务管理核心逻辑
- **数据层**: JSON文件持久化

```
┌─────────────────────────────────────┐
│         CLI Interface Layer          │
│  (argparse, 命令解析, 用户交互)      │
└─────────────────────┬───────────────┘
                      │
┌─────────────────────▼───────────────┐
│      Business Logic Layer            │
│  (TaskManager, 任务CRUD, 业务规则)  │
└─────────────────────┬───────────────┘
                      │
┌─────────────────────▼───────────────┐
│        Data Access Layer             │
│  (Storage, JSON读写, 数据持久化)    │
└─────────────────────────────────────┘
```

## 2. 模块设计

### 2.1 核心模块

#### 模块1: `task.py` - 任务数据模型
**职责**: 定义Task类，封装任务属性和方法

```python
class Task:
    - id: int
    - title: str
    - description: str
    - priority: str (high/medium/low)
    - status: str (pending/in_progress/done)
    - created_at: datetime
    - due_date: Optional[datetime]
    - completed_at: Optional[datetime]

    + to_dict() -> dict
    + from_dict(data: dict) -> Task
    + mark_done()
    + is_overdue() -> bool
```

#### 模块2: `storage.py` - 数据存储
**职责**: 处理JSON文件的读写操作

```python
class Storage:
    - file_path: str

    + load() -> List[dict]
    + save(tasks: List[dict])
    + ensure_file_exists()
```

#### 模块3: `manager.py` - 任务管理器
**职责**: 业务逻辑核心，协调Task和Storage

```python
class TaskManager:
    - storage: Storage
    - tasks: List[Task]
    - next_id: int

    + add_task(title, description, priority, due_date) -> Task
    + get_task(task_id: int) -> Optional[Task]
    + update_task(task_id: int, **kwargs) -> bool
    + delete_task(task_id: int) -> bool
    + mark_done(task_id: int) -> bool
    + list_tasks(filter_str: Optional[str] = None) -> List[Task]
    + save()
    + load()
```

#### 模块4: `cli.py` - 命令行接口
**职责**: 解析命令行参数，调用TaskManager

```python
class CLI:
    - manager: TaskManager

    + run()
    + parse_args()
    + handle_add(args)
    + handle_list(args)
    + handle_edit(args)
    + handle_done(args)
    + handle_delete(args)
```

#### 模块5: `main.py` - 入口文件
**职责**: 程序入口点

```python
def main():
    cli = CLI()
    cli.run()
```

## 3. 数据结构

### 3.1 Task数据字典格式
```json
{
  "id": 1,
  "title": "购买 groceries",
  "description": "买牛奶和面包",
  "priority": "high",
  "status": "pending",
  "created_at": "2026-03-05T04:30:00",
  "due_date": "2026-03-10T00:00:00",
  "completed_at": null
}
```

### 3.2 数据文件结构
```json
{
  "version": "1.0",
  "next_id": 5,
  "tasks": [
    {...},
    {...}
  ]
}
```

## 4. 目录结构
```
multi_agent_demo/
├── todo/
│   ├── __init__.py
│   ├── task.py
│   ├── storage.py
│   ├── manager.py
│   └── cli.py
├── main.py
├── setup.py
├── README.md
└── 01_requirements.md
└── 02_architecture.md
```
