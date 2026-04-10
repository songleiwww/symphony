#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
code_auditor.py - 内核级代码审计程序
====================================
实现在编码过程中对AI输出的代码进行自动审计，错误自动重试，连续错误直接拦截。

设计目标：
1. 生成代码后立即进行多维度审计检查
2. 发现错误返回给模型，让模型重新修正输出
3. 连续失败两次直接拦截，避免浪费token
4. 支持可扩展的审计规则，方便添加新规则
5. 记录审计历史，用于后续学习优化

工作流程：
┌─────────────────┐
│  AI生成代码     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  运行审计规则   │ ← 多条规则并行检查
└────────┬────────┘
         │ 有错误
         ▼
┌─────────────────┐
│  计数 + 反馈    │
└────────┬────────┘
         │ 第一次错
         ▼
┌─────────────────┐
│  返回模型重试   │
└────────┬────────┘
         │ 又错了
         ▼
┌─────────────────┐
│  直接拦截终止   │ → 抛出异常，记录错误
└─────────────────┘

支持的审计规则（可扩展）：
- 语法检查：Python语法是否正确
- 导入检查：是否导入了禁止的旁路模块
- 安全检查：是否包含危险操作（rmtree, os.system, eval等）
- 路径检查：是否使用了错误的绝对路径
- 约束检查：是否违反内核级秩序规则
- 依赖检查：是否使用了未声明的依赖
"""

import sys
import os
import ast
import re
import traceback
from typing import List, Dict, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('CodeAuditor')

# 导入旁路防护
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Kernel.bypass_protection import get_detector

class AuditStatus(Enum):
    """审计结果状态"""
    PASS = "pass"           # 通过
    WARNING = "warning"     # 警告（可以继续）
    FAIL = "fail"           # 失败，需要重试
    BLOCK = "block"         # 阻塞，必须终止

@dataclass
class AuditRule:
    """审计规则"""
    name: str
    description: str
    checker: Callable[[str], Tuple[AuditStatus, str]]  # 返回 (状态, 错误信息)
    is_blocking: bool = False  # 如果失败是否直接阻塞
    enabled: bool = True

@dataclass
class AuditFinding:
    """审计发现"""
    rule_name: str
    status: AuditStatus
    message: str
    line_number: Optional[int] = None

@dataclass
class AuditResult:
    """一次完整的审计结果"""
    code: str
    findings: List[AuditFinding] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 2
    passed: bool = False
    blocked: bool = False
    summary: str = ""
    
    def add_finding(self, finding: AuditFinding) -> None:
        """添加发现"""
        self.findings.append(finding)
    
    def get_errors(self) -> List[AuditFinding]:
        """获取所有错误"""
        return [f for f in self.findings if f.status in (AuditStatus.FAIL, AuditStatus.BLOCK)]
    
    def get_warnings(self) -> List[AuditFinding]:
        """获取所有警告"""
        return [f for f in self.findings if f.status == AuditStatus.WARNING]
    
    def is_passed(self) -> bool:
        """是否通过"""
        return self.passed and not self.blocked
    
    def should_retry(self) -> bool:
        """是否应该重试"""
        errors = self.get_errors()
        if not errors:
            return False
        # 如果有阻塞错误，不应该重试，直接阻断
        if any(f.status == AuditStatus.BLOCK for f in errors):
            return False
        # 如果重试次数还没到最大，应该重试
        return self.retry_count < self.max_retries
    
    def get_feedback_prompt(self) -> str:
        """生成给AI的反馈提示，告诉它哪里错了需要修正"""
        errors = self.get_errors()
        if not errors:
            return ""
        
        prompt = [
            "你的代码输出存在问题，请根据以下审计结果修正代码：",
            "",
        ]
        for i, err in enumerate(errors, 1):
            line_info = f" (行 {err.line_number})" if err.line_number else ""
            prompt.append(f"{i}. [{err.rule_name}]{line_info}: {err.message}")
        prompt.append("")
        prompt.append("请修正这些问题后重新输出完整代码。")
        return "\n".join(prompt)

# ==================== 内置审计规则 ====================

def check_python_syntax(code: str) -> Tuple[AuditStatus, str]:
    """检查Python语法是否正确
    
    使用ast.parse解析，如果失败说明语法错误
    """
    try:
        ast.parse(code)
        return AuditStatus.PASS, "语法检查通过"
    except SyntaxError as e:
        return AuditStatus.FAIL, f"Python语法错误: {e.msg} 在行 {e.lineno}"
    except Exception as e:
        return AuditStatus.FAIL, f"解析错误: {str(e)}"

def check_forbidden_imports(code: str) -> Tuple[AuditStatus, str]:
    """检查是否导入了禁止的旁路模块
    
    禁止直接导入: openai, dashscope, zhipuai, minimax
    这些必须走内核统一调度，禁止旁路调用
    """
    forbidden_modules = [
        'openai',
        'dashscope',
        'zhipuai',
        'minimax',
    ]
    
    # 遍历AST查找import语句
    try:
        tree = ast.parse(code)
        forbidden_found = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
                    if module_name in forbidden_modules:
                        forbidden_found.append((module_name, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module.split('.')[0] if node.module else ''
                if module_name in forbidden_modules:
                    forbidden_found.append((module_name, node.lineno))
        
        if forbidden_found:
            modules = ', '.join([name for name, _ in forbidden_found])
            return AuditStatus.FAIL, f"导入了禁止的旁路模块: {modules}，必须走内核统一调度，禁止直接使用厂商SDK"
        
        return AuditStatus.PASS, "未检测到禁止导入"
    except:
        # 语法错误已经在前面检查过了，这里放过
        return AuditStatus.PASS, "跳过检查（语法错误已在其他规则处理）"

def check_dangerous_operations(code: str) -> Tuple[AuditStatus, str]:
    """检查危险操作
    
    危险操作可能破坏系统，需要警告或阻断
    """
    dangerous_patterns = [
        (r'os\.system\(', "os.system调用，可能执行任意系统命令"),
        (r'subprocess\..*run\(', "subprocess调用，可能执行任意系统命令"),
        (r'eval\(', "eval调用，执行任意代码，存在安全风险"),
        (r'exec\(', "exec调用，执行任意代码，存在安全风险"),
        (r'shutil\.rmtree\(', "递归删除目录，可能大量删除文件"),
        (r'os\.remove\(', "删除文件操作"),
        (r'os\.unlink\(', "删除文件操作"),
        (r'openclaw.*config.*openclaw\.json', "尝试修改openclaw.json配置，违反固化规则"),
        (r'openclaw.*gateway.*restart', "尝试重启网关，违反规则，必须用户手动执行"),
    ]
    
    findings = []
    for i, line in enumerate(code.splitlines(), 1):
        for pattern, description in dangerous_patterns:
            if re.search(pattern, line):
                findings.append((description, i))
    
    if findings:
        desc = '; '.join([f"{d} (行 {i})" for d, i in findings])
        return AuditStatus.WARNING, f"检测到危险操作: {desc}，请确认操作必要性"
    
    return AuditStatus.PASS, "未检测到危险操作"

def check_kernel_constraints(code: str) -> Tuple[AuditStatus, str]:
    """检查是否违反内核级秩序规则
    
    检查点：
    1. 是否违反向量存储规则（保存原始文本不保存向量）
    2. 是否违反Token预算优化规则
    3. 是否尝试修改优先级
    4. 是否绕过了核心调度
    """
    violations = []
    
    # 检查是否直接存储了numpy向量
    if re.search(r'numpy\.save.*vector', code, re.IGNORECASE) or \
       re.search(r'\\.npy', code) or \
       re.search(r'np\\.save', code):
        violations.append("直接存储向量，违反内核级向量存储规则：必须保存原始文本，不持久化存储向量")
    
    # 检查是否让大模型做预处理（违反Token优化规则）
    if re.search(r'main_model.*preprocess|大模型.*预处理', code):
        violations.append("让主模型做预处理，违反Token预算优化规则：中小模型做预处理，主模型只做汇总")
    
    # 检查是否修改优先级
    if re.search(r'PRIORITY_ORDER\s*=', code) and \
       not 'bypass_protection' in code:
        violations.append("尝试修改优先级顺序，违反内核旁路防护规则")
    
    # 检查是否绕过get_enabled_providers直接调用
    if re.search(r'get_enabled_providers.*=', code) and \
       not 'symphony_scheduler' in code:
        violations.append("尝试绕过核心调度读取服务商配置")
    
    if violations:
        return AuditStatus.FAIL, "违反内核级秩序规则: " + "; ".join(violations)
    
    return AuditStatus.PASS, "符合内核级秩序规则"

def check_path_correctness(code: str) -> Tuple[AuditStatus, str]:
    """检查路径是否正确
    
    序境系统根目录固定: C:\\Users\\Administrator\\.openclaw\\workspace\\skills\\symphony
    数据库路径固定: .../data/symphony.db
    """
    wrong_patterns = [
        (r'symphony_working\.db', "错误的数据库名，正确数据库名是 symphony.db"),
        (r'/.*openclaw.*workspace.*symphony', "使用了Linux路径分隔符，Windows应该使用反斜杠"),
        (r'~\/.openclaw', "使用了用户目录相对路径，应该使用绝对路径"),
    ]
    
    findings = []
    for i, line in enumerate(code.splitlines(), 1):
        for pattern, description in wrong_patterns:
            if re.search(pattern, line):
                findings.append((description, i))
    
    if findings:
        desc = '; '.join([f"{d} (行 {i})" for d, i in findings])
        return AuditStatus.FAIL, desc
    
    return AuditStatus.PASS, "路径检查通过"

def check_indentation(code: str) -> Tuple[AuditStatus, str]:
    """检查缩进是否一致
    
    Python对缩进要求严格，混合tab和空格会出问题
    """
    mixed_indent = False
    has_tab = False
    has_space = False
    
    for i, line in enumerate(code.splitlines(), 1):
        stripped = line.lstrip()
        if stripped:
            indent = line[:-len(stripped)]
            if '\t' in indent and ' ' in indent:
                mixed_indent = True
                break
            if '\t' in indent:
                has_tab = True
            if ' ' in indent:
                has_space = True
    
    if mixed_indent:
        return AuditStatus.FAIL, "缩进混合使用了Tab和空格，会导致Python解析错误，请统一使用4个空格缩进"
    
    if has_tab and has_space:
        return AuditStatus.WARNING, "不同行使用了不同的缩进（Tab和空格混合），建议统一使用4个空格"
    
    return AuditStatus.PASS, "缩进检查通过"

# ==================== 代码审计器主类 ====================

class KernelCodeAuditor:
    """内核级代码审计器
    
    工作流程：
    1. audit(code) - 审计代码
    2. 如果失败且可重试，生成反馈提示让AI修正
    3. 重试失败达到最大次数，直接拦截
    """
    
    def __init__(self, max_retries: int = 2):
        """初始化
        
        参数:
            max_retries: 最大重试次数，默认2次（首次错了重试1次，再错就是2次直接拦）
            用户需求: 连续两次错误直接拦截，所以max_retries=2意味着:
            - 第1次错 → retry_count=1 → 允许重试
            - 第2次错 → retry_count=2 → 达到最大，拦截
        """
        self.max_retries = max_retries
        self.rules: List[AuditRule] = []
        self.audit_history: List[AuditResult] = []
        self._register_default_rules()
    
    def _register_default_rules(self) -> None:
        """注册默认规则"""
        # 优先级：语法检查最先做，语法错了不用往下检查
        self.add_rule(AuditRule(
            name="Python语法检查",
            description="验证Python语法是否正确",
            checker=check_python_syntax,
            is_blocking=False,
            enabled=True
        ))
        
        self.add_rule(AuditRule(
            name="缩进检查",
            description="检查缩进是否一致，避免Tab和空格混合",
            checker=check_indentation,
            is_blocking=False,
            enabled=True
        ))
        
        self.add_rule(AuditRule(
            name="禁止导入检查",
            description="禁止导入旁路厂商SDK，必须走内核统一调度",
            checker=check_forbidden_imports,
            is_blocking=True,  # 导入禁止模块直接阻塞
            enabled=True
        ))
        
        self.add_rule(AuditRule(
            name="路径正确性检查",
            description="检查数据库路径和系统路径是否正确",
            checker=check_path_correctness,
            is_blocking=False,
            enabled=True
        ))
        
        self.add_rule(AuditRule(
            name="内核秩序约束检查",
            description="检查是否违反内核级秩序规则（向量存储、Token优化、旁路防护）",
            checker=check_kernel_constraints,
            is_blocking=True,  # 违反内核规则直接阻塞
            enabled=True
        ))
        
        self.add_rule(AuditRule(
            name="危险操作检查",
            description="检查是否包含危险操作，发出警告",
            checker=check_dangerous_operations,
            is_blocking=False,  # 危险操作只警告，不阻塞，由人确认
            enabled=True
        ))
    
    def add_rule(self, rule: AuditRule) -> None:
        """添加自定义审计规则"""
        self.rules.append(rule)
    
    def enable_rule(self, name: str) -> None:
        """启用规则"""
        for rule in self.rules:
            if rule.name == name:
                rule.enabled = True
                return
    
    def disable_rule(self, name: str) -> None:
        """禁用规则"""
        for rule in self.rules:
            if rule.name == name:
                rule.enabled = False
                return
    
    def audit(self, code: str) -> AuditResult:
        """执行一次审计
        
        参数:
            code: AI输出的代码
            
        返回:
            AuditResult 包含所有检查结果
        """
        result = AuditResult(
            code=code,
            retry_count=0,
            max_retries=self.max_retries,
            passed=False,
            blocked=False
        )
        
        has_blocking_error = False
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            try:
                status, message = rule.checker(code)
                finding = AuditFinding(
                    rule_name=rule.name,
                    status=status,
                    message=message
                )
                result.add_finding(finding)
                
                if status == AuditStatus.BLOCK:
                    has_blocking_error = True
                    logger.warning(f"[{rule.name}] 阻塞性错误: {message}")
                elif status == AuditStatus.FAIL:
                    logger.warning(f"[{rule.name}] 失败: {message}")
                
            except Exception as e:
                # 规则本身出错，记录但不阻塞
                result.add_finding(AuditFinding(
                    rule_name=rule.name,
                    status=AuditStatus.WARNING,
                    message=f"规则执行异常: {str(e)}"
                ))
        
        # 判断结果
        errors = result.get_errors()
        if has_blocking_error:
            result.blocked = True
            result.passed = False
            result.summary = f"发现阻塞性错误，直接拦截: {'; '.join([e.message for e in errors])}"
            logger.error(result.summary)
        elif not errors:
            result.passed = True
            result.summary = "所有规则检查通过"
            logger.info(result.summary)
        else:
            result.passed = False
            result.summary = f"发现 {len(errors)} 个错误，需要重试"
            logger.info(result.summary)
        
        # 记录到历史
        self.audit_history.append(result)
        
        return result
    
    def audit_and_retry(self, code: str, generate_func: Callable[[str], str]) -> Tuple[bool, str, Optional[str]]:
        """审计并自动重试
        
        参数:
            code: 初始代码
            generate_func: 生成函数，接收反馈提示，返回修正后的代码
            
        返回:
            (success, final_code, error_message)
            success: 是否成功通过
            final_code: 最终代码（成功时就是通过的代码，失败是最后一次尝试）
            error_message: 错误信息（失败时）
        """
        current_code = code
        retry_count = 0
        
        while True:
            result = self.audit(current_code)
            result.retry_count = retry_count
            
            if result.is_passed():
                return True, current_code, None
            
            if result.blocked or not result.should_retry():
                # 阻塞或达到最大重试次数
                errors = result.get_errors()
                error_msg = "\\n".join([f"- {f.rule_name}: {f.message}" for f in errors])
                return False, current_code, f"审计失败，连续{retry_count + 1}次错误，已拦截:\\n{error_msg}"
            
            # 需要重试，生成反馈让AI修正
            feedback = result.get_feedback_prompt()
            retry_count += 1
            logger.info(f"第 {retry_count} 次重试，反馈: {feedback[:100]}...")
            current_code = generate_func(feedback)
    
    def get_statistics(self) -> Dict:
        """获取审计统计"""
        total = len(self.audit_history)
        passed = sum(1 for r in self.audit_history if r.passed)
        blocked = sum(1 for r in self.audit_history if r.blocked)
        retried = sum(1 for r in self.audit_history if r.retry_count > 0)
        
        return {
            'total_audits': total,
            'passed': passed,
            'blocked': blocked,
            'retried': retried,
            'failed': total - passed - blocked,
            'pass_rate': passed / total if total > 0 else 0
        }
    
    def print_summary(self) -> None:
        """打印审计统计摘要"""
        stats = self.get_statistics()
        print("=" * 60)
        print("内核级代码审计 - 统计摘要")
        print("=" * 60)
        print(f"总审计次数: {stats['total_audits']}")
        print(f"通过: {stats['passed']}")
        print(f"重试: {stats['retried']}")
        print(f"拦截: {stats['blocked']}")
        if stats['total_audits'] > 0:
            print(f"通过率: {stats['pass_rate']:.1%}")
        print("=" * 60)

def quick_audit(code: str) -> Tuple[bool, List[str]]:
    """快速审计，一次检查
    
    返回: (passed, error_messages)
    """
    auditor = KernelCodeAuditor(max_retries=2)
    result = auditor.audit(code)
    errors = [f"{f.rule_name}: {f.message}" for f in result.get_errors()]
    return result.is_passed(), errors

if __name__ == "__main__":
    # 测试
    print("测试内核级代码审计器")
    print("=" * 60)
    
    # 测试正确代码
    test_code_1 = """
def hello():
    print(\"Hello World\")
    return 42
"""
    
    auditor = KernelCodeAuditor()
    result = auditor.audit(test_code_1)
    print(f"测试1（正确代码）: {'通过' if result.is_passed() else '失败'}")
    if not result.is_passed():
        for err in result.get_errors():
            print(f"  {err.rule_name}: {err.message}")
    print()
    
    # 测试语法错误代码
    test_code_2 = """
def hello()
    print(\"Hello World\")
    return 42
"""
    
    result = auditor.audit(test_code_2)
    print(f"测试2（语法错误）: {'通过' if result.is_passed() else '失败'}")
    for err in result.get_errors():
        print(f"  {err.rule_name}: {err.message}")
    print()
    
    # 测试禁止导入
    test_code_3 = """
import openai
client = openai.OpenAI()
"""
    
    result = auditor.audit(test_code_3)
    print(f"测试3（禁止导入）: {'通过' if result.is_passed() else '失败'}")
    for err in result.get_errors():
        print(f"  {err.rule_name}: {err.message}")
    print(f"  是否阻塞: {result.blocked}")
    print()
    
    # 打印统计
    auditor.print_summary()
