#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一错误处理系统 - Global Error Handler
v1.0.0
"""

from dataclasses import dataclass
from enum import Enum
import time
from functools import wraps
from typing import Dict, Any, Callable, Optional


class ErrorCategory(Enum):
    RETRYABLE = "retryable"
    FATAL = "fatal"
    WARNING = "warning"


@dataclass
class ErrorInfo:
    error_type: str
    message: str
    context: Dict[str, Any]
    timestamp: str
    category: ErrorCategory


class GlobalErrorHandler:
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.error_history: list[ErrorInfo] = []
    
    def wait_time(self, attempt: int) -> float:
        wait = self.base_delay * (2 ** attempt)
        return min(wait, self.max_delay)
    
    def should_retry(self, error_info: ErrorInfo) -> bool:
        return error_info.category == ErrorCategory.RETRYABLE
    
    def handle(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(self.max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_info = ErrorInfo(
                        error_type=type(e).__name__,
                        message=str(e),
                        context={"attempt": attempt},
                        timestamp=datetime.now().isoformat(),
                        category=self._classify_error(e)
                    )
                    self.error_history.append(error_info)
                    
                    if self.should_retry(error_info) and attempt < self.max_retries - 1:
                        wait = self.wait_time(attempt)
                        time.sleep(wait)
                    else:
                        last_error = error_info
                        break
            
            if last_error:
                raise RuntimeError(
                    f"Failed after {self.max_retries} attempts: {last_error.message}"
                )
        
        return wrapper
    
    def _classify_error(self, error: Exception) -> ErrorCategory:
        if isinstance(error, (ConnectionError, TimeoutError)):
            return ErrorCategory.RETRYABLE
        elif isinstance(error, (ValueError, TypeError)):
            return ErrorCategory.FATAL
        else:
            return ErrorCategory.WARNING
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_errors": len(self.error_history),
            "retryable": sum(1 for e in self.error_history if e.category == ErrorCategory.RETRYABLE),
            "fatal": sum(1 for e in self.error_history if e.category == ErrorCategory.FATAL)
        }


# 全局实例
global_handler = GlobalErrorHandler()
