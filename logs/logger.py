"""
序境内核 - 日志记录
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class LogEntry:
    level: str
    message: str
    timestamp: float = field(default_factory=time.time)
    model_name: str = ""
    provider: str = ""
    tokens: int = 0
    user_id: str = ""


class XujingLogger:
    def __init__(self, max_entries: int = 10000):
        self.max_entries = max_entries
        self.entries: List[LogEntry] = []
    
    def log(self, level: str, message: str, model_name: str = "", provider: str = "", tokens: int = 0, user_id: str = ""):
        entry = LogEntry(level=level, message=message, model_name=model_name, provider=provider, tokens=tokens, user_id=user_id)
        self.entries.append(entry)
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
        logger.info(f"[{level}] {message} | model:{model_name} tokens:{tokens}")
    
    def log_dispatch(self, model_name: str, provider: str, tokens: int, user_id: str = ""):
        self.log("info", "调度完成", model_name=model_name, provider=provider, tokens=tokens, user_id=user_id)
    
    def query(self, model_name: Optional[str] = None, provider: Optional[str] = None, limit: int = 100) -> List[Dict]:
        results = self.entries
        if model_name:
            results = [e for e in results if e.model_name == model_name]
        if provider:
            results = [e for e in results if e.provider == provider]
        results = results[-limit:]
        return [{"timestamp": e.timestamp, "level": e.level, "message": e.message, "model_name": e.model_name, "provider": e.provider, "tokens": e.tokens} for e in results]
    
    def get_summary(self) -> Dict:
        return {"total": len(self.entries), "total_tokens": sum(e.tokens for e in self.entries)}


_logger: Optional[XujingLogger] = None


def get_logger() -> XujingLogger:
    global _logger
    if _logger is None:
        _logger = XujingLogger()
    return _logger
