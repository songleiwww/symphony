# 豆包API官方文档
# https://www.volcengine.com/docs/82379/1928261?lang=zh

# API端点
BASE_URL = "https://ark.cn-beijing.volces.com/api/coding/v3"

# 支持的模型
SUPPORTED_MODELS = [
    "ark-code-latest",      # 豆包代码模型
    "deepseek-v3.2",        # DeepSeek
    "glm-4.7",              # 智谱清言
    "kimi-k2.5",            # Moonshot
]

# 请求格式（OpenAI兼容）
# {
#   "model": "ark-code-latest",
#   "messages": [{"role": "user", "content": "你的问题"}],
#   "max_tokens": 1024,
#   "temperature": 0.7
# }

# 响应格式（OpenAI兼容）
# {
#   "choices": [
#     {
#       "message": {"role": "assistant", "content": "回答内容"},
#       "finish_reason": "stop"
#     }
#   ],
#   "usage": {"total_tokens": 100}
# }
