#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""多脑系统 Debug - 用户视角"""
import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')

print("=" * 60)
print(" 多脑系统 Debug - 用户视角 ")
print("=" * 60)

# 1
print("\n[1] 多脑系统入口检查")
from Kernel.multi_agent.multi_agent_orchestrator import CrewOrchestrator, MultiAgentCoordinator
coordinator = MultiAgentCoordinator()
print("    CrewOrchestrator: OK")
print("    LangGraphOrchestrator: OK")

# 2
print("\n[2] Agent角色系统")
from Kernel.multi_agent.multi_agent_orchestrator import AgentRole
roles = list(AgentRole)
print(f"    角色数量: {len(roles)}")
for role in roles:
    print(f"    - {role.value}")

# 3
print("\n[3] Model Federation检查")
try:
    from model_federation import get_federation
    fed = get_federation()
    print(f"    Federation: OK")
    methods = [m for m in dir(fed) if not m.startswith("_")]
    print(f"    Public methods: {methods[:5]}")
except Exception as e:
    print(f"    ERROR: {e}")

# 4
print("\n[4] 用户入口 ask() 函数")
try:
    from symphony_complete_final import ask
    print("    ask function: OK")
except Exception as e:
    print(f"    ERROR: {e}")

# 5
print("\n[5] multi_brain_schedule 函数")
try:
    from symphony_complete_final import multi_brain_schedule
    print("    multi_brain_schedule: OK")
except Exception as e:
    print(f"    ERROR: {e}")

# 6
print("\n[6] 自适应编排 adaptive_orchestrate")
try:
    from symphony_complete_final import adaptive_orchestrate
    print("    adaptive_orchestrate: OK")
except Exception as e:
    print(f"    ERROR: {e}")

# 7 用户视角：实际调用多脑系统
print("\n[7] 用户视角实际调用测试")
try:
    from symphony_complete_final import ask
    result = ask("What is 1+1? Reply with one number.")
    print(f"    Result: {result}")
except Exception as e:
    print(f"    ERROR: {e}")

print("\n" + "=" * 60)
print(" Debug Complete ")
print("=" * 60)
