#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响开发建议 - 真实调用3个模型
Symphony Development Suggestions - Real 3-Model Call
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
# 从OpenClaw配置读取模型
# =============================================================================

def load_models_from_config() -> List[Dict[str, Any]]:
    """从OpenClaw配置加载模型"""
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


def call_model(model_config: Dict, prompt: str) -> Dict[str, Any]:
    """调用单个模型并获取Token用量"""
    url = f"{model_config['base_url']}/chat/completions"
    headers = {
        "Authorization": f"Bearer {model_config['api_key']}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_config["model_id"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 800,
        "temperature": 0.7
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=120)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # 获取Token用量
            usage = result.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
            
            return {
                "success": True,
                "model": model_config["name"],
                "provider": model_config["provider"],
                "response": content,
                "elapsed": elapsed,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "model": model_config["name"],
                "provider": model_config["provider"],
                "error": f"HTTP {response.status_code}",
                "elapsed": elapsed,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "success": False,
            "model": model_config["name"],
            "provider": model_config["provider"],
            "error": str(e)[:100],
            "elapsed": time.time() - start_time,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """主程序"""
    print("=" * 80)
    print("🎼 交响开发建议 - 真实调用3个模型")
    print("Symphony Development Suggestions - Real 3-Model Call")
    print("=" * 80)
    
    # 1. 加载模型
    print("\n📂 加载模型配置...")
    models = load_models_from_config()
    print(f"   已加载 {len(models)} 个模型")
    
    # 2. 选择3个模型
    print("\n📋 选择3个模型...")
    
    # 优先选择NVIDIA模型
    nvidia_models = [m for m in models if m["provider"] == "cherry-nvidia"]
    
    # 选择3个不同的模型
    selected = nvidia_models[:3] if len(nvidia_models) >= 3 else models[:3]
    
    print(f"   选择 {len(selected)} 个模型:")
    for i, m in enumerate(selected, 1):
        print(f"   {i}. {m['name']} ({m['provider']})")
    
    # 3. 准备问题
    question = """请为交响（Symphony）多模型协作系统提供开发建议。
要求：
1. 专注于一个方面（如架构、性能、可靠性等）
2. 提供具体的改进建议
3. 用中文回答
4. 回答要简洁，最多5条建议"""
    
    print(f"\n❓ 问题: {question[:50]}...")
    
    # 4. 依次调用3个模型
    print("\n" + "=" * 80)
    print("🚀 开始调用模型...")
    print("=" * 80)
    
    results = []
    total_prompt_tokens = 0
    total_completion_tokens = 0
    
    for i, model in enumerate(selected, 1):
        print(f"\n[{i}/{len(selected)}] 调用 {model['name']}...")
        
        result = call_model(model, question)
        results.append(result)
        
        if result["success"]:
            total_prompt_tokens += result["prompt_tokens"]
            total_completion_tokens += result["completion_tokens"]
            
            print(f"   ✅ 成功! 耗时: {result['elapsed']:.2f}s")
            print(f"   📊 Token: 输入={result['prompt_tokens']}, 输出={result['completion_tokens']}, 总计={result['total_tokens']}")
            print(f"\n   💬 回答:")
            # 缩进显示回答
            for line in result["response"].split('\n')[:10]:
                print(f"      {line}")
        else:
            print(f"   ❌ 失败: {result['error'][:50]}")
        
        # 每个模型之间稍作休息
        if i < len(selected):
            time.sleep(2)
    
    # 5. 汇总结果
    print("\n" + "=" * 80)
    print("📊 结果汇总")
    print("=" * 80)
    
    success_count = sum(1 for r in results if r["success"])
    
    print(f"\n🎯 成功调用: {success_count}/{len(results)} 个模型")
    print(f"\n📈 Token用量统计:")
    print(f"   输入Token: {total_prompt_tokens}")
    print(f"   输出Token: {total_completion_tokens}")
    print(f"   总Token: {total_prompt_tokens + total_completion_tokens}")
    
    print(f"\n📋 各模型贡献:")
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"\n{status} {r['model']} ({r['provider']})")
        if r["success"]:
            print(f"   Token: {r['total_tokens']} (输入{r['prompt_tokens']}/输出{r['completion_tokens']})")
            print(f"   建议: {r['response'][:200]}...")
        else:
            print(f"   错误: {r['error']}")
    
    # 6. 保存结果
    output = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "models_called": len(selected),
        "success_count": success_count,
        "total_tokens": {
            "prompt": total_prompt_tokens,
            "completion": total_completion_tokens,
            "total": total_prompt_tokens + total_completion_tokens
        },
        "results": results
    }
    
    with open("symphony_dev_suggestions.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 已保存到: symphony_dev_suggestions.json")
    
    print("\n" + "=" * 80)
    print("✅ 交响开发建议获取完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
