# 信息排队优先级系统
# Priority Queue System

**版本**: 1.0.0  
**开发时间**: 2026-03-05

---

## 🎯 核心功能

| 功能 | 说明 |
|------|------|
| 1. **任务排队** | 添加任务到队列 |
| 2. **优先级管理** | 5级优先级（1-5，1最高） |
| 3. **混合调度** | 优先级 + FIFO混合 |
| 4. **状态跟踪** | pending/running/completed/failed/cancelled |
| 5. **统计信息** | 完整的统计和历史 |

---

## 📋 目录

1. [快速开始](#快速开始)
2. [优先级说明](#优先级说明)
3. [任务状态](#任务状态)
4. [使用示例](#使用示例)

---

## 🚀 快速开始

```python
from priority_queue_system import PriorityQueueSystem

# 1. 创建排队系统
queue_system = PriorityQueueSystem()

# 2. 添加任务
queue_system.add_task(
    task_description="紧急：修复生产环境bug",
    priority=1,  # 1=最高优先级
    task_type="debug"
)

queue_system.add_task(
    task_description="普通：写文档",
    priority=3,  # 3=普通（默认）
    task_type="writing"
)

# 3. 执行任务（按优先级）
while True:
    task = queue_system.get_next_task()
    if not task:
        break
    
    # 执行任务...
    success, result, error = execute_my_task(task)
    
    if success:
        queue_system.complete_task(task.task_id, result)
    else:
        queue_system.fail_task(task.task_id, error)

# 4. 查看统计
stats = queue_system.get_statistics()
print(f"总任务: {stats['total']}")
print(f"成功率: {stats['success_rate']:.0%}")
```

---

## 🏷️ 优先级说明（5级）

| 优先级 | 值 | 名称 | 说明 | 使用场景 |
|--------|----|------|------|----------|
| CRITICAL | 1 | 紧急 | 最高优先级 | 生产环境故障、安全问题 |
| HIGH | 2 | 高 | 高优先级 | 重要功能开发、客户需求 |
| NORMAL | 3 | 普通 | 默认优先级 | 日常任务、文档编写 |
| LOW | 4 | 低 | 低优先级 | 清理、优化 |
| BACKGROUND | 5 | 后台 | 后台任务 | 备份、归档、统计 |

### 调度策略
1. **优先级高的先执行**
2. **相同优先级按FIFO**（先进先出）

---

## 📊 任务状态

| 状态 | 说明 |
|------|------|
| pending | 等待中 |
| running | 运行中 |
| completed | 已完成 |
| failed | 失败 |
| cancelled | 已取消 |

---

## 💡 使用示例

### 示例1：基本使用

```python
from priority_queue_system import PriorityQueueSystem

# 创建排队系统
queue_system = PriorityQueueSystem()

# 添加任务
queue_system.add_task(
    task_description="紧急：修复生产环境bug",
    priority=1,
    task_type="debug"
)

queue_system.add_task(
    task_description="高优先级：开发新功能",
    priority=2,
    task_type="coding"
)

queue_system.add_task(
    task_description="普通：写文档",
    priority=3,
    task_type="writing"
)

# 查看队列状态
status = queue_system.get_queue_status()
print(f"队列长度: {status['queue_length']}")
print(f"等待任务: {status['pending_count']}")

# 执行任务
def mock_execute(task):
    import time
    time.sleep(0.3)
    return (True, {"result": "done"}, None)

while True:
    task = queue_system.get_next_task()
    if not task:
        break
    
    success, result, error = mock_execute(task)
    
    if success:
        queue_system.complete_task(task.task_id, result)
    else:
        queue_system.fail_task(task.task_id, error)

# 查看统计
stats = queue_system.get_statistics()
print(f"总任务: {stats['total']}")
print(f"已完成: {stats['completed']}")
print(f"成功率: {stats['success_rate']:.0%}")
```

### 示例2：取消任务

```python
from priority_queue_system import PriorityQueueSystem

queue_system = PriorityQueueSystem()

# 添加任务
task1 = queue_system.add_task("任务1", priority=3)
task2 = queue_system.add_task("任务2", priority=2)

# 取消任务
queue_system.cancel_task(task1.task_id)

# 查看队列状态
status = queue_system.get_queue_status()
print(f"队列长度: {status['queue_length']}")  # 应该是1
```

### 示例3：查看统计

```python
from priority_queue_system import PriorityQueueSystem

queue_system = PriorityQueueSystem()

# 添加并执行一些任务...

# 获取统计
stats = queue_system.get_statistics()

print("=== 统计信息 ===")
print(f"总任务: {stats['total']}")
print(f"已完成: {stats['completed']}")
print(f"失败: {stats['failed']}")
print(f"已取消: {stats['cancelled']}")
print(f"成功率: {stats['success_rate']:.0%}")
print(f"平均耗时: {stats['average_execution_time']:.2f}秒")

print("\n=== 按优先级 ===")
for p_name, p_stats in stats['by_priority'].items():
    print(f"{p_name}:")
    print(f"  总数: {p_stats['total']}")
    print(f"  完成: {p_stats['completed']}")
    print(f"  成功率: {p_stats['success_rate']:.0%}")
```

### 示例4：查看队列状态

```python
from priority_queue_system import PriorityQueueSystem

queue_system = PriorityQueueSystem()

# 添加一些任务...

# 获取队列状态
status = queue_system.get_queue_status()

print("=== 队列状态 ===")
print(f"队列长度: {status['queue_length']}")
print(f"等待任务: {status['pending_count']}")

if status['current_task']:
    print(f"\n当前任务:")
    print(f"  ID: {status['current_task']['task_id']}")
    print(f"  描述: {status['current_task']['task_description']}")
    print(f"  优先级: {status['current_task']['priority_name']}")

print(f"\n等待任务（前10个）:")
for task in status['pending_tasks']:
    print(f"  [{task['priority_name']}] {task['task_description']}")

print(f"\n按优先级:")
for p_name, count in status['by_priority'].items():
    if count > 0:
        print(f"  {p_name}: {count}个")
```

---

## 📊 API参考

### PriorityQueueSystem

#### `add_task(task_description, priority=3, task_type="general", metadata=None)`
添加任务到队列

**参数：**
- `task_description`: 任务描述
- `priority`: 优先级（1-5，默认3）
- `task_type`: 任务类型
- `metadata`: 附加元数据

**返回：** `QueuedTask` 对象

---

#### `get_next_task()`
获取下一个要执行的任务

**返回：** `QueuedTask` 对象或 `None`

---

#### `complete_task(task_id, result=None)`
完成任务

**参数：**
- `task_id`: 任务ID
- `result`: 任务结果

**返回：** `bool`

---

#### `fail_task(task_id, error)`
任务失败

**参数：**
- `task_id`: 任务ID
- `error`: 错误信息

**返回：** `bool`

---

#### `cancel_task(task_id)`
取消任务

**参数：**
- `task_id`: 任务ID

**返回：** `bool`

---

#### `get_queue_status()`
获取队列状态

**返回：** `Dict`

---

#### `get_statistics()`
获取统计信息

**返回：** `Dict`

---

#### `list_all_tasks(limit=20)`
列出所有任务（最近的）

**参数：**
- `limit`: 返回数量限制（默认20）

**返回：** `List[Dict]`

---

**品牌标语**: "智韵交响，共创华章"
