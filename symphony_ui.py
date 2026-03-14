#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony Beautiful UI - 交响美观用户界面
A clean, clear, and beautiful CLI interface for Symphony.
为交响提供干净、清晰、美观的CLI界面。
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
    
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


class SymphonyUI:
    """
    Symphony Beautiful UI - 交响美观用户界面
    
    Provides clean, clear, and beautiful CLI output.
    提供干净、清晰、美观的CLI输出。
    """
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors
        self.c = ColorScheme()
    
    def _color(self, text: str, color_code: str) -> str:
        """Apply color if enabled - 如果启用则应用颜色"""
        if self.use_colors:
            return f"{color_code}{text}{self.c.RESET}"
        return text
    
    def header_main(self, title: str, subtitle: Optional[str] = None) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append(f"    {self._color(title, self.c.BOLD + self.c.BRIGHT_BLUE)}")
        if subtitle:
            lines.append(f"    {self._color(subtitle, self.c.DIM)}")
        lines.append("=" * 60)
        return "\n".join(lines)
    
    def header_section(self, title: str) -> str:
        lines = []
        lines.append("-" * 50)
        lines.append(f"  {self._color(title, self.c.BOLD + self.c.CYAN)}")
        lines.append("-" * 50)
        return "\n".join(lines)
    
    def success(self, message: str) -> str:
        return f"[OK] {message}"
    
    def error(self, message: str) -> str:
        return f"[ERROR] {message}"
    
    def warning(self, message: str) -> str:
        return f"[WARN] {message}"
    
    def info(self, message: str) -> str:
        return f"[INFO] {message}"
    
    def list_items(self, items: List[str], numbered: bool = False) -> str:
        lines = []
        for i, item in enumerate(items, 1):
            prefix = f"{i}." if numbered else "-"
            lines.append(f"  {prefix} {item}")
        return "\n".join(lines)
    
    def key_value(self, data: Dict[str, Any], indent: int = 2) -> str:
        lines = []
        indent_spaces = " " * indent
        for key, value in data.items():
            lines.append(f"{indent_spaces}{key}: {value}")
        return "\n".join(lines)
    
    def progress_bar(self, current: int, total: int, width: int = 40) -> str:
        if total == 0:
            percent = 0
        else:
            percent = int((current / total) * 100)
        filled = int((current / total) * width)
        bar = "=" * filled + " " * (width - filled)
        return f"[{bar}] {percent}% ({current}/{total})"
    
    def table(self, headers: List[str], rows: List[List[str]]) -> str:
        if not headers or not rows:
            return ""
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        lines = []
        separator = "-" * (sum(col_widths) + len(headers) * 3 + 2)
        lines.append(separator)
        header_cells = [h.ljust(col_widths[i]) for i, h in enumerate(headers)]
        lines.append("  " + " | ".join(header_cells))
        lines.append(separator)
        for row in rows:
            row_cells = [str(cell).ljust(col_widths[i]) if i < len(col_widths) else str(cell) for i, cell in enumerate(row)]
            lines.append("  " + " | ".join(row_cells))
        lines.append(separator)
        return "\n".join(lines)
    
    def divider(self, style: str = "medium") -> str:
        if style == "thick":
            return "#" * 60
        elif style == "thin":
            return "-" * 60
        else:
            return "=" * 60
    
    def newline(self, count: int = 1) -> str:
        return "\n" * count
    
    def space(self, count: int = 4) -> str:
        return " " * count
    
    def summary_box(self, title: str, items: Dict[str, str]) -> str:
        lines = []
        lines.append("=" * 50)
        lines.append(f"  {title}")
        lines.append("-" * 50)
        lines.append(self.key_value(items, indent=2))
        lines.append("=" * 50)
        return "\n".join(lines)


ui = SymphonyUI(use_colors=True)

if __name__ == "__main__":
    print(ui.header_main("Symphony UI Demo", "交响UI演示"))
    print(ui.newline())
    
    print(ui.header_section("Messages - 消息"))
    print(ui.success("Operation completed successfully!"))
    print(ui.error("Something went wrong!"))
    print(ui.warning("Please check your input!"))
    print(ui.info("Here is some information."))
    print(ui.newline())
    
    print(ui.header_section("Lists - 列表"))
    print(ui.list_items(["First item", "Second item", "Third item"], numbered=False))
    print(ui.newline())
    print(ui.list_items(["Step 1", "Step 2", "Step 3"], numbered=True))
    print(ui.newline())
    
    print(ui.header_section("Key-Value - 键值对"))
    print(ui.key_value({"Name": "Symphony", "Version": "v0.4.9", "Status": "Active"}))
    print(ui.newline())
    
    print(ui.header_section("Progress - 进度"))
    print(ui.progress_bar(25, 50))
    print(ui.progress_bar(50, 50))
    print(ui.newline())
    
    print(ui.header_section("Table - 表格"))
    print(ui.table(
        ["Model", "Provider", "Status"],
        [
            ["ark-code-latest", "cherry-doubao", "Active"],
            ["deepseek-v3.2", "cherry-doubao", "Active"],
            ["MiniMax-M2.5", "cherry-minimax", "Active"]
        ]
    ))
    print(ui.newline())
    
    print(ui.summary_box("Summary - 总结", {"Version": "v0.4.9", "Status": "Success", "UI": "Beautiful"}))
