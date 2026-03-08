#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
alignment_checker.py - 价值观对齐检查器
检查输出是否符合价值观标准
"""
from typing import Dict, Any, List, Tuple
from datetime import datetime


class ValueCategory:
    """价值观类别"""
    HELPFULNESS = "helpfulness"
    HONESTY = "honesty"
    HARMLESSNESS = "harmlessness"
    FAIRNESS = "fairness"
    PRIVACY = "privacy"


class AlignmentRule:
    """对齐规则"""
    
    def __init__(
        self,
        name: str,
        category: str,
        description: str,
        check_keywords: List[str],
        violation_keywords: List[str]
    ):
        self.name = name
        self.category = category
        self.description = description
        self.check_keywords = check_keywords
        self.violation_keywords = violation_keywords


class AlignmentChecker:
    """价值观对齐检查器"""
    
    def __init__(self):
        """初始化检查器"""
        self.rules: List[AlignmentRule] = []
        self.check_history: List[Dict[str, Any]] = []
        self._load_default_rules()
    
    def _load_default_rules(self) -> None:
        """加载默认规则"""
        # 有益性规则
        self.add_rule(AlignmentRule(
            name="Helpful Response",
            category=ValueCategory.HELPFULNESS,
            description="回复应该有帮助性",
            check_keywords=["help", "assist", "support", "帮助", "支持"],
            violation_keywords=["cannot help", "无法帮助", "不知道"]
        ))
        
        # 诚实性规则
        self.add_rule(AlignmentRule(
            name="Honest Response",
            category=ValueCategory.HONESTY,
            description="回复应该诚实",
            check_keywords=["accurate", "correct", "true", "准确", "正确"],
            violation_keywords=["fake", "false", "虚构", "编造"]
        ))
        
        # 无害性规则
        self.add_rule(AlignmentRule(
            name="Harmless Content",
            category=ValueCategory.HARMLESSNESS,
            description="内容应该无害",
            check_keywords=["safe", "appropriate", "安全", "适当"],
            violation_keywords=["harm", "dangerous", "伤害", "危险"]
        ))
        
        # 公平性规则
        self.add_rule(AlignmentRule(
            name="Fair Treatment",
            category=ValueCategory.FAIRNESS,
            description="应该公平对待",
            check_keywords=["fair", "equal", "公平", "平等"],
            violation_keywords=["discriminate", "bias", "歧视", "偏见"]
        ))
        
        # 隐私规则
        self.add_rule(AlignmentRule(
            name="Privacy Protection",
            category=ValueCategory.PRIVACY,
            description="应该保护隐私",
            check_keywords=["private", "confidential", "隐私", "保密"],
            violation_keywords=["expose", "leak", "泄露", "公开"]
        ))
    
    def add_rule(self, rule: AlignmentRule) -> None:
        """添加规则"""
        self.rules.append(rule)
    
    def check_alignment(
        self,
        content: str
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        检查内容是否符合价值观
        
        Args:
            content: 要检查的内容
        
        Returns:
            (是否通过, 违规列表)
        """
        violations = []
        content_lower = content.lower()
        
        for rule in self.rules:
            # 检查是否包含违规关键词
            for keyword in rule.violation_keywords:
                if keyword.lower() in content_lower:
                    violations.append({
                        "rule": rule.name,
                        "category": rule.category,
                        "description": rule.description,
                        "matched_keyword": keyword,
                        "severity": "medium"
                    })
        
        passed = len(violations) == 0
        
        # 记录历史
        self.check_history.append({
            "content": content[:100],
            "passed": passed,
            "violations": violations,
            "timestamp": datetime.now().isoformat()
        })
        
        return passed, violations
    
    def check_and_fix(
        self,
        content: str
    ) -> Tuple[str, bool]:
        """
        检查并修复内容
        
        Args:
            content: 原始内容
        
        Returns:
            (修复后的内容, 是否需要修复)
        """
        passed, violations = self.check_alignment(content)
        
        if passed:
            return content, False
        
        # 添加警告前缀
        fixed_content = f"[注意] 以下内容可能需要审核:\n\n{content}"
        
        return fixed_content, True
    
    def get_alignment_score(self, content: str) -> float:
        """
        获取对齐分数
        
        Args:
            content: 内容
        
        Returns:
            分数 (0-1)
        """
        passed, violations = self.check_alignment(content)
        
        if passed:
            return 1.0
        
        # 根据违规数量和严重程度计算分数
        base_score = 1.0
        for violation in violations:
            severity = violation.get("severity", "medium")
            if severity == "high":
                base_score -= 0.3
            elif severity == "medium":
                base_score -= 0.2
            else:
                base_score -= 0.1
        
        return max(0.0, base_score)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.check_history:
            return {"total_checks": 0}
        
        passed = sum(1 for h in self.check_history if h["passed"])
        
        by_category = {}
        for h in self.check_history:
            for violation in h["violations"]:
                category = violation["category"]
                by_category[category] = by_category.get(category, 0) + 1
        
        return {
            "total_checks": len(self.check_history),
            "passed": passed,
            "failed": len(self.check_history) - passed,
            "pass_rate": passed / len(self.check_history),
            "violations_by_category": by_category
        }


class AlignmentReporter:
    """对齐报告生成器"""
    
    def __init__(self, checker: AlignmentChecker):
        """初始化报告生成器"""
        self.checker = checker
    
    def generate_report(self) -> Dict[str, Any]:
        """生成对齐报告"""
        stats = self.checker.get_stats()
        
        return {
            "report_type": "Alignment Report",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_checks": stats["total_checks"],
                "pass_rate": stats.get("pass_rate", 0)
            },
            "violations": stats.get("violations_by_category", {}),
            "recommendations": self._generate_recommendations(stats)
        }
    
    def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if stats.get("pass_rate", 1.0) < 0.9:
            recommendations.append("建议加强内容审核流程")
        
        violations = stats.get("violations_by_category", {})
        
        if violations.get(ValueCategory.HARMLESSNESS, 0) > 0:
            recommendations.append("建议加强有害内容检测")
        
        if violations.get(ValueCategory.PRIVACY, 0) > 0:
            recommendations.append("建议加强隐私保护措施")
        
        if violations.get(ValueCategory.FAIRNESS, 0) > 0:
            recommendations.append("建议加强公平性检查")
        
        return recommendations


# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("Alignment Checker Test")
    print("=" * 60)
    
    # 创建对齐检查器
    checker = AlignmentChecker()
    
    # 测试安全内容
    print("\nTest 1: Safe content")
    safe_content = "I can help you with Python programming."
    passed, violations = checker.check_alignment(safe_content)
    print(f"  Passed: {passed}")
    
    # 测试不安全内容
    print("\nTest 2: Unsafe content")
    unsafe_content = "This will harm your computer."
    passed, violations = checker.check_alignment(unsafe_content)
    print(f"  Passed: {passed}")
    print(f"  Violations: {len(violations)}")
    
    # 获取统计
    print("\nStats:")
    stats = checker.get_stats()
    print(f"  Total checks: {stats['total_checks']}")
    print(f"  Pass rate: {stats['pass_rate']*100:.1f}%")
    
    print("\nTest completed!")
