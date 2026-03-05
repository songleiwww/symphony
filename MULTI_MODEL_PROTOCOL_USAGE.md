# 多模型对话协议与协作系统
# Symphony Multi-Model Communication Protocol & Collaboration System

**版本**: 1.0.0  
**开发时间**: 2026-03-05

---

## 📋 目录

1. [系统概述](#系统概述)
2. [核心组件](#核心组件)
3. [对话约定协议](#对话约定协议)
4. [审计系统](#审计系统)
5. [工具协作框架](#工具协作框架)
6. [使用示例](#使用示例)
7. [模型注册](#模型注册)

---

## 🚀 系统概述

### 目标
- 定义我（编排器）与交响专家模型之间的对话规则
- 审计其他模型提供的信息
- 约定如何使用工具协作处理事件
- 开发模型自己使用工具的功能
- 提高多模型交互能力

### 核心功能
1. **对话约定协议** - 定义模型间对话规则
2. **审计系统** - 审计其他模型提供的信息
3. **工具协作框架** - 定义如何协作使用工具
4. **多模型通信协议** - 提高多模型交互能力

---

## 🏗️ 核心组件

### 1. AuditSystem（审计系统）
```python
audit_system = AuditSystem()

# 审计模型响应
result = audit_system.audit(
    content="模型响应内容",
    source_model="ark-code-latest",
    context={"required_keys": ["info", "source"]}
)
```

**审计维度**:
| 维度 | 权重 | 检查项 |
|------|------|--------|
| 准确性 | 30% | 事实核查、数据一致性、逻辑正确性 |
| 安全性 | 30% | 有害内容、隐私保护、合规性 |
| 完整性 | 20% | 信息完整、上下文清晰、满足需求 |
| 可靠性 | 20% | 来源可靠、证据充分、可验证 |

**审计级别**:
- PASS (≥0.8) - 通过
- WARNING (0.6-0.8) - 警告
- REVIEW (0.4-0.6) - 需要审核
- FAIL (<0.4) - 失败

### 2. ToolCollaborationFramework（工具协作框架）
```python
tool_framework = ToolCollaborationFramework()

# 检查工具权限
permission = tool_framework.can_use_tool("web_search", "ark-code-latest")

# 计划协作
plan = tool_framework.plan_collaboration(
    task="分析项目代码",
    available_models=[model1, model2, model3]
)
```

**工具分类**:
| 工具 | 需要审批 | 异步支持 |
|------|----------|----------|
| read | 否 | 否 |
| write | 否 | 否 |
| exec | 是 | 是 |
| web_search | 否 | 是 |
| web_fetch | 否 | 是 |
| message | 是 | 否 |

### 3. MultiModelProtocol（多模型通信协议）
```python
protocol = MultiModelProtocol(audit_system, tool_framework)

# 注册模型
protocol.register_model({
    "model_id": "ark-code-latest",
    "capabilities": ["analysis", "code"],
    "trust_level": 0.9,
    "tools_allowed": ["read", "write"]
})

# 发送消息（自动审计）
message = protocol.send_message(
    from_model="user",
    to_model="ark-code-latest",
    content="请分析这段代码",
    message_type="request"
)
```

### 4. SymphonyOrchestrator（主编排器）
```python
orchestrator = SymphonyOrchestrator()

# 处理用户请求
result = orchestrator.process_user_request("分析项目代码并生成报告")

# 审计模型响应
audit_result = orchestrator.audit_model_response(
    model_name="ark-code-latest",
    response="分析结果..."
)

# 请求工具使用
tool_result = orchestrator.request_tool_from_model(
    model_name="ark-code-latest",
    tool_name="web_search",
    params={"query": "相关信息"}
)
```

---

## 📝 对话约定协议

### 对话角色
| 角色 | 说明 |
|------|------|
| USER | 用户 |
| ORCHESTRATOR | 编排器（我） |
| EXPERT | 专家模型 |
| TOOL | 工具 |
| AUDITOR | 审计员 |
| VALIDATOR | 验证员 |

### 消息类型
| 类型 | 说明 |
|------|------|
| REQUEST | 请求 |
| RESPONSE | 响应 |
| AUDIT | 审计 |
| TOOL_CALL | 工具调用 |
| TOOL_RESULT | 工具结果 |
| COLLABORATION | 协作 |
| VALIDATION | 验证 |
| ERROR | 错误 |

### 对话流程
```
1. 用户发送请求
2. 编排器分析请求复杂度
3. 编排器计划协作（确定需要的模型和工具）
4. 注册模型到协议系统
5. 按计划调用模型
6. 每个模型响应都经过审计系统审计
7. 模型可以请求使用工具（需要审批）
8. 汇总结果，返回给用户
```

---

## 🔍 审计系统

### 审计规则
```python
audit_rules = {
    "accuracy_check": {
        "weight": 0.3,
        "checks": ["事实核查", "数据一致性", "逻辑正确性"]
    },
    "safety_check": {
        "weight": 0.3,
        "checks": ["有害内容检测", "隐私保护", "合规性"]
    },
    "completeness_check": {
        "weight": 0.2,
        "checks": ["信息是否完整", "上下文是否清晰", "是否满足需求"]
    },
    "reliability_check": {
        "weight": 0.2,
        "checks": ["来源可靠性", "证据充分性", "可验证性"]
    }
}
```

### 审计结果
```python
{
    "level": "pass",           # pass/warning/review/fail
    "score": 0.85,             # 0.0-1.0
    "issues": ["问题列表"],
    "recommendations": ["建议列表"],
    "verified_by": "AuditSystem",
    "timestamp": "2026-03-05T22:37:00"
}
```

---

## 🔧 工具协作框架

### 工具权限矩阵
| 模型 | read | write | exec | web_search | web_fetch | message |
|------|------|-------|------|------------|-----------|---------|
| ark-code-latest | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ |
| deepseek-v3.2 | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| doubao-seed-2.0-code | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| glm-4.7 | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| kimi-k2.5 | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| MiniMax-M2.5 | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

### 协作模式
```python
# 简单任务：单个模型
plan = {
    "task": "查询天气",
    "phases": [
        {"phase": 1, "action": "direct_execution", "model": "ark-code-latest", "tools": []}
    ]
}

# 中等任务：2个模型协作
plan = {
    "task": "分析数据",
    "phases": [
        {"phase": 1, "action": "research", "model": "deepseek-v3.2", "tools": ["web_search"]},
        {"phase": 2, "action": "execution", "model": "doubao-seed-2.0-code", "tools": ["read", "write"]}
    ]
}

# 复杂任务：3个以上模型协作
plan = {
    "task": "开发项目",
    "phases": [
        {"phase": 1, "action": "research", "model": "deepseek-v3.2", "tools": ["web_search", "web_fetch"]},
        {"phase": 2, "action": "analysis", "model": "kimi-k2.5", "tools": ["read"]},
        {"phase": 3, "action": "execution", "model": "doubao-seed-2.0-code", "tools": ["write", "exec"]}
    ]
}
```

---

## 💡 使用示例

### 示例1: 处理用户请求
```python
from multi_model_protocol import SymphonyOrchestrator

orchestrator = SymphonyOrchestrator()

# 处理复杂请求
result = orchestrator.process_user_request(
    "分析这个Python项目的代码结构，搜索相关资料，并生成报告"
)

print(f"需要的模型: {result['plan']['models_needed']}")
print(f"计划阶段: {len(result['plan']['phases'])}")
for phase in result['plan']['phases']:
    print(f"  阶段{phase['phase']}: {phase['action']} by {phase['model']}")
```

### 示例2: 审计模型响应
```python
# 审计专家模型的响应
audit_result = orchestrator.audit_model_response(
    model_name="ark-code-latest",
    response="根据分析，这个项目使用了模块化架构..."
)

print(f"审计级别: {audit_result.level}")
print(f"审计分数: {audit_result.score:.2f}")
if audit_result.issues:
    print(f"发现问题: {audit_result.issues}")
```

### 示例3: 请求使用工具
```python
# 模型请求使用工具
tool_result = orchestrator.request_tool_from_model(
    model_name="deepseek-v3.2",
    tool_name="web_search",
    params={"query": "Python best practices 2024"}
)

if tool_result['approved']:
    if tool_result.get('requires_user_approval'):
        print("需要用户审批才能使用工具")
    else:
        print("工具使用批准，可以执行")
else:
    print(f"工具使用被拒绝: {tool_result['reason']}")
```

---

## 📋 模型注册

### 模型信息结构
```python
model_info = {
    "model_id": "ark-code-latest",        # 模型ID
    "provider": "cherry-doubao",          # 提供商
    "alias": "Doubao Ark",               # 别名
    "capabilities": [                     # 能力
        "analysis",
        "architecture",
        "code"
    ],
    "trust_level": 0.9,                  # 信任级别 (0.0-1.0)
    "tools_allowed": [                    # 允许使用的工具
        "read",
        "write",
        "web_search",
        "web_fetch"
    ]
}
```

### 当前注册模型（6个）
| 模型 | 提供商 | 能力 | 信任级别 |
|------|--------|------|----------|
| ark-code-latest | cherry-doubao | analysis, architecture, code | 0.9 |
| deepseek-v3.2 | cherry-doubao | research, analysis, writing | 0.85 |
| doubao-seed-2.0-code | cherry-doubao | code, debug, optimization | 0.8 |
| glm-4.7 | cherry-doubao | analysis, reasoning, writing | 0.8 |
| kimi-k2.5 | cherry-doubao | analysis, long_context, reading | 0.85 |
| MiniMax-M2.5 | cherry-minimax | analysis, multimodal | 0.8 |

---

## 🎯 总结

### 系统优势
1. **自动化审计** - 所有模型响应都经过审计
2. **明确的工具权限** - 每个模型有明确的工具使用权限
3. **灵活的协作模式** - 根据任务复杂度自动选择协作模式
4. **完整的日志** - 记录所有对话和操作

### 下一步计划
- 集成真实模型调用
- 添加更多工具支持
- 实现异步协作
- 添加更多审计规则

---

**品牌标语**: "智韵交响，共创华章"
