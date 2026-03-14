#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响系统 - 智能调度器
整合自适应调节和动态编排
"""

import sys
import io

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, Any, List, Optional

# =============================================================================
# 配置
# =============================================================================

CONFIG = {
    "api_key": "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",
    "base_url": "https://integrate.api.nvidia.com/v1",
    "models": [
        "z-ai/glm4.7",
        "meta/llama-3.1-405b-instruct",
        "qwen/qwen3.5-397b-a17b",
    ]
}


# =============================================================================
# 任务复杂度分析器
# =============================================================================

class ComplexityAnalyzer:
    """任务复杂度分析器"""
    
    def __init__(self):
        self.complexity_keywords = {
            "简单": ["介绍", "是什么", "定义", "解释", "简单", "基础"],
            "中等": ["比较", "分析", "建议", "方案", "设计", "实现"],
            "复杂": ["创造", "开发", "系统", "架构", "优化", "研究", "创新"]
        }
    
    def analyze(self, prompt: str) -> str:
        """分析任务复杂度"""
        prompt_lower = prompt.lower()
        
        complex_score = sum(1 for kw in self.complexity_keywords["复杂"] if kw in prompt_lower)
        medium_score = sum(1 for kw in self.complexity_keywords["中等"] if kw in prompt_lower)
        simple_score = sum(1 for kw in self.complexity_keywords["简单"] if kw in prompt_lower)
        
        if complex_score >= 2:
            return "复杂"
        elif medium_score >= 2:
            return "中等"
        elif simple_score >= 1:
            return "简单"
        else:
            return "中等"  # 默认
    
    def get_model_count(self, complexity: str) -> int:
        """根据复杂度返回模型数量"""
        mapping = {
            "简单": 1,
            "中等": 2,
            "复杂": 3
        }
        return mapping.get(complexity, 1)


# =============================================================================
# 动态编排器
# =============================================================================

class DynamicOrchestrator:
    """动态编排器"""
    
    def __init__(self):
        self.config = CONFIG
        self.analyzer = ComplexityAnalyzer()
        self.model_stats = {}  # 记录每个模型的响应时间
    
    def call_model(self, model_id: str, prompt: str) -> Dict[str, Any]:
        """调用单个模型"""
        url = f"{self.config['base_url']}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        start = time.time()
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=60)
            elapsed = time.time() - start
            
            if resp.status_code == 200:
                result = resp.json()
                return {
                    "success": True,
                    "model": model_id,
                    "response": result["choices"][0]["message"]["content"],
                    "elapsed": elapsed
                }
            else:
                return {"success": False, "model": model_id, "error": f"Status {resp.status_code}"}
        except Exception as e:
            return {"success": False, "model": model_id, "error": str(e)}
    
    def select_models(self, complexity: str, count: int) -> List[str]:
        """根据复杂度选择模型"""
        # 简单任务用单个模型，复杂任务用多个
        if count == 1:
            return [self.config["models"][0]]  # 主模型
        else:
            return self.config["models"][:count]
    
    def orchestrate(self, prompt: str) -> Dict[str, Any]:
        """智能编排"""
        # 1. 分析复杂度
        complexity = self.analyzer.analyze(prompt)
        model_count = self.analyzer.get_model_count(complexity)
        
        print(f"\n📊 任务复杂度: {complexity}")
        print(f"📊 使用模型数: {model_count}")
        
        # 2. 选择模型
        selected_models = self.select_models(complexity, model_count)
        print(f"📊 选中模型: {selected_models}")
        
        # 3. 并行调用
        results = []
        with ThreadPoolExecutor(max_workers=len(selected_models)) as executor:
            futures = {executor.submit(self.call_model, m, prompt): m for m in selected_models}
            
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except:
                    pass
        
        # 4. 返回结果
        success_count = sum(1 for r in results if r.get("success"))
        
        return {
            "complexity": complexity,
            "model_count": model_count,
            "selected_models": selected_models,
            "results": results,
            "success_count": success_count,
            "total": len(results)
        }


# =============================================================================
# 主函数
# =============================================================================

def main():
    print("\n" + "="*60)
    print("交响智能调度器测试")
    print("="*60)
    
    orchestrator = DynamicOrchestrator()
    
    # 测试不同复杂度的任务
    test_cases = [
        ("简单任务", "请介绍一下你自己"),
        ("中等任务", "请比较Python和JavaScript的优缺点"),
        ("复杂任务", "请设计一个高并发的分布式系统架构方案"),
    ]
    
    for name, prompt in test_cases:
        print(f"\n\n{'='*60}")
        print(f"测试: {name}")
        print(f"问题: {prompt}")
        print("="*60)
        
        result = orchestrator.orchestrate(prompt)
        
        print(f"\n📊 结果:")
        print(f"  复杂度: {result['complexity']}")
        print(f"  成功: {result['success_count']}/{result['total']}")
        
        for r in result["results"]:
            if r.get("success"):
                print(f"\n  ✅ {r['model']} ({r['elapsed']:.2f}s)")
                print(f"     {r['response'][:100]}...")


if __name__ == "__main__":
    main()
