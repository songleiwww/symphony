#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony Enhanced Beautiful UI - 交响增强美观用户界面
Optimized for input understanding and beautiful output.
优化输入理解和美观输出。
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ColorScheme:
    """配色方案 - Color scheme (ANSI escape codes)"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


@dataclass
class InputUnderstanding:
    """输入理解增强 - Input Understanding Enhancement"""
    
    @staticmethod
    def normalize_input(text: str) -> str:
        """规范化用户输入 - Normalize user input"""
        text = text.strip()
        while "  " in text:
            text = text.replace("  ", " ")
        return text
    
    @staticmethod
    def detect_intent(text: str) -> Dict[str, Any]:
        """检测用户意图 - Detect user intent"""
        text = text.lower()
        
        intent = {
            "type": "unknown",
            "confidence": 0.5,
            "entities": []
        }
        
        if any(keyword in text for keyword in ["help", "帮助", "怎么", "如何"]):
            intent["type"] = "help"
            intent["confidence"] = 0.9
        elif any(keyword in text for keyword in ["test", "测试", "检查"]):
            intent["type"] = "test"
            intent["confidence"] = 0.9
        elif any(keyword in text for keyword in ["create", "创建", "生成", "开发"]):
            intent["type"] = "create"
            intent["confidence"] = 0.8
        elif any(keyword in text for keyword in ["优化", "改进", "improve", "optimize"]):
            intent["type"] = "optimize"
            intent["confidence"] = 0.8
        
        return intent


class SymphonyEnhancedUI:
    """
    Symphony Enhanced Beautiful UI - 交响增强美观用户界面
    
    Optimized for input understanding and beautiful output.
    优化输入理解和美观输出。
    """
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors
        self.c = ColorScheme()
        self.input_understanding = InputUnderstanding()
    
    def _color(self, text: str, color_code: str) -> str:
        """Apply color if enabled - 如果启用则应用颜色"""
        if self.use_colors:
            return f"{color_code}{text}{self.c.RESET}"
        return text
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """Process and understand user input - 处理并理解用户输入"""
        normalized = self.input_understanding.normalize_input(user_input)
        intent = self.input_understanding.detect_intent(normalized)
        
        return {
            "original": user_input,
            "normalized": normalized,
            "intent": intent,
            "processed": True
        }
    
    def header_grand(self, title: str, subtitle: Optional[str] = None, 
                   tagline: Optional[str] = None) -> str:
        """Grand header - 盛大标题"""
        lines = []
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"    {self._color(title, self.c.BOLD + self.c.BRIGHT_BLUE)}")
        if subtitle:
            lines.append(f"    {self._color(subtitle, self.c.DIM)}")
        if tagline:
            lines.append("")
            lines.append(f"    {self._color(f'"{tagline}"', self.c.BRIGHT_MAGENTA)}")
        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)
    
    def header_section(self, title: str) -> str:
        """Section header - 章节标题"""
        lines = []
        lines.append("-" * 50)
        lines.append(f"  {self._color(title, self.c.BOLD + self.c.CYAN)}")
        lines.append("-" * 50)
        return "\n".join(lines)
    
    def success(self, message: str, details: Optional[str] = None) -> str:
        """Success message - 成功消息"""
        lines = [f"[OK] {message}"]
        if details:
            lines.append(f"     {details}")
        return "\n".join(lines)
    
    def error(self, message: str, hint: Optional[str] = None) -> str:
        """Error message - 错误消息"""
        lines = [f"[ERROR] {message}"]
        if hint:
            lines.append(f"     Hint: {hint}")
        return "\n".join(lines)
    
    def warning(self, message: str, note: Optional[str] = None) -> str:
        """Warning message - 警告消息"""
        lines = [f"[WARN] {message}"]
        if note:
            lines.append(f"     Note: {note}")
        return "\n".join(lines)
    
    def info(self, message: str, context: Optional[str] = None) -> str:
        """Info message - 信息消息"""
        lines = [f"[INFO] {message}"]
        if context:
            lines.append(f"     {context}")
        return "\n".join(lines)
    
    def list_numbered(self, items: List[str], title: Optional[str] = None) -> str:
        """Numbered list - 有序列表"""
        lines = []
        if title:
            lines.append(f"  {title}")
        for i, item in enumerate(items, 1):
            lines.append(f"  {i}. {item}")
        return "\n".join(lines)
    
    def list_bulleted(self, items: List[str], title: Optional[str] = None) -> str:
        """Bulleted list - 无序列表"""
        lines = []
        if title:
            lines.append(f"  {title}")
        for item in items:
            lines.append(f"  - {item}")
        return "\n".join(lines)
    
    def key_value_pretty(self, data: Dict[str, Any], title: Optional[str] = None) -> str:
        """Pretty key-value pairs - 美观键值对"""
        lines = []
        if title:
            lines.append(f"  {title}")
        if not data:
            return "\n".join(lines)
        max_key_len = max(len(str(k)) for k in data.keys())
        for key, value in data.items():
            key_str = str(key).ljust(max_key_len)
            lines.append(f"  {key_str}: {value}")
        return "\n".join(lines)
    
    def progress_bar(self, current: int, total: int, label: Optional[str] = None) -> str:
        """Progress bar - 进度条"""
        if total == 0:
            percent = 0
        else:
            percent = int((current / total) * 100)
        filled = int((current / total) * 40)
        bar = "=" * filled + " " * (40 - filled)
        parts = [f"[{bar}]", f"{percent}%", f"({current}/{total})"]
        if label:
            parts.insert(0, f"{label}:")
        return " ".join(parts)
    
    def table(self, headers: List[str], rows: List[List[str]], title: Optional[str] = None) -> str:
        """Simple table - 简单表格"""
        if not headers or not rows:
            return ""
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        lines = []
        if title:
            lines.append(f"  {title}")
        separator = "-" * (sum(col_widths) + len(headers) * 3 + 2)
        lines.append(separator)
        header_cells = [h.ljust(col_widths[i]) for i, h in enumerate(headers)]
        lines.append("  " + " | ".join(header_cells))
        lines.append(separator)
        for row in rows:
            row_cells = [str(cell).ljust(col_widths[i]) if i < len(col_widths) else str(cell)
                        for i, cell in enumerate(row)]
            lines.append("  " + " | ".join(row_cells))
        lines.append(separator)
        return "\n".join(lines)
    
    def summary_card(self, title: str, items: Dict[str, str], subtitle: Optional[str] = None) -> str:
        """Summary card - 总结卡片"""
        lines = []
        lines.append("=" * 50)
        lines.append(f"  {title}")
        if subtitle:
            lines.append(f"  {subtitle}")
        lines.append("-" * 50)
        for key, value in items.items():
            lines.append(f"  {key}: {value}")
        lines.append("=" * 50)
        return "\n".join(lines)
    
    def divider(self, style: str = "medium") -> str:
        """Divider - 分隔线"""
        if style == "thick":
            return "#" * 60
        elif style == "thin":
            return "-" * 60
        else:
            return "=" * 60
    
    def newline(self, count: int = 1) -> str:
        """Newlines - 换行"""
        return "\n" * count


ui = SymphonyEnhancedUI(use_colors=True)

if __name__ == "__main__":
    print(ui.header_grand("Symphony Enhanced UI Demo", 
                         "交响增强UI演示",
                         "智韵交响，共创华章"))
    print(ui.newline())
    
    print(ui.header_section("Beautiful Messages - 美观消息"))
    print(ui.success("All systems operational!", "Everything is working perfectly"))
    print(ui.error("Failed to connect to server", "Check your internet connection"))
    print(ui.warning("Low memory detected", "Consider closing some applications"))
    print(ui.info("Starting up...", "System initialization in progress"))
    print(ui.newline())
    
    print(ui.header_section("Beautiful Lists - 美观列表"))
    print(ui.list_numbered(["Design UI", "Implement features", "Test thoroughly", "Deploy to production"], 
                          "Development Steps"))
    print(ui.newline())
    print(ui.list_bulleted(["Memory System", "Async Core", "Task Queue", "UX Improvements"], 
                          "Core Modules"))
    print(ui.newline())
    
    print(ui.header_section("Beautiful Key-Value - 美观键值对"))
    print(ui.key_value_pretty({
        "Project Name": "Symphony",
        "Version": "v0.5.0",
        "Author": "步花间 (Huajian Bu)",
        "Status": "Active",
        "Modules": "17"
    }, "Project Info"))
    print(ui.newline())
    
    print(ui.header_section("Beautiful Progress - 美观进度"))
    print(ui.progress_bar(0, 100, "Initializing"))
    print(ui.progress_bar(25, 100, "Loading"))
    print(ui.progress_bar(50, 100, "Processing"))
    print(ui.progress_bar(75, 100, "Finishing"))
    print(ui.progress_bar(100, 100, "Complete"))
    print(ui.newline())
    
    print(ui.header_section("Beautiful Table - 美观表格"))
    print(ui.table(
        ["Name", "Role", "Model", "Status"],
        [
            ["林思远", "Input Architect", "ark-code-latest", "Active"],
            ["陈美琪", "Visual Designer", "deepseek-v3.2", "Active"],
            ["王浩然", "Interaction Engineer", "glm-4.7", "Active"],
            ["刘心怡", "Content Strategist", "kimi-k2.5", "Active"],
            ["张明远", "QA Lead", "doubao-seed-2.0-code", "Active"],
            ["赵敏", "Project Coordinator", "MiniMax-M2.5", "Active"]
        ],
        "Team Members"
    ))
    print(ui.newline())
    
    print(ui.summary_card("Release Summary - 发布总结", {
        "Version": "v0.5.0",
        "Status": "Success",
        "UI": "Enhanced & Beautiful",
        "Tests": "All Passed",
        "Team": "6 Experts"
    }, "Symphony Optimization Complete"))
