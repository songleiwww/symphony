# 完整标准化多模型协作协议
# Complete Standardized Multi-Model Collaboration Protocol

**版本**: 1.2.0  
**开发时间**: 2026-03-05

---

## 🎯 完整功能列表

### 6大核心系统

1. **规范系统** - 我给模型的规范灌输
2. **记忆同步系统** - 我和模型记忆同步
3. **工具验证系统** - 验证工具使用正确
4. **任务编排系统** - 任务安排 + 协作验证
5. **标记解析器** - 节省tokens语法
6. **完整协议** - 统一调度

---

## 📋 目录

1. [快速开始](#快速开始)
2. [规范系统](#规范系统)
3. [记忆同步系统](#记忆同步系统)
4. [工具验证系统](#工具验证系统)
5. [任务编排系统](#任务编排系统)
6. [完整协议](#完整协议)

---

## 🚀 快速开始

```python
from complete_protocol import CompleteProtocol

# 1. 创建完整协议
protocol = CompleteProtocol()

# 2. 给模型的完整提示词（规范+记忆）
full_prompt = protocol.get_full_prompt_for_model("ark-code-latest")

# 3. 使用各个系统
# - 规范系统: protocol.spec_system
# - 记忆系统: protocol.memory_system
# - 工具验证: protocol.tool_validation
# - 任务编排: protocol.task_orchestrator
```

---

## 📜 规范系统 - 我给模型的规范

### 功能
- 给模型灌输必须遵守的规范
- 按优先级排序
- 可添加自定义规范

### 默认规范（4个）

| 规范ID | 规范名 | 内容 | 优先级 |
|--------|--------|------|--------|
| spec_json_only | 只输出JSON | 所有输出必须是JSON格式 | 1 |
| spec_markers | 使用标记语法 | 使用S/W/E/I/T/R/C标记 | 2 |
| spec_tool_verify | 工具使用验证 | 使用工具后必须验证 | 3 |
| spec_collaboration | 协作规范 | 协作时保持友好 | 4 |

### 使用示例

```python
from complete_protocol import SpecificationSystem, ProtocolSpec

# 创建规范系统
spec_system = SpecificationSystem()

# 获取给模型的规范
specs = spec_system.get_spec_for_model("ark-code-latest")

# 获取规范提示词
prompt = spec_system.get_spec_prompt("ark-code-latest")
print(prompt)
```

### 输出示例

```
你必须遵守以下规范：
1. [1] 只输出JSON: 所有输出必须是JSON格式
2. [2] 使用标记语法: 使用S/W/E/I/T/R/C标记，分隔符用|
3. [3] 工具使用验证: 使用工具后必须验证工具使用是否正确
4. [4] 协作规范: 与其他模型协作时必须保持友好，尊重其他模型的输出
```

---

## 🧠 记忆同步系统 - 我和模型记忆同步

### 功能
- 我和模型共享记忆
- 记忆类型：fact（事实）、decision（决策）、context（上下文）
- 来源：me（我）、model（模型）、both（双方）
- 记忆验证

### 使用示例

```python
from complete_protocol import MemorySyncSystem, SharedMemory

# 创建记忆系统
memory_system = MemorySyncSystem()

# 添加记忆
memory = SharedMemory(
    memory_id="mem_001",
    memory_type="fact",
    memory_content="品牌标语是'智韵交响，共创华章'",
    source="both",
    created_by="me"
)
memory_system.add_memory(memory)

# 获取给模型的记忆
memories = memory_system.get_memories_for_model("ark-code-latest")

# 获取记忆提示词
prompt = memory_system.get_memory_prompt("ark-code-latest")
print(prompt)

# 验证记忆
memory_system.verify_memory("mem_001")
```

### 输出示例

```
共享记忆：
1. [fact] 品牌标语是'智韵交响，共创华章'
```

---

## 🔧 工具验证系统 - 验证工具使用正确

### 功能
- 验证模型工具使用是否正确
- 预定义验证规则
- 支持自定义规则

### 默认验证规则（3个）

| 工具名 | 验证规则 |
|--------|----------|
| web_search | 必须返回至少3个结果，每个有title/url/snippet |
| read | 必须返回文件内容，包含路径，内容不为空 |
| write | 必须确认文件已写入，包含路径和内容 |

### 使用示例

```python
from complete_protocol import ToolValidationSystem

# 创建工具验证系统
tool_validation = ToolValidationSystem()

# 验证工具使用
tool_result = {
    "results": [
        {"title": "最佳实践1", "url": "https://...", "snippet": "..."},
        {"title": "最佳实践2", "url": "https://...", "snippet": "..."},
        {"title": "最佳实践3", "url": "https://...", "snippet": "..."}
    ]
}
validation = tool_validation.validate_tool_call("web_search", tool_result)
print(validation)
```

### 输出示例

```python
{
    "valid": True,
    "passed": [
        "必须返回至少3个结果",
        "每个结果必须有title和url",
        "必须提供snippet"
    ],
    "issues": [],
    "rule_used": {...}
}
```

---

## 🎯 任务编排系统 - 任务安排 + 协作验证

### 功能
- 给模型安排任务
- 任务依赖管理
- 协作验证（确保协作正确）

### 使用示例

```python
from complete_protocol import TaskOrchestrator

# 创建任务编排器
orchestrator = TaskOrchestrator()

# 创建任务安排
assignment1 = orchestrator.create_assignment(
    task_description="研究AI多模型协作的最佳实践",
    assigned_to="ark-code-latest"
)
assignment2 = orchestrator.create_assignment(
    task_description="验证研究结果",
    assigned_to="deepseek-v3.2",
    depends_on=[assignment1.task_id]
)

# 创建协作验证
collab = orchestrator.create_collaboration(
    [assignment1, assignment2],
    rules=[
        "所有任务必须完成",
        "任务顺序正确",
        "输出格式正确"
    ]
)

# 验证协作
outputs = [
    {"task_id": assignment1.task_id, "status": "success"},
    {"task_id": assignment2.task_id, "status": "success"}
]
verification = orchestrator.verify_collaboration(collab.collaboration_id, outputs)
print(verification)
```

### 输出示例

```python
{
    "valid": True,
    "passed": [
        "所有任务都有输出",
        "任务1有status",
        "任务2有status",
        "没有任务失败"
    ],
    "issues": [],
    "collaboration": {...}
}
```

---

## 🏷️ 标记解析器 - 节省tokens语法

### 标记列表

| 标记 | 含义 |
|------|------|
| S | success（成功） |
| W | warning（警告） |
| E | error（错误） |
| I | info（信息） |
| T | tool_call（工具调用） |
| R | result（结果） |
| C | conclusion（结论） |
| V | verify（验证） |
| A | accept（接受） |

### 使用示例

```python
from complete_protocol import MarkerParser

# 解析标记
parsed = MarkerParser.parse_markers("S|T|R|V")
print(parsed)

# 创建标记
markers = MarkerParser.create_markers(
    status="success",
    has_tool=True,
    has_verify=True
)
print(markers)  # "S|T|V|R"
```

### 输出示例

```python
{
    "markers": ["success", "tool_call", "result", "verify"],
    "has_success": True,
    "has_verify": True,
    "has_accept": False,
    "has_tool_call": True
}
```

---

## 📦 完整协议 - 统一调度

### 使用示例

```python
from complete_protocol import CompleteProtocol

# 创建完整协议
protocol = CompleteProtocol()

# 获取给模型的完整提示词
full_prompt = protocol.get_full_prompt_for_model("ark-code-latest")
print(full_prompt)

# 使用各个系统
# 规范系统
specs = protocol.spec_system.get_spec_for_model("ark-code-latest")
# 记忆系统
memories = protocol.memory_system.get_memories_for_model("ark-code-latest")
# 工具验证
validation = protocol.tool_validation.validate_tool_call("web_search", result)
# 任务编排
assignment = protocol.task_orchestrator.create_assignment(...)

# 获取摘要
summary = protocol.get_summary()
print(summary)
```

### 输出示例

```python
{
    "version": "1.2.0",
    "specs": 4,
    "memories": 1,
    "tool_rules": 3,
    "assignments": 2,
    "collaborations": 1
}
```

---

## 💡 完整示例

```python
from complete_protocol import CompleteProtocol, SharedMemory

# 1. 创建完整协议
protocol = CompleteProtocol()

# 2. 添加共享记忆
memory = SharedMemory(
    memory_id="mem_001",
    memory_type="fact",
    memory_content="品牌标语是'智韵交响，共创华章'",
    source="both",
    created_by="me"
)
protocol.memory_system.add_memory(memory)

# 3. 获取给模型的完整提示词
full_prompt = protocol.get_full_prompt_for_model("ark-code-latest")
print("给模型的提示词：")
print(full_prompt)

# 4. 安排任务
assignment = protocol.task_orchestrator.create_assignment(
    task_description="研究AI多模型协作的最佳实践",
    assigned_to="ark-code-latest"
)
print(f"\n任务安排: {assignment.task_id}")

# 5. 获取摘要
summary = protocol.get_summary()
print(f"\n协议摘要: {summary}")
```

---

## ⚠️ 重要提醒

### 我做什么？
1. ✅ 给模型灌输规范
2. ✅ 和模型同步记忆
3. ✅ 给模型安排任务
4. ✅ 验证工具使用正确
5. ✅ 验证协作是否正确
6. ✅ 分析结果

### 模型做什么？
1. ✅ 遵守我给的规范
2. ✅ 使用共享记忆
3. ✅ 自己使用工具
4. ✅ 自己执行任务
5. ✅ 输出JSON + 标记
6. ✅ 与其他模型协作

---

**品牌标语**: "智韵交响，共创华章"
