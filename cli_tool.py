#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony CLI Tool - 一键启动
v1.0.0
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime


def print_banner():
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                    智韵交响，共创华章                       ║
║                    Symphony v1.0.0                          ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(banner)


def cmd_start():
    print_banner()
    print(f"🚀 Symphony 已启动！")
    print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💡 使用 'symphony --help' 查看更多命令")


def cmd_list():
    print("📋 可用模型：")
    models = [
        "MiniMax-M2.5",
        "ark-code-latest",
        "deepseek-v3.2",
        "doubao-seed-2.0-code",
        "glm-4.7",
        "kimi-k2.5"
    ]
    for i, model in enumerate(models, 1):
        print(f"  {i}. {model}")


def cmd_help():
    help_text = """
Symphony CLI - 使用帮助

命令:
  symphony start    - 启动Symphony
  symphony list     - 列出可用模型
  symphony help     - 显示帮助
  symphony version  - 显示版本

示例:
  symphony start
  symphony list
"""
    print(help_text)


def cmd_version():
    print("Symphony v1.0.0")


def main():
    parser = argparse.ArgumentParser(description="Symphony CLI")
    parser.add_argument("command", nargs="?", default="start",
                       help="命令: start, list, help, version")
    
    args = parser.parse_args()
    
    commands = {
        "start": cmd_start,
        "list": cmd_list,
        "help": cmd_help,
        "version": cmd_version
    }
    
    if args.command in commands:
        commands[args.command]()
    else:
        print(f"❌ 未知命令: {args.command}")
        print("使用 'symphony help' 查看帮助")
        sys.exit(1)


if __name__ == "__main__":
    main()
