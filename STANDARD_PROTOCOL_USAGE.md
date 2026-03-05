# 标准化多模型协作协议
# Standardized Multi-Model Collaboration Protocol

**版本**: 1.0.0  
**开发时间**: 2026-03-05

---

## 🎯 核心原则（最重要！）

### 我的职责（只做这两件！）
1. **调度模型** - 选择合适的模型
2. **分析结果** - 读取JSON，分析结果

### 模型的职责（他们自己做！）
1. **使用工具** - 模型自己决定什么时候用工具
2. **执行任务** - 模型自己完成任务
3. **输出JSON** - 统一的JSON格式

### 统一格式（没有不同处理逻辑！）
- ✅ **只有JSON** - 没有其他格式
- ✅ **单一结构** - 所有输出结构相同
- ✅ **单一逻辑** - 我只有一套分析代码

---

## 📋 目录

1. [快速开始](#快速开始)
2. [标准化输入](#标准化输入)
3. [标准化输出](#标准化输出)
4. [工具使用](#工具使用)
5. [模型调度](#模型调度)
6. [结果分析](#结果分析)
7. [完整示例](#完整示例)

---

## 🚀 快速开始

### 3步流程（只有这3步！）

```python
from standard_protocol import StandardizedProtocol, TaskType

# 1. 创建协议
protocol = StandardizedProtocol()

# 2. 创建标准化输入
task_input = protocol.create_standardized_input(
    task_type=TaskType.RESEARCH.value,
    description="研究AI多模型协作的最佳实践"
)

# 3. 我调度模型，模型执行，我分析结果
selected_model = protocol.select_model(task_input)
analysis = protocol.analyze_result(output_file, task_input)
```

---

## 📥 标准化输入

### 输入结构（只有一种！）

```json
{
  "protocol_version": "1.0.0",
  "task_id": "task_1234567890",
  "task_type": "research",
  "task_description": "研究AI多模型协作的最佳实践",
  "required_capabilities": ["research", "analysis"],
  "expected_output": {
    "format": "JSON",
    "encoding": "UTF-8",
    "structure": {
      "summary": "string",
      "details": "dict",
      "conclusion": "string"
    }
  },
  "constraints": ["使用可靠来源", "提供证据"],
  "tools_allowed": ["read", "web_search", "web_fetch"],
  "max_iterations": 3
}
```

### 任务类型（8种）

| 类型 | 说明 |
|------|------|
| research | 研究/搜索 |
| analysis | 分析 |
| coding | 代码 |
| writing | 写作 |
| design | 设计 |
| debug | 调试 |
| optimization | 优化 |
| review | 评审 |

---

## 📤 标准化输出

### 输出结构（只有一种！）

```json
{
  "protocol_version": "1.0.0",
  "task_id": "task_1234567890",
  "model_id": "ark-code-latest",
  "status": "success",
  "result": {
    "summary": "研究完成，发现了3个最佳实践",
    "details": {
      "best_practices": ["分层架构", "标准化协议", "审计系统"]
    },
    "conclusion": "推荐使用标准化协议"
  },
  "tool_calls": [
    {
      "tool_name": "web_search",
      "parameters": {"query": "最佳实践"},
      "purpose": "查找相关文献"
    }
  ],
  "issues": [],
  "timestamp": "2026-03-05T23:00:00",
  "execution_time": 45.5,
  "token_usage": {
    "prompt": 1000,
    "completion": 500,
    "total": 1500
  }
}
```

### 状态值（3种）

| 状态 | 说明 |
|------|------|
| success | ✅ 成功 |
| partial | ⚠️ 部分完成 |
| failed | ❌ 失败 |

---

## 🔧 工具使用（模型自己做！）

### 模型自己请求工具

```python
# 模型决定使用工具（不是我！）
tool_request = ToolCallRequest(
    tool_name="web_search",
    parameters={"query": "最佳实践"},
    purpose="查找相关文献"
)
```

### 工具返回结果

```python
tool_result = ToolCallResult(
    tool_name="web_search",
    success=True,
    result=[...]
)
```

### 模型记录工具调用

```json
"tool_calls": [
  {
    "tool_name": "web_search",
    "parameters": {"query": "最佳实践"},
    "purpose": "查找相关文献"
  }
]
```

---

## 🎯 模型调度（我做！）

### 调度逻辑（单一逻辑！）

1. **不同provider优先**（防限流）
   - MiniMax-M2.5 (cherry-minimax) 优先
   - 然后是 cherry-doubao

2. **匹配任务类型**
   - 模型的 preferred_task_types

3. **匹配能力**
   - 模型的 capabilities

### 可用模型（6个）

| 模型 | 提供商 | 能力 | 偏好任务 |
|------|--------|------|----------|
| MiniMax-M2.5 | cherry-minimax | analysis, research | research, analysis |
| ark-code-latest | cherry-doubao | analysis, code | coding, design |
| deepseek-v3.2 | cherry-doubao | research, writing | research, writing |
| doubao-seed-2.0-code | cherry-doubao | code, debug | coding, debug |
| glm-4.7 | cherry-doubao | analysis, reasoning | analysis, writing |
| kimi-k2.5 | cherry-doubao | analysis, reading | analysis, review |

---

## 🔍 结果分析（我做！只有JSON！）

### 分析流程（单一逻辑！）

```python
# 只有这一套代码！
analysis = protocol.analyze_result(
    output_file="task_123_output.json",
    task_input=task_input
)
```

### 分析结果结构

```python
{
    "success": True,
    "model": "ark-code-latest",
    "status": "success",
    "result_summary": "研究完成...",
    "tool_calls": 2,
    "execution_time": 45.5,
    "token_usage": {"total": 1500},
    "analysis": "✅ 任务成功完成\n📝 结果摘要...\n🔧 使用了2个工具...",
    "raw_output": {...}  # 原始JSON
}
```

---

## 💡 完整示例

### 示例：研究任务

```python
from standard_protocol import StandardizedProtocol, TaskType
from pathlib import Path

# 1. 创建协议
protocol = StandardizedProtocol()

# 2. 创建标准化输入
task_input = protocol.create_standardized_input(
    task_type=TaskType.RESEARCH.value,
    description="研究AI多模型协作的最佳实践",
    required_capabilities=["research", "analysis"],
    constraints=["使用可靠来源", "提供证据"]
)

# 3. 选择模型
selected_model = protocol.select_model(task_input)
print(f"选择模型: {selected_model.alias}")

# 4. 保存输入（给模型）
test_dir = Path("test")
test_dir.mkdir(exist_ok=True)
input_path = protocol.save_input(task_input, test_dir)
print(f"输入文件: {input_path}")

# 5. 模型自己执行...（使用工具...）
# (这部分由模型自己完成)

# 6. 我分析结果（只有JSON！）
output_path = protocol.get_output_path(task_input, test_dir)
analysis = protocol.analyze_result(output_path, task_input)
print(f"分析: {analysis['analysis']}")
```

---

## ⚠️ 重要提醒

### 我只做这两件事！
1. ✅ 调度模型
2. ✅ 分析结果

### 模型自己做这三件事！
1. ✅ 使用工具
2. ✅ 执行任务
3. ✅ 输出JSON

### 只有一种格式！
1. ✅ 只有JSON
2. ✅ 只有一种结构
3. ✅ 只有一套处理逻辑

---

**品牌标语**: "智韵交响，共创华章"
