# 🎼 Symphony 统一调度器

> **智韵交响，共创华章**
>
> 一个完整的多模型协作和任务调度平台，整合模型管理器、故障处理系统、技能管理器和MCP协议

---

## 📋 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [核心概念](#核心概念)
- [使用指南](#使用指南)
- [API参考](#api参考)
- [配置说明](#配置说明)
- [示例演示](#示例演示)
- [架构设计](#架构设计)
- [常见问题](#常见问题)

---

## ✨ 功能特性

### 🤖 核心功能
- **统一任务调度** - 支持优先级、依赖关系的智能任务队列
- **技能管理** - 内置技能、自定义技能、MCP技能的统一管理
- **MCP协议集成** - 完整的 Model Context Protocol 支持
- **模型管理** - 整合现有的模型管理器和故障处理系统
- **容错机制** - 自动重试、熔断器、降级、故障转移
- **指标监控** - 完整的任务指标收集和监控

### 🎯 任务调度特性
- ✅ 优先级队列
- ✅ 任务依赖关系
- ✅ 自动重试机制
- ✅ 超时控制
- ✅ 状态跟踪
- ✅ 并行/顺序执行

### 🔧 技能系统
- ✅ 内置技能
- ✅ 自定义技能
- ✅ MCP工具集成
- ✅ 技能版本管理
- ✅ 参数验证

---

## 🚀 快速开始

### 前置要求

- Python 3.7 或更高版本
- 现有的 `model_manager.py` 和 `fault_tolerance.py`（可选）

### 基本使用

```python
from symphony_core import create_symphony

# 1. 创建 Symphony 实例
symphony = create_symphony(register_builtins=True)

try:
    # 2. 启动调度器
    symphony.start(num_workers=4)

    # 3. 提交任务
    task_id = symphony.submit_task(
        name="问候任务",
        skill_name="greet",
        parameters={"name": "Symphony"}
    )

    # 4. 等待任务完成
    import time
    time.sleep(1)

    # 5. 检查结果
    task = symphony.task_queue.get_task_status(task_id)
    print(f"结果: {task.result}")

finally:
    # 6. 停止调度器
    symphony.stop()
```

### 运行示例

```bash
# 运行完整演示
python symphony_example.py

# 或者只运行核心示例
python symphony_core.py
```

---

## 🧩 核心概念

### Task（任务）
任务是 Symphony 中的基本执行单元。每个任务包含：
- 名称和描述
- 要使用的技能或模型
- 参数
- 优先级
- 依赖关系
- 重试策略

### Skill（技能）
技能是可重用的功能模块。支持三种类型：
- **BUILTIN** - 内置技能
- **CUSTOM** - 用户自定义技能
- **MCP** - 通过MCP协议提供的工具

### SymphonyCore（调度核心）
整个系统的中央协调器，负责：
- 管理任务队列
- 调度工作线程
- 协调各组件
- 收集指标

---

## 📖 使用指南

### 1. 创建自定义技能

```python
from symphony_core import Skill, SkillType

# 定义技能函数
def my_skill(param1: str, param2: int = 0) -> dict:
    """
    我的自定义技能
    """
    return {
        "result": f"处理了 {param1}",
        "value": param2 * 2
    }

# 创建技能对象
skill = Skill(
    name="my_skill",
    skill_type=SkillType.CUSTOM,
    description="我的自定义技能",
    version="1.0.0",
    handler=my_skill,
    parameters_schema={
        "type": "object",
        "properties": {
            "param1": {"type": "string"},
            "param2": {"type": "integer", "default": 0}
        },
        "required": ["param1"]
    },
    tags=["example", "custom"]
)

# 注册技能
symphony.skill_manager.register_skill(skill)
```

### 2. 提交任务

#### 基本任务
```python
task_id = symphony.submit_task(
    name="简单任务",
    description="这是一个简单的任务",
    skill_name="greet",
    parameters={"name": "World"}
)
```

#### 带优先级的任务
```python
task_id = symphony.submit_task(
    name="紧急任务",
    skill_name="important_skill",
    parameters={...},
    priority=100  # 数字越大优先级越高
)
```

#### 有依赖的任务
```python
# 先提交任务A
task_a = symphony.submit_task(name="任务A", ...)

# 任务B依赖任务A完成
task_b = symphony.submit_task(
    name="任务B",
    ...,
    dependencies=[task_a]  # 只有任务A完成后才会执行
)
```

#### 带重试的任务
```python
task_id = symphony.submit_task(
    name="不稳定任务",
    skill_name="flaky_skill",
    ...,
    max_retries=5  # 失败时最多重试5次
)
```

### 3. 监控任务

```python
# 获取单个任务状态
task = symphony.task_queue.get_task_status(task_id)
print(f"状态: {task.status.value}")
print(f"结果: {task.result}")
print(f"错误: {task.error}")

# 列出所有任务
all_tasks = symphony.task_queue.list_tasks()

# 按状态筛选
pending_tasks = symphony.task_queue.list_tasks(TaskStatus.PENDING)
completed_tasks = symphony.task_queue.list_tasks(TaskStatus.COMPLETED)

# 获取系统状态
status = symphony.get_status()
print(f"总任务: {status['tasks']['total']}")
print(f"已完成: {status['tasks']['completed']}")

# 获取指标
metrics = symphony.get_metrics()
print(f"技能调用: {metrics['skill_calls']}")
print(f"平均耗时: {metrics['avg_task_duration']:.2f}s")
```

### 4. 使用MCP工具

```python
# 注册MCP服务器
symphony.mcp_manager.register_server(
    "filesystem",
    {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/"]
    }
)

# 连接服务器
symphony.mcp_manager.connect_server("filesystem")

# 获取工具列表
tools = symphony.mcp_manager.get_server_tools("filesystem")

# 调用工具
result = symphony.mcp_manager.call_tool(
    "read_file",
    {"path": "/tmp/test.txt"},
    server_name="filesystem"
)
```

---

## 🔌 API参考

### SymphonyCore

#### 构造函数
```python
SymphonyCore(config: Optional[Dict] = None, logger: Optional[Logger] = None)
```

#### 方法

##### start(num_workers: int = 4)
启动调度器。

**参数:**
- `num_workers`: 工作线程数量，默认4

##### stop()
停止调度器。

##### submit_task(...)
提交任务。

**参数:**
- `name`: 任务名称
- `description`: 任务描述（可选）
- `skill_name`: 技能名称（可选）
- `model_name`: 模型名称（可选）
- `parameters`: 参数字典（可选）
- `priority`: 优先级，默认0
- `max_retries`: 最大重试次数，默认3
- `dependencies`: 依赖的任务ID列表（可选）
- `tags`: 标签列表（可选）
- `metadata`: 元数据字典（可选）

**返回:** 任务ID字符串

##### get_status() -> Dict
获取系统状态。

**返回:** 状态字典

##### get_metrics() -> Dict
获取指标。

**返回:** 指标字典

##### register_builtin_skills()
注册内置技能。

### SkillManager

#### 方法

##### register_skill(skill: Skill) -> bool
注册技能。

##### get_skill(name: str) -> Optional[Skill]
获取技能。

##### list_skills(skill_type: Optional[SkillType] = None) -> List[Skill]
列出技能。

##### execute_skill(skill_name: str, **kwargs) -> Any
执行技能。

##### unregister_skill(name: str) -> bool
注销技能。

### TaskQueue

#### 方法

##### add_task(task: Task) -> bool
添加任务。

##### get_task(timeout: Optional[float] = None) -> Optional[Task]
获取任务。

##### complete_task(task_id: str, result: Any = None) -> bool
完成任务。

##### fail_task(task_id: str, error: str) -> bool
标记任务失败。

##### retry_task(task_id: str) -> bool
重试任务。

##### get_task_status(task_id: str) -> Optional[Task]
获取任务状态。

##### list_tasks(status: Optional[TaskStatus] = None) -> List[Task]
列出任务。

### MCPManager

#### 方法

##### register_server(server_name: str, config: Dict) -> bool
注册MCP服务器。

##### connect_server(server_name: str) -> bool
连接MCP服务器。

##### disconnect_server(server_name: str) -> bool
断开MCP服务器。

##### get_server_tools(server_name: str) -> List[MCPTool]
获取服务器工具。

##### call_tool(tool_name: str, arguments: Dict, server_name: str = "default") -> Any
调用工具。

##### list_servers() -> List[Dict]
列出所有服务器。

---

## ⚙️ 配置说明

在 `config.py` 中的 `SYMPHONY_CONFIG` 配置项：

```python
SYMPHONY_CONFIG = {
    # 工作线程数量
    "num_workers": 4,

    # 任务队列配置
    "task_queue": {
        "max_size": 1000,
        "default_priority": 0,
        "default_max_retries": 3
    },

    # 技能配置
    "skills": {
        "auto_register_builtins": True,
        "custom_skills_path": "./skills",
        "enabled_skills": ["greet", "calculate"]
    },

    # MCP配置
    "mcp": {
        "enabled": True,
        "servers": {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/"]
            }
        },
        "auto_connect": False
    },

    # 指标配置
    "metrics": {
        "enabled": True,
        "export_interval": 60,
        "export_path": "./metrics",
        "retention_days": 7
    },

    # 健康检查配置
    "health_check": {
        "enabled": True,
        "interval": 30,
        "check_skills": True,
        "check_models": True,
        "check_workers": True
    }
}
```

---

## 🎬 示例演示

### 运行完整示例

```bash
cd multi_agent_demo
python symphony_example.py
```

### 示例内容

`symphony_example.py` 包含6个完整示例：

1. **基本用法** - 创建调度器并提交简单任务
2. **自定义技能** - 注册和使用自定义技能
3. **任务依赖** - 创建有依赖关系的任务链
4. **优先级队列** - 演示不同优先级任务的执行顺序
5. **错误处理** - 展示错误处理和自动重试
6. **指标监控** - 查看系统指标和监控信息

### 快速测试

```python
# test_symphony.py
from symphony_core import create_symphony
import time

symphony = create_symphony()
symphony.start(num_workers=2)

# 提交任务
task_id = symphony.submit_task(
    name="测试",
    skill_name="greet",
    parameters={"name": "测试用户"}
)

print(f"任务已提交: {task_id}")

# 等待完成
time.sleep(1)

# 查看结果
task = symphony.task_queue.get_task_status(task_id)
print(f"结果: {task.result}")

symphony.stop()
```

---

## 🏗️ 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      Symphony Core                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────┐  │
│  │ Task Queue   │    │ Skill Manager│    │ MCP Manager │  │
│  │              │    │              │    │             │  │
│  │ - Priority   │    │ - Builtin    │    │ - Servers   │  │
│  │ - Dependencies│   │ - Custom     │    │ - Tools     │  │
│  │ - Retries    │    │ - MCP        │    │ - Calls     │  │
│  └──────────────┘    └──────────────┘    └─────────────┘  │
│         │                    │                    │          │
│         └────────────────────┼────────────────────┘          │
│                              │                               │
│  ┌───────────────────────────┴───────────────────────────┐  │
│  │                    Worker Pool                         │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │  │
│  │  │Worker 1 │ │Worker 2 │ │Worker 3 │ │Worker 4 │  │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                              │                               │
│  ┌───────────────────────────┴───────────────────────────┐  │
│  │                  Model / Fault Tolerance              │  │
│  │  (可选整合)                                            │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件

1. **SymphonyCore** - 中央协调器
2. **TaskQueue** - 任务队列（支持优先级和依赖）
3. **SkillManager** - 技能管理器
4. **MCPManager** - MCP协议管理器
5. **Worker Pool** - 工作线程池
6. **Metrics** - 指标收集

### 数据流程

```
用户提交任务
    ↓
TaskQueue（排队、排序）
    ↓
Worker（从队列获取）
    ↓
SkillManager / ModelManager（执行）
    ↓
返回结果 / 错误处理
    ↓
更新任务状态
    ↓
收集指标
```

---

## ❓ 常见问题

### Q: Symphony 和现有的 model_manager 有什么关系？

A: Symphony 可以独立使用，也可以整合现有的 model_manager 和 fault_tolerance 模块。如果这些模块可用，Symphony 会自动加载它们。

### Q: 如何处理长时间运行的任务？

A: 可以：
1. 增加任务的超时设置
2. 使用后台任务模式
3. 通过 task.status 定期检查进度

### Q: 支持分布式部署吗？

A: 当前版本是单机版本。分布式支持在计划中。

### Q: 如何添加自定义的任务处理器？

A: 可以注册自定义技能，或者继承 SymphonyCore 并重写 `_execute_custom_task` 方法。

### Q: MCP 工具如何使用？

A: 首先需要注册 MCP 服务器，连接后可以像普通技能一样使用 MCP 工具。

---

## 📚 更多资源

- [model_manager.py](./model_manager.py) - 模型管理器
- [fault_tolerance.py](./fault_tolerance.py) - 故障处理系统
- [symphony_example.py](./symphony_example.py) - 完整示例
- [config.py](./config.py) - 配置文件

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

<div align="center">

**如果这个项目对你有帮助，请给它一个 ⭐️**

**智韵交响，共创华章** 🎼

</div>
