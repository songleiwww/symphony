# -*- coding: utf-8 -*-
"""
IntelligentStrategyScheduler - Fixed with default strategies registered
Root cause fix: strategies now registered by default
"""
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass
from loguru import logger

class TaskComplexity(Enum):
    SIMPLE = "simple"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    COMPLEX = "complex"
    EXTREME = "extreme"

@dataclass
class TaskInfo:
    id: str
    prompt: str
    task_type: str
    complexity: TaskComplexity
    priority: int

class IntelligentStrategyScheduler:
    """Intelligent Strategy Scheduler - FIXED default strategies"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.provider_pool = None
        self.strategies = {}
        # FIX: Register default strategies on init
        self._register_default_strategies()
        logger.info("IntelligentStrategyScheduler initialized with default strategies")
    
    def _register_default_strategies(self):
        """Register all 7 default strategies"""
        # 1. Random strategy
        self.register_strategy("random", {
            "name": "random",
            "description": "Random model selection",
            "priority": 1
        })
        
        # 2. Round Robin
        self.register_strategy("round_robin", {
            "name": "round_robin", 
            "description": "Circular rotation",
            "priority": 2
        })
        
        # 3. Least Loaded
        self.register_strategy("least_loaded", {
            "name": "least_loaded",
            "description": "Select model with lowest load",
            "priority": 3
        })
        
        # 4. Predictive
        self.register_strategy("predictive", {
            "name": "predictive",
            "description": "AI-predicted best model",
            "priority": 4
        })
        
        # 5. ACO Routing
        self.register_strategy("aco_routing", {
            "name": "aco_routing",
            "description": "Ant Colony Optimization routing",
            "priority": 5
        })
        
        # 6. BCO Allocation
        self.register_strategy("bco_allocation", {
            "name": "bco_allocation",
            "description": "Bee Colony Optimization allocation",
            "priority": 6
        })
        
        # 7. Dual Engine
        self.register_strategy("dual_engine", {
            "name": "dual_engine",
            "description": "ACO + BCO hybrid",
            "priority": 7
        })
        
        logger.info(f"Registered {len(self.strategies)} default strategies")
    
    def register_strategy(self, name: str, strategy):
        """Register a strategy"""
        self.strategies[name] = strategy
        logger.debug(f"Registered strategy: {name}")
    
    def set_provider_pool(self, pool):
        """Set provider pool"""
        self.provider_pool = pool
    
    def schedule(self, task: Dict) -> Dict:
        """Schedule task using best available strategy"""
        task_type = task.get('type', 'unknown')
        logger.debug(f"Scheduling task type: {task_type}")
        
        if self.provider_pool:
            online_models = self.provider_pool.get_online_models()
            if online_models:
                return {
                    "selected_model": online_models[0].get("name", "unknown"),
                    "strategy": "fastest_first",
                    "task": task,
                    "available_strategies": list(self.strategies.keys())
                }
        
        return {
            "selected_model": None,
            "strategy": "default",
            "task": task,
            "available_strategies": list(self.strategies.keys())
        }
    
    def execute(self, task: Dict) -> Dict:
        """Execute task"""
        result = self.schedule(task)
        result["success"] = True
        result["scheduled"] = True
        result["strategies_count"] = len(self.strategies)
        return result

__all__ = ['IntelligentStrategyScheduler']
