#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
待办事项管理工具 - 主入口文件
"""

from todo.cli import CLI


def main():
    """主函数"""
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
