"""
Symphony Rate Limit Optimizer - 限流优化策略
"""
import time
import threading
from collections import deque
from typing import Dict, Optional


class RateLimitOptimizer:
    """限流优化器"""
    
    def __init__(self):
        # 模型调用记录
        self.call_history: Dict[int, deque] = {}
        # 限流配置
        self.config = {
            "max_calls_per_minute": 10,  # 每分钟最大调用
            "cooldown_seconds": 30,       # 冷却时间
            "max_retries": 3,             # 最大重试
            "backoff_multiplier": 1.5     # 退避系数
        }
        self.lock = threading.Lock()
    
    def can_call(self, model_index: int) -> bool:
        """检查是否可以调用"""
        with self.lock:
            now = time.time()
            
            if model_index not in self.call_history:
                self.call_history[model_index] = deque()
            
            # 清理超过1分钟的记录
            history = self.call_history[model_index]
            while history and now - history[0] > 60:
                history.popleft()
            
            # 检查是否超过限制
            if len(history) >= self.config["max_calls_per_minute"]:
                return False
            
            # 记录调用
            history.append(now)
            return True
    
    def get_wait_time(self, model_index: int) -> float:
        """获取需要等待的时间"""
        with self.lock:
            if model_index not in self.call_history:
                return 0
            
            history = self.call_history[model_index]
            if not history:
                return 0
            
            oldest = history[0]
            wait = 60 - (time.time() - oldest)
            return max(0, wait)
    
    def should_retry(self, model_index: int, retry_count: int) -> bool:
        """判断是否应该重试"""
        if retry_count >= self.config["max_retries"]:
            return False
        
        wait_time = self.get_wait_time(model_index)
        return wait_time < self.config["cooldown_seconds"]
    
    def get_optimal_model(self, available_models: list) -> Optional[int]:
        """获取最优模型"""
        best_model = None
        min_wait = float('inf')
        
        for idx in available_models:
            wait = self.get_wait_time(idx)
            if wait < min_wait:
                min_wait = wait
                best_model = idx
        
        return best_model


# 全局实例
rate_optimizer = RateLimitOptimizer()
