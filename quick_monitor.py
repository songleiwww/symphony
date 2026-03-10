#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响调度器 - 一键启动 + 自动监控
同时启动模型调用和监控界面
"""

import subprocess
import sys
import os
import time
import json
from pathlib import Path

# 设置编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

print("="*60)
print("🎼 交响序境调度器 - 一键启动")
print("="*60)

# 日志文件
LOG_FILE = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\orchestration_log.json"
SYMPHONY_PATH = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony"

def show_monitor():
    """显示监控状态"""
    if Path(LOG_FILE).exists():
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            events = json.load(f)
        
        # 统计
        total = len(events)
        running = sum(1 for e in events if e.get("status") == "running")
        completed = sum(1 for e in events if e.get("status") == "completed")
        errors = sum(1 for e in events if e.get("status") == "error")
        
        print(f"\n📊 实时状态 (共{total}条):")
        print(f"   🔄 运行中: {running}")
        print(f"   ✅ 已完成: {completed}")
        print(f"   ❌ 失败: {errors}")
        
        # 最近5条
        print(f"\n📜 最近事件:")
        for e in events[-5:]:
            ts = e.get("timestamp", "")[-8:]
            model = e.get("model", "-")
            status = e.get("status", "")
            icon = {"running": ">>>", "completed": "✅", "error": "❌"}.get(status, "?")
            print(f"   {icon} [{ts}] {model} | {status}")
    else:
        print("\n暂无监控数据")

# 显示当前状态
print("\n当前监控状态:")
show_monitor()

print("\n" + "="*60)
print("使用说明:")
print("="*60)
print("1. 先在这个窗口运行: symphony.py")
print("2. 选择 2 实时监控")
print("3. 在另一个终端运行模型调用")
print("")
print("或者直接运行: python auto_call_models.py")
print("="*60)
