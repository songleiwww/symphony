#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony UX Improvements - 交响用户体验改进
Progress bars, friendly error messages, and confirmation dialogs
进度条、友好错误提示和确认对话框
"""

import sys
import os
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class UXMessageType(Enum):
    """UX message type - UX消息类型"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class FriendlyError:
    """Friendly error - 友好错误"""
    error_type: str
    user_message: str
    technical_details: str
    suggestion: str = ""
    recovery_steps: List[str] = None


class UXImprovements:
    """用户体验改进"""
    
    def __init__(self):
        self.last_progress = 0.0
        self._progress_line_length = 0
    
    # =========================================================================
    # Progress Bar - 进度条
    # =========================================================================
    
    def show_progress(self, progress: float, message: str = "", bar_length: int = 30):
        """Show progress bar - 显示进度条"""
        progress = max(0.0, min(1.0, progress))
        filled = int(bar_length * progress)
        bar = "[" + "=" * filled + " " * (bar_length - filled) + "]"
        percent = int(progress * 100)
        
        line = f"\r{message} {bar} {percent}%"
        # Clear previous line if shorter
        if len(line) < self._progress_line_length:
            line += " " * (self._progress_line_length - len(line))
        
        print(line, end="", flush=True)
        self._progress_line_length = len(line)
        
        if progress >= 1.0:
            print()  # New line when done
    
    def show_progress_with_eta(self, progress: float, eta_seconds: float, message: str = ""):
        """Show progress with ETA - 显示带预计剩余时间的进度"""
        eta_str = ""
        if eta_seconds > 0:
            if eta_seconds < 60:
                eta_str = f"ETA: {eta_seconds:.0f}s"
            elif eta_seconds < 3600:
                eta_str = f"ETA: {eta_seconds/60:.0f}m {eta_seconds%60:.0f}s"
            else:
                eta_str = f"ETA: {eta_seconds/3600:.0f}h"
        
        full_message = f"{message} {eta_str}" if eta_str else message
        self.show_progress(progress, full_message)
    
    # =========================================================================
    # Friendly Messages - 友好消息
    # =========================================================================
    
    def show_message(self, message: str, msg_type: UXMessageType = UXMessageType.INFO):
        """Show message - 显示消息"""
        prefix = {
            UXMessageType.INFO: "[INFO]",
            UXMessageType.SUCCESS: "[OK]",
            UXMessageType.WARNING: "[WARNING]",
            UXMessageType.ERROR: "[ERROR]"
        }.get(msg_type, "[INFO]")
        
        print(f"{prefix} {message}")
    
    def show_success(self, message: str):
        """Show success - 显示成功"""
        self.show_message(message, UXMessageType.SUCCESS)
    
    def show_warning(self, message: str):
        """Show warning - 显示警告"""
        self.show_message(message, UXMessageType.WARNING)
    
    def show_error(self, message: str):
        """Show error - 显示错误"""
        self.show_message(message, UXMessageType.ERROR)
    
    # =========================================================================
    # Friendly Errors - 友好错误
    # =========================================================================
    
    def create_friendly_error(self, error: Exception, context: str = "") -> FriendlyError:
        """Create friendly error - 创建友好错误"""
        error_type = type(error).__name__
        error_str = str(error)
        
        # Common error mappings
        error_map = {
            "ConnectionError": ("网络连接错误", "请检查网络连接", "确认网络正常后重试"),
            "TimeoutError": ("操作超时", "服务器响应较慢", "请稍后重试，或检查网络"),
            "FileNotFoundError": ("文件不存在", "找不到指定的文件", "确认文件路径正确"),
            "PermissionError": ("权限不足", "没有足够的权限", "请检查文件权限或使用管理员权限"),
            "MemoryError": ("内存不足", "系统内存不足", "请关闭其他程序后重试"),
        }
        
        base_msg = error_map.get(error_type, ("操作失败", "发生了一个错误", "请查看技术详情"))
        
        return FriendlyError(
            error_type=error_type,
            user_message=base_msg[0],
            technical_details=f"{error_type}: {error_str}",
            suggestion=base_msg[1],
            recovery_steps=[base_msg[2]] if base_msg[2] else []
        )
    
    def show_friendly_error(self, error: Exception, context: str = ""):
        """Show friendly error - 显示友好错误"""
        friendly = self.create_friendly_error(error, context)
        
        print("\n" + "=" * 60)
        print(friendly.user_message)
        if friendly.suggestion:
            print(f"提示: {friendly.suggestion}")
        if friendly.recovery_steps:
            print("\n建议操作:")
            for i, step in enumerate(friendly.recovery_steps, 1):
                print(f"  {i}. {step}")
        print("\n技术详情:")
        print(f"  {friendly.technical_details}")
        print("=" * 60 + "\n")
    
    # =========================================================================
    # Confirmation Dialogs - 确认对话框
    # =========================================================================
    
    def confirm(self, message: str, default: bool = False) -> bool:
        """Ask for confirmation - 请求确认"""
        default_str = "Y/n" if default else "y/N"
        while True:
            try:
                response = input(f"{message} [{default_str}] ").strip().lower()
                if not response:
                    return default
                if response in ("y", "yes"):
                    return True
                if response in ("n", "no"):
                    return False
                print("请输入 y(es) 或 n(o)")
            except (EOFError, KeyboardInterrupt):
                print("\n取消操作")
                return False
    
    def confirm_dangerous(self, message: str) -> bool:
        """Confirm dangerous operation - 确认危险操作"""
        warning = "⚠️  警告：这是一个危险操作！"
        print(warning)
        return self.confirm(f"{message}\n确定要继续吗？", default=False)
    
    # =========================================================================
    # Quick Stats - 快速统计
    # =========================================================================
    
    def show_stats(self, title: str, stats: Dict[str, Any]):
        """Show statistics - 显示统计信息"""
        print("\n" + "=" * 60)
        print(title)
        print("=" * 60)
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print("=" * 60 + "\n")


def create_ux_improvements() -> UXImprovements:
    """Create UX improvements - 创建UX改进"""
    return UXImprovements()


if __name__ == "__main__":
    print("Symphony UX Improvements")
    print("交响用户体验改进")
    print("=" * 60)
    
    ux = create_ux_improvements()
    
    # Test 1: Progress bar
    print("\n[Test 1] Progress bar...")
    for i in range(11):
        progress = i / 10.0
        ux.show_progress(progress, "Processing")
        time.sleep(0.1)
    print("  OK: Progress bar")
    
    # Test 2: Messages
    print("\n[Test 2] Messages...")
    ux.show_success("Operation completed successfully!")
    ux.show_warning("This might take a while...")
    ux.show_message("Starting task...", UXMessageType.INFO)
    print("  OK: Messages")
    
    # Test 3: Friendly error
    print("\n[Test 3] Friendly error...")
    try:
        raise FileNotFoundError("test.txt")
    except Exception as e:
        ux.show_friendly_error(e, "Reading file")
    print("  OK: Friendly error")
    
    # Test 4: Stats
    print("\n[Test 4] Stats...")
    ux.show_stats("Quick Stats", {
        "Tasks": 10,
        "Completed": 8,
        "Failed": 2,
        "Success Rate": "80%"
    })
    print("  OK: Stats")
    
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)
