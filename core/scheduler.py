"""
序境内核 - 核心调度模块
基于序境系统总则构建
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ModelStatus(Enum):
    """模型状态 (总则第15条: 模型失效原则)"""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADE = "degrade"


@dataclass
class ModelConfig:
    """模型配置 (总则第12条: 模型配置表)"""
    model_id: str
    model_name: str
    provider: str
    api_url: str
    api_key: str
    weight: int = 1
    status: ModelStatus = ModelStatus.ONLINE
    fail_count: int = 0
    success_count: int = 0
    avg_latency: float = 0.0


@dataclass
class SchedulerConfig:
    """调度配置"""
    model_switch: int = 0
    lc_threshold: float = 0.3
    fail_threshold: int = 3


class Scheduler:
    """序境调度器 (总则第7/8条)"""
    
    def __init__(self, config: Optional[SchedulerConfig] = None):
        self.config = config or SchedulerConfig()
        self.models: Dict[str, ModelConfig] = {}
        self.stats = {"total_requests": 0, "total_tokens": 0, "by_model": {}, "by_provider": {}}
    
    def register_model(self, model: ModelConfig):
        """注册模型"""
        self.models[model.model_id] = model
        logger.info(f"注册模型: {model.model_name} ({model.provider})")
    
    def select_model(self) -> Optional[ModelConfig]:
        """选择模型"""
        available = [m for m in self.models.values() if m.status == ModelStatus.ONLINE]
        if not available:
            degraded = [m for m in self.models.values() if m.status == ModelStatus.DEGRADE]
            if degraded:
                return degraded[0]
            return None
        return min(available, key=lambda m: m.success_count / max(m.weight, 1))
    
    def on_success(self, model: ModelConfig, tokens: int, latency: float):
        """请求成功"""
        model.success_count += 1
        model.avg_latency = model.avg_latency * 0.9 + latency * 0.1
        model.fail_count = 0
        if model.status == ModelStatus.DEGRADE and model.avg_latency < self.config.lc_threshold * 1000:
            model.status = ModelStatus.ONLINE
        self.stats["total_requests"] += 1
        self.stats["total_tokens"] += tokens
        self.stats["by_model"][model.model_name] = self.stats["by_model"].get(model.model_name, 0) + tokens
        self.stats["by_provider"][model.provider] = self.stats["by_provider"].get(model.provider, 0) + tokens
    
    def on_fail(self, model: ModelConfig):
        """请求失败"""
        model.fail_count += 1
        if model.fail_count >= self.config.fail_threshold:
            model.status = ModelStatus.DEGRADE
            logger.warning(f"模型 {model.model_name} 已降级")
    
    def get_stats(self) -> Dict:
        return {
            "total_requests": self.stats["total_requests"],
            "total_tokens": self.stats["total_tokens"],
            "by_model": self.stats["by_model"],
            "by_provider": self.stats["by_provider"]
        }


_scheduler: Optional[Scheduler] = None


def get_scheduler() -> Scheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = Scheduler()
    return _scheduler
