#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

# 切换到项目根目录
os.chdir(r"C:\Users\Administrator\.openclaw\workspace\skills\symphony")
sys.path.insert(0, os.getcwd())

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("Symphony System Test - Direct Path")
print("=" * 60)

# Test 1: Database
print("\n[Test 1] Database")
import sqlite3
conn = sqlite3.connect("data/symphony.db")
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM 官属角色表")
roles = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM 模型配置表")
models = cursor.fetchone()[0]
conn.close()
print(f"  OK - Roles: {roles}, Models: {models}")

# Test 2: Kernel
print("\n[Test 2] Kernel Loader")
from kernel.kernel_loader import get_kernel
kernel = get_kernel()
print(f"  OK - Roles: {len(kernel.roles)}, Models: {len(kernel.models)}")

# Test 3: Task Manager
print("\n[Test 3] Task Manager")
from core.task_manager import get_task_manager
tm = get_task_manager()
task = tm.create_task(content="Test task")
print(f"  OK - Task: {task.task_id[:8]}")

# Test 4: Memory
print("\n[Test 4] Memory System")
from core.memory_system import get_memory_system
ms = get_memory_system()
mem_id = ms.add_memory("Test memory", "short_term", 0.5)
print(f"  OK - Memory: {mem_id}")

# Test 5: Model Manager
print("\n[Test 5] Model Manager")
from core.model_call_manager import get_model_manager
mm = get_model_manager()
print(f"  OK - Models loaded: {len(mm.model_configs)}")

print("\n" + "=" * 60)
print("All Tests PASSED!")
print("=" * 60)
