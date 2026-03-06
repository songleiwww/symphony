#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rate Limit Tracker - Multi-Model API Management
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import time
import json

class RateLimitType(Enum):
    HOURLY = "hourly"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SLIDING = "sliding"

class ModelAvailability(Enum):
    AVAILABLE = "available"
    RATE_LIMITED = "rate_limited"
    DISABLED = "disabled"

@dataclass
class RateLimitInfo:
    """Rate limit information for a model"""
    provider: str
    model_id: str
    limit_type: RateLimitType
    limit_value: int
    current_usage: int = 0
    reset_time: Optional[datetime] = None
    last_check: Optional[datetime] = None

@dataclass
class TrackedModel:
    """Model being tracked for rate limits"""
    model_id: str
    provider: str
    availability: ModelAvailability = ModelAvailability.AVAILABLE
    rate_limits: List[RateLimitInfo] = field(default_factory=list)
    error_count: int = 0
    last_error: Optional[str] = None
    recovery_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class RateLimitTracker:
    """Track rate limits for multi-model API management"""
    
    def __init__(self):
        self._tracked_models: Dict[str, TrackedModel] = {}
        self._history: List[Dict] = []
    
    def register_model(
        self,
        model_id: str,
        provider: str,
        limits: List[Dict[str, Any]]
    ):
        """Register a model with rate limit info"""
        rate_limits = []
        for limit in limits:
            rate_limits.append(RateLimitInfo(
                provider=provider,
                model_id=model_id,
                limit_type=RateLimitType(limit.get("type", "hourly")),
                limit_value=limit.get("value", 0),
                reset_time=limit.get("reset_time")
            ))
        
        self._tracked_models[model_id] = TrackedModel(
            model_id=model_id,
            provider=provider,
            rate_limits=rate_limits
        )
    
    def mark_rate_limited(
        self,
        model_id: str,
        error_code: str,
        reset_time: Optional[datetime] = None
    ):
        """Mark model as rate limited"""
        if model_id not in self._tracked_models:
            return
        
        model = self._tracked_models[model_id]
        model.availability = ModelAvailability.RATE_LIMITED
        model.error_count += 1
        model.last_error = error_code
        
        # Calculate recovery time
        if reset_time:
            model.recovery_time = reset_time
        else:
            # Default: assume 1 hour for hourly limits
            model.recovery_time = datetime.now() + timedelta(hours=1)
        
        self._history.append({
            "time": datetime.now().isoformat(),
            "model_id": model_id": "rate_limited",
            ",
            "actionreset_time": model.recovery_time.isoformat() if model.recovery_time else None
        })
    
    def mark_available(self, model_id: str):
        """Mark model as available again"""
        if model_id not in self._tracked_models:
            return
        
        model = self._tracked_models[model_id]
        model.availability = ModelAvailability.AVAILABLE
        model.recovery_time = None
        
        self._history.append({
            "time": datetime.now().isoformat(),
            "model_id": model_id,
            "action": "available"
        })
    
    def get_status(self, model_id: str) -> Optional[Dict]:
        """Get status of a model"""
        if model_id not in self._tracked_models:
            return None
        
        model = self._tracked_models[model_id]
        return {
            "model_id": model.model_id,
            "provider": model.provider,
            "availability": model.availability.value,
            "recovery_time": model.recovery_time.isoformat() if model.recovery_time else None,
            "time_to_recovery": self._get_time_to_recovery(model),
            "error_count": model.error_count,
            "last_error": model.last_error
        }
    
    def _get_time_to_recovery(self, model: TrackedModel) -> Optional[int]:
        """Get seconds until recovery"""
        if not model.recovery_time:
            return None
        delta = model.recovery_time - datetime.now()
        return max(0, int(delta.total_seconds()))
    
    def get_all_status(self) -> List[Dict]:
        """Get status of all tracked models"""
        return [
            self.get_status(model_id)
            for model_id in self._tracked_models.keys()
        ]
    
    def get_available_models(self) -> List[str]:
        """Get list of available model IDs"""
        return [
            model_id for model_id, model in self._tracked_models.items()
            if model.availability == ModelAvailability.AVAILABLE
        ]
    
    def check_and_recover(self) -> List[str]:
        """Check and recover rate-limited models"""
        recovered = []
        now = datetime.now()
        
        for model_id, model in self._tracked_models.items():
            if model.availability == ModelAvailability.RATE_LIMITED:
                if model.recovery_time and now >= model.recovery_time:
                    self.mark_available(model_id)
                    recovered.append(model_id)
        
        return recovered
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """Get recent history"""
        return self._history[-limit:]


# Example usage
if __name__ == "__main__":
    tracker = RateLimitTracker()
    
    # Register volcengine models
    tracker.register_model(
        "ark-code-latest",
        "volcengine",
        [
            {"type": "sliding", "value": 1200, "reset_time": None},  # 5小时1200次
            {"type": "weekly", "value": 9000, "reset_time": "2026-03-09T00:00:00"},
            {"type": "monthly", "value": 18000, "reset_time": "2026-04-01T00:00:00"}
        ]
    )
    
    # Mark as rate limited
    tracker.mark_rate_limited(
        "ark-code-latest",
        "AccountQuotaExceeded",
        datetime(2026, 3, 9, 0, 0, 0)
    )
    
    # Check status
    status = tracker.get_status("ark-code-latest")
    print(json.dumps(status, indent=2, ensure_ascii=False, default=str))
