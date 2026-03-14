#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
retry_manager.py - 重试管理器
实现指数退避重试机制，提高API调用成功率
"""
import time
import random
from typing import Callable, Optional, Dict, Any
from datetime import datetime


class RetryManager:
    """重试管理器 - 指数退避重试机制"""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """
        初始化重试管理器
        
        Args:
            max_retries: 最大重试次数
            base_delay: 基础延迟时间（秒）
            max_delay: 最大延迟时间（秒）
            exponential_base: 指数基数
            jitter: 是否添加随机抖动
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retry_history = []
    
    def calculate_delay(self, attempt: int) -> float:
        """
        计算退避延迟时间
        
        Args:
            attempt: 当前重试次数
        
        Returns:
            延迟时间（秒）
        """
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # 添加随机抖动，避免雷群效应
            delay = delay * (0.5 + random.random())
        
        return delay
    
    def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行函数并在失败时重试
        
        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            执行结果字典
        """
        last_exception = None
        start_time = time.time()
        
        for attempt in range(self.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                
                # 记录成功
                self.retry_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "attempt": attempt + 1,
                    "success": True,
                    "total_time": time.time() - start_time
                })
                
                return {
                    "success": True,
                    "result": result,
                    "attempts": attempt + 1,
                    "total_time": time.time() - start_time
                }
            
            except Exception as e:
                last_exception = e
                
                # 记录失败
                self.retry_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "attempt": attempt + 1,
                    "success": False,
                    "error": str(e),
                    "delay": self.calculate_delay(attempt)
                })
                
                # 如果还有重试机会，等待后重试
                if attempt < self.max_retries:
                    delay = self.calculate_delay(attempt)
                    time.sleep(delay)
        
        # 所有重试都失败
        return {
            "success": False,
            "error": str(last_exception),
            "attempts": self.max_retries + 1,
            "total_time": time.time() - start_time
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取重试统计信息"""
        if not self.retry_history:
            return {"total_calls": 0}
        
        success_count = sum(1 for r in self.retry_history if r["success"])
        total_calls = len(self.retry_history)
        
        return {
            "total_calls": total_calls,
            "success_count": success_count,
            "success_rate": success_count / total_calls if total_calls > 0 else 0,
            "failure_count": total_calls - success_count
        }


class ModelRetryManager:
    """模型调用专用重试管理器"""
    
    def __init__(self):
        self.retry_manager = RetryManager(
            max_retries=3,
            base_delay=1.0,
            max_delay=30.0
        )
        self.call_stats = {}
    
    def call_model_with_retry(
        self,
        model_name: str,
        call_func: Callable,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        调用模型并在失败时重试
        
        Args:
            model_name: 模型名称
            call_func: 调用函数
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            调用结果
        """
        result = self.retry_manager.execute_with_retry(
            call_func, *args, **kwargs
        )
        
        # 更新模型统计
        if model_name not in self.call_stats:
            self.call_stats[model_name] = {
                "total_calls": 0,
                "success_calls": 0,
                "failed_calls": 0,
                "total_retries": 0
            }
        
        self.call_stats[model_name]["total_calls"] += 1
        if result["success"]:
            self.call_stats[model_name]["success_calls"] += 1
        else:
            self.call_stats[model_name]["failed_calls"] += 1
        self.call_stats[model_name]["total_retries"] += result["attempts"] - 1
        
        return result
    
    def get_model_stats(self, model_name: str) -> Dict[str, Any]:
        """获取指定模型的统计信息"""
        return self.call_stats.get(model_name, {})
    
    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有模型的统计信息"""
        return self.call_stats


# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("🦊 重试管理器测试")
    print("=" * 60)
    
    # 创建重试管理器
    retry_mgr = RetryManager(max_retries=3, base_delay=0.5)
    
    # 模拟失败的函数
    call_count = [0]
    
    def unreliable_function():
        call_count[0] += 1
        if call_count[0] < 3:
            raise Exception(f"模拟失败 (第{call_count[0]}次调用)")
        return f"成功！第{call_count[0]}次调用成功"
    
    # 测试重试
    print("\n测试指数退避重试...")
    result = retry_mgr.execute_with_retry(unreliable_function)
    print(f"结果: {result}")
    
    # 获取统计
    print("\n重试统计:")
    stats = retry_mgr.get_stats()
    print(f"  总调用: {stats['total_calls']}")
    print(f"  成功率: {stats['success_rate']*100:.1f}%")
    
    print("\n✅ 重试管理器测试完成")
