#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统 - 矩阵路由模块
开发者: 杜子美 (军师参议)
功能: 智能模型选择, 动态负载均衡, 响应时间优化
"""

import time
import asyncio
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ModelStatus(Enum):
    """模型状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OVERLOADED = "overloaded"
    FAILED = "failed"


@dataclass
class ModelInfo:
    """模型信息"""
    model_id: str
    model_name: str
    provider: str
    api_url: str
    api_key: str
    status: ModelStatus = ModelStatus.HEALTHY
    
    # 性能指标
    avg_latency: float = 1.0       # 平均延迟 (秒)
    success_rate: float = 1.0       # 成功率
    total_requests: int = 0         # 总请求数
    active_connections: int = 0    # 当前连接数
    
    # 权重配置
    weight: int = 100              # 调度权重
    priority: int = 1              # 优先级 (1=最高)
    
    # 熔断相关
    consecutive_failures: int = 0
    last_failure_time: float = 0
    cooldown_seconds: int = 60     # 冷却时间


class CircuitBreaker:
    """熔断器"""
    
    def __init__(
        self,
        failure_threshold: int = 3,    # 连续失败次数阈值
        timeout_seconds: int = 60,     # 熔断超时
        recovery_threshold: int = 2    # 恢复所需的成功次数
    ):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.recovery_threshold = recovery_threshold
        
        self._state: Dict[str, ModelStatus] = {}
        self._failure_count: Dict[str, int] = defaultdict(int)
        self._last_failure_time: Dict[str, float] = {}
        self._recovery_count: Dict[str, int] = defaultdict(int)
    
    def is_available(self, model_id: str) -> bool:
        """检查模型是否可用"""
        status = self._state.get(model_id, ModelStatus.HEALTHY)
        
        if status == ModelStatus.HEALTHY:
            return True
        
        # 检查是否超时
        if status == ModelStatus.FAILED:
            last_failure = self._last_failure_time.get(model_id, 0)
            if time.time() - last_failure > self.timeout_seconds:
                # 尝试恢复
                self._state[model_id] = ModelStatus.DEGRADED
                self._recovery_count[model_id] = 0
                return True
            return False
        
        return True
    
    def record_success(self, model_id: str) -> None:
        """记录成功"""
        if self._state.get(model_id) == ModelStatus.DEGRADED:
            self._recovery_count[model_id] += 1
            if self._recovery_count[model_id] >= self.recovery_threshold:
                self._state[model_id] = ModelStatus.HEALTHY
                self._failure_count[model_id] = 0
                logger.info(f"模型 {model_id} 恢复健康")
        else:
            self._failure_count[model_id] = 0
    
    def record_failure(self, model_id: str) -> None:
        """记录失败"""
        self._failure_count[model_id] += 1
        self._last_failure_time[model_id] = time.time()
        
        if self._failure_count[model_id] >= self.failure_threshold:
            self._state[model_id] = ModelStatus.FAILED
            logger.warning(f"模型 {model_id} 触发熔断")
    
    def get_status(self, model_id: str) -> ModelStatus:
        return self._state.get(model_id, ModelStatus.HEALTHY)


