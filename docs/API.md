# Symphony API 文档

**版本** v3.6.0
**更新日期** 2026-03-08

---

## 一、配置模块 (config.py)

### MODEL_CHAIN

模型配置链，包含17个可用模型。

**参数说明**

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| name | str | 模型内部名称 |
| provider | str | 提供商（zhipu/modelscope/nvidia） |
| model_id | str | 模型ID |
| base_url | str | API端点 |
| api_key | str | API密钥 |
| priority | int | 优先级（1最高） |
| enabled | bool | 是否启用 |

**使用示例**

```python
from config import MODEL_CHAIN
for model in MODEL_CHAIN:
    print(model["name"], model["alias"])
```

---

## 二、重试管理器 (retry_manager.py)

### RetryManager

指数退避重试机制。

**方法**

| 方法 | 参数 | 返回值 | 说明 |
| --- | --- | --- | --- |
| `execute_with_retry(func, *args)` | func, args | Any | 带重试执行函数 |

**配置**

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| max_retries | 3 | 最大重试次数 |
| base_delay | 1.0 | 基础延迟（秒） |
| max_delay | 60.0 | 最大延迟（秒） |

---

## 三、超时优化器 (timeout_optimizer.py)

### TimeoutOptimizer

动态超时调整机制。

**方法**

| 方法 | 参数 | 返回值 | 说明 |
| --- | --- | --- | --- |
| `get_timeout()` | 无 | float | 获取当前超时值 |
| `record_success(duration)` | duration | None | 记录成功调用 |
| `record_failure()` | 无 | None | 记录失败调用 |

---

## 四、健康检查器 (health_checker.py)

### HealthChecker

模型健康状态监控。

**方法**

| 方法 | 参数 | 返回值 | 说明 |
| --- | --- | --- | --- |
| `check_health(model_name)` | model_name | dict | 检查模型健康 |
| `get_health_status()` | 无 | dict | 获取整体状态 |

**返回值**

```json
{
    "status": "healthy",
    "last_check": "2026-03-08T10:00:00",
    "success_rate": 0.95
}
```

---

## 五、内容过滤器 (content_filter.py)

### ContentFilter

内容安全过滤。

**方法**

| 方法 | 参数 | 返回值 | 说明 |
| --- | --- | --- | --- |
| `check(content)` | content | ContentType | 检查内容类型 |
| `filter(content)` | content | str | 过滤敏感内容 |

**ContentType枚举**

| 值 | 说明 |
| --- | --- |
| SAFE | 安全内容 |
| WARNING | 警告内容 |
| DANGEROUS | 危险内容 |
| UNKNOWN | 未知内容 |

---

## 六、记忆系统 (memory_layers.py)

### MemorySystem

四层记忆架构。

**方法**

| 方法 | 参数 | 返回值 | 说明 |
| --- | --- | --- | --- |
| `add_conversation(content, role)` | content, role | None | 添加对话 |
| `remember(key, value, category)` | key, value, category | None | 存储长期记忆 |
| `recall(key)` | key | Any | 回忆信息 |
| `get_full_context()` | 无 | dict | 获取完整上下文 |

---

## 七、RAG检索器 (rag_retriever.py)

### RAGRetriever

检索增强生成。

**方法**

| 方法 | 参数 | 返回值 | 说明 |
| --- | --- | --- | --- |
| `add_document(content, metadata)` | content, metadata | str | 添加文档 |
| `retrieve(query, top_k)` | query, top_k | list | 检索相关文档 |
| `get_context_for_query(query)` | query | str | 获取查询上下文 |

---

## 八、人设配置

### SYMPHONY_CONFIG["persona"]

交交的人设配置。

**参数**

| 参数 | 值 | 说明 |
| --- | --- | --- |
| name | 交交 | 系统名称 |
| nickname | 娇娇 | 暧昧昵称 |
| identity | 青丘女狐 | 身份 |
| title | 青丘一族的主人 | 称号 |
| user_name | 造梦者 | 用户称呼 |
| user_nickname | 亲爱的 | 用户昵称 |
| brand_slogan | 智韵交响，共创华章 | 品牌标语 |

---

## 九、错误码说明

| 错误码 | 说明 |
| --- | --- |
| E001 | API调用失败 |
| E002 | 模型不可用 |
| E003 | 内容过滤触发 |
| E004 | 超时错误 |
| E005 | 重试次数耗尽 |

---

## 十、使用示例

### 完整调用流程

```python
from retry_manager import RetryManager
from timeout_optimizer import TimeoutOptimizer
from health_checker import HealthChecker
from content_filter import ContentFilter
from memory_layers import MemorySystem

# 初始化各模块
retry_mgr = RetryManager()
timeout_opt = TimeoutOptimizer()
health_chk = HealthChecker()
content_flt = ContentFilter()
memory = MemorySystem()

# 执行带重试的调用
def my_api_call():
    return "result"

result = retry_mgr.execute_with_retry(my_api_call)
print(result)
```

---

**文档版本** v1.0
**维护者** 赵心怡（文档工程师）
**更新日期** 2026-03-08
