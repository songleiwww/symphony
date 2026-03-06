# Symphony 技能

## 触发关键字

当用户消息包含以下关键字时，自动触发交响功能：

| 关键字 | 示例 |
|--------|------|
| `交响` | "使用交响"、"启动交响" |
| `symphony` | "run symphony"、"symphony讨论" |
| `交响工具` | "打开交响工具" |
| `多模型` | "多模型讨论"、"调用多个模型" |
| `模型开会` | "让模型开会"、"模型讨论" |

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
