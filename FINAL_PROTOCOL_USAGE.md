# 最终标准化多模型协作协议
# Final Standardized Multi-Model Collaboration Protocol

**版本**: 1.3.0  
**开发时间**: 2026-03-05

---

## 🎯 完整功能列表

### 8大核心系统

| 系统 | 功能 |
|------|------|
| 1. **规范系统** | 我给模型的规范灌输 |
| 2. **记忆同步系统** | 我和模型记忆同步 |
| 3. **工具验证系统** | 验证工具使用正确 |
| 4. **任务编排系统** | 任务安排 + 协作验证 |
| 5. **标记解析器** | 节省tokens语法 |
| 6. **模型能力智能匹配** | 了解模型擅长什么，智能选择 |
| 7. **替补模型调度** | 模型异常时自动调度替补 |
| 8. **最终协议** | 统一调度所有系统 |

---

## 📋 目录

1. [快速开始](#快速开始)
2. [模型能力智能匹配](#模型能力智能匹配)
3. [替补模型调度](#替补模型调度)
4. [完整协议](#完整协议)

---

## 🚀 快速开始

```python
from final_protocol import FinalProtocol

# 1. 创建最终协议
protocol = FinalProtocol()

# 2. 模型能力智能匹配
selection = protocol.select_and_explain(
    required_capabilities=["research", "analysis"],
    task_type="research"
)
print(selection['explanation'])

# 3. 替补模型调度
result = protocol.scheduler.execute_with_fallback(
    task_id="task_001",
    required_capabilities=["research", "analysis"],
    task_type="research",
    execute_fn=my_execute_function
)
```

---

## 🧠 模型能力智能匹配系统

### 功能
- 详细的模型能力描述（7个维度评分）
- 任务类型偏好
- 可靠性、成功率、延迟指标
- 综合分数计算
- 智能选择最佳模型
- 不同provider优先（防限流）

### 模型能力评分（0-10）

| 维度 | 说明 |
|------|------|
| analysis_score | 分析能力 |
| coding_score | 编码能力 |
| research_score | 研究能力 |
| writing_score | 写作能力 |
| reasoning_score | 推理能力 |
| debugging_score | 调试能力 |
| design_score | 设计能力 |

### 默认模型能力（6个）

| 模型 | 提供商 | 擅长 | 核心能力 |
|------|--------|------|----------|
| MiniMax-M2.5 | cherry-minimax | 研究、分析 | 研究:10, 分析:9 |
| ark-code-latest | cherry-doubao | 代码、架构 | 编码:10, 设计:9 |
| deepseek-v3.2 | cherry-doubao | 研究、写作 | 写作:10, 研究:9 |
| doubao-seed-2.0-code | cherry-doubao | 代码、调试 | 编码:10, 调试:10 |
| glm-4.7 | cherry-doubao | 分析、推理 | 分析:10, 推理:10 |
| kimi-k2.5 | cherry-doubao | 分析、阅读 | 分析:9, 评审:10 |

### 使用示例

```python
from final_protocol import ModelCapabilityMatcher

# 创建匹配器
matcher = ModelCapabilityMatcher()

# 选择最佳模型
model = matcher.select_best_model(
    required_capabilities=["research", "analysis"],
    task_type="research"
)
print(f"选择模型: {model.alias}")

# 获取综合分数
score = model.get_overall_score(
    required_capabilities=["research", "analysis"],
    task_type="research"
)
print(f"综合分数: {score:.1f}")

# 解释选择原因
explanation = matcher.explain_selection(
    model,
    required_capabilities=["research", "analysis"],
    task_type="research"
)
print(explanation)
```

### 输出示例

```
选择模型: MiniMax (MiniMax-M2.5)
选择理由:
  - research能力: 10/10分
  - analysis能力: 9/10分
  - research任务偏好: 10/10分
  - 可靠性: 92%
  - 成功率: 95%
  - 平均延迟: 8.5秒
```

---

## 🔄 替补模型调度系统

### 功能
- 模型异常时自动调度替补
- 预设替补模型
- 自动重试（默认2次）
- 完整的执行历史
- 统计信息

### 替补模型配置

| 模型 | 预设替补 |
|------|----------|
| MiniMax-M2.5 | glm-4.7, kimi-k2.5 |
| ark-code-latest | doubao-seed-2.0-code, deepseek-v3.2 |
| deepseek-v3.2 | glm-4.7, MiniMax-M2.5 |
| doubao-seed-2.0-code | ark-code-latest, deepseek-v3.2 |
| glm-4.7 | kimi-k2.5, MiniMax-M2.5 |
| kimi-k2.5 | glm-4.7, deepseek-v3.2 |

### 使用示例

```python
from final_protocol import FinalProtocol

# 创建协议
protocol = FinalProtocol()

# 定义执行函数
def my_execute_function(model_id: str):
    """执行函数返回: (success, output, error)"""
    try:
        # 实际执行模型的代码
        result = call_model(model_id, task)
        return (True, result, None)
    except Exception as e:
        return (False, None, str(e))

# 执行任务（带替补调度）
result = protocol.scheduler.execute_with_fallback(
    task_id="task_001",
    required_capabilities=["research", "analysis"],
    task_type="research",
    execute_fn=my_execute_function
)

# 检查结果
print(f"模型: {result.model_id}")
print(f"成功: {result.success}")
print(f"使用替补: {result.used_backup}")
if result.used_backup:
    print(f"原模型: {result.original_model}")

# 获取统计
stats = protocol.scheduler.get_statistics()
print(f"总执行: {stats['total']}")
print(f"成功率: {stats['success_rate']:.0%}")
print(f"替补使用率: {stats['fallback_rate']:.0%}")
```

### 输出示例

```
[尝试1] 模型: MiniMax
  ❌ 失败: 模拟失败
[尝试2] 模型: GLM 4.7
  ✅ 成功！

执行结果:
  模型: glm-4.7
  成功: True
  使用替补: True
  原模型: MiniMax-M2.5

调度统计:
  总执行: 2
  成功率: 50%
  替补使用率: 50%
```

---

## 📦 完整协议 - 统一调度

### 使用示例

```python
from final_protocol import FinalProtocol

# 1. 创建最终协议
protocol = FinalProtocol()

# 2. 模型能力智能匹配
print("=== 模型选择 ===")
selection = protocol.select_and_explain(
    required_capabilities=["coding", "debugging"],
    task_type="coding"
)
if selection:
    print(selection['explanation'])

# 3. 替补模型调度
print("\n=== 任务执行 ===")

def mock_execute(model_id: str):
    """模拟执行"""
    if model_id == "ark-code-latest":
        return (False, None, "连接超时")
    return (True, {"code": "def hello(): print('hello')"}, None)

result = protocol.scheduler.execute_with_fallback(
    task_id="task_coding_001",
    required_capabilities=["coding", "debugging"],
    task_type="coding",
    execute_fn=mock_execute
)

print(f"\n结果:")
print(f"  模型: {result.model_id}")
print(f"  成功: {result.success}")
print(f"  使用替补: {result.used_backup}")

# 4. 获取摘要
print("\n=== 协议摘要 ===")
summary = protocol.get_summary()
print(summary)
```

---

## 💡 完整示例

```python
from final_protocol import FinalProtocol

# 1. 创建最终协议
protocol = FinalProtocol()

# 2. 场景：研究任务
print("=" * 60)
print("场景1: 研究任务")
print("=" * 60)

# 选择模型
research_selection = protocol.select_and_explain(
    required_capabilities=["research", "analysis"],
    task_type="research"
)
if research_selection:
    print(research_selection['explanation'])

# 3. 场景：代码任务
print("\n" + "=" * 60)
print("场景2: 代码任务")
print("=" * 60)

coding_selection = protocol.select_and_explain(
    required_capabilities=["coding", "debugging"],
    task_type="coding"
)
if coding_selection:
    print(coding_selection['explanation'])

# 4. 场景：替补调度演示
print("\n" + "=" * 60)
print("场景3: 替补调度")
print("=" * 60)

def demo_execute(model_id: str):
    """演示：第一个失败，第二个成功"""
    print(f"  尝试执行: {model_id}")
    if model_id == "MiniMax-M2.5":
        return (False, None, "API rate limit")
    return (True, {"result": "Success!"}, None)

result = protocol.scheduler.execute_with_fallback(
    task_id="demo_task_001",
    required_capabilities=["research", "analysis"],
    task_type="research",
    execute_fn=demo_execute
)

print(f"\n最终结果:")
print(f"  模型: {result.model_id}")
print(f"  成功: {result.success}")
print(f"  使用替补: {result.used_backup}")

# 5. 统计
print("\n" + "=" * 60)
print("统计信息")
print("=" * 60)
stats = protocol.scheduler.get_statistics()
print(f"总执行: {stats['total']}")
print(f"成功率: {stats.get('success_rate', 0):.0%}")
print(f"替补使用率: {stats.get('fallback_rate', 0):.0%}")
```

---

## ⚠️ 重要提醒

### 我做什么？
1. ✅ 给模型灌输规范
2. ✅ 和模型同步记忆
3. ✅ 了解模型擅长什么
4. ✅ 智能选择最佳模型
5. ✅ 给模型安排任务
6. ✅ 模型异常时调度替补
7. ✅ 验证工具使用正确
8. ✅ 验证协作是否正确
9. ✅ 分析结果

### 模型做什么？
1. ✅ 遵守我给的规范
2. ✅ 使用共享记忆
3. ✅ 自己使用工具
4. ✅ 自己执行任务
5. ✅ 输出JSON + 标记
6. ✅ 与其他模型协作

---

**品牌标语**: "智韵交响，共创华章"
