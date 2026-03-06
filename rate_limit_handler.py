#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rate Limit Handler - Integration with BrainstormPanel
"""
import time
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

class ModelAvailability(Enum):
    AVAILABLE = "available"
    RATE_LIMITED = "rate_limited"
    DISABLED = "disabled"

@dataclass
class UsageStats:
    """Usage statistics for a model"""
    total_tokens: int = 0
    success_calls: int = 0
    error_calls: int = 0
    rate_limit_calls: int = 0
    last_call: Optional[datetime] = None

class RateLimitHandler:
    """Handle rate limits for BrainstormPanel integration"""
    
    def __init__(
        self,
        config: Dict[str, Any],
        on_rate_limit: Callable = None,
        on_recovery: Callable = None
    ):
        self.config = config
        self.on_rate_limit = on_rate_limit
        self.on_recovery = on_recovery
        
        # Model configuration
        self.primary_model = config.get("primary_model", "")
        self.backup_models = config.get("backup_models", [])
        self.default_cooldown = config.get("default_cooldown", 300)  # 5 minutes
        
        # State tracking
        self.model_usage: Dict[str, UsageStats] = {}
        self.rate_limited_models: Dict[str, datetime] = {}
        self._init_usage_stats()
    
    def _init_usage_stats(self):
        """Initialize usage statistics for all models"""
        models = [self.primary_model] + self.backup_models
        for model in models:
            if model:
                self.model_usage.setdefault(model, UsageStats())
    
    def before_call(self, model_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if model is available before making a call.
        Returns: (is_available, reason_if_not)
        """
        # Check if rate limited
        if model_id in self.rate_limited_models:
            reset_time = self.rate_limited_models[model_id]
            if datetime.now() < reset_time:
                remaining = int((reset_time - datetime.now()).total_seconds())
                return False, f"Rate limited, {remaining}s until reset"
            else:
                # Rate limit expired, clear it
                del self.rate_limited_models[model_id]
                if self.on_recovery:
                    self.on_recovery(model_id)
        
        return True, None
    
    def on_error(self, model_id: str, error: Exception, status_code: int = None):
        """
        Handle errors from model calls.
        Detect rate limit errors (429) and update tracking.
        """
        if model_id not in self.model_usage:
            self.model_usage[model_id] = UsageStats()
        
        stats = self.model_usage[model_id]
        stats.error_calls += 1
        
        # Check for rate limit (429)
        if status_code == 429:
            stats.rate_limit_calls += 1
            reset_time = datetime.now() + timedelta(seconds=self.default_cooldown)
            self.rate_limited_models[model_id] = reset_time
            
            if self.on_rate_limit:
                self.on_rate_limit(model_id, reset_time)
            
            return "rate_limited"
        
        return "error"
    
    def after_call(self, model_id: str, tokens_used: int = 0):
        """Update usage statistics after successful call"""
        if model_id not in self.model_usage:
            self.model_usage[model_id] = UsageStats()
        
        stats = self.model_usage[model_id]
        stats.success_calls += 1
        stats.total_tokens += tokens_used
        stats.last_call = datetime.now()
    
    def get_available_model(self) -> Optional[str]:
        """
        Get next available model.
        Tries primary first, then falls back to backups.
        """
        # Check primary
        if self.primary_model and self.primary_model not in self.rate_limited_models:
            return self.primary_model
        
        # Check backups
        for backup in self.backup_models:
            if backup and backup not in self.rate_limited_models:
                return backup
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            model: {
                "success_calls": stats.success_calls,
                "error_calls": stats.error_calls,
                "rate_limit_calls": stats.rate_limit_calls,
                "total_tokens": stats.total_tokens,
                "last_call": stats.last_call.isoformat() if stats.last_call else None,
                "is_rate_limited": model in self.rate_limited_models,
                "reset_time": self.rate_limited_models[model].isoformat() 
                    if model in self.rate_limited_models else None
            }
            for model, stats in self.model_usage.items()
        }
    
    def force_enable(self, model_id: str):
        """Manually enable a rate-limited model"""
        if model_id in self.rate_limited_models:
            del self.rate_limited_models[model_id]
    
    def force_disable(self, model_id: str, cooldown: int = None):
        """Manually disable a model for specified cooldown"""
        reset_time = datetime.now() + timedelta(seconds=cooldown or self.default_cooldown)
        self.rate_limited_models[model_id] = reset_time


# Example integration with BrainstormPanel
class BrainstormPanelWithRLH:
    """BrainstormPanel with rate limit handling"""
    
    def __init__(self, panel, config: Dict[str, Any]):
        self.panel = panel
        self.rlh = RateLimitHandler(
            config,
            on_rate_limit=self._on_rate_limit,
            on_recovery=self._on_recovery
        )
    
    def _on_rate_limit(self, model_id: str, reset_time: datetime):
        print(f"[RateLimit] Model {model_id} rate limited until {reset_time}")
    
    def _on_recovery(self, model_id: str):
        print(f"[RateLimit] Model {model_id} recovered!")
    
    def call_model(self, prompt: str, model_id: str = None, **kwargs) -> Any:
        """Call model with rate limit handling"""
        # Use provided model_id or get available
        target_model = model_id or self.rlh.get_available_model()
        
        # Check availability
        available, reason = self.rlh.before_call(target_model)
        if not available:
            # Try to get alternative
            alt_model = self.rlh.get_available_model()
            if alt_model:
                print(f"[RateLimit] Switching from {target_model} to {alt_model}")
                target_model = alt_model
            else:
                raise RuntimeError(f"No available models: {reason}")
        
        # Make the call
        try:
            result = self.panel.call_model(prompt, model_id=target_model, **kwargs)
            
            if result.success:
                self.rlh.after_call(target_model, result.tokens)
            else:
                # Check for rate limit in error
                if "429" in result.error or "rate limit" in result.error.lower():
                    self.rlh.on_error(target_model, Exception(result.error), 429)
            
            return result
            
        except Exception as e:
            # Check if it's a rate limit error
            error_str = str(e)
            if "429" in error_str or "rate limit" in error_str.lower():
                self.rlh.on_error(target_model, e, 429)
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get status including rate limit info"""
        return {
            "available_models": self.rlh.get_available_model(),
            "rate_limit_stats": self.rlh.get_stats()
        }
