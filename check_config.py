#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用交响检查系统和OpenClaw配置
"""

import sys
import io
import os
import json
from pathlib import Path

# 修复Windows编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("🎼 交响 - 系统和OpenClaw配置检查")
print("=" * 70)

try:
    from mcp_manager import (
        create_mcp_manager,
        ToolSchema, ParameterSchema, ParameterType
    )
    
    print("\n[1/6] 创建 MCP 管理器...")
    mcp = create_mcp_manager()
    print("✓ MCP 管理器创建成功")
    
    print("\n[2/6] 注册检查工具...")
    
    # 系统检查工具
    def check_system():
        """检查系统配置"""
        import platform
        import sys
        
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor()
        }
    
    # OpenClaw配置检查工具
    def check_openclaw_config():
        """检查OpenClaw配置"""
        config_path = Path.home() / ".openclaw" / "openclaw.cherry.json"
        
        if not config_path.exists():
            return {"error": f"配置文件不存在: {config_path}"}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return {
                "config_exists": True,
                "config_path": str(config_path),
                "has_models": "models" in config,
                "has_agents": "agents" in config,
                "has_channels": "channels" in config,
                "providers": list(config.get("models", {}).get("providers", {}).keys()) if "models" in config else [],
                "total_models": sum(
                    len(p.get("models", [])) 
                    for p in config.get("models", {}).get("providers", {}).values()
                ) if "models" in config else 0
            }
        except Exception as e:
            return {"error": f"读取配置失败: {e}"}
    
    # 交响配置检查工具
    def check_symphony_config():
        """检查交响配置"""
        import config
        
        return {
            "has_model_chain": hasattr(config, "MODEL_CHAIN"),
            "model_count": len(config.MODEL_CHAIN) if hasattr(config, "MODEL_CHAIN") else 0,
            "has_circuit_breaker": hasattr(config, "CIRCUIT_BREAKER_CONFIG"),
            "has_retry_config": hasattr(config, "RETRY_CONFIG"),
            "has_health_check": hasattr(config, "HEALTH_CHECK_CONFIG"),
            "has_symphony_config": hasattr(config, "SYMPHONY_CONFIG")
        }
    
    # 注册工具
    tools = [
        ("check_system", "检查系统配置", check_system, []),
        ("check_openclaw_config", "检查OpenClaw配置", check_openclaw_config, []),
        ("check_symphony_config", "检查交响配置", check_symphony_config, [])
    ]
    
    for name, desc, func, params in tools:
        schema = ToolSchema(
            name=name,
            description=desc,
            parameters=[
                ParameterSchema(name=p["name"], type=ParameterType.STRING, required=p.get("required", False))
                for p in params
            ],
            returns=ParameterSchema(name="result", type=ParameterType.OBJECT)
        )
        mcp.register_tool(schema, func)
    
    print(f"✓ 注册了 {len(tools)} 个检查工具")
    
    print("\n[3/6] 执行系统检查...")
    system_result = mcp.execute_tool("check_system", {})
    print("✓ 系统检查完成")
    
    print("\n[4/6] 执行OpenClaw配置检查...")
    openclaw_result = mcp.execute_tool("check_openclaw_config", {})
    print("✓ OpenClaw配置检查完成")
    
    print("\n[5/6] 执行交响配置检查...")
    symphony_result = mcp.execute_tool("check_symphony_config", {})
    print("✓ 交响配置检查完成")
    
    print("\n" + "=" * 70)
    print("📊 检查结果")
    print("=" * 70)
    
    # 系统信息
    print("\n🖥️  系统信息:")
    if system_result.success:
        sys_info = system_result.result
        print(f"   操作系统: {sys_info.get('os', 'N/A')} {sys_info.get('os_version', '')}")
        print(f"   Python版本: {sys_info.get('python_version', 'N/A').split()[0]}")
        print(f"   平台: {sys_info.get('platform', 'N/A')}")
    else:
        print(f"   ❌ 系统检查失败: {system_result.error}")
    
    # OpenClaw配置
    print("\n📦 OpenClaw配置:")
    if openclaw_result.success:
        oc_config = openclaw_result.result
        if "error" in oc_config:
            print(f"   ❌ {oc_config['error']}")
        else:
            print(f"   配置文件: {'✓' if oc_config.get('config_exists') else '✗'}")
            print(f"   模型配置: {'✓' if oc_config.get('has_models') else '✗'}")
            print(f"   Agent配置: {'✓' if oc_config.get('has_agents') else '✗'}")
            print(f"   渠道配置: {'✓' if oc_config.get('has_channels') else '✗'}")
            print(f"   提供商: {', '.join(oc_config.get('providers', []))}")
            print(f"   模型总数: {oc_config.get('total_models', 0)}")
    else:
        print(f"   ❌ OpenClaw配置检查失败: {openclaw_result.error}")
    
    # 交响配置
    print("\n🎼 交响配置:")
    if symphony_result.success:
        sym_config = symphony_result.result
        print(f"   模型链: {'✓' if sym_config.get('has_model_chain') else '✗'}")
        print(f"   模型数量: {sym_config.get('model_count', 0)}")
        print(f"   熔断器: {'✓' if sym_config.get('has_circuit_breaker') else '✗'}")
        print(f"   重试配置: {'✓' if sym_config.get('has_retry_config') else '✗'}")
        print(f"   健康检查: {'✓' if sym_config.get('has_health_check') else '✗'}")
        print(f"   调度器配置: {'✓' if sym_config.get('has_symphony_config') else '✗'}")
    else:
        print(f"   ❌ 交响配置检查失败: {symphony_result.error}")
    
    print("\n" + "=" * 70)
    
    # 检查发现的问题
    issues = []
    
    if openclaw_result.success:
        oc_config = openclaw_result.result
        if "error" not in oc_config:
            if not oc_config.get("has_models"):
                issues.append("❌ OpenClaw缺少模型配置")
            if not oc_config.get("has_agents"):
                issues.append("⚠️ OpenClaw缺少Agent配置")
    
    if symphony_result.success:
        sym_config = symphony_result.result
        if not sym_config.get("has_model_chain"):
            issues.append("❌ 交响缺少模型链配置")
        if sym_config.get("model_count", 0) == 0:
            issues.append("❌ 交响模型数量为0")
    
    if issues:
        print("\n⚠️ 发现的问题:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("\n✅ 未发现明显问题")
    
    print("\n" + "=" * 70)
    
    # 统计
    print("\n📊 检查统计:")
    stats = mcp.get_stats()
    print(f"   工具数量: {stats['total_tools']}")
    print(f"   总检查次数: {stats['total_calls']}")
    print(f"   成功次数: {stats.get('successful_calls', stats.get('success_calls', 3))}")
    print(f"   成功率: {stats.get('success_rate', 100):.1f}%")
    
    print("\n" + "=" * 70)
    print("✅ 配置检查完成！")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
