#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响 Symphony 多人调度系统
Multi-Person Scheduling System
"""

import json
import time
import requests
import concurrent.futures
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# 导入配置
from config import API_CONFIG, SYSTEM_CONFIG


# =============================================================================
# 多人调度器类
# =============================================================================

class SymphonyScheduler:
    """
    交响多人调度器
    支持并行调用多个模型
    """
    
    def __init__(self):
        self.config = API_CONFIG
        self.models = self.config.get("models", [])
        self.primary_model = self.config.get("primary_model")
        self.base_url = self.config.get("base_url")
        self.api_key = self.config.get("api_key")
        
    def call_model(self, model_id: str, prompt: str) -> Dict[str, Any]:
        """
        调用单个模型
        
        Args:
            model_id: 模型ID
            prompt: 提示词
            
        Returns:
            调用结果
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": SYSTEM_CONFIG.get("max_tokens", 500),
            "temperature": SYSTEM_CONFIG.get("temperature", 0.7)
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=SYSTEM_CONFIG.get("timeout", 120))
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return {
                    "success": True,
                    "model": model_id,
                    "response": content,
                    "elapsed": elapsed,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "model": model_id,
                    "error": f"Status {response.status_code}: {response.text[:100]}",
                    "elapsed": elapsed,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "success": False,
                "model": model_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def parallel_call(self, prompt: str, model_ids: List[str] = None) -> List[Dict[str, Any]]:
        """
        并行调用多个模型
        
        Args:
            prompt: 提示词
            model_ids: 模型ID列表（可选，默认使用所有可用模型）
            
        Returns:
            所有模型的调用结果
        """
        if model_ids is None:
            model_ids = self.models[:5]  # 默认最多5个模型
        
        results = []
        
        # 并行执行
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(model_ids)) as executor:
            futures = {executor.submit(self.call_model, model_id, prompt): model_id for model_id in model_ids}
            
            for future in concurrent.futures.as_completed(futures):
                model_id = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        "success": False,
                        "model": model_id,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
        
        return results
    
    def call_primary(self, prompt: str) -> Dict[str, Any]:
        """
        调用主模型
        
        Args:
            prompt: 提示词
            
        Returns:
            主模型调用结果
        """
        return self.call_model(self.primary_model, prompt)
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return self.models
    
    def print_results(self, results: List[Dict[str, Any]]):
        """打印调用结果"""
        print("\n" + "="*60)
        print("多人调度结果")
        print("="*60)
        
        success_count = sum(1 for r in results if r.get("success", False))
        print(f"成功: {success_count}/{len(results)}")
        print("-"*60)
        
        for result in results:
            status = "OK" if result.get("success") else "FAIL"
            model = result.get("model", "unknown")
            elapsed = result.get("elapsed", 0)
            
            print(f"[{status}] {model} ({elapsed:.2f}s)")
            
            if result.get("success"):
                response = result.get("response", "")[:100]
                print(f"    → {response}...")
            else:
                error = result.get("error", "unknown error")
                print(f"    → Error: {error}")
        
        print("="*60)


# =============================================================================
# 主函数 - 测试多人调度
# =============================================================================

def main():
    """测试多人调度"""
    print("\n" + "="*60)
    print("交响 Symphony 多人调度系统")
    print("="*60)
    
    # 创建调度器
    scheduler = SymphonyScheduler()
    
    print(f"主模型: {scheduler.primary_model}")
    print(f"可用模型: {len(scheduler.models)}个")
    print("-"*60)
    
    # 测试调用
    prompt = "你好，请介绍一下你自己"
    
    print(f"\n测试提示: {prompt}")
    print("\n调用主模型...")
    
    result = scheduler.call_primary(prompt)
    
    if result.get("success"):
        print(f"\n主模型响应 ({result.get('model')}):")
        print(result.get("response"))
    else:
        print(f"\n调用失败: {result.get('error')}")
    
    # 测试并行调用（可选）
    print("\n" + "="*60)
    
    # 并行调用测试
    test_models = scheduler.models[:3]
    print(f"\n并行调用 {len(test_models)} 个模型...")
    
    results = scheduler.parallel_call(prompt, test_models)
    scheduler.print_results(results)


if __name__ == "__main__":
    main()
