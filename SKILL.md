# Symphony 技能

## 触发关键字（v2.0 优化版）

当用户消息包含以下关键字时，自动触发交响功能：

| 优先级 | 关键字 | 示例 |
|--------|--------|------|
| P0 | `交响`, `symphony` | "使用交响"、"启动symphony" |
| P0 | `交响工具` | "打开交响工具" |
| P1 | `讨论`, `开会`, `协作` | "模型讨论"、"让模型开会" |
| P1 | `多模型`, | "多模型 `多个模型`讨论"、"调用多个模型" |
| P1 | `专家会诊`, `头脑风暴` | "专家会诊"、"头脑风暴" |
| P2 | `模型开会`, `模型讨论` | "让模型开会讨论" |

### 智能意图识别

```python
TRIGGER_KEYWORDS = [
    # 核心词 (P0)
    "交响", "symphony", "交响工具",
    # 动作词 (P1)  
    "讨论", "开会", "协作", "头脑风暴", "辩论", "会诊",
    # 需求词 (P1)
    "多模型", "多个模型", "模型开会", "专家",
    # 英文 (P1)
    "discuss", "debate", "brainstorm", "meeting", "collab"
]

def should_activate(user_input: str) -> bool:
    text = user_input.lower()
    # 精确匹配
    if any(kw in text for kw in TRIGGER_KEYWORDS):
        return True
    # 模糊：包含2个以上"模型"
    if text.count("模型") >= 2 or text.count("model") >= 2:
        return True
    return False
```

## 功能说明

**Symphony** 是一个多模型协作工具，可以：

1. **头脑风暴(brainstorm)** - 多个模型针对主题贡献创意
2. **辩论(debate)** - 正反方模型进行观点交锋
3. **评估(evaluate)** - 多模型综合评估方案

## 使用方式

```
交响: 主题内容
模型: deepseek-ai/DeepSeek-R1-0528
模式: brainstorm
```

或简单模式：
```
交响讨论：如何提升产品用户体验
```

## 配置

- **模型**: deepseek-ai/DeepSeek-R1-0528 (ModelScope推理模型)
- **API**: https://api-inference.modelscope.cn/v1

## 技术实现

核心文件：
- `config.py` - 模型配置
- `brainstorm_panel_v2.py` - 主工具
- `smart_fallback_caller.py` - 智能调度器
- `passive_trigger_engine.py` - 被动触发引擎（新增）

## 被动触发功能（v2.0 新增）

**核心文件**: `passive_trigger_engine.py`

当用户消息匹配以下模式时，自动激活：

| 优先级 | 触发模式 | 示例 |
|--------|----------|------|
| P0 | `交响`开头/结尾 | "交响讨论..." |
| P1 | `动作词+冒号` | "讨论："、"开会：" |
| P1 | `让XX模型` | "让GPT和Claude讨论" |
| P2 | `多模型需求` | "多模型头脑风暴" |
| P3 | `英文动作` | "brainstorm: AI" |
| P4 | `智能推断` | "帮我分析这个方案" |

**测试结果**: 7/8 测试通过 ✅

## 使用示例

```python
from_panel_v2 import Brainstorm brainstormPanel

panel = BrainstormPanel()

头脑# 风暴
result = panel.discuss("AI未来发展趋势", mode="brainstorm", num_experts=3)

# 辩论
result = panel.discuss("AI是否会取代人类工作", mode="debate", num_experts=3)

# 评估
result = panel.discuss("推荐系统方案评估", mode="evaluate", num_experts=3)
```

---

**🎼 智韵交响，共创华章！**
