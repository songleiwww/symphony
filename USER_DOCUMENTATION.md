# 交响 (Symphony) 使用文档

> 多模型协作智能系统 | Multi-Model Collaboration Intelligence System

---

## 目录

1. [概述](#1-概述)
2. [安装说明](#2-安装说明)
3. [快速开始](#3-快速开始)
4. [API参考](#4-api参考)
5. [示例代码](#5-示例代码)
6. [配置详解](#6-配置详解)
7. [故障处理](#7-故障处理)

---

## 1. 概述

### 1.1 什么是交响 (Symphony)?

**交响 (Symphony)** 是一个多模型协作智能系统，通过协调多个AI模型实现复杂任务处理。系统会自动选择最优模型，失败时自动降级，确保服务高可用。

### 1.2 核心特性

| 特性 | 说明 |
|------|------|
| 🎯 **多模型协作** | 支持17+模型并行/顺序调用 |
| 🔄 **智能调度** | 根据任务自动选择最优模型 |
| ⚡ **限流优化** | 自动检测和处理API限流 |
| 🛡️ **错误恢复** | 完善的熔断器+重试机制 |
| 📝 **记忆协调** | 与OpenClaw记忆系统同步 |
| 🧠 **人性化触发** | 主动/被动智能帮助 |

### 1.3 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Symphony 智韵交响                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   CLI/Web   │  │   API调用   │  │   OpenClaw集成      │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                     │              │
│  ┌──────▼────────────────▼─────────────────────▼──────────┐  │
│  │                    调度层 (Dispatcher)                   │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │  │
│  │  │ 并行调度器    │  │ 顺序调度器    │  │ 动态调度器   │  │  │
│  │  └──────────────┘  └──────────────┘  └─────────────┘  │  │
│  └──────────────────────────┬──────────────────────────────┘  │
│                             │                                 │
│  ┌──────────────────────────▼──────────────────────────────┐  │
│  │                    模型管理层 (ModelManager)              │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │           模型降级链 (Failover Chain)              │  │  │
│  │  │  Priority 1 → 2 → 3 → ... → 17                   │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  ┌──────────────┐  ┌────────────┐  ┌────────────────┐  │  │
│  │  │ 熔断器       │  │ 重试策略   │  │ 健康检查       │  │  │
│  │  │ (Circuit)    │  │ (Retry)    │  │ (HealthCheck) │  │  │
│  │  └──────────────┘  └────────────┘  └────────────────┘  │  │
│  └──────────────────────────┬──────────────────────────────┘  │
│                             │                                 │
│  ┌──────────────────────────▼──────────────────────────────┐  │
│  │                    模型提供商                             │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌───────┐  │  │
│  │  │ cherry-    │ │ cherry-    │ │ cherry-    │ │cherry-│  │  │
│  │  │ doubao     │ │ minimax    │ │ nvidia     │ │model- │  │  │
│  │  │            │ │            │ │            │ │scope  │  │  │
│  │  └────────────┘ └────────────┘ └────────────┘ └───────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

---

## 2. 安装说明

### 2.1 环境要求

| 要求 | 最低版本 |
|------|----------|
| Python | 3.8+ |
| requests | 最新版 |
| openai | 1.0+ |

### 2.2 安装步骤

#### 步骤1：克隆仓库

```bash
git clone https://github.com/songleiwww/symphony.git
cd symphony
```

#### 步骤2：安装依赖

```bash
pip install requests openai
```

#### 步骤3：配置API密钥

```bash
# 复制配置模板
cp config.template.py config.py

# 编辑 config.py，填入你的API密钥
```

#### 步骤4：验证安装

```bash
python -c "from symphony_core import Symphony; print('安装成功!')"
```

### 2.3 Docker安装 (可选)

```bash
# 构建镜像
docker build -t symphony .

# 运行容器
docker run -v $(pwd):/app symphony
```

---

## 3. 快速开始

### 3.1 5分钟快速入门

```python
# 方式1：使用核心类
from symphony_core import Symphony

# 初始化
s = Symphony()

# 简单调用
result = s.call("你好，请介绍一下自己")
print(result)
```

### 3.2 使用示例

#### 示例1：天气播报

```bash
python weather_final.py
```

#### 示例2：天机播报

```bash
python tianji_final.py
```

#### 示例3：多模型讨论

```bash
python model_discussion_final.py
```

### 3.3 快速配置

在 `config.py` 中配置模型：

```python
MODEL_CHAIN = [
    {
        "name": "doubao_ark_code",
        "provider": "cherry-doubao",
        "model_id": "ark-code-latest",
        "base_url": "https://ark.cn-beijing.volces.com/api/coding/v3",
        "api_key": "YOUR_API_KEY",
        "enabled": True,
        "priority": 1
    },
    # 添加更多模型...
]
```

---

## 4. API参考

### 4.1 Symphony 核心类

#### `Symphony`

```python
from symphony_core import Symphony
```

**构造函数：**

```python
Symphony(memory_path: str = "symphony_memory.json")
```

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| memory_path | str | 记忆文件路径 | "symphony_memory.json" |

**方法：**

##### `call(prompt: str, **kwargs) -> str`

调用模型获取响应

```python
result = s.call("你的问题")
```

| 参数 | 类型 | 说明 |
|------|------|------|
| prompt | str | 输入提示 |

**返回：** `str` - 模型响应

---

### 4.2 模型管理器

```python
from model_manager import ModelManager
```

#### `ModelManager`

模型管理器，负责模型降级和故障转移。

**构造函数：**

```python
ModelManager(model_configs: List[Dict] = None)
```

**方法：**

##### `execute(func: Callable, *args, **kwargs) -> Any`

执行模型调用，自动处理降级

```python
manager = ModelManager()

def my_call(model, prompt):
    return model.call(prompt)

result = manager.execute(my_call, "hello")
```

##### `get_status() -> Dict`

获取系统状态

```python
status = manager.get_status()
print(status['total_models'])
```

##### `start_health_check()`

启动健康检查线程

##### `stop_health_check()`

停止健康检查线程

---

### 4.3 熔断器

```python
from model_manager import CircuitBreaker
```

#### `CircuitBreaker`

实现熔断器模式，防止故障扩散。

**构造函数：**

```python
CircuitBreaker(
    model_name: str,
    failure_threshold: int = 5,      # 失败次数阈值
    failure_window: int = 60,        # 失败时间窗口(秒)
    recovery_timeout: int = 30,      # 恢复超时(秒)
    half_open_max_calls: int = 2,   # 半开状态最大调用数
    half_open_success_threshold: float = 0.5  # 半开状态成功率阈值
)
```

**方法：**

| 方法 | 说明 |
|------|------|
| `can_execute()` | 检查是否可以执行请求 |
| `on_success()` | 报告成功 |
| `on_failure(error)` | 报告失败 |
| `get_metrics()` | 获取熔断器指标 |
| `reset()` | 重置熔断器 |

**状态转换：**

```
CLOSED (正常) ──失败阈值达─→ OPEN (熔断)
    ↑                      ↓
    │    恢复超时后       │
    └── HALF_OPEN (半开) ←┘
           ↑
      成功率达标
```

---

### 4.4 重试策略

```python
from model_manager import RetryPolicy
```

#### `RetryPolicy`

实现指数退避重试机制。

**构造函数：**

```python
RetryPolicy(
    max_retries: int = 3,           # 最大重试次数
    initial_delay: float = 1.0,     # 初始延迟(秒)
    backoff_factor: float = 2.0,    # 退避倍数
    max_delay: float = 30.0,        # 最大延迟(秒)
    jitter_factor: float = 0.1      # 抖动因子(0-1)
)
```

**方法：**

##### `calculate_delay(attempt: int) -> float`

计算第n次重试的延迟

```python
delay = policy.calculate_delay(0)  # 1.0秒
delay = policy.calculate_delay(1)  # 2.0秒
delay = policy.calculate_delay(2)  # 4.0秒
```

##### `execute(func: Callable, *args, **kwargs) -> Any`

执行函数，失败时自动重试

```python
result = policy.execute(my_function, arg1, arg2)
```

---

### 4.5 记忆系统

```python
from symphony_core import SymphonyCore
```

#### `SymphonyCore`

集成记忆系统的核心类。

**构造函数：**

```python
SymphonyCore(memory_path: str = "symphony_memory.json")
```

**方法：**

| 方法 | 说明 |
|------|------|
| `add_memory(content, type, importance, tags, category)` | 添加记忆 |
| `get_memory(memory_id)` | 获取记忆 |
| `search_memories(query, tags, min_importance)` | 搜索记忆 |
| `set_preference(key, value)` | 设置偏好 |
| `get_preference(key, default)` | 获取偏好 |
| `get_stats()` | 获取统计信息 |

---

## 5. 示例代码

### 5.1 基础调用

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""交响基础调用示例"""

from symphony_core import Symphony

# 创建实例
symphony = Symphony()

# 简单调用
response = symphony.call("你好，请介绍一下交响系统")
print(response)
```

### 5.2 多模型并行调用

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""多模型并行调用示例"""

import asyncio
from parallel_orchestrator import ParallelOrchestrator

async def main():
    orchestrator = ParallelOrchestrator()
    
    prompts = [
        "解释什么是机器学习",
        "解释什么是深度学习",
        "解释什么是强化学习"
    ]
    
    results = await orchestrator.parallel_call(prompts)
    
    for i, result in enumerate(results):
        print(f"\n模型 {i+1} 结果:")
        print(result)

asyncio.run(main())
```

### 5.3 动态调度

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""动态调度示例"""

from dynamic_orchestrator import DynamicOrchestrator

def main():
    orchestrator = DynamicOrchestrator()
    
    # 根据任务类型动态选择模型
    task = {
        "type": "code",
        "prompt": "写一个快速排序算法",
        "complexity": "high"
    }
    
    result = orchestrator.dispatch(task)
    print(result)

main()
```

### 5.4 自定义重试策略

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自定义重试策略示例"""

import time
from model_manager import RetryPolicy

# 创建自定义重试策略
policy = RetryPolicy(
    max_retries=5,
    initial_delay=2.0,
    backoff_factor=3.0,
    max_delay=60.0,
    jitter_factor=0.2
)

# 定义可能失败的函数
def unstable_function():
    import random
    if random.random() < 0.7:
        raise Exception("模拟失败")
    return "成功!"

# 使用重试策略执行
try:
    result = policy.execute(unstable_function)
    print(f"结果: {result}")
except Exception as e:
    print(f"最终失败: {e}")
```

### 5.5 熔断器使用

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""熔断器使用示例"""

from model_manager import CircuitBreaker

# 创建熔断器
breaker = CircuitBreaker(
    model_name="my_model",
    failure_threshold=3,
    failure_window=60,
    recovery_timeout=30
)

# 模拟调用
for i in range(10):
    if breaker.can_execute():
        print(f"请求 {i+1}: 可以执行")
        # 模拟失败
        breaker.on_failure(Exception("模拟API错误"))
    else:
        print(f"请求 {i+1}: 熔断器打开，拒绝执行")
    
    time.sleep(0.1)

# 查看状态
print("\n熔断器状态:")
print(breaker.get_metrics())
```

### 5.6 记忆系统使用

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""记忆系统使用示例"""

from symphony_core import SymphonyCore

# 创建核心实例
core = SymphonyCore()

# 添加记忆
core.add_memory(
    content="用户偏好使用中文回答",
    memory_type="long_term",
    importance=0.9,
    tags=["preference", "language"],
    category="user"
)

core.add_memory(
    content="用户感兴趣的技术主题: AI, Python, 机器学习",
    memory_type="short_term",
    importance=0.7,
    tags=["interest", "tech"],
    category="user"
)

# 搜索记忆
results = core.search_memories(
    query="语言",
    min_importance=0.5
)

print("搜索结果:")
for mem in results:
    print(f"  - {mem.content}")

# 设置偏好
core.set_preference("response_language", "中文")
core.set_preference("detail_level", "详细")

# 获取统计
stats = core.get_stats()
print(f"\n记忆统计: {stats}")
```

### 5.7 完整的多模型协作

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完整的多模型协作示例"""

import json
from model_manager import ModelManager
from symphony_core import SymphonyCore

def main():
    # 1. 初始化组件
    core = SymphonyCore()
    manager = ModelManager()
    
    # 2. 定义模型调用
    def call_model(model_wrapper, prompt):
        """实际的模型调用逻辑"""
        print(f"使用模型: {model_wrapper.name}")
        # 这里应该是真实的API调用
        # response = openai.ChatCompletion.create(...)
        return f"[{model_wrapper.name}] 处理: {prompt}"
    
    # 3. 执行调用
    try:
        result = manager.execute(
            call_model,
            "解释量子计算的基本原理"
        )
        print(f"\n最终结果: {result}")
        
        # 4. 保存到记忆
        core.add_memory(
            content=f"成功处理请求: 量子计算",
            memory_type="short_term",
            importance=0.6,
            tags=["request", "quantum"],
            category="session"
        )
        
    except Exception as e:
        print(f"错误: {e}")
        
        # 记录失败
        core.add_memory(
            content=f"请求失败: {str(e)}",
            memory_type="short_term",
            importance=0.8,
            tags=["error", "failed"],
            category="session"
        )
    
    # 5. 打印状态
    print("\n模型状态:")
    print(json.dumps(manager.get_status(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
```

---

## 6. 配置详解

### 6.1 模型配置

```python
MODEL_CHAIN = [
    {
        "name": "模型名称",
        "provider": "提供商标识",
        "model_id": "模型ID",
        "alias": "显示名称",
        "base_url": "API地址",
        "api_key": "API密钥",
        "api_type": "openai-completions",
        "context_window": 128000,
        "timeout": 120,
        "max_retries": 3,
        "enabled": True,
        "priority": 1
    }
]
```

### 6.2 提供商配置

| 提供商 | Base URL | 模型数量 |
|--------|----------|----------|
| cherry-doubao | `https://ark.cn-beijing.volces.com/api/coding/v3` | 5 |
| cherry-minimax | `https://api.minimaxi.com/anthropic` | 1 |
| cherry-nvidia | `https://integrate.api.nvidia.com/v1` | 10 |
| cherry-modelscope | `https://api-inference.modelscope.cn` | 2 |

### 6.3 系统配置

```python
SYMPHONY_CONFIG = {
    "system_name": "交响 (Symphony)",
    "version": "1.4.0",
    "max_concurrent_calls": 5,
    "default_timeout": 120,
    "enable_fallback": True,
    "enable_monitoring": True,
}
```

### 6.4 熔断器配置

```python
CIRCUIT_BREAKER_CONFIG = {
    "failure_threshold": 5,           # 失败次数阈值
    "failure_window": 60,             # 失败时间窗口(秒)
    "recovery_timeout": 30,           # 恢复超时(秒)
    "half_open_max_calls": 2,         # 半开状态最大调用数
    "half_open_success_threshold": 0.5 # 半开状态成功率阈值
}
```

### 6.5 重试配置

```python
RETRY_CONFIG = {
    "max_retries": 3,
    "initial_delay": 1.0,
    "backoff_factor": 2.0,
    "max_delay": 30.0,
    "jitter_factor": 0.1
}
```

---

## 7. 故障处理

### 7.1 故障转移流程

```
用户请求
    ↓
尝试优先级1模型
    ↓ 失败
尝试优先级2模型
    ↓ 失败
...
    ↓
尝试优先级17模型
    ↓ 失败
触发故障处理
```

### 7.2 异常类型

| 异常类 | 说明 |
|--------|------|
| `ModelError` | 模型调用异常基类 |
| `ModelTimeoutError` | 模型调用超时 |
| `ModelAPIError` | 模型API错误 |
| `CircuitBreakerOpenError` | 熔断器打开 |
| `NoAvailableModelError` | 没有可用模型 |

### 7.3 最佳实践

1. **总是处理异常**
   ```python
   try:
       result = symphony.call("prompt")
   except NoAvailableModelError:
       print("所有模型都不可用")
   except Exception as e:
       print(f"错误: {e}")
   ```

2. **使用健康检查**
   ```python
   manager.start_health_check()
   # ... 使用 ...
   manager.stop_health_check()
   ```

3. **监控熔断器状态**
   ```python
   status = manager.get_status()
   for name, metrics in status['models'].items():
       print(f"{name}: {metrics['circuit_breaker']['state']}")
   ```

---

## 附录

### A. 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0.0 | 2026-03-08 | 首发版发布 |
| v1.1.0 | - | 增加动态调度器 |
| v1.4.0 | - | 完善故障容错机制 |

### B. 常见问题

**Q: 如何添加新的模型?**
A: 在 `MODEL_CHAIN` 中添加配置，设置 `priority` 确定优先级。

**Q: 熔断器打开后如何恢复?**
A: 等待 `recovery_timeout` 秒后，系统会自动进入半开状态尝试恢复。

**Q: 如何禁用某个模型?**
A: 设置配置中的 `"enabled": False`。

---

**智韵交响，共创华章！** 🎵

*文档版本: 1.0*
*最后更新: 2026-03-09*
