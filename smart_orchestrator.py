#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能调度器 - 支持多种调度策略，控制主模型负担
Smart Orchestrator - Multiple strategies, control main model load
"""

import json
import time
import requests
import concurrent.futures
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from enum import Enum


# =============================================================================
# 修复Windows编码
# =============================================================================

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# =============================================================================
# 调度策略枚举
# =============================================================================

class OrchestrationStrategy(Enum):
    PARALLEL = "parallel"      # 并行调度
    SEQUENTIAL = "sequential"   # 顺序调度
    CHAIN = "chain"            # 链式调度（模型1→分析→模型2）
    ADAPTIVE = "adaptive"       # 自适应调度


# =============================================================================
# 从配置文件读取模型
# =============================================================================

def load_models_from_config() -> List[Dict[str, Any]]:
    """从OpenClaw配置读取模型"""
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
                "enabled": True,
                "failure_count": 0,
                "success_count": 0,
                "avg_latency": 0
            })
    
    return models


# =============================================================================
# 模型调用
# =============================================================================

def call_model(model_params: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    """调用单个模型"""
    url = f"{model_params['base_url']}/chat/completions"
    headers = {
        "Authorization": f"Bearer {model_params['api_key']}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_params["model_id"],
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
                "model": model_params["model_id"],
                "provider": model_params["provider"],
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
                "model": model_params["model_id"],
                "provider": model_params["provider"],
                "error": f"HTTP {response.status_code}",
                "elapsed": elapsed,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "success": False,
            "model": model_params["model_id"],
            "provider": model_params["provider"],
            "error": str(e)[:100],
            "elapsed": time.time() - start_time,
            "timestamp": datetime.now().isoformat()
        }


# =============================================================================
# 智能调度器
# =============================================================================

class SmartOrchestrator:
    """智能调度器"""
    
    def __init__(self):
        self.models = load_models_from_config()
        self.call_history = []
        self.api_limit_detected = False
        self.main_model_load = 0
        
    def detect_api_limits(self) -> bool:
        """检测API限制"""
        # 检查最近失败的调用
        recent_failures = sum(
            1 for h in self.call_history[-10:] 
            if not h.get("success", False) and "429" in str(h.get("error", ""))
        )
        
        if recent_failures >= 3:
            self.api_limit_detected = True
            print("⚠️  检测到API限制！")
            return True
        
        return False
    
    def select_strategy(self) -> OrchestrationStrategy:
        """选择调度策略"""
        # 检测API限制
        if self.detect_api_limits():
            return OrchestrationStrategy.SEQUENTIAL
        
        # 检查主模型负担
        if self.main_model_load > 80:
            return OrchestrationStrategy.CHAIN
        
        # 默认使用并行
        return OrchestrationStrategy.PARALLEL
    
    def parallel_schedule(self, models: List[Dict], prompt: str) -> List[Dict]:
        """并行调度"""
        print("\n⚡ 使用并行调度策略")
        
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(models)) as executor:
            future_to_model = {
                executor.submit(call_model, m, prompt): m 
                for m in models
            }
            
            for future in concurrent.futures.as_completed(future_to_model):
                result = future.result()
                results.append(result)
                self.call_history.append(result)
                
                status = "✅" if result["success"] else "❌"
                print(f"  {status} {result['model']}: {result.get('elapsed', 0):.2f}s")
        
        return results
    
    def sequential_schedule(self, models: List[Dict], prompt: str) -> List[Dict]:
        """顺序调度"""
        print("\n🔄 使用顺序调度策略")
        
        results = []
        
        for i, model in enumerate(models, 1):
            print(f"  [{i}/{len(models)}] 调用 {model['model_id']}...")
            
            result = call_model(model, prompt)
            results.append(result)
            self.call_history.append(result)
            
            status = "✅" if result["success"] else "❌"
            print(f"    {status} 耗时: {result.get('elapsed', 0):.2f}s")
            
            # 每个模型之间增加延迟，避免API限制
            if i < len(models):
                time.sleep(3)
        
        return results
    
    def chain_schedule(self, models: List[Dict], prompt: str) -> List[Dict]:
        """
        链式调度 - 减轻主模型负担
        流程：模型1 → 我分析 → 模型2 → 我分析
        """
        print("\n🔗 使用链式调度策略（减轻主模型负担）")
        
        results = []
        
        for i, model in enumerate(models, 1):
            print(f"\n  [{i}/{len(models)}] 链式调用 {model['model_id']}...")
            
            # 1. 调用模型
            result = call_model(model, prompt)
            results.append(result)
            self.call_history.append(result)
            
            status = "✅" if result["success"] else "❌"
            print(f"    {status} 模型响应: {result.get('elapsed', 0):.2f}s")
            
            if result["success"]:
                # 2. 我分析结果（减轻主模型负担）
                analysis = f"分析 {model['model_id']} 的回答：\n{result['response'][:200]}..."
                print(f"    📝 我已分析结果")
                result["analysis"] = analysis
            
            # 增加延迟
            if i < len(models):
                time.sleep(2)
        
        return results
    
    def orchestrate(self, prompt: str, strategy: Optional[OrchestrationStrategy] = None) -> List[Dict]:
        """执行调度"""
        # 选择模型
        nvidia_models = [m for m in self.models if m["provider"] == "cherry-nvidia"]
        selected = nvidia_models[:3]
        
        print("=" * 80)
        print(f"🎯 智能调度器")
        print("=" * 80)
        print(f"\n📋 选择 {len(selected)} 个模型:")
        for m in selected:
            print(f"   - {m['name']} ({m['provider']})")
        
        # 选择策略
        if strategy is None:
            strategy = self.select_strategy()
        
        print(f"\n🚀 使用策略: {strategy.value}")
        
        # 执行调度
        if strategy == OrchestrationStrategy.PARALLEL:
            return self.parallel_schedule(selected, prompt)
        elif strategy == OrchestrationStrategy.SEQUENTIAL:
            return self.sequential_schedule(selected, prompt)
        elif strategy == OrchestrationStrategy.CHAIN:
            return self.chain_schedule(selected, prompt)
        else:
            return self.parallel_schedule(selected, prompt)


# =============================================================================
# 主程序
# =============================================================================

def main():
    """主程序"""
    print("=" * 80)
    print("🎯 智能调度器 - 多策略控制主模型负担")
    print("Smart Orchestrator - Control Main Model Load")
    print("=" * 80)
    
    # 初始化
    orchestrator = SmartOrchestrator()
    
    # 准备任务
    prompt = "请用一句话介绍你自己，并说明你最擅长什么"
    
    # 执行调度（自动选择策略）
    results = orchestrator.orchestrate(prompt)
    
    # 汇总结果
    print("\n" + "=" * 80)
    print("📊 结果汇总")
    print("=" * 80)
    
    success = sum(1 for r in results if r["success"])
    tokens = sum(r.get("total_tokens", 0) for r in results if r["success"])
    
    print(f"\n成功: {success}/{len(results)}")
    print(f"Token: {tokens}")
    
    # 保存结果
    output = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "success_count": success,
        "total_tokens": tokens
    }
    
    with open("smart_orchestrator_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 已保存到: smart_orchestrator_results.json")
    print("\n✅ 完成!")


if __name__ == "__main__":
    main()
