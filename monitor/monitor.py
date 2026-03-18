"""
序境内核 - 实时监控
"""

import time
from typing import Dict, Optional
from dataclasses import dataclass, field
from collections import deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class Metric:
    name: str
    value: float
    timestamp: float = field(default_factory=time.time)
    tags: Dict = field(default_factory=dict)


class Monitor:
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.metrics: Dict[str, deque] = {}
        self.alerts: list = []
    
    def record(self, name: str, value: float, tags: Optional[Dict] = None):
        if name not in self.metrics:
            self.metrics[name] = deque(maxlen=self.history_size)
        self.metrics[name].append(Metric(name=name, value=value, tags=tags or {}))
    
    def get_latest(self, name: str) -> Optional[float]:
        if name not in self.metrics or not self.metrics[name]:
            return None
        return self.metrics[name][-1].value
    
    def get_stats(self) -> Dict:
        return {
            "metrics": list(self.metrics.keys()),
            "alerts_count": len(self.alerts),
            "latest": {name: self.get_latest(name) for name in self.metrics.keys()}
        }


_monitor: Optional[Monitor] = None


def get_monitor() -> Monitor:
    global _monitor
    if _monitor is None:
        _monitor = Monitor()
    return _monitor
