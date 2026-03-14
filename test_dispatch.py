# -*- coding: utf-8 -*-
"""
测试序境系统 - 模拟用户提问
"""
import sys, os, importlib.util

os.chdir(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')

# Load kernel
spec = importlib.util.spec_from_file_location('kl', 'Kernel/kernel_loader.py')
kl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kl)
kernel = kl.get_kernel()

# Simulate user question
user_question = "帮我写一个Python爬虫"

print("=== 用户提问 ===")
print(f"问题: {user_question}")
print()

# Simple task matching - find best official
# For now, use a simple heuristic
best_official = None
for role in kernel.roles:
    if role.get('角色等级', 5) <= 2:  # High level officials
        best_official = role
        break

if best_official:
    print("=== 调度官属 ===")
    print(f"官名: {best_official.get('官名', '未知')}")
    print(f"职位: {best_official.get('职位', '未知')}")
    print(f"模型: {best_official.get('模型名称')}")
    print(f"服务商: {best_official.get('模型服务商')}")
    print()
    print("=== 回答 ===")
    print("本官收到指令，正在处理...")
    print(f"使用 {best_official.get('模型名称')} 模型进行回答")
else:
    print("未找到合适的官属")
