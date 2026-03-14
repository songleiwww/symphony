# Symphony Active Trigger
# 开发者: 林思远 (触发规则设计师)
# 生成时间: 2026-03-08T02:14:20.667558
# 版本: 1.7.0

```json
{
  "triggerRules": [
    {
      "triggerType": "userQuery",
      "keywords": ["怎么", "为什么", "不懂"],
      "responsePriority": "P1",
      "description": "用户表达困惑，系统友好询问以提供帮助。"
    },
    {
      "triggerType": "failureCount",
      "maxFailures": 2,
      "responsePriority": "P1",
      "description": "用户连续2次尝试失败，系统友好询问以提供帮助。"
    },
    {
      "triggerType": "responseTime",
      "maxTime": 30,
      "responsePriority": "P2",
      "description": "用户长时间无响应，系统静默准备可能需要帮助。"
    },
    {
      "triggerType": "errorKeywords",
      "keywords": ["报错", "失败", "不行"],
      "responsePriority": "P0",
      "description": "用户输入错误关键词，系统立即响应以提供帮助。"
    },
    {
      "triggerType": "userHelpRequest",
      "keywords": ["帮帮我", "怎么办"],
      "responsePriority": "P0",
      "description": "用户明确求助，系统立即响应以提供帮助。"
    }
  ]
}
```