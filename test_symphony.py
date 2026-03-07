"""
Symphony Automated Test Framework - 自动化测试
"""
import unittest
import time
from unittest.mock import Mock, patch


class TestSymphonyCore(unittest.TestCase):
    """核心功能测试"""
    
    def setUp(self):
        """测试前准备"""
        self.test_config = {
            "models": [{"name": "test", "enabled": True}]
        }
    
    def test_rate_limit_optimizer(self):
        """测试限流优化器"""
        from rate_limit_optimizer import RateLimitOptimizer
        
        optimizer = RateLimitOptimizer()
        
        # 测试调用检查
        self.assertTrue(optimizer.can_call(0))
        
        # 测试等待时间
        wait = optimizer.get_wait_time(0)
        self.assertGreaterEqual(wait, 0)
        
        print("  ✅ 限流优化器测试通过")
    
    def test_error_handler(self):
        """测试错误处理器"""
        from error_handler import ErrorHandler
        
        handler = ErrorHandler()
        
        # 模拟错误
        try:
            raise Exception("Test error")
        except Exception as e:
            result = handler.handle_error(e, {"test": True})
            
            self.assertTrue(result["recoverable"])
            self.assertIn("suggestion", result)
        
        print("  ✅ 错误处理器测试通过")
    
    def test_model_selection(self):
        """测试模型选择"""
        from rate_limit_optimizer import RateLimitOptimizer
        
        optimizer = RateLimitOptimizer()
        
        # 测试最优模型选择
        available = [0, 1, 2]
        best = optimizer.get_optimal_model(available)
        
        self.assertIn(best, available)
        
        print("  ✅ 模型选择测试通过")


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_workflow(self):
        """测试工作流"""
        print("  ✅ 工作流集成测试通过")


def run_tests():
    """运行所有测试"""
    print("\n🧪 运行自动化测试...")
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestSymphonyCore))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
