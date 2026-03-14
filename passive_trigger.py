# Symphony Passive Trigger
# 开发者: 王明远 (被动触发架构师)
# 生成时间: 2026-03-08T02:14:20.668753
# 版本: 1.7.0

```json
{
  "passiveTrigger": {
    "enabled": true,
    "conditions": [
      {
        "type": "keywordMatch",
        "keywords": ["交响", "symphony", "讨论"],
        "description": "用户消息中包含与交响或讨论相关的关键词"
      },
      {
        "type": "taskAlignment",
        "description": "用户当前正在处理Symphony系统擅长的任务领域（如音乐创作、文本分析、逻辑推理等）"
      },
      {
        "type": "capabilityInquiry",
        "keywords": ["你能做什么", "有什么功能", "支持哪些", "能力范围", "擅长什么"],
        "description": "用户主动询问系统的能力或功能范围"
      }
    ],
    "responseStrategy": [
      {
        "type": "friendlyPrompt",
        "message": "我可以帮你...",
        "triggerOn": ["keywordMatch", "taskAlignment"]
      },
      {
        "type": "capabilityShowcase",
        "message": "我的能力包括音乐结构分析、创意文本生成、逻辑推理支持和跨领域知识整合，特别是在交响式思维模式下提供深度洞察。",
        "triggerOn": ["capabilityInquiry"]
      },
      {
        "type": "proactiveAsk",
        "message": "需要我用交响帮你讨论吗？",
        "triggerOn": ["keywordMatch", "taskAlignment"]
      }
    ],
    "activationLogic": "any", // 满足任意一个条件即可触发
    "cooldownSeconds": 30 // 防止频繁重复触发
  }
}
```