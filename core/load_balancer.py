"""
序境内核 - 负载均衡器
"""

import time
import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LoadBalanceAlgorithm(Enum):
    """负载均衡算法"""
    LEAST_CONNECTIONS = "lc"  # 最少连接
    WEIGHTED_ROUND_ROBIN = "wrr"  # 加权轮询
    WEIGHTED_LEAST_CONNECTIONS = "wlrc"  # 加权最少连接
    RANDOM = "random"  # 随机
    ADAPTIVE = "adaptive"  # 自适应


class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, algorithm: LoadBalanceAlgorithm = LoadBalanceAlgorithm.ADAPTIVE):
        self.algorithm = algorithm
        self._weights: Dict[str, int] = {}
        self._connection_counts: Dict[str, int] = {}
        self._last_update = time.time()
    
    def select(self, models: List) -> Optional:
        """选择模型"""
        if not models:
            return None
        
        # 过滤可用模型
        available = [m for m in models if m.status.value == "online"]
        if not available:
            # 尝试降级的
            available = [m for m in models if m.status.value == "degrade"]
        
        if not available:
            return None
        
        if self.algorithm == LoadBalanceAlgorithm.LEAST_CONNECTIONS:
            return self._least_connections(available)
        elif self.algorithm == LoadBalanceAlgorithm.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin(available)
        elif self.algorithm == LoadBalanceAlgorithm.ADAPTIVE:
            return self._adaptive_select(available)
        elif self.algorithm == LoadBalanceAlgorithm.RANDOM:
            return random.choice(available)
        
        return available[0]
    
    def _least_connections(self, models: List) -> Optional:
        """最少连接数算法"""
        return min(models, key=lambda m: self._connection_counts.get(m.model_id, 0))
    
    def _weighted_round_robin(self, models: List) -> Optional:
        """加权轮询算法"""
        # 简单的wrr实现
        total_weight = sum(self._weights.get(m.model_id, m.weight) for m in models)
        if total_weight == 0:
            return models[0]
        
        rand = random.randint(0, total_weight - 1)
        cumulative = 0
        
        for m in models:
            weight = self._weights.get(m.model_id, m.weight)
            cumulative += weight
            if rand < cumulative:
                return m
        
        return models[0]
    
    def _adaptive_select(self, models: List) -> Optional:
        """自适应选择 - 综合考虑连接数、延迟、成功率"""
        scores = []
        
        for m in models:
            connections = self._connection_counts.get(m.model_id, 0)
            latency = getattr(m, 'avg_latency', 0) or 0
            fail_rate = getattr(m, 'fail_count', 0) / max(getattr(m, 'success_count', 1), 1)
            
            # 得分越低越好
            score = (
                connections * 1.0 +
                latency * 0.1 +
                fail_rate * 100
            )
            scores.append((score, m))
        
        scores.sort(key=lambda x: x[0])
        return scores[0][1] if scores else None
    
    def increment_connection(self, model_id: str):
        """增加连接计数"""
        self._connection_counts[model_id] = self._connection_counts.get(model_id, 0) + 1
    
    def decrement_connection(self, model_id: str):
        """减少连接计数"""
        if model_id in self._connection_counts:
            self._connection_counts[model_id] = max(0, self._connection_counts[model_id] - 1)
    
    def set_weight(self, model_id: str, weight: int):
        """设置权重"""
        self._weights[model_id] = weight
    
    def get_stats(self) -> Dict:
        """获取负载均衡统计"""
        return {
            "algorithm": self.algorithm.value,
            "connection_counts": self._connection_counts,
            "weights": self._weights
        }


# 全局负载均衡器
_balancer: Optional[LoadBalancer] = None


def get_balancer(algorithm: LoadBalanceAlgorithm = LoadBalanceAlgorithm.ADAPTIVE) -> LoadBalancer:
    global _balancer
    if _balancer is None:
        _balancer = LoadBalancer(algorithm)
    return _balancer
