#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
传参调度器 - 读取真实模型参数，并行调度
Parameter-Based Orchestrator - Read real model params, parallel scheduling
"""

import json
import time
import requests
import concurrent.futures
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path


# =============================================================================
# 修复Windows编码
# =============================================================================

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# =============================================================================
# 从配置文件读取真实模型参数
# =============================================================================

def load_model_params_from_config() -> List[Dict[str, Any]]:
    """从OpenClaw配置读取真实模型参数"""
    config_path = Path(r"C:\Users\Administrator\.openclaw\openclaw.cherry.json")
    
    if not config_path.exists():
        print(f"Config not found: {config_path}")
        return []
    
    config = json.loads(config_path.read_text(encoding='utf-8'))
    
    models = []
    providers = config.get("models", {}).get("providers", {})
    
    for provider_name, provider_config in providers.items():
        base_url = provider_config.get("baseUrl", "")
        api_key = provider_config.get("apiKey", "")
        api_type = provider_config.get("api", "")
        
        for model in provider_config.get("models", []):
            model_id = model.get("id", "")
            context_window = model.get("contextWindow", 128000)
            
            models.append({
                "name": model_id,
                "provider": provider_name,
                "model_id": model_id,
                "base_url": base_url,
                "api_key": api_key,
                "api_type": api_type,
                "context_window": context_window,
                "enabled": True
            })
    
    return models


# =============================================================================
# 模型调用器
# =============================================================================

def call_model(model_params: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    """使用传入的模型参数调用模型"""
    
    # 从参数中提取配置
    base_url = model_params.get("base_url", "")
    api_key = model_params.get("api_key", "")
    model_id = model_params.get("model_id", "")
    provider = model_params.get("provider", "")
    
    # 构建请求
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})
            
            return {
                "success": True,
                "model": model_id,
                "provider": provider,
                "response": content,
                "elapsed": elapsed,
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "model": model_id,
                "provider": provider,
                "error": f"HTTP {response.status_code}",
                "elapsed": elapsed,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "success": False,
            "model": model_id,
            "provider": provider,
            "error": str(e)[:100],
            "elapsed": time.time() - start_time,
            "timestamp": datetime.now().isoformat()
        }


# =============================================================================
# 并行调度器
# =============================================================================

def parallel_schedule(model_params_list: List[Dict[str, Any]], prompt: str) -> List[Dict[str, Any]]:
    """并行调度多个模型"""
    
    print(f"\n⚡ 并行调度 {len(model_params_list)} 个模型")
    print(f"   Prompt: {prompt[:50]}...")
    
    results = []
    
    # 使用线程池并行调用
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(model_params_list)) as executor:
        # 提交所有任务
        future_to_model = {
            executor.submit(call_model, params, prompt): params 
            for params in model_params_list
        }
        
        # 收集结果
        for future in concurrent.futures.as_completed(future_to_model):
            params = future_to_model[future]
            try:
                result = future.result()
                results.append(result)
                
                status = "✅" if result["success"] else "❌"
                print(f"\n{status} {result['model']} ({result['provider']})")
                if result["success"]:
                    print(f"   耗时: {result['elapsed']:.2f}s")
                    print(f"   Token: {result.get('total_tokens', 0)}")
                else:
                    print(f"   错误: {result['error'][:50]}")
            except Exception as e:
                print(f"\n❌ {params['model_id']}: 异常 {str(e)[:50]}")
    
    return results


# =============================================================================
# 主程序
# =============================================================================

def main():
    """主程序"""
    print("=" * 80)
    print("⚡ 传参调度器 - 并行调度真实模型")
    print("Parameter-Based Orchestrator - Parallel Real Model Scheduling")
    print("=" * 80)
    
    # 1. 从配置文件读取真实模型参数
    print("\n📂 步骤1: 从配置文件读取真实模型参数...")
    all_models = load_model_params_from_config()
    print(f"   已加载 {len(all_models)} 个模型的参数")
    
    # 显示可用的模型
    print("\n📋 可用模型:")
    for i, m in enumerate(all_models[:5], 1):
        print(f"   {i}. {m['name']} ({m['provider']})")
    
    # 2. 选择要调度的模型（选择NVIDIA的模型）
    print("\n📋 步骤2: 选择要调度的模型...")
    
    # 过滤NVIDIA模型
    nvidia_models = [m for m in all_models if m["provider"] == "cherry-nvidia"]
    
    # 选择3个不同的模型
    selected_params = nvidia_models[:3]
    
    print(f"   选择 {len(selected_params)} 个模型:")
    for m in selected_params:
        print(f"   - {m['name']} ({m['provider']})")
        print(f"     API: {m['base_url'][:50]}...")
    
    # 3. 准备任务
    prompt = "请用一句话介绍你自己，并说明你最擅长什么领域"
    
    print(f"\n📝 步骤3: 准备调度任务...")
    print(f"   Prompt: {prompt}")
    
    # 4. 并行调度
    print(f"\n🚀 步骤4: 启动并行调度...")
    print("=" * 80)
    
    start = time.time()
    results = parallel_schedule(selected_params, prompt)
    total_time = time.time() - start
    
    # 5. 汇总结果
    print("\n" + "=" * 80)
    print("📊 并行调度结果汇总")
    print("=" * 80)
    
    success_count = sum(1 for r in results if r["success"])
    total_tokens = sum(r.get("total_tokens", 0) for r in results if r["success"])
    
    print(f"\n✅ 成功: {success_count}/{len(results)}")
    print(f"📈 总Token: {total_tokens}")
    print(f"⏱️ 总耗时: {total_time:.2f}s")
    
    print(f"\n📋 各模型结果:")
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"\n{status} {r['model']} ({r['provider']})")
        if r["success"]:
            print(f"   回答: {r['response'][:100]}...")
            print(f"   耗时: {r['elapsed']:.2f}s")
            print(f"   Token: {r.get('total_tokens', 0)}")
        else:
            print(f"   错误: {r['error']}")
    
    # 6. 保存结果
    output = {
        "timestamp": datetime.now().isoformat(),
        "mode": "parallel",
        "models_count": len(selected_params),
        "success_count": success_count,
        "total_tokens": total_tokens,
        "total_time": total_time,
        "results": results
    }
    
    with open("parallel_orchestrator_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 结果已保存到: parallel_orchestrator_results.json")
    
    print("\n" + "=" * 80)
    print("✅ 传参并行调度完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
