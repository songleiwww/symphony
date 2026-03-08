#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
timeout_optimizer.py - 超时优化器
实现动态超时调整，优化API调用效率
"""
import time
from typing import Dict, Any, List
from datetime import datetime
from collections import deque


class TimeoutOptimizer:
    """超时优化器 - 动态超时调整"""
    
    def __init__(
        self,
        default_timeout: float = 60.0,
        min_timeout: float = 10.0,
        max_timeout: float = 120.0,
        history_size: int = 10
    ):
        """
        初始化超时优化器
        
        Args:
            default_timeout: 默认超时时间
            min_timeout: 最小超时时间
            max_timeout: 最大超时时间
            history_size: 历史记录大小
        """
        self.default_timeout = default_timeout
        self.min_timeout = min_timeout
        self.max_timeout = max_timeout
        self.history_size = history_size
        
        # 模型超时历史
        self.timeout_history: Dict[str, deque] = {}
        # 模型当前超时设置
        self.current_timeouts: Dict[str, float] = {}
    
    def get_timeout(self, model_name: str) -> float:
        """
        获取模型的超时时间
        
        Args:
            model_name: 模型名称
        
        Returns:
            超时时间（秒）
        """
        if model_name not in self.current_timeouts:
            self.current_timeouts[model_name] = self.default_timeout
        
        return self.current_timeouts[model_name]
    
    def record_response_time(
        self,
        model_name: str,
        response_time: float,
        success: bool
    ) -> None:
        """
        记录响应时间并调整超时
        
        Args:
            model_name: 模型名称
            response_time: 响应时间
            success: 是否成功
        """
        if model_name not in self.timeout_history:
            self.timeout_history[model_name] = deque(maxlen=self.history_size)
        
        self.timeout_history[model_name].append({
            "time": response_time,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })
        
        # 根据历史调整超时
        self._adjust_timeout(model_name)
    
    def _adjust_timeout(self, model_name: str) -> None:
        """
        调整模型的超时时间
        
        Args:
            model_name: 模型名称
        """
        history = self.timeout_history.get(model_name, [])
        if len(history) < 3:
            return
        
        # 计算平均响应时间
        successful_times = [h["time"] for h in history if h["success"]]
        if not successful_times:
            # 所有都失败，增加超时
            new_timeout = self.current_timeouts.get(model_name, self.default_timeout) * 1.5
        else:
            avg_time = sum(successful_times) / len(successful_times)
            # 超时设置为平均响应时间的2倍，再加安全边际
            new_timeout = avg_time * 2 + 10
        
        # 限制在最小和最大范围内
        new_timeout = max(self.min_timeout, min(self.max_timeout, new_timeout))
        
        self.current_timeouts[model_name] = new_timeout
    
    def get_timeout_stats(self, model_name: str) -> Dict[str, Any]:
        """
        获取模型的超时统计
        
        Args:
            model_name: 模型名称
        
        Returns:
            统计信息
        """
        history = self.timeout_history.get(model_name, [])
        if not history:
            return {"model": model_name, "calls": 0}
        
        successful = [h for h in history if h["success"]]
        failed = [h for h in history if not h["success"]]
        
        return {
            "model": model_name,
            "calls": len(history),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(history) if history else 0,
            "current_timeout": self.current_timeouts.get(model_name, self.default_timeout),
            "avg_response_time": sum(h["time"] for h in successful) / len(successful) if successful else 0
        }
    
    def get_all_stats(self) -> List[Dict[str, Any]]:
        """获取所有模型的统计信息"""
        return [self.get_timeout_stats(model) for model in self.timeout_history]


class NetworkAwareTimeout:
    """网络感知超时优化器"""
    
    def __init__(self):
        self.timeout_optimizer = TimeoutOptimizer()
        self.network_quality = "good"  # good, medium, poor
    
    def check_network_quality(self) -> str:
        """
        检测网络质量
        
        Returns:
            网络质量等级
        """
        # 简单的网络质量检测
        # 实际应用中可以添加ping测试等
        return self.network_quality
    
    def get_adaptive_timeout(self, model_name: str) -> float:
        """
        获取自适应超时时间
        
        Args:
            model_name: 模型名称
        
        Returns:
            超时时间
        """
        base_timeout = self.timeout_optimizer.get_timeout(model_name)
        
        # 根据网络质量调整
        quality = self.check_network_quality()
        if quality == "poor":
            return base_timeout * 1.5
        elif quality == "medium":
            return base_timeout * 1.2
        else:
            return base_timeout
    
    def set_network_quality(self, quality: str) -> None:
        """设置网络质量"""
        if quality in ["good", "medium", "poor"]:
            self.network_quality = quality


# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("🦊 超时优化器测试")
    print("=" * 60)
    
    # 创建超时优化器
    optimizer = TimeoutOptimizer(default_timeout=60.0)
    
    # 模拟响应时间记录
    print("\n模拟记录响应时间...")
    
    # 模型1：快速响应
    for i in range(5):
        optimizer.record_response_time("model_fast", 5.0 + i, True)
    
    # 模型2：慢速响应
    for i in range(5):
        optimizer.record_response_time("model_slow", 30.0 + i * 2, True)
    
    # 模型3：部分失败
    for i in range(5):
        success = i % 2 == 0
        optimizer.record_response_time("model_unstable", 20.0, success)
    
    # 获取统计
    print("\n超时统计:")
    for stat in optimizer.get_all_stats():
        print(f"  {stat['model']}:")
        print(f"    成功率: {stat['success_rate']*100:.1f}%")
        print(f"    当前超时: {stat['current_timeout']:.1f}秒")
        print(f"    平均响应: {stat['avg_response_time']:.1f}秒")
    
    # 测试网络感知
    print("\n网络感知测试:")
    net_aware = NetworkAwareTimeout()
    net_aware.set_network_quality("poor")
    timeout = net_aware.get_adaptive_timeout("model_fast")
    print(f"  网络质量差时超时: {timeout:.1f}秒")
    
    print("\n✅ 超时优化器测试完成")
