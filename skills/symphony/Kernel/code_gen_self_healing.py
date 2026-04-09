# -*- coding: utf-8 -*-
"""
Code Generation Self-Healing
代码生成自愈系统
=========================

核心逻辑：
1. 生成代码 → 执行
2. 执行错误 → 记录错误 → 返回给LLM重新生成
3. 最多重试3次
4. 3次都失败 → 停止 + 报告

防止死循环：
- 错误计数连续3次 → 强制中断
- 相同错误重复出现 → 标记为顽固错误
- 执行超时 → 强制终止
"""

import time
import traceback
import subprocess
from dataclasses import dataclass, field
from typing import Callable, Optional, Dict, Any, List
from enum import Enum

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'


class ErrorSeverity(Enum):
    """错误严重程度"""
    SYNTAX = "syntax"           # 语法错误
    RUNTIME = "runtime"         # 运行时错误
    IMPORT = "import"           # 导入错误
    TIMEOUT = "timeout"         # 超时
    UNKNOWN = "unknown"         # 未知


@dataclass
class CodeGenerationAttempt:
    """单次代码生成尝试"""
    attempt_number: int
    code: str
    error: Optional[str] = None
    error_type: ErrorSeverity = ErrorSeverity.UNKNOWN
    execution_time: float = 0
    success: bool = False
    timestamp: float = field(default_factory=time.time)


@dataclass
class GenerationResult:
    """最终生成结果"""
    final_code: str
    success: bool
    total_attempts: int
    attempts: List[CodeGenerationAttempt]
    final_error: Optional[str] = None
    interrupted: bool = False


class CodeGenerationSelfHealer:
    """
    代码生成自愈器
    
    使用方法：
    ```python
    healer = CodeGenerationSelfHealer(max_retries=3)
    result = healer.generate_and_validate(
        prompt="写一个求斐波那契的函数",
        execute_fn=lambda code: exec(code),  # 执行函数
        language="python"
    )
    ```
    """
    
    def __init__(self, max_retries: int = 3, timeout: int = 30):
        self.max_retries = max_retries
        self.timeout = timeout
        self.attempts: List[CodeGenerationAttempt] = []
        self.error_history: List[str] = []
        
        # 错误模式识别
        self.error_patterns = {
            ErrorSeverity.SYNTAX: [
                "SyntaxError", "IndentationError", "TabError",
                "unexpected indent", "invalid syntax", "expected ':'"
            ],
            ErrorSeverity.IMPORT: [
                "ImportError", "ModuleNotFoundError", "No module named",
                "cannot import", "ImportWarning"
            ],
            ErrorSeverity.RUNTIME: [
                "NameError", "TypeError", "ValueError", "AttributeError",
                "IndexError", "KeyError", "ZeroDivisionError", "OverflowError"
            ],
            ErrorSeverity.TIMEOUT: [
                "TimeoutExpired", "timed out", "took too long"
            ]
        }
    
    def generate_and_validate(
        self,
        prompt: str,
        generate_fn: Callable[[str, int], str],  # (prompt, attempt) -> code
        execute_fn: Callable[[str], Dict],        # code -> {"success": bool, "error": str, "output": any}
        context: Optional[Dict] = None
    ) -> GenerationResult:
        """
        生成代码并验证
        
        Args:
            prompt: 生成提示词
            generate_fn: 生成函数 (prompt, attempt_num) -> code
            execute_fn: 执行函数 code -> {"success", "error", "output"}
            context: 额外上下文（错误历史等）
        
        Returns:
            GenerationResult: 最终结果
        """
        self.attempts = []
        self.error_history = []
        context = context or {}
        
        for attempt in range(1, self.max_retries + 1):
            print(f"[CodeHealer] 第 {attempt}/{self.max_retries} 次尝试...")
            
            # 生成代码
            start_time = time.time()
            try:
                code = generate_fn(prompt, attempt)
            except Exception as e:
                code = None
                error_msg = f"生成失败: {str(e)}"
                error_type = ErrorSeverity.UNKNOWN
            
            if code is None:
                continue
            
            # 记录尝试
            attempt_record = CodeGenerationAttempt(
                attempt_number=attempt,
                code=code
            )
            
            # 执行代码
            try:
                exec_result = execute_fn(code)
                attempt_record.success = exec_result.get("success", False)
                attempt_record.error = exec_result.get("error")
                attempt_record.execution_time = time.time() - start_time
                
                if attempt_record.success:
                    self.attempts.append(attempt_record)
                    print(f"[CodeHealer] ✅ 第 {attempt} 次成功!")
                    return GenerationResult(
                        final_code=code,
                        success=True,
                        total_attempts=attempt,
                        attempts=self.attempts
                    )
                else:
                    # 执行失败，分析错误
                    attempt_record.error_type = self._classify_error(attempt_record.error)
                    self.error_history.append(attempt_record.error)
                    print(f"[CodeHealer] ❌ 第 {attempt} 次失败: {attempt_record.error[:100]}")
                    
            except subprocess.TimeoutExpired:
                attempt_record.error = f"执行超时 ({self.timeout}s)"
                attempt_record.error_type = ErrorSeverity.TIMEOUT
                print(f"[CodeHealer] ❌ 第 {attempt} 次超时")
            except Exception as e:
                attempt_record.error = f"执行异常: {str(e)}"
                attempt_record.error_type = ErrorSeverity.UNKNOWN
                print(f"[CodeHealer] ❌ 第 {attempt} 次异常: {str(e)[:100]}")
            
            self.attempts.append(attempt_record)
            
            # 检查是否连续失败3次
            if attempt >= self.max_retries:
                print(f"[CodeHealer] ⚠️ 已达最大重试次数 {self.max_retries}，强制中断")
                return GenerationResult(
                    final_code=code or "",
                    success=False,
                    total_attempts=attempt,
                    attempts=self.attempts,
                    final_error=attempt_record.error,
                    interrupted=True
                )
            
            # 检查是否有顽固错误（同样的错误重复3次）
            if self._is_stubborn_error():
                print(f"[CodeHealer] ⚠️ 检测到顽固错误模式，中断")
                return GenerationResult(
                    final_code=code or "",
                    success=False,
                    total_attempts=attempt,
                    attempts=self.attempts,
                    final_error="顽固错误: " + attempt_record.error,
                    interrupted=True
                )
            
            # 准备下一轮提示词（加入错误信息）
            context["last_error"] = attempt_record.error
            context["error_type"] = attempt_record.error_type.value
            context["attempt_history"] = self._summarize_history()
        
        return GenerationResult(
            final_code=self.attempts[-1].code if self.attempts else "",
            success=False,
            total_attempts=len(self.attempts),
            attempts=self.attempts,
            final_error="未知的生成失败"
        )
    
    def _classify_error(self, error: str) -> ErrorSeverity:
        """分类错误类型"""
        if not error:
            return ErrorSeverity.UNKNOWN
        
        error_upper = error.upper()
        for severity, patterns in self.error_patterns.items():
            for pattern in patterns:
                if pattern.upper() in error_upper:
                    return severity
        return ErrorSeverity.UNKNOWN
    
    def _is_stubborn_error(self) -> bool:
        """检查是否是顽固错误（同样错误重复）"""
        if len(self.error_history) < 3:
            return False
        
        # 最后3个错误是否相同
        last_3 = self.error_history[-3:]
        if len(set(last_3)) == 1:
            return True
        
        # 检查是否有重复模式
        recent = self.error_history[-5:]
        for i in range(len(recent)):
            for j in range(i + 1, len(recent)):
                if recent[i] and recent[j] and recent[i] == recent[j]:
                    return True
        
        return False
    
    def _summarize_history(self) -> str:
        """总结历史错误"""
        if not self.attempts:
            return ""
        
        lines = ["=== 代码生成历史 ==="]
        for a in self.attempts:
            status = "✅" if a.success else "❌"
            lines.append(f"第{a.attempt_number}次: {status} {a.error_type.value}")
            if a.error:
                lines.append(f"  错误: {a.error[:80]}")
        
        return "\n".join(lines)


