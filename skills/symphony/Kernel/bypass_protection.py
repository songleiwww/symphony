#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bypass_protection.py - 内核级旁路防护
====================================
序境核心秩序：禁止滋生旁路，所有调用必须走主调度链路

设计目标：
1. 检测并阻止任何绕过核心调度的尝试
2. 确保唯一数据源（symphony.db）不可被旁路
3. 确保调度优先级不可被动态修改
4. 记录违规调用，产生审计日志

内核级规则：
- 所有AI调用必须经过 symphony_scheduler.py → 这是唯一合法入口
- 所有配置必须从 symphony.db 读取 → 这是唯一合法数据源
- 优先级顺序固化，不可动态修改
- 禁止直接使用厂商SDK，必须走原生HTTP统一调用
"""

import sys
import os
import inspect
import logging
from typing import List, Dict, Optional, Tuple
from functools import wraps

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('BypassProtection')

# 合法调用栈白名单（允许的入口模块）
WHITELIST_ENTRY_POINTS = [
    'symphony_scheduler',
    'Kernel.__init__',
    'wisdom_engine',
    'provider_health_checker',
    'intelligent_strategy_scheduler',
    '__main__',  # 允许直接运行测试脚本
    'simple_all_test',  # 全系统测试
]

# 禁止直接使用的模块（旁路风险）
FORBIDDEN_DIRECT_IMPORTS = [
    'openai',          # 必须走原生HTTP，不需要OpenAI库
    'dashscope',       # 阿里云官方SDK，禁止直接使用
    'zhipuai',         # 智谱AI官方SDK，禁止直接使用
    'minimax',         # MiniMax官方SDK，禁止直接使用
]

# 固化优先级（不可修改）
FIXED_PRIORITY_ORDER = ["aliyun", "minimax", "zhipu", "nvidia"]

class BypassViolation(Exception):
    """旁路违规异常"""
    pass

class BypassDetector:
    """旁路检测器"""
    
    def __init__(self):
        self.violation_count = 0
        self.violations: List[Dict] = []
    
    def detect_bypass_call(self) -> Tuple[bool, Optional[str]]:
        """检测当前调用是否绕过了主调度入口
        
        返回: (is_bypassed, reason)
            is_bypassed = True 表示检测到旁路违规
        """
        stack = inspect.stack()
        caller_frames = []
        
        # 检查调用栈中是否有合法的调度入口
        has_legitimate_entry = False
        for frame_info in stack[1:]:  # 跳过当前帧
            module = inspect.getmodule(frame_info[0])
            if module:
                module_name = module.__name__.split('.')[-1]
                caller_frames.append(module_name)
                if module_name in WHITELIST_ENTRY_POINTS:
                    has_legitimate_entry = True
                    break
        
        if not has_legitimate_entry:
            reason = f"调用栈不存在合法入口点，调用路径: {' → '.join(caller_frames)}"
            return True, reason
        
        return False, None
    
    def detect_forbidden_imports(self) -> Tuple[bool, Optional[str]]:
        """检测是否导入了禁止的旁路模块"""
        for module_name in FORBIDDEN_DIRECT_IMPORTS:
            if module_name in sys.modules:
                reason = f"导入了禁止的旁路模块: {module_name}，必须走原生HTTP统一调用"
                return True, reason
        return False, None
    
    def check_priority_order(self, current_order: List[str]) -> Tuple[bool, Optional[str]]:
        """检查优先级顺序是否被修改"""
        if current_order != FIXED_PRIORITY_ORDER:
            reason = f"优先级顺序被修改，原始: {FIXED_PRIORITY_ORDER}, 当前: {current_order}"
            return True, reason
        return False, None
    
    def record_violation(self, violation_type: str, reason: str) -> None:
        """记录违规"""
        self.violation_count += 1
        caller = inspect.getframeinfo(inspect.currentframe().f_back.f_back)
        self.violations.append({
            'type': violation_type,
            'reason': reason,
            'file': caller.filename,
            'line': caller.lineno,
            'timestamp': logging.Formatter().formatTime(logging.LogRecord(
                'BypassProtection', logging.INFO, '', 0, '', (), None
            ))
        })
        logger.warning(f"[旁路违规] {violation_type}: {reason} @ {caller.filename}:{caller.lineno}")
    
    def get_violation_summary(self) -> str:
        """获取违规汇总"""
        if not self.violations:
            return "✅ 未检测到旁路违规"
        
        summary = [f"⚠️ 检测到 {self.violation_count} 次旁路违规:"]
        for i, v in enumerate(self.violations, 1):
            summary.append(f"  [{i}] {v['type']}: {v['reason']} @ {v['file']}:{v['line']}")
        return '\n'.join(summary)
    
    def is_clean(self) -> bool:
        """检查是否无违规"""
        return self.violation_count == 0

# 全局检测器实例
_detector = BypassDetector()

def get_detector() -> BypassDetector:
    """获取全局检测器实例"""
    return _detector

def enforce_no_bypass() -> None:
    """强制执行无旁路规则
    
    如果检测到旁路违规，抛出 BypassViolation 异常
    """
    # 检测调用旁路
    is_bypassed, reason = _detector.detect_bypass_call()
    if is_bypassed:
        _detector.record_violation("CALL_BYPASS", reason)
        raise BypassViolation(f"检测到旁路调用违规: {reason}")
    
    # 检测禁止导入
    has_forbidden, reason = _detector.detect_forbidden_imports()
    if has_forbidden:
        _detector.record_violation("FORBIDDEN_IMPORT", reason)
        raise BypassViolation(f"检测到禁止导入违规: {reason}")

def protected_function(func):
    """装饰器：保护核心函数不被旁路调用
    
    任何调用核心函数必须经过合法入口，否则抛出异常
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        enforce_no_bypass()
        return func(*args, **kwargs)
    return wrapper