class MatrixRouter:
    """矩阵路由器 - 核心路由逻辑"""
    
    def __init__(
        self,
        strategy: str = "weighted_round_robin",
        enable_circuit_breaker: bool = True
    ):
        self.strategy = strategy
        self.enable_circuit_breaker = enable_circuit_breaker
        
        # 模型注册表
        self.models: Dict[str, ModelInfo] = {}
        
        # 熔断器
        self.circuit_breaker = CircuitBreaker() if enable_circuit_breaker else None
        
        # 路由统计
        self.stats = {
            "total_routes": 0,
            "route_distribution": defaultdict(int),
            "total_latency": 0.0,
            "cache_hits": 0
        }
        
        # 轮询指针 (加权轮询)
        self._round_robin_index: Dict[str, int] = {}
    
    def register_model(self, model: ModelInfo) -> None:
        """注册模型"""
        self.models[model.model_id] = model
        logger.info(f"注册模型: {model.model_id} ({model.model_name})")
    
    def unregister_model(self, model_id: str) -> None:
        """注销模型"""
        if model_id in self.models:
            del self.models[model_id]
            logger.info(f"注销模型: {model_id}")
    
    def _select_weighted_round_robin(self, prompt: str) -> Optional[ModelInfo]:
        """加权轮询选择"""
        # 按优先级和权重过滤可用模型
        available = [
            m for m in self.models.values()
            if (not self.circuit_breaker or self.circuit_breaker.is_available(m.model_id))
            and m.status == ModelStatus.HEALTHY
        ]
        
        if not available:
            return None
        
        # 按权重排序
        available.sort(key=lambda x: (-x.priority, -x.weight))
        
        # 轮询选择
        model_id = available[0].model_id
        if model_id not in self._round_robin_index:
            self._round_robin_index[model_id] = 0
        
        index = self._round_robin_index[model_id]
        selected = available[index % len(available)]
        
        # 更新指针
        self._round_robin_index[model_id] = (index + 1) % len(available)
        
        return selected
    
    def _select_least_connections(self, prompt: str) -> Optional[ModelInfo]:
        """最少连接选择"""
        available = [
            m for m in self.models.values()
            if (not self.circuit_breaker or self.circuit_breaker.is_available(m.model_id))
            and m.status == ModelStatus.HEALTHY
        ]
        
        if not available:
            return None
        
        # 选择连接数最少的
        return min(available, key=lambda x: x.active_connections)
    
    def _select_fastest(self, prompt: str) -> Optional[ModelInfo]:
        """最低延迟选择"""
        available = [
            m for m in self.models.values()
            if (not self.circuit_breaker or self.circuit_breaker.is_available(m.model_id))
            and m.status == ModelStatus.HEALTHY
        ]
        
        if not available:
            return None
        
        # 选择延迟最低的
        return min(available, key=lambda x: x.avg_latency)
    
    def _select_by_content(self, prompt: str) -> Optional[ModelInfo]:
        """基于内容选择 (简单关键词匹配)"""
        prompt_lower = prompt.lower()
        
        # 关键词到模型的映射
        keyword_models = {
            "code": ["code", "coder", "programming"],
            "math": ["math", "reasoning", "mathematician"],
            "creative": ["creative", "writing", "story"],
            "general": ["general", "chat", "default"]
        }
        
        # 检测意图
        intent = "general"
        for key, keywords in keyword_models.items():
            if any(kw in prompt_lower for kw in keywords):
                intent = key
                break
        
        # 筛选匹配的模型
        available = [
            m for m in self.models.values()
            if (not self.circuit_breaker or self.circuit_breaker.is_available(m.model_id))
            and m.status == ModelStatus.HEALTHY
        ]
        
        if not available:
            return None
        
        # 优先选择匹配意图的模型
        for model in available:
            if intent in model.model_name.lower():
                return model
        
        # 回退到最快模型
        return min(available, key=lambda x: x.avg_latency)
    
    def select_model(self, prompt: str) -> Optional[ModelInfo]:
        """选择最佳模型"""
        strategies = {
            "weighted_round_robin": self._select_weighted_round_robin,
            "least_connections": self._select_least_connections,
            "fastest": self._select_fastest,
            "by_content": self._select_by_content
        }
        
        selector = strategies.get(self.strategy, self._select_weighted_round_robin)
        selected = selector(prompt)
        
        if selected:
            self.stats["total_routes"] += 1
            self.stats["route_distribution"][selected.model_id] += 1
            selected.active_connections += 1
        
        return selected
    
    def release_connection(self, model_id: str) -> None:
        """释放连接"""
        if model_id in self.models:
            self.models[model_id].active_connections = max(
                0, 
                self.models[model_id].active_connections - 1
            )
    
    def record_success(self, model_id: str, latency: float) -> None:
        """记录成功调用"""
        if model_id in self.models:
            model = self.models[model_id]
            model.total_requests += 1
            
            # 更新平均延迟 (指数移动平均)
            model.avg_latency = 0.7 * model.avg_latency + 0.3 * latency
            
            # 更新成功率
            model.success_rate = min(1.0, model.success_rate + 0.01)
            
            if self.circuit_breaker:
                self.circuit_breaker.record_success(model_id)
            
            self.stats["total_latency"] += latency
    
    def record_failure(self, model_id: str) -> None:
        """记录失败调用"""
        if model_id in self.models:
            model = self.models[model_id]
            model.total_requests += 1
            model.success_rate = max(0, model.success_rate - 0.1)
            
            if self.circuit_breaker:
                self.circuit_breaker.record_failure(model_id)
    
    def get_stats(self) -> Dict:
        """获取路由统计"""
        return {
            "total_routes": self.stats["total_routes"],
            "route_distribution": dict(self.stats["route_distribution"]),
            "avg_latency": (
                self.stats["total_latency"] / max(1, self.stats["total_routes"])
            ),
            "models": {
                mid: {
                    "name": m.model_name,
                    "status": m.status.value,
                    "avg_latency": m.avg_latency,
                    "success_rate": m.success_rate,
                    "active_connections": m.active_connections
                }
                for mid, m in self.models.items()
            }
        }