def create_python_executor(timeout: int = 30):
    """创建 Python 执行器"""
    def execute(code: str) -> Dict:
        """执行 Python 代码"""
        import io
        import sys
        
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            # 重定向输出
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            
            # 执行（带超时）
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("执行超时")
            
            # Windows 不支持 SIGALRM，使用线程超时
            import threading
            
            result = {"success": False, "output": None, "error": None}
            
            def run_code():
                try:
                    exec(code, {"__name__": "__main__"})
                    result["success"] = True
                except Exception as e:
                    result["error"] = f"{type(e).__name__}: {str(e)}"
            
            thread = threading.Thread(target=run_code)
            thread.daemon = True
            thread.start()
            thread.join(timeout=timeout)
            
            if thread.is_alive():
                result["error"] = f"执行超时 ({timeout}s)"
                # 强制终止（Python 线程无法真正终止，只能标记）
            else:
                if not result["success"] and not result["error"]:
                    result["success"] = True  # 无异常即成功
            
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            result["output"] = stdout_capture.getvalue()
            return result
            
        except Exception as e:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            return {"success": False, "output": None, "error": str(e)}
    
    return execute


# 简单测试
if __name__ == "__main__":
    print("=== Code Generation Self-Healer Test ===")
    
    healer = CodeGenerationSelfHealer(max_retries=3)
    
    def simple_generate(prompt, attempt):
        """模拟代码生成"""
        if attempt == 1:
            return "def fib(n):\n    return fib(n-1) + fib(n-2)"  # 错误：没有基线
        elif attempt == 2:
            return "def fib(n):\n    if n <= 1:\n        return n\n    return fib(n-1) + fib(n-2)"
        else:
            return "print('hello')"
    
    execute = create_python_executor()
    
    result = healer.generate_and_validate(
        prompt="写一个斐波那契函数",
        generate_fn=simple_generate,
        execute_fn=execute
    )
    
    print(f"\n最终结果:")
    print(f"  成功: {result.success}")
    print(f"  尝试次数: {result.total_attempts}")
    print(f"  中断: {result.interrupted}")
    if result.final_error:
        print(f"  最终错误: {result.final_error[:100]}")
