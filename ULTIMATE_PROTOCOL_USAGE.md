# 终极标准化多模型协作协议
# Ultimate Standardized Multi-Model Collaboration Protocol

**版本**: 1.4.0  
**开发时间**: 2026-03-05

---

## 🎯 完整功能列表

### 9大核心系统

| 系统 | 功能 |
|------|------|
| 1. **规范系统** | 我给模型的规范灌输 |
| 2. **记忆同步系统** | 我和模型记忆同步 |
| 3. **工具验证系统** | 验证工具使用正确 |
| 4. **任务编排系统** | 任务安排 + 协作验证 |
| 5. **标记解析器** | 节省tokens语法 |
| 6. **模型能力智能匹配** | 了解模型擅长什么，智能选择 |
| 7. **替补模型调度** | 模型异常时自动调度替补 |
| 8. **我指定哪个模型干什么活** | 直接指定模型执行任务！ |
| 9. **终极协议** | 统一调度所有系统 |

---

## 📋 目录

1. [快速开始](#快速开始)
2. [我指定哪个模型干什么活](#我指定哪个模型干什么活)
3. [列出可用模型](#列出可用模型)
4. [完整协议](#完整协议)

---

## 🚀 快速开始

```python
from ultimate_protocol import UltimateProtocol

# 1. 创建终极协议
protocol = UltimateProtocol()

# 2. 我指定哪个模型干什么活！
result = protocol.create_and_execute_direct(
    task_description="写一篇关于AI的文章",
    assigned_model="deepseek-v3.2",  # 我指定！
    task_type="writing",
    execute_fn=my_execute_function,
    required_capabilities=["writing", "research"],
    notes="这是我直接指定的任务"
)

# 3. 检查结果
print(f"模型: {result.model_id}")
print(f"成功: {result.success}")
print(f"直接指定: {result.is_direct_assignment}")
```

---

## 🎯 我指定哪个模型干什么活！

### 核心功能
- 我直接指定模型执行任务
- 验证模型是否存在
- 支持任务备注
- 标记语法支持 "D" (direct)
- 完整的执行历史

### 使用示例

```python
from ultimate_protocol import UltimateProtocol

# 创建协议
protocol = UltimateProtocol()

# 定义执行函数
def my_execute_function(model_id: str):
    """执行函数返回: (success, output, error)"""
    try:
        # 实际执行模型的代码
        result = call_model(model_id, "你的任务")
        return (True, result, None)
    except Exception as e:
        return (False, None, str(e))

# 我指定哪个模型干什么活！
result = protocol.create_and_execute_direct(
    task_description="写一篇关于AI多模型协作的文章",
    assigned_model="deepseek-v3.2",  # 我指定！
    task_type="writing",
    execute_fn=my_execute_function,
    required_capabilities=["writing", "research"],
    notes="要用中文写，不少于500字"
)

# 检查结果
print(f"模型: {result.model_id}")
print(f"成功: {result.success}")
print(f"直接指定: {result.is_direct_assignment}")
print(f"标记: {result.markers}")

if result.success:
    print(f"输出: {result.output}")
else:
    print(f"错误: {result.error}")
```

### 输出示例

```
[直接指定] 模型: DeepSeek (deepseek-v3.2)
  任务: 写一篇关于AI多模型协作的文章
  备注: 要用中文写，不少于500字
  ✅ 成功！

执行结果:
  模型: deepseek-v3.2
  成功: True
  直接指定: True
  标记: S|D|R
```

---

## 📋 列出可用模型

### 功能
- 列出所有可用模型
- 显示模型别名和ID
- 方便我选择要指定的模型

### 使用示例

```python
from ultimate_protocol import UltimateProtocol

# 创建协议
protocol = UltimateProtocol()

# 列出所有可用模型
models = protocol.list_available_models()
print(f"共 {len(models)} 个模型:")
for m in models:
    print(f"  - {m['alias']} ({m['model_id']})")
    print(f"    提供商: {m['provider']}")
    print(f"    编码能力: {m['coding_score']}/10")
    print(f"    研究能力: {m['research_score']}/10")
```

### 输出示例

```
共 6 个模型:
  - MiniMax (MiniMax-M2.5)
    提供商: cherry-minimax
    编码能力: 6/10
    研究能力: 10/10
  - Doubao Ark (ark-code-latest)
    提供商: cherry-doubao
    编码能力: 10/10
    研究能力: 7/10
  - DeepSeek (deepseek-v3.2)
    提供商: cherry-doubao
    编码能力: 8/10
    研究能力: 9/10
  - Doubao Seed (doubao-seed-2.0-code)
    提供商: cherry-doubao
    编码能力: 10/10
    研究能力: 6/10
  - GLM 4.7 (glm-4.7)
    提供商: cherry-doubao
    编码能力: 7/10
    研究能力: 8/10
  - Kimi K2.5 (kimi-k2.5)
    提供商: cherry-doubao
    编码能力: 6/10
    研究能力: 7/10
```

---

## 📦 可用模型（6个）

| 模型 | 提供商 | 别名 | 擅长 |
|------|--------|------|------|
| MiniMax-M2.5 | cherry-minimax | MiniMax | 研究、分析 |
| ark-code-latest | cherry-doubao | Doubao Ark | 代码、架构 |
| deepseek-v3.2 | cherry-doubao | DeepSeek | 研究、写作 |
| doubao-seed-2.0-code | cherry-doubao | Doubao Seed | 代码、调试 |
| glm-4.7 | cherry-doubao | GLM 4.7 | 分析、推理 |
| kimi-k2.5 | cherry-doubao | Kimi K2.5 | 分析、阅读 |

---

## 💡 完整示例

```python
from ultimate_protocol import UltimateProtocol

# 1. 创建终极协议
protocol = UltimateProtocol()

# 2. 列出所有可用模型
print("=" * 60)
print("可用模型")
print("=" * 60)
models = protocol.list_available_models()
for m in models:
    print(f"{m['alias']} ({m['model_id']})")

# 3. 我指定 deepseek-v3.2 写文章
print("\n" + "=" * 60)
print("任务1: 指定 DeepSeek 写文章")
print("=" * 60)

def execute_writing(model_id: str):
    return (True, {"article": "AI多模型协作是未来的趋势..."}, None)

result1 = protocol.create_and_execute_direct(
    task_description="写一篇关于AI多模型协作的文章",
    assigned_model="deepseek-v3.2",  # 我指定！
    task_type="writing",
    execute_fn=execute_writing,
    required_capabilities=["writing", "research"],
    notes="要用中文写"
)

print(f"\n结果:")
print(f"  模型: {result1.model_id}")
print(f"  成功: {result1.success}")
print(f"  直接指定: {result1.is_direct_assignment}")

# 4. 我指定 ark-code-latest 写代码
print("\n" + "=" * 60)
print("任务2: 指定 Doubao Ark 写代码")
print("=" * 60)

def execute_coding(model_id: str):
    return (True, {"code": "def hello(): print('hello')"}, None)

result2 = protocol.create_and_execute_direct(
    task_description="写一个Python问候函数",
    assigned_model="ark-code-latest",  # 我指定！
    task_type="coding",
    execute_fn=execute_coding,
    required_capabilities=["coding", "debugging"],
    notes="代码要简洁"
)

print(f"\n结果:")
print(f"  模型: {result2.model_id}")
print(f"  成功: {result2.success}")
print(f"  直接指定: {result2.is_direct_assignment}")

# 5. 统计
print("\n" + "=" * 60)
print("统计信息")
print("=" * 60)
stats = protocol.direct_orchestrator.get_statistics()
print(f"总执行: {stats['total']}")
print(f"直接指定: {stats['direct_assignments']}")
print(f"成功率: {stats['success_rate']:.0%}")
```

---

## ⚠️ 重要提醒

### 我做什么？
1. ✅ 给模型灌输规范
2. ✅ 和模型同步记忆
3. ✅ 了解模型擅长什么
4. ✅ 智能选择最佳模型
5. ✅ **我指定哪个模型干什么活！**
6. ✅ 给模型安排任务
7. ✅ 模型异常时调度替补
8. ✅ 验证工具使用正确
9. ✅ 验证协作是否正确
10. ✅ 分析结果

### 模型做什么？
1. ✅ 遵守我给的规范
2. ✅ 使用共享记忆
3. ✅ 自己使用工具
4. ✅ 自己执行任务
5. ✅ 输出JSON + 标记
6. ✅ 与其他模型协作

---

**品牌标语**: "智韵交响，共创华章"
