
"""
Symphony Test Framework - 测试框架
"""
import pytest
import unittest
from unittest.mock import Mock, patch

class TestFaultIsolator(unittest.TestCase):
    """故障隔离器测试"""
    
    def test_circuit_breaker_opens_after_failures(self):
        """测试熔断器在失败后打开"""
        from fault_isolator import CircuitBreaker
        
        cb = CircuitBreaker(failure_threshold=3, timeout=60)
        
        def failing_func():
            raise Exception("Test error")
        
        for _ in range(3):
            try:
                cb.call(failing_func)
            except:
                pass
        
        self.assertEqual(cb.state, "OPEN")
    
    def test_isolate_decorator(self):
        """测试隔离装饰器"""
        from fault_isolator import isolate
        
        @isolate(max_retries=2)
        def test_func():
            if not hasattr(test_func, 'called'):
                test_func.called = True
                raise Exception("First call fails")
            return "success"
        
        result = test_func()
        self.assertEqual(result, "success")

class TestFallback(unittest.TestCase):
    """降级策略测试"""
    
    def test_fallback_execution(self):
        """测试降级执行"""
        from fallback_manager import fallback_manager, with_fallback
        
        def primary_func():
            raise Exception("Primary failed")
        
        def fallback_func():
            return "fallback result"
        
        fallback_manager.register("test", fallback_func)
        
        @with_fallback("test")
        def decorated_func():
            return primary_func()
        
        result = decorated_func()
        self.assertEqual(result, "fallback result")

if __name__ == "__main__":
    unittest.main()
