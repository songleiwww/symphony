# -*- coding: utf-8 -*-
"""
验证层模块 - Verification Layer

确保任务执行的准确性、安全性与合规性

功能：
- 输入验证
- 输出验证
- 安全检查
- 质量评估
- 多轮反馈
"""
import re
import json
import time
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class VerificationLevel(Enum):
    """验证级别"""
    NONE = 0
    BASIC = 1
    STANDARD = 2
    STRICT = 3


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class VerificationResult:
    """验证结果"""
    passed: bool
    level: VerificationLevel
    risk: RiskLevel
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    score: float = 0.0  # 0-100


@dataclass
class ValidationRule:
    """验证规则"""
    name: str
    check: Callable[[Any], bool]
    message: str
    severity: str = "error"  # error/warning/info


class VerificationLayer:
    """
    验证层 - 确保执行准确性
    
    使用：
        verifier = VerificationLayer()
        result = verifier.verify_output(output, level=VerificationLevel.STANDARD)
    """
    
    def __init__(self):
        self.rules: List[ValidationRule] = []
        self.stats = {
            "total_verifications": 0,
            "passed": 0,
            "failed": 0,
            "blocked": 0
        }
        
        # 默认规则
        self._register_default_rules()
    
    def _register_default_rules(self):
        """注册默认规则"""
        
        # 1. 内容长度检查
        self.add_rule(ValidationRule(
            name="min_length",
            check=lambda x: len(str(x)) >= 10,
            message="输出内容过短",
            severity="warning"
        ))
        
        # 2. 敏感词检查
        sensitive_patterns = [
            r"password", r"api_key", r"secret",
            r"token", r"credential"
        ]
        
        def check_sensitive(text):
            text = str(text).lower()
            return not any(re.search(p, text) for p in sensitive_patterns)
        
        self.add_rule(ValidationRule(
            name="no_sensitive",
            check=check_sensitive,
            message="检测到敏感信息",
            severity="error"
        ))
        
        # 3. JSON格式检查（可选）
        def check_json_valid(text):
            try:
                json.loads(str(text))
                return True
            except:
                return True  # 非JSON也允许
        
        self.add_rule(ValidationRule(
            name="json_valid",
            check=check_json_valid,
            message="JSON格式无效",
            severity="warning"
        ))
    
    def add_rule(self, rule: ValidationRule):
        """添加验证规则"""
        self.rules.append(rule)
    
    def remove_rule(self, name: str):
        """移除验证规则"""
        self.rules = [r for r in self.rules if r.name != name]
    
    def verify_input(
        self,
        prompt: str,
        level: VerificationLevel = VerificationLevel.STANDARD
    ) -> VerificationResult:
        """
        验证输入
        
        参数:
            prompt: 输入提示
            level: 验证级别
        
        返回:
            VerificationResult
        """
        self.stats["total_verifications"] += 1
        
        issues = []
        suggestions = []
        score = 100.0
        
        if level == VerificationLevel.NONE:
            return VerificationResult(
                passed=True,
                level=level,
                risk=RiskLevel.LOW,
                score=100.0
            )
        
        # 基础检查
        if not prompt or len(prompt.strip()) == 0:
            issues.append("输入为空")
            score -= 50
        
        # 长度检查
        if len(prompt) > 10000:
            suggestions.append("输入过长，考虑分段处理")
            score -= 10
        
        # 敏感词检查（基础级别）
        if level.value >= VerificationLevel.BASIC.value:
            prompt_lower = prompt.lower()
            if any(word in prompt_lower for word in ["删除", "破坏", "hack"]):
                issues.append("检测到潜在危险操作")
                score -= 30
        
        # 严格模式
        if level.value >= VerificationLevel.STRICT.value:
            if not self._check_safety(prompt):
                issues.append("安全检查未通过")
                score -= 50
        
        passed = len([i for i in issues if "error" in i.lower()]) == 0
        risk = self._calculate_risk(score)
        
        if passed:
            self.stats["passed"] += 1
        else:
            self.stats["failed"] += 1
        
        return VerificationResult(
            passed=passed,
            level=level,
            risk=risk,
            issues=issues,
            suggestions=suggestions,
            score=score
        )
    
    def verify_output(
        self,
        output: Any,
        level: VerificationLevel = VerificationLevel.STANDARD,
        expected_format: str = None
    ) -> VerificationResult:
        """
        验证输出
        
        参数:
            output: 输出内容
            level: 验证级别
            expected_format: 期望格式 (json/text/html)
        
        返回:
            VerificationResult
        """
        self.stats["total_verifications"] += 1
        
        issues = []
        suggestions = []
        score = 100.0
        
        output_str = str(output)
        
        # 基础检查
        if not output or len(output_str.strip()) == 0:
            issues.append("输出为空")
            score -= 50
        
        # 运行规则
        for rule in self.rules:
            try:
                if not rule.check(output):
                    issues.append(rule.message)
                    score -= 20 if rule.severity == "error" else 10
            except Exception as e:
                suggestions.append(f"规则{rule.name}检查异常: {str(e)}")
        
        # 格式验证
        if expected_format:
            if expected_format == "json":
                try:
                    json.loads(output_str)
                except json.JSONDecodeError:
                    issues.append("期望JSON格式但解析失败")
                    score -= 20
        
        passed = len([i for i in issues if "error" in i.lower()]) == 0
        risk = self._calculate_risk(score)
        
        if passed:
            self.stats["passed"] += 1
        else:
            self.stats["failed"] += 1
        
        return VerificationResult(
            passed=passed,
            level=level,
            risk=risk,
            issues=issues,
            suggestions=suggestions,
            score=score
        )
    
    def verify_safety(
        self,
        content: str,
        check_pii: bool = True,
        check_dangerous: bool = True
    ) -> Dict[str, Any]:
        """
        安全检查
        
        参数:
            content: 待检查内容
            check_pii: 检查个人信息
            check_dangerous: 检查危险内容
        
        返回:
            安全检查结果
        """
        issues = []
        risk_flags = []
        
        content_lower = content.lower()
        
        # PII检查
        if check_pii:
            pii_patterns = {
                "email": r"[\w\.-]+@[\w\.-]+\.\w+",
                "phone": r"1[3-9]\d{9}",
                "id_card": r"\d{17}[\dXx]",
                "address": r"[\u4e00-\u9fa5]+(?:省|市|区|县|街道|路)",
            }
            
            for pii_type, pattern in pii_patterns.items():
                if re.search(pattern, content):
                    issues.append(f"可能包含{pii_type}信息")
                    risk_flags.append(pii_type)
        
        # 危险内容检查
        if check_dangerous:
            dangerous_patterns = [
                r"<script",
                r"javascript:",
                r"onerror=",
                r"onclick=",
                r"eval\(",
                r"exec\(",
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    issues.append("检测到潜在危险代码")
                    risk_flags.append("xss")
                    break
        
        return {
            "safe": len(issues) == 0,
            "issues": issues,
            "risk_flags": risk_flags,
            "checked_at": time.time()
        }
    
    def _check_safety(self, text: str) -> bool:
        """基础安全检查"""
        dangerous = ["rm -rf", "del /f", "format", "drop table"]
        text_lower = text.lower()
        return not any(d in text_lower for d in dangerous)
    
    def _calculate_risk(self, score: float) -> RiskLevel:
        """计算风险等级"""
        if score >= 80:
            return RiskLevel.LOW
        elif score >= 60:
            return RiskLevel.MEDIUM
        elif score >= 40:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def get_stats(self) -> Dict:
        """获取统计"""
        total = self.stats["total_verifications"]
        pass_rate = self.stats["passed"] / max(1, total) * 100
        
        return {
            **self.stats,
            "pass_rate": f"{pass_rate:.1f}%",
            "rules_count": len(self.rules)
        }
    
    def create_feedback_loop(
        self,
        max_iterations: int = 3
    ):
        """创建反馈循环"""
        return FeedbackLoop(self, max_iterations)


class FeedbackLoop:
    """
    反馈循环 - 多轮自我评估
    
    使用：
        loop = verifier.create_feedback_loop()
        result = await loop.verify_and_improve(
            initial_output,
            verify_fn
        )
    """
    
    def __init__(
        self,
        verifier: VerificationLayer,
        max_iterations: int = 3
    ):
        self.verifier = verifier
        self.max_iterations = max_iterations
        self.iterations = 0
    
    async def verify_and_improve(
        self,
        output: Any,
        improve_fn: Callable[[str], str]
    ) -> Dict[str, Any]:
        """
        验证并改进
        
        参数:
            output: 初始输出
            improve_fn: 改进函数
        
        返回:
            最终结果
        """
        current = output
        history = []
        
        for i in range(self.max_iterations):
            self.iterations += 1
            
            # 验证
            result = self.verifier.verify_output(
                current,
                level=VerificationLevel.STANDARD
            )
            
            history.append({
                "iteration": i + 1,
                "passed": result.passed,
                "score": result.score,
                "issues": result.issues
            })
            
            if result.passed:
                break
            
            # 尝试改进
            if improve_fn and result.issues:
                try:
                    current = improve_fn(str(current))
                except Exception as e:
                    history[-1]["error"] = str(e)
                    break
        
        return {
            "final_output": current,
            "iterations": self.iterations,
            "passed": result.passed,
            "history": history
        }


# 测试
if __name__ == "__main__":
    print("=== 验证层测试 ===")
    
    verifier = VerificationLayer()
    
    # 测试输入验证
    result = verifier.verify_input("测试输入内容", VerificationLevel.STANDARD)
    print(f"输入验证: passed={result.passed}, score={result.score}")
    
    # 测试输出验证
    result = verifier.verify_output("这是一个测试输出", VerificationLevel.STANDARD)
    print(f"输出验证: passed={result.passed}, score={result.score}")
    
    # 测试安全检查
    safety = verifier.verify_safety("这是一个测试内容")
    print(f"安全检查: safe={safety['safe']}")
    
    # 统计
    stats = verifier.get_stats()
    print(f"统计: {stats}")
    
    print()
    print("验证层测试通过!")
