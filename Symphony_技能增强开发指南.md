# Symphony 技能增强开发指南

## 🎯 目标

使AI模型能够准确调用交响技能来调用真实模型，而不是自己模拟。

---

## ✅ 已完成的工作

### 1. Symphony Skill Wrapper (`symphony_skill_wrapper.py`)

**核心改进：**

- ✅ **Function Calling格式的工具定义** - AI模型可以通过标准Function Calling调用
- ✅ **`require_real_api`参数** - 强制要求真实API调用，禁止模拟
- ✅ **`execution_mode`标记** - 返回结果明确标记为`real_api`或`simulated`
- ✅ **参数强验证** - JSON Schema确保参数正确
- ✅ **完整的错误处理** - 清晰的错误信息

---

## 📋 如何让模型使用这个技能

### 方法1：在提示词中明确说明（推荐）

```
你可以使用以下工具：

【symphony_orchestrator】
这是一个调用真实AI模型进行多模型讨论的工具。

⚠️  重要规则：
1. 当用户要求"多模型讨论"、"交响"、"几个模型一起讨论"等时，必须使用此工具
2. 禁止自己模拟多个模型的发言，必须调用此工具
3. 调用时必须设置 require_real_api=true
4. 此工具会调用真实的模型API，不是模拟！

参数说明：
- topic: 讨论主题（必填）
- mode: 运行模式（discussion/brainstorm/dev_team/critique）
- num_models: 参与模型数量（3-10）
- require_real_api: 必须设置为true
```

---

### 方法2：提供Few-shot示例

```
示例1：
用户：用3个模型讨论一下人工智能的未来
正确做法：调用symphony_orchestrator工具
参数：{
  "topic": "人工智能的未来发展趋势",
  "mode": "discussion",
  "num_models": 3,
  "require_real_api": true
}

示例2：
用户：交响一下这个问题
正确做法：调用symphony_orchestrator工具
```

---

### 方法3：系统提示词约束

```
【强制规则】
- 任何涉及"多模型"、"交响"、"几个模型讨论"的请求，必须使用symphony_orchestrator工具
- 禁止自己模拟多个模型的对话
- 禁止在回复中说"让我模拟几个模型"等类似内容
- 必须调用真实的工具，使用真实的API
```

---

## 🔧 工具参数说明

```json
{
  "name": "symphony_orchestrator",
  "parameters": {
    "topic": "讨论主题，要具体明确",
    "mode": "运行模式",
    "enum": ["discussion", "brainstorm", "dev_team", "critique"],
    "num_models": "参与模型数量，3-10个",
    "require_real_api": "必须设置为true（禁止模拟）"
  }
}
```

### Mode说明

| Mode | 说明 |
|------|------|
| `discussion` | 多模型圆桌讨论（默认） |
| `brainstorm` | 多模型头脑风暴 |
| `dev_team` | 多模型开发团队协作 |
| `critique` | 多模型评论/反馈 |

---

## 📊 返回结果格式

```json
{
  "success": true,
  "topic": "讨论主题",
  "mode": "discussion",
  "num_models": 5,
  "execution_mode": "real_api",  // 关键：标记为真实API
  "results": [
    {
      "panelist": "战略分析师",
      "model": "cherry-doubao/deepseek-v3.2",
      "response": "..."
    }
  ],
  "output_file": "path/to/result.json"
}
```

---

## 🎯 关键改进点

### 1. 明确的工具定义
- AI模型清楚知道什么时候应该使用这个工具
- 参数有明确的类型和枚举约束

### 2. 禁止模拟的机制
- `require_real_api`参数强制设为true
- 返回结果明确标记`execution_mode: "real_api"`

### 3. 完整的验证
- JSON Schema参数验证
- 防止提示注入
- 安全的调用流程

---

## 🚀 使用示例

### 示例1：基本讨论

**用户输入：**
```
用3个模型讨论一下人工智能如何改变未来的工作方式
```

**AI应做：**
1. 调用`symphony_orchestrator`工具
2. 参数：
```json
{
  "topic": "人工智能如何改变未来的工作方式",
  "mode": "discussion",
  "num_models": 3,
  "require_real_api": true
}
```

---

### 示例2：交响模式

**用户输入：**
```
交响一下这个问题：如何提高编程效率
```

**AI应做：**
1. 调用`symphony_orchestrator`工具
2. 参数：
```json
{
  "topic": "如何提高编程效率",
  "mode": "brainstorm",
  "num_models": 5,
  "require_real_api": true
}
```

---

## ⚠️ 常见错误及避免

### ❌ 错误做法1：自己模拟

```
用户：用几个模型讨论一下
AI：好的，让我模拟一下...
模型1：...
模型2：...
```

### ✅ 正确做法

```
用户：用几个模型讨论一下
AI：[调用symphony_orchestrator工具]
```

---

### ❌ 错误做法2：忘记require_real_api

```json
{
  "topic": "...",
  "mode": "discussion",
  "num_models": 5
  // 缺少 require_real_api: true
}
```

### ✅ 正确做法

```json
{
  "topic": "...",
  "mode": "discussion",
  "num_models": 5,
  "require_real_api": true
}
```

---

## 📁 文件清单

| 文件 | 说明 |
|------|------|
| `symphony_skill_wrapper.py` | 交响技能封装器（新开发） |
| `Symphony_技能增强开发指南.md` | 本文档 |
| `real_model_caller.py` | 真实模型调用器（已有） |
| `skill_manager.py` | 技能管理器（已有） |

---

## 🎉 总结

**核心改进：**

1. ✅ 提供Function Calling格式的工具定义
2. ✅ 强制`require_real_api=true`禁止模拟
3. ✅ 返回结果明确标记`execution_mode`
4. ✅ 完整的参数验证和错误处理
5. ✅ 清晰的使用指南和示例

**效果：**
- AI模型知道何时使用交响技能
- AI模型不会自己模拟多个模型
- 确保调用的是真实的模型API

---

**智韵交响，共创华章！** 🎼
