#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rate Limit Auto-Recovery Scheduler
"""
import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
import threading

class ModelStatus(Enum):
    ACTIVE = "active"
    RATE_LIMITED = "rate_limited"
    RECOVERING = "recovering"
    ERROR = "error"

@dataclass
class ModelInfo:
    model_id: str
    provider: str
    api_key: str
    rate_limit_reset_time: Optional[datetime] = None
    status: ModelStatus = ModelStatus.ACTIVE
    check_interval: int = 300  # 5 minutes default
    failed_checks: int = 0
    recovery_callback: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class RateLimitScheduler:
    """Auto-recovery scheduler for rate-limited models"""
    
    def __init__(self, default_check_interval: int = 300, max_backoff: int = 3600):
        self.default_check_interval = default_check_interval
        self.max_backoff = max_backoff
        self.models: Dict[str, ModelInfo] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        self._callbacks: List[Callable] = []
    
    def register_model(
        self,
        model_id: str,
        provider: str,
        api_key: str,
        check_interval: int = None,
        recovery_callback: Callable = None
    ):
        """Register a model for tracking"""
        with self._lock:
            self.models[model_id] = ModelInfo(
                model_id=model_id,
                provider=provider,
                api_key=api_key,
                check_interval=check_interval or self.default_check_interval,
                recovery_callback=recovery_callback
            )
            self.logger.info(f"Registered model: {model_id}")
    
    def mark_rate_limited(
        self,
        model_id: str,
        reset_time: Optional[datetime] = None
    ):
        """Mark model as rate limited"""
        with self._lock:
            if model_id not in self.models:
                return
            
            model = self.models[model_id]
            model.status = ModelStatus.RATE_LIMITED
            
            if reset_time:
                model.rate_limit_reset_time = reset_time
            else:
                # Default: check again in 5 minutes
                model.rate_limit_reset_time = datetime.now() + timedelta(minutes=5)
            
            # Increase check interval with backoff
            model.check_interval = min(
                model.check_interval * 2,
                self.max_backoff
            )
            self.logger.warning(
                f"Model {model_id} rate limited. "
                f"Will retry at {model.rate_limit_reset_time}"
            )
    
    def add_recovery_callback(self, callback: Callable):
        """Add callback for model recovery events"""
        self._callbacks.append(callback)
    
    def _notify_recovery(self, model_id: str):
        """Notify about model recovery"""
        for callback in self._callbacks:
            try:
                callback(model_id)
            except Exception as e:
                self.logger.error(f"Callback error: {e}")
    
    def check_and_recover(self) -> List[str]:
        """Check all models and recover if possible"""
        recovered = []
        now = datetime.now()
        
        with self._lock:
            for model_id, model in self.models.items():
                if model.status == ModelStatus.RATE_LIMITED:
                    if model.rate_limit_reset_time and now >= model.rate_limit_reset_time:
                        model.status = ModelStatus.RECOVERING
                        
                        # Try to verify recovery with a test call
                        if self._test_model(model):
                            model.status = ModelStatus.ACTIVE
                            model.rate_limit_reset_time = None
                            model.check_interval = self.default_check_interval
                            model.failed_checks = 0
                            recovered.append(model_id)
                            self._notify_recovery(model_id)
                            self.logger.info(f"Model {model_id} recovered!")
                        else:
                            model.failed_checks += 1
                            model.status = ModelStatus.RATE_LIMITED
                            # Schedule next check
                            model.rate_limit_reset_time = now + timedelta(
                                seconds=model.check_interval
                            )
                            self.logger.warning(
                                f"Model {model_id} check failed, "
                                f"retry at {model.rate_limit_reset_time}"
                            )
        
        return recovered
    
    def _test_model(self, model: ModelInfo) -> bool:
        """Test if model is available (placeholder - implement actual test)"""
        # In real implementation, make a simple API call to test
        return True
    
    def start(self):
        """Start the scheduler"""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self.logger.info("Rate limit scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        self.logger.info("Rate limit scheduler stopped")
    
    def _run_loop(self):
        """Main loop"""
        while self._running:
            try:
                recovered = self.check_and_recover()
                if recovered:
                    self.logger.info(f"Recovered models: {recovered}")
            except Exception as e:
                self.logger.error(f"Check error: {e}")
            
            time.sleep(60)  # Check every minute
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all tracked models"""
        with self._lock:
            return {
                model_id: {
                    "status": m.status.value,
                    "rate_limit_reset_time": m.rate_limit_reset_time.isoformat() if m.rate_limit_reset_time else None,
                    "check_interval": m.check_interval,
                    "failed_checks": m.failed_checks
                }
                for model_id, m in self.models.items()
            }
    
    def get_available_models(self) -> List[str]:
        """Get list of available model IDs"""
        with self._lock:
            return [
                model_id for model_id, m in self.models.items()
                if m.status == ModelStatus.ACTIVE
            ]


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scheduler = RateLimitScheduler(default_check_interval=300)
    
    def on_recovery(model_id):
        print(f"Model recovered: {model_id}")
    
    scheduler.add_recovery_callback(on_recovery)
    
    # Register models
    scheduler.register_model(
        "ark-code-latest",
        "volcengine",
        "your-api-key"
    )
    
    # Mark as rate limited
    scheduler.mark_rate_limited(
        "ark-code-latest",
        reset_time=datetime.now() + timedelta(hours=1)
    )
    
    # Start scheduler
    scheduler.start()
    
    # Check status
    print(scheduler.get_status())
    
    # Stop after 5 seconds for demo
    time.sleep(5)
    scheduler.stop()
