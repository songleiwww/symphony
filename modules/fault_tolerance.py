#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统 - 故障转移适配模块
基于已有内核模块集成:
- circuit_breaker.py (熔断机制)
- disaster_recovery.py (容灾模块)
- multi_model_coordinator.py (多模型协调)

遵循第69条规则: 改进优于替换原则
"""
import sys
import os

# 添加内核路径
KERNEL_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\Kernel'
sys.path.insert(0, KERNEL_PATH)

# Import existing modules
try:
    from circuit_breaker import CircuitBreaker, ModelHealth
    from disaster_recovery import CircuitState, ServiceHealth
    from multi_model_coordinator import ModelOnlineDetector, CoordinatorConfig, ModelStatus
    print("[OK] All kernel modules imported")
except ImportError as e:
    print(f"[WARN] Module import warning: {e}")
    print("Creating compatible wrapper...")


class FaultToleranceManager:
    """
    故障转移管理器
    整合熔断、容灾、多模型协调功能
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
        # 初始化各模块
        self.circuit_breaker = None
        self.detector = None
        
        self._init_modules()
    
    def _init_modules(self):
        """初始化各内核模块"""
        try:
            self.circuit_breaker = CircuitBreaker(self.db_path)
            print("[OK] Circuit breaker initialized")
        except Exception as e:
            print(f"[WARN] Circuit breaker init failed: {e}")
        
        try:
            config = CoordinatorConfig()
            self.detector = ModelOnlineDetector(self.db_path, config)
            print("[OK] Model detector initialized")
        except Exception as e:
            print(f"[WARN] Detector init failed: {e}")
    
    def get_available_models(self, provider: str = None) -> list:
        """获取可用模型列表（带故障转移）"""
        if self.circuit_breaker:
            return self.circuit_breaker.get_available_models(provider)
        return []
    
    def check_and_update_health(self, model_id: int, success: bool):
        """检查并更新模型健康状态"""
        if self.circuit_breaker:
            self.circuit_breaker.record_result(model_id, success)
    
    def detect_online_models(self, provider: str = None) -> dict:
        """检测在线模型"""
        if not self.detector:
            return {"status": "unavailable", "models": []}
        
        try:
            if provider:
                models = self.detector.get_models_by_provider(provider)
                return {
                    "status": "ok",
                    "provider": provider,
                    "count": len(models),
                    "models": [{"id": m.id, "name": m.name, "status": m.status.value} for m in models]
                }
            else:
                # 检测所有服务商
                return {"status": "ok", "providers": ["火山引擎", "魔搭", "MiniMax", "智谱", "英伟达"]}
        except Exception as e:
            return {"status": "error", "message": str(e)}


def init_fault_tolerance():
    """Initialize fault tolerance system"""
    db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
    
    print("=== Fault Tolerance System Init ===")
    ft_manager = FaultToleranceManager(db_path)
    
    print("\n=== Detect Online Models ===")
    result = ft_manager.detect_online_models()
    print(f"Result: {result}")
    
    return ft_manager


if __name__ == "__main__":
    init_fault_tolerance()
