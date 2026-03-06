#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实模型调用连接检测
"""

import sys
import io

# 修复Windows编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
import time
import requests
from datetime import datetime
from pathlib import Path

# 加载OpenClaw配置
config_path = Path.home() / ".openclaw" / "openclaw.cherry.json"

print("=" * 80)
print("🔗 真实模型调用连接检测")
print("=" * 80)

# 1. 加载配置
print(f"\n[1] 加载OpenClaw配置...")
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    print(f"   ✅ 配置加载成功: {config_path}")
except Exception as e:
    print(f"   ❌ 配置加载失败: {e}")
    sys.exit(1)

# 2. 提取提供商和模型
print(f"\n[2] 提取模型配置...")
providers = config.get("models", {}).get("providers", {})
print(f"   ✅ 提供商数量: {len(providers)}")

all_models = []
for provider_name, provider_config in providers.items():
    models = provider_config.get("models", [])
    api_key = provider_config.get("apiKey", "")
    base_url = provider_config.get("baseURL", "")
    api_type = provider_config.get("apiType", "openai-completions")
    
    for model in models:
        all_models.append({
            "provider": provider_name,
            "model_id": model.get("id", ""),
            "alias": model.get("name", model.get("id", "")),
            "api_key": api_key,
            "base_url": base_url,
            "api_type": api_type
        })

print(f"   ✅ 模型总数: {len(all_models)}")

# 3. 显示前3个模型
print(f"\n[3] 模型列表（前3个）:")
for i, model in enumerate(all_models[:3], 1):
    print(f"\n   {i}. {model['alias']}")
    print(f"      提供商: {model['provider']}")
    print(f"      模型ID: {model['model_id']}")
    print(f"      API类型: {model['api_type']}")
    print(f"      Base URL: {model['base_url']}")
    print(f"      API Key: {model['api_key'][:30]}...")

# 4. 连接检测
print(f"\n[4] 连接检测...")
results = []

for i, model in enumerate(all_models[:3], 1):  # 只测试前3个，避免消耗太多
    print(f"\n   测试 {i}: {model['alias']}...")
    
    start_time = time.time()
    success = False
    error_msg = ""
    latency = 0
    
    try:
        if model["api_type"] == "openai-completions":
            # 测试OpenAI兼容API
            url = f"{model['base_url']}/chat/completions"
            headers = {
                "Authorization": f"Bearer {model['api_key']}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model["model_id"],
                "messages": [{"role": "user", "content": "你好"}],
                "max_tokens": 50,
                "temperature": 0.7
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                success = True
                result_data = response.json()
                print(f"      ✅ 连接成功！")
                print(f"      响应: {result_data['choices'][0]['message']['content'][:50]}...")
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                print(f"      ❌ 连接失败: {error_msg}")
        
        elif model["api_type"] == "anthropic-messages":
            # 测试Anthropic Messages API
            url = f"{model['base_url']}/v1/messages"
            headers = {
                "x-api-key": model["api_key"],
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            data = {
                "model": model["model_id"],
                "messages": [{"role": "user", "content": "你好"}],
                "max_tokens": 50
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                success = True
                result_data = response.json()
                print(f"      ✅ 连接成功！")
                print(f"      响应: {result_data['content'][0]['text'][:50]}...")
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                print(f"      ❌ 连接失败: {error_msg}")
    
    except Exception as e:
        error_msg = f"异常: {str(e)}"
        print(f"      ❌ 连接异常: {error_msg}")
    
    latency = time.time() - start_time
    
    results.append({
        "model": model["alias"],
        "provider": model["provider"],
        "success": success,
        "latency": latency,
        "error": error_msg,
        "timestamp": datetime.now().isoformat()
    })

# 5. 生成报告
print(f"\n" + "=" * 80)
print("📊 真实模型调用连接检测报告")
print("=" * 80)

print(f"\n📅 检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"🔢 测试模型数: {len(results)}")

success_count = sum(1 for r in results if r["success"])
print(f"✅ 成功: {success_count}/{len(results)}")
print(f"❌ 失败: {len(results) - success_count}/{len(results)}")

print(f"\n📋 详细结果:")
for i, result in enumerate(results, 1):
    status = "✅" if result["success"] else "❌"
    print(f"\n{i}. {status} {result['model']} ({result['provider']})")
    print(f"   延迟: {result['latency']:.2f}秒")
    if not result["success"]:
        print(f"   错误: {result['error']}")

print(f"\n" + "=" * 80)
print("✅ 连接检测完成！")
print("=" * 80)

# 6. 保存报告
report_path = Path(__file__).parent / "REAL_CONNECTION_TEST_REPORT.json"
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump({
        "test_time": datetime.now().isoformat(),
        "total_models": len(results),
        "success_count": success_count,
        "results": results
    }, f, ensure_ascii=False, indent=2)

print(f"\n📄 报告已保存: {report_path}")