# ==================== 真实API测试 ====================

async def test_router_with_real_api():
    """使用真实API测试路由器"""
    import requests
    
    API_URL = "https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions"
    API_KEY = "your-api-key-here"  # 需替换
    
    # 创建路由器
    router = MatrixRouter(strategy="weighted_round_robin")
    
    # 注册测试模型
    test_models = [
        ModelInfo(
            model_id="ep-test-1",
            model_name="ep-code-latest",
            provider="volcengine",
            api_url=API_URL,
            api_key=API_KEY,
            weight=100,
            priority=1
        ),
        ModelInfo(
            model_id="ep-test-2", 
            model_name="ep-reasoning",
            provider="volcengine",
            api_url=API_URL,
            api_key=API_KEY,
            weight=80,
            priority=2
        )
    ]
    
    for model in test_models:
        router.register_model(model)
    
    # 测试路由
    test_prompts = [
        "写一个Python函数",
        "解释一下机器学习",
        "给我讲个故事",
        "计算一下 123 * 456",
        "如何学习编程"
    ]
    
    for prompt in test_prompts:
        model = router.select_model(prompt)
        if model:
            print(f"Prompt: {prompt[:20]}... -> Model: {model.model_name}")
            
            # 模拟API调用
            start = time.time()
            try:
                # 真实API调用 (注释掉以避免实际请求)
                # headers = {"Authorization": f"Bearer {model.api_key}"}
                # resp = requests.post(model.api_url, headers=headers, 
                #                     json={"model": model.model_name, 
                #                           "messages": [{"role": "user", "content": prompt}]})
                latency = time.time() - start
                router.record_success(model.model_id, latency)
            except Exception as e:
                router.record_failure(model.model_id)
                print(f"  Error: {e}")
    
    # 输出统计
    stats = router.get_stats()
    print("\n=== 路由测试结果 ===")
    print(f"总路由次数: {stats['total_routes']}")
    print(f"平均延迟: {stats['avg_latency']:.3f}s")
    print("\n模型分布:")
    for mid, info in stats['models'].items():
        print(f"  {info['name']}: {info['active_connections']} 连接, "
              f"延迟 {info['avg_latency']:.2f}s, "
              f"成功率 {info['success_rate']*100:.0f}%")


if __name__ == "__main__":
    asyncio.run(test_router_with_real_api())
