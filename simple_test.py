#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本 - 验证MCP管理器基本功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("MCP管理器 - 简单测试")
print("=" * 60)

try:
    from mcp_manager import (
        MCPManager, create_mcp_manager,
        ToolSchema, ParameterSchema, ParameterType
    )
    
    print("✓ 模块导入成功")
    
    # 创建管理器
    mcp = create_mcp_manager()
    print("✓ MCP管理器创建成功")
    
    # 定义一个简单工具
    def add(a, b):
        return a + b
    
    schema = ToolSchema(
        name="add",
        description="加法工具",
        parameters=[
            ParameterSchema(name="a", type=ParameterType.INTEGER, required=True),
            ParameterSchema(name="b", type=ParameterType.INTEGER, required=True)
        ],
        returns=ParameterSchema(name="result", type=ParameterType.INTEGER)
    )
    
    mcp.register_tool(schema, add)
    print("✓ 工具注册成功")
    
    # 执行工具
    result = mcp.execute_tool("add", {"a": 5, "b": 3})
    
    if result.success:
        print(f"✓ 工具执行成功: 5 + 3 = {result.result}")
    else:
        print(f"✗ 工具执行失败: {result.error}")
    
    # 显示统计
    stats = mcp.get_stats()
    print(f"\n统计信息:")
    print(f"  工具数量: {stats['total_tools']}")
    print(f"  总调用次数: {stats['total_calls']}")
    print(f"  成功率: {stats['success_rate']:.1f}%")
    
    print("\n" + "=" * 60)
    print("所有测试通过！✓")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
