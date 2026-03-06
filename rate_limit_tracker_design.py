To solve this problem, we need to design a rate limit tracking system for managing multi-model API usage across different providers. The system should track rate limits per provider and model, handle different types of limits (hourly, weekly, monthly), detect 429 errors, calculate recovery times, and provide a status check API.

### Approach
1. **Data Structures**: Use dataclasses to represent rate limit records and model status. Each `RateLimitRecord` stores details like limit type, value, reset time, and current usage. The `ModelStatus` class aggregates these records along with availability status and recovery time.
2. **Rate Limit Tracking**: Maintain a nested dictionary structure where the outer key is the provider and the inner key is the model, mapping to `ModelStatus` instances.
3. **Handling 429 Errors**: When a 429 error is encountered, the corresponding model is marked as unavailable, and the recovery time is set based on the provided reset timestamp.
4. **Status Check API**: The `get_status` method checks if the recovery time has passed and updates the availability status accordingly. It returns a detailed status report for the specified model.

### Solution Code
```python
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

@dataclass
class RateLimitRecord:
    limit_type: str  # 'hourly', 'weekly', 'monthly'
    limit_value: int
    reset_time: float  # Unix timestamp
    current_usage: int = 0

@dataclass
class ModelStatus:
    provider: str
    model: str
    rate_limits: Dict[str, RateLimitRecord] = field(default_factory=dict)
    available: bool = True
    recovery_time: float = 0.0  # Unix timestamp for when the model becomes available again

class RateLimitTracker:
    def __init__(self):
        self._store: Dict[str, Dict[str, ModelStatus]] = {}

    def _get_model_status(self, provider: str, model: str) -> Optional[ModelStatus]:
        return self._store.get(provider, {}).get(model)

    def add_rate_limit(
        self,
        provider: str,
        model: str,
        limit_type: str,
        limit_value: int,
        reset_time: float
    ) -> None:
        if provider not in self._store:
            self._store[provider] = {}
        if model not in self._store[provider]:
            self._store[provider][model] = ModelStatus(provider=provider, model=model)
        
        model_status = self._store[provider][model]
        model_status.rate_limits[limit_type] = RateLimitRecord(
            limit_type=limit_type,
            limit_value=limit_value,
            reset_time=reset_time
        )

    def update_usage(
        self,
        provider: str,
        model: str,
        limit_type: str,
        usage_increment: int
    ) -> None:
        model_status = self._get_model_status(provider, model)
        if not model_status:
            raise ValueError(f"No rate limits configured for provider: {provider}, model: {model}")
        
        if limit_type not in model_status.rate_limits:
            raise ValueError(f"Limit type {limit_type} not found for provider: {provider}, model: {model}")
        
        record = model_status.rate_limits[limit_type]
        record.current_usage += usage_increment

    def handle_429(
        self,
        provider: str,
        model: str,
        reset_time: float
    ) -> None:
        model_status = self._get_model_status(provider, model)
        if not model_status:
            raise ValueError(f"No rate limits configured for provider: {provider}, model: {model}")
        
        model_status.available = False
        model_status.recovery_time = reset_time

    def get_status(
        self,
        provider: str,
        model: str
    ) -> Dict[str, Union[bool, float, Dict[str, Dict[str, Union[int, float]]]]]:
        model_status = self._get_model_status(provider, model)
        if not model_status:
            raise ValueError(f"No rate limits configured for provider: {provider}, model: {model}")
        
        current_time = time.time()
        if not model_status.available and current_time >= model_status.recovery_time:
            model_status.available = True
            model_status.recovery_time = 0.0
        
        rate_limits_status = {}
        for limit_type, record in model_status.rate_limits.items():
            rate_limits_status[limit_type] = {
                'limit_value': record.limit_value,
                'reset_time': record.reset_time,
                'current_usage': record.current_usage
            }
        
        return {
            'available': model_status.available,
            'recovery_time': model_status.recovery_time if not model_status.available else 0.0,
            'rate_limits': rate_limits_status
        }
```

### Explanation
1. **Data Structures**:
   - `RateLimitRecord`: Stores details of a rate limit, including type, value, reset time, and current usage.
   - `ModelStatus`: Aggregates multiple rate limit records for a model, along with its availability status and recovery time.
   - `RateLimitTracker`: Manages a nested dictionary to store `ModelStatus` instances per provider and model.

2. **Key Methods**:
   - `add_rate_limit`: Adds a new rate limit record for a specific provider and model.
   - `update_usage`: Increments the current usage for a specified rate limit type.
   - `handle_429`: Marks a model as unavailable and sets its recovery time upon encountering a 429 error.
   - `get_status`: Provides the current status of a model, including availability, recovery time, and detailed rate limit usage. It automatically updates the availability status if the recovery time has passed.

This design efficiently tracks rate limits, handles errors, and provides a clear status API, ensuring robust multi-model API management.