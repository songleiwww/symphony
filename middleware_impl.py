# Symphony Middleware Impl
# 开发者: 王明远 (中间件架构师)
# 生成时间: 2026-03-08T01:57:37.906418
# 版本: 1.5.1

```python
"""
Symphony 系统中间件层实现

包含 ModelAdapter（模型适配器）、MessageRouter（消息路由器）和 DataTransformer（数据转换器）
提供统一接口、错误处理、重试机制、负载均衡、状态追踪和缓存功能。
"""

import asyncio
import json
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Union
from functools import wraps
import logging
from datetime import datetime
from hashlib import md5

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =======================
# 1. ModelAdapter - 模型适配器基类
# =======================

class ModelProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"


@dataclass
class ModelResponse:
    """标准化模型响应"""
    content: str
    model: str
    usage: Dict[str, int]
    latency: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ModelRequest:
    """标准化模型请求"""
    prompt: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 1024
    metadata: Dict[str, Any] = field(default_factory=dict)


class RetryConfig:
    """重试配置"""
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 10.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay


class ModelAdapterError(Exception):
    """模型适配器通用异常"""
    pass


class ModelTimeoutError(ModelAdapterError):
    """模型超时异常"""
    pass


class RateLimitError(ModelAdapterError):
    """速率限制异常"""
    pass


class AuthenticationError(ModelAdapterError):
    """认证失败异常"""
    pass


class ModelAdapter(ABC):
    """
    模型适配器基类，用于适配不同模型API
    支持统一错误处理和自动重试
    """

    def __init__(
        self,
        provider: ModelProvider,
        api_key: str,
        endpoint: Optional[str] = None,
        retry_config: Optional[RetryConfig] = None,
        timeout: float = 30.0
    ):
        self.provider = provider
        self.api_key = api_key
        self.endpoint = endpoint or self._get_default_endpoint()
        self.retry_config = retry_config or RetryConfig()
        self.timeout = timeout
        self.session_id = str(uuid.uuid4