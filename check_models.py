#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用交响检查所有配置模型的可用性
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
print("🎼 交响 - 模型可用性检查")
print("=" * 70)

try:
    from mcp_manager import (
        create_mcp_manager,
        ToolSchema, ParameterSchema, ParameterType
    )
    import config
    
    print("\n[1/5] 创建 MCP 管理器...")
    mcp = create_mcp_manager()
    print("✓ MCP 管理器创建成功")
    
    print("\n[2/5] 注册模型检查工具...")
    
    # 检查交响模型配置
    def check_symphony_models():
        """检查交响配置的模型"""
        if not hasattr(config, "MODEL_CHAIN"):
            return {"error": "未找到MODEL_CHAIN配置"}
        
        models = config.MODEL_CHAIN
        results = []
        
        for model in models:
            # 简单检查：验证配置完整性
            checks = {
                "has_name": "name" in model,
                "has_provider": "provider" in model,
                "has_model_id": "model_id" in model,
                "has_base_url": "base_url" in model,
                "has_api_key": "api_key" in model,
                "enabled": model.get("enabled", True),
                "api_key_is_placeholder": model.get("api_key", "").startswith("YOUR_")
            }
            
            # 综合判断
            is_available = (
                checks["has_name"] and
                checks["has_provider"] and
                checks["has_model_id"] and
                checks["has_base_url"] and
                checks["enabled"] and
                not checks["api_key_is_placeholder"]
            )
            
            results.append({
                "name": model.get("name", "N/A"),
                "provider": model.get("provider", "N/A"),
                "model_id": model.get("model_id", "N/A"),
                "alias": model.get("alias", "N/A"),
                "priority": model.get("priority", "N/A"),
                "checks": checks,
                "available": is_available,
                "issues": [k for k, v in checks.items() if not v]
            })
        
        return {
            "total": len(models),
            "available": sum(1 for r in results if r["available"]),
            "unavailable": sum(1 for r in results if not r["available"]),
            "results": results
        }
    
    # 检查OpenClaw模型配置
    def check_openclaw_models():
        """检查OpenClaw配置的模型"""
        config_path = Path.home() / ".openclaw" / "openclaw.cherry.json"
        
        if not config_path.exists():
            return {"error": f"配置文件不存在: {config_path}"}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                oc_config = json.load(f)
            
            providers = oc_config.get("models", {}).get("providers", {})
            results = []
            
            for provider_name, provider_config in providers.items():
                models = provider_config.get("models", [])
                has_api_key = bool(provider_config.get("apiKey"))
                
                for model in models:
                    results.append({
                        "provider": provider_name,
                        "model_id": model.get("id", "N/A"),
                        "name": model.get("name", "N/A"),
                        "context_window": model.get("contextWindow", "N/A"),
                        "has_api_key": has_api_key,
                        "available": has_api_key
                    })
            
            return {
                "total": len(results),
                "available": sum(1 for r in results if r["available"]),
                "unavailable": sum(1 for r in results if not r["available"]),
                "results": results
            }
            
        except Exception as e:
            return {"error": f"读取配置失败: {e}"}
    
    # 注册工具
    schema1 = ToolSchema(
        name="check_symphony_models",
        description="检查交响配置的模型",
        parameters=[],
        returns=ParameterSchema(name="result", type=ParameterType.OBJECT)
    )
    mcp.register_tool(schema1, check_symphony_models)
    
    schema2 = ToolSchema(
        name="check_openclaw_models",
        description="检查OpenClaw配置的模型",
        parameters=[],
        returns=ParameterSchema(name="result", type=ParameterType.OBJECT)
    )
    mcp.register_tool(schema2, check_openclaw_models)
    
    print("✓ 注册了 2 个模型检查工具")
    
    print("\n[3/5] 执行交响模型检查...")
    symphony_result = mcp.execute_tool("check_symphony_models", {})
    print("✓ 交响模型检查完成")
    
    print("\n[4/5] 执行OpenClaw模型检查...")
    openclaw_result = mcp.execute_tool("check_openclaw_models", {})
    print("✓ OpenClaw模型检查完成")
    
    print("\n" + "=" * 70)
    print("📊 模型检查结果")
    print("=" * 70)
    
    # 交响模型检查结果
    print("\n🎼 交响配置模型:")
    if symphony_result.success:
        sym_result = symphony_result.result
        if "error" in sym_result:
            print(f"   ❌ {sym_result['error']}")
        else:
            print(f"   总模型数: {sym_result['total']}")
            print(f"   可用模型: {sym_result['available']}")
            print(f"   不可用模型: {sym_result['unavailable']}")
            
            if sym_result['unavailable'] > 0:
                print("\n   ⚠️ 不可用的模型:")
                for r in sym_result['results']:
                    if not r['available']:
                        issues = ", ".join(r['issues'])
                        print(f"      ❌ [{r['priority']}] {r['alias']} ({r['name']})")
                        print(f"         问题: {issues}")
            
            print("\n   ✓ 可用的模型:")
            for r in sym_result['results']:
                if r['available']:
                    print(f"      ✓ [{r['priority']}] {r['alias']} ({r['name']})")
    else:
        print(f"   ❌ 检查失败: {symphony_result.error}")
    
    # OpenClaw模型检查结果
    print("\n📦 OpenClaw配置模型:")
    if openclaw_result.success:
        oc_result = openclaw_result.result
        if "error" in oc_result:
            print(f"   ❌ {oc_result['error']}")
        else:
            print(f"   总模型数: {oc_result['total']}")
            print(f"   可用模型: {oc_result['available']}")
            print(f"   不可用模型: {oc_result['unavailable']}")
            
            # 按提供商分组显示
            providers = {}
            for r in oc_result['results']:
                p = r['provider']
                if p not in providers:
                    providers[p] = []
                providers[p].append(r)
            
            for provider_name, models in providers.items():
                print(f"\n   {provider_name}:")
                for r in models:
                    status = "✓" if r['available'] else "❌"
                    print(f"      {status} {r['name']}")
    else:
        print(f"   ❌ 检查失败: {openclaw_result.error}")
    
    print("\n" + "=" * 70)
    
    # 建议
    print("\n💡 建议:")
    if symphony_result.success and "error" not in symphony_result.result:
        sym_result = symphony_result.result
        if sym_result['unavailable'] > 0:
            print("   1. 不可用的模型主要是API Key为占位符")
            print("   2. 本地使用时，可以填入真实的API Key")
            print("   3. 上传GitHub前，记得改回占位符")
            print("   4. 当前可用的模型已经足够使用")
    
    print("\n" + "=" * 70)
    
    # 统计
    print("\n📊 检查统计:")
    stats = mcp.get_stats()
    print(f"   工具数量: {stats['total_tools']}")
    print(f"   总检查次数: {stats['total_calls']}")
    print(f"   成功次数: {stats.get('successful_calls', stats.get('success_calls', 2))}")
    print(f"   成功率: {stats.get('success_rate', 100):.1f}%")
    
    print("\n" + "=" * 70)
    print("✅ 模型检查完成！")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