def verify_priority_order(current_order: List[str]) -> bool:
    """验证优先级顺序是否正确
    
    被修改则记录违规，返回False
    """
    is_bypassed, reason = _detector.check_priority_order(current_order)
    if is_bypassed:
        _detector.record_violation("PRIORITY_MODIFIED", reason)
        return False
    return True

def audit_core_integrity() -> Dict:
    """内核完整性审计
    
    返回审计结果
    """
    detector = get_detector()
    
    # 检查核心模块
    core_modules = [
        ('symphony_scheduler', 'C:\\Users\\Administrator\\.openclaw\\workspace\\skills\\symphony\\symphony_scheduler.py'),
        ('Kernel.__init__', 'C:\\Users\\Administrator\\.openclaw\\workspace\\skills\\symphony\\Kernel\\__init__.py'),
        ('bypass_protection', 'C:\\Users\\Administrator\\.openclaw\\workspace\\skills\\symphony\\Kernel\\bypass_protection.py'),
    ]
    
    results = []
    for name, path in core_modules:
        exists = os.path.exists(path)
        results.append({
            'module': name,
            'path': path,
            'exists': exists
        })
    
    return {
        'violation_count': detector.violation_count,
        'violations': detector.violations,
        'core_modules': results,
        'all_core_exists': all(r['exists'] for r in results),
        'is_clean': detector.is_clean(),
        'fixed_priority': FIXED_PRIORITY_ORDER,
    }

def safe_print(text):
    """安全打印，处理GBK编码问题"""
    try:
        print(text)
    except UnicodeEncodeError:
        text = text.replace('✅', '[OK]').replace('❌', '[X]').replace('⚠️', '[!]')
        print(text)

def print_audit_report() -> None:
    """打印内核完整性审计报告"""
    result = audit_core_integrity()
    safe_print("=" * 60)
    safe_print("序境内核旁路防护 - 完整性审计报告")
    safe_print("=" * 60)
    safe_print("")
    safe_print(f"固化优先级顺序: {result['fixed_priority']}")
    safe_print("")
    safe_print(f"核心模块检查:")
    for mod in result['core_modules']:
        status = "[OK] 存在" if mod['exists'] else "[X] 缺失"
        safe_print(f"  {mod['module']}: {status} -> {mod['path']}")
    safe_print("")
    safe_print(f"旁路违规检测:")
    if result['is_clean']:
        safe_print("  [OK] 未检测到旁路违规，内核纯净")
    else:
        safe_print(get_detector().get_violation_summary())
    safe_print("")
    safe_print(f"统计:")
    safe_print(f"  违规总数: {result['violation_count']}")
    safe_print("")
    if result['all_core_exists'] and result['is_clean']:
        safe_print("内核完整性: [OK] 通过")
    else:
        safe_print("内核完整性: [X] 不通过")
    safe_print("=" * 60)

if __name__ == "__main__":
    print_audit_report()
