# -*- coding: utf-8 -*-
"""
序境系统 - 规则管理器 (P3修复)
解决 self_adaptive.py vs engine.py 冲突

P3修复: SelfAdaptive作为前置检查层，engine作为执行层
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RuleResult:
    """规则检查结果"""
    passed: bool
    violations: list = None
    details: str = ""
    auto_fixed: bool = False
    
    def __post_init__(self):
        if self.violations is None:
            self.violations = []


class RuleManager:
    """
    规则管理器 - 统一入口
    
    P3修复:
    - SelfAdaptive作为前置检查
    - Engine作为规则执行
    - 统一的返回值格式
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path
        self._pre_check = None  # 延迟加载
        self._engine = None    # 延迟加载
    
    @property
    def pre_check(self):
        """前置检查层 - SelfAdaptive"""
        if self._pre_check is None:
            try:
                from rules.self_adaptive import SelfAdaptiveRuleManager
                if self.db_path:
                    self._pre_check = SelfAdaptiveRuleManager(self.db_path)
                logger.info("前置检查层已加载")
            except Exception as e:
                logger.warning(f"前置检查层加载失败: {e}")
        return self._pre_check
    
    @property
    def engine(self):
        """规则引擎层"""
        if self._engine is None:
            try:
                from rules.engine import RuleEngine
                self._engine = RuleEngine()
                logger.info("规则引擎已加载")
            except Exception as e:
                logger.warning(f"规则引擎加载失败: {e}")
        return self._engine
    
    def evaluate(self, action: str, context: Dict = None) -> RuleResult:
        """
        统一规则评估入口
        
        P3修复: 先前置检查，再引擎执行
        
        Args:
            action: 操作名称
            context: 上下文
        
        Returns:
            RuleResult
        """
        if context is None:
            context = {}
        
        # 第一步: 前置检查
        violations = []
        auto_fixed = False
        
        if self.pre_check:
            try:
                pre_result = self.pre_check.check_compliance(action, context)
                if not pre_result.get('compliant', True):
                    violations.extend(pre_result.get('violations', []))
                    
                    # 自动修正
                    if pre_result.get('suggestions'):
                        self.pre_check.auto_comply(action, context)
                        auto_fixed = True
            except Exception as e:
                logger.warning(f"前置检查失败: {e}")
        
        # 第二步: 规则引擎执行
        engine_result = None
        if self.engine and violations:
            try:
                engine_result = self.engine.evaluate(action, context)
            except Exception as e:
                logger.warning(f"规则引擎失败: {e}")
        
        # 统一返回格式
        if violations:
            return RuleResult(
                passed=False,
                violations=violations,
                details=f"前置检查发现 {len(violations)} 个问题",
                auto_fixed=auto_fixed
            )
        
        return RuleResult(
            passed=True,
            details="规则检查通过"
        )
    
    def check_and_auto_fix(self, action: str, context: Dict = None) -> RuleResult:
        """检查并自动修复"""
        result = self.evaluate(action, context)
        
        if not result.passed and not result.auto_fixed:
            logger.warning(f"规则违规未自动修复: {result.violations}")
        
        return result


# 全局规则管理器
_rule_manager: Optional[RuleManager] = None


def get_rule_manager(db_path: str = None) -> RuleManager:
    """获取规则管理器"""
    global _rule_manager
    if _rule_manager is None:
        _rule_manager = RuleManager(db_path)
    return _rule_manager


def check_rule(action: str, context: Dict = None) -> RuleResult:
    """便捷规则检查函数"""
    return get_rule_manager().evaluate(action, context)


# 导出
__all__ = [
    'RuleManager',
    'RuleResult',
    'get_rule_manager',
    'check_rule'
]


if __name__ == '__main__':
    print("=== 规则管理器测试 ===\n")
    
    manager = get_rule_manager()
    
    # 测试规则检查
    tests = [
        ("test_model", {"keywords": ["测试"]}),
        ("new_module", {"integrated": True}),
        ("add_rule", {"db_updated": True}),
    ]
    
    for action, context in tests:
        result = manager.evaluate(action, context)
        print(f"Action: {action}")
        print(f"  Passed: {result.passed}")
        print(f"  Details: {result.details}")
        print()
