# 增强型多模型对话协议与协作系统
# Enhanced Multi-Model Communication Protocol & Collaboration System

**版本**: 2.0.0  
**开发时间**: 2026-03-05

---

## 📋 目录

1. [系统概述](#系统概述)
2. [核心组件](#核心组件)
3. [对话约定](#对话约定)
4. [智能调度](#智能调度)
5. [工具协作](#工具协作)
6. [审计系统](#审计系统)
7. [使用示例](#使用示例)

---

## 🚀 系统概述

### 目标
- 定义我（编排器）与交响专家模型之间的完整对话规则
- 审计其他模型提供的信息
- 约定如何使用工具协作处理事件
- 开发模型自己使用工具的功能
- 提高多模型交互能力

### 核心功能
1. **完整对话约定** - 8种消息类型，6种角色
2. **智能协作调度** - 根据任务复杂度自动调度
3. **工具协作框架** - 7个工具，权限管理
4. **增强审计系统** - 4维度审计
5. **模型自主工具请求** - 模型可以请求使用工具
6. **非同公司优先** - 防止API限流

---

## 🏗️ 核心组件

### 1. 消息类型（8种）
| 类型 | 说明 |
|------|------|
| REQUEST | 请求 |
| RESPONSE | 响应 |
| QUERY | 查询 |
| ANSWER | 回答 |
| AUDIT | 审计 |
| TOOL_REQUEST | 工具请求 |
| TOOL_CALL | 工具调用 |
| COLLABORATION | 协作 |

### 2. 对话角色（6种）
| 角色 | 说明 |
|------|------|
| USER | 用户 |
| ORCHESTRATOR | 编排器（我） |
| EXPERT | 专家模型 |
| TOOL | 工具 |
| AUDITOR | 审计员 |
| COORDINATOR | 协调员 |

### 3. 任务复杂度（5级）
| 复杂度 | 说明 | 需要模型数 |
|--------|------|-----------|
| TRIVIAL | 非常简单 | 1 |
| SIMPLE | 简单 | 1 |
| MEDIUM | 中等 | 2 |
| COMPLEX | 复杂 | 3 |
| VERY_COMPLEX | 非常复杂 | 4 |

---

## 🧠 智能调度

### 调度策略
1. **分析任务复杂度** - 自动识别任务难度
2. **计算所需模型数** - 根据复杂度确定
3. **推断所需能力** - 分析任务需要的技能
4. **选择模型** - 不同provider优先（防限流）
5. **创建协作计划** - 分阶段执行

### 模型选择算法
```python
# 策略：不同provider优先
1. 按provider分组
2. 轮流选择不同provider的模型
3. 优先选择信任级别高的
4. 确保不超出count数量
```

---

## 🔧 工具协作

### 可用工具（7个）
| 工具 | 需要审批 | 异步支持 |
|------|----------|----------|
| read | ❌ | ❌ |
| write | ✅ | ❌ |
| edit | ✅ | ❌ |
| exec | ✅ | ✅ |
| web_search | ❌ | ✅ |
| web_fetch | ❌ | ✅ |
| message | ✅ | ❌ |

### 工具请求流程
```
1. 模型发送工具请求
2. 系统检查权限
3. 需要审批→返回待审批状态
4. 不需要审批→直接执行
5. 用户批准→执行工具
```

---

## 🔍 审计系统

### 审计维度
| 维度 | 权重 | 检查项 |
|------|------|--------|
| 准确性 | 30% | 事实核查、数据一致性、逻辑正确性 |
| 安全性 | 30% | 有害内容、隐私保护、合规性 |
| 完整性 | 20% | 信息完整、上下文清晰 |
| 可靠性 | 20% | 来源可靠、证据充分 |

### 审计级别
- PASS (≥0.8) - 通过
- WARNING (0.6-0.8) - 警告
- REVIEW (0.4-0.6) - 需要审核
- FAIL (<0.4) - 失败

---

## 📋 对话约定

### 对话流程
```
用户请求
    ↓
编排器分析复杂度
    ↓
选择模型（不同provider优先）
    ↓
创建协作计划（分阶段）
    ↓
按阶段调用模型
    ↓
每个响应经过审计
    ↓
模型可以请求工具
    ↓
汇总结果返回用户
```

### 模型自主工具请求
```python
# 模型可以主动请求使用工具
result = protocol.request_tool(
    model_name="deepseek-v3.2",
    tool_name="web_search",
    params={"query": "相关信息"},
    reason="需要搜索最新资料"
)
```

---

## 💡 使用示例

### 示例1: 处理用户请求
```python
from enhanced_protocol import EnhancedOrchestrator

orchestrator = EnhancedOrchestrator()

# 处理复杂请求
result = orchestrator.process_request(
    "开发一个完整的Web应用系统"
)

print(f"复杂度: {result['plan']['complexity']}")
print(f"需要模型: {result['plan']['models_needed']}")
for phase in result['plan']['phases']:
    print(f"  阶段{phase['phase']}: {phase['action']} - {phase['model']}")
```

### 示例2: 审计模型响应
```python
audit = orchestrator.audit_response(
    "ark-code-latest",
    "根据分析，这个项目..."
)
print(f"审计级别: {audit.level}")
print(f"审计分数: {audit.score:.2f}")
```

### 示例3: 模型请求工具
```python
tool_result = orchestrator.request_tool(
    model_name="deepseek-v3.2",
    tool_name="web_search",
    params={"query": "最佳实践"},
    reason="需要搜索相关信息"
)

if tool_result['approved']:
    if tool_result.get('requires_user_approval'):
        print("需要用户审批")
    else:
        print("工具使用批准")
```

---

## 📊 模型优先级（防限流）

| 优先级 | 模型 | 提供商 | 同公司 |
|--------|------|--------|--------|
| 1 | MiniMax-M2.5 | cherry-minimax | ❌ 否 |
| 11 | ark-code-latest | cherry-doubao | ✅ 是 |
| 12 | deepseek-v3.2 | cherry-doubao | ✅ 是 |
| 13 | doubao-seed-2.0-code | cherry-doubao | ✅ 是 |
| 14 | glm-4.7 | cherry-doubao | ✅ 是 |
| 15 | kimi-k2.5 | cherry-doubao | ✅ 是 |

---

## 🎯 总结

### 系统优势
1. **智能调度** - 自动分析复杂度，选择合适的模型数量
2. **防止限流** - 不同provider优先，分散API调用
3. **完整审计** - 4维度审计，确保信息质量
4. **工具协作** - 模型可以请求使用工具
5. **灵活扩展** - 易于添加新模型和新工具

### 核心流程
```
用户请求 → 复杂度分析 → 模型选择 → 协作计划 → 执行 → 审计 → 工具 → 汇总
```

---

**品牌标语**: "智韵交响，共创华章"
