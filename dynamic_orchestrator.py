#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版动态多模型调度器 - 优先选择能工作的模型
Optimized Dynamic Multi-Model Orchestrator
"""

import json
import time
import requests
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
# 从OpenClaw配置读取真实模型
# =============================================================================

def load_models_from_config() -> List[Dict[str, Any]]:
    """从OpenClaw配置文件加载模型"""
    config_path = Path(r"C:\Users\Administrator\.openclaw\openclaw.cherry.json")
    
    if not config_path.exists():
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


def call_openai_model(model_config: Dict, prompt: str) -> Dict[str, Any]:
    """调用OpenAI格式的模型"""
    url = f"{model_config['base_url']}/chat/completions"
    headers = {
        "Authorization": f"Bearer {model_config['api_key']}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_config["model_id"],
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
            return {
                "success": True,
                "model": model_config["name"],
                "provider": model_config["provider"],
                "response": content,
                "elapsed": elapsed,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "model": model_config["name"],
                "provider": model_config["provider"],
                "error": f"HTTP {response.status_code}",
                "elapsed": elapsed,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "success": False,
            "model": model_config["name"],
            "provider": model_config["provider"],
            "error": str(e)[:100],
            "elapsed": time.time() - start_time,
            "timestamp": datetime.now().isoformat()
        }


def call_model(model_config: Dict, prompt: str) -> Dict[str, Any]:
    """调用单个模型"""
    # 目前只支持OpenAI格式
    return call_openai_model(model_config, prompt)


def sequential_schedule(models: List[Dict], prompt: str) -> List[Dict[str, Any]]:
    """顺序调度多个模型"""
    results = []
    
    print(f"\n🔄 顺序调度 {len(models)} 个模型")
    
    for i, model in enumerate(models, 1):
        print(f"\n[{i}/{len(models)}] {model['name']} ({model['provider']})...")
        
        result = call_model(model, prompt)
        results.append(result)
        
        if result["success"]:
            print(f"   ✅ 成功! {result['elapsed']:.2f}s")
            print(f"   → {result['response'][:100]}...")
        else:
            print(f"   ❌ 失败: {result['error'][:50]}")
        
        if i < len(models):
            time.sleep(0.5)
    
    return results


def main():
    """主程序"""
    print("=" * 80)
    print("Optimized Dynamic Multi-Model Orchestrator")
    print("优化版动态多模型调度器")
    print("=" * 80)
    
    # 1. 读取配置
    print("\n📂 读取配置...")
    models = load_models_from_config()
    print(f"   已加载 {len(models)} 个模型")
    
    # 2. 过滤能工作的模型（NVIDIA模型API是正常的）
    print("\n📋 过滤能工作的模型...")
    
    # 优先选择NVIDIA的模型（已知能工作）
    working_models = [m for m in models if m["provider"] == "cherry-nvidia"]
    
    # 如果NVIDIA模型不够，选择其他能工作的
    if len(working_models) < 2:
        working_models = [m for m in models if m["provider"] in ["cherry-nvidia", "cherry-modelscope"]]
    
    print(f"   可用模型: {len(working_models)}个")
    
    # 3. 选择不同提供商的模型（每个提供商选一个）
    selected = []
    used_providers = set()
    
    for m in working_models:
        if m["provider"] not in used_providers:
            selected.append(m)
            used_providers.add(m["provider"])
            if len(selected) >= 3:  # 选择3个模型
                break
    
    # 如果不够3个，从同一提供商补充
    if len(selected) < 3:
        for m in working_models:
            if m not in selected:
                selected.append(m)
                if len(selected) >= 3:
                    break
    
    print(f"   选择 {len(selected)} 个模型:")
    for m in selected:
        print(f"   - {m['name']} ({m['provider']})")
    
    # 4. 调度任务
    prompt = "请用一句话介绍你自己，并说明你最擅长什么"
    
    print(f"\n🚀 执行调度...")
    print(f"   Prompt: {prompt}")
    
    # 5. 执行顺序调度
    results = sequential_schedule(selected, prompt)
    
    # 6. 汇总
    print("\n" + "=" * 80)
    print("📊 结果汇总")
    print("=" * 80)
    
    success = sum(1 for r in results if r["success"])
    print(f"\n成功: {success}/{len(results)}")
    
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"\n{status} {r['model']}")
        if r["success"]:
            print(f"   {r['response'][:150]}...")
            print(f"   耗时: {r['elapsed']:.2f}s")
        else:
            print(f"   错误: {r['error']}")
    
    # 保存
    output = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "success_count": success
    }
    
    with open("orchestration_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 已保存到 orchestration_results.json")
    print("\n✅ 完成!")


if __name__ == "__main__":
    main()
