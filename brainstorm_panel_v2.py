#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BrainstormPanel v2.2.0 - 真实模型调用
直接使用config.py配置，不再依赖openclaw.cherry.json
"""

import time
import requests
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

# 直接从config.py加载配置
from config import MODEL_CHAIN


@dataclass
class TokenStats:
    """Token使用统计"""
    model_name: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_seconds: float = 0.0


@dataclass
class SymphonyResult:
    """讨论结果"""
    success: bool
    model_name: str
    response: str = ""
    error: str = ""
    tokens: int = 0
    latency: float = 0.0


class BrainstormPanel:
    """
    多模型协作工具 v2.2.0
    直接使用config.py配置
    """
    
    def __init__(self):
        self.name = "brainstorm_panel"
        self.version = "2.2.0"
        
        # 直接从config.py加载MODEL_CHAIN
        self.models = MODEL_CHAIN
        
        # 角色配置 - 使用MODEL_CHAIN中的模型
        self.roles_config = {
            "debate": [
                {"name": "正方专家", "model": "deepseek-ai/DeepSeek-R1-0528"},
                {"name": "反方专家", "model": "deepseek-ai/DeepSeek-R1-0528"},
                {"name": "调解员", "model": "deepseek-ai/DeepSeek-R1-0528"},
            ],
            "brainstorm": [
                {"name": "创意专家", "model": "deepseek-ai/DeepSeek-R1-0528"},
                {"name": "行业专家", "model": "deepseek-ai/DeepSeek-R1-0528"},
                {"name": "用户代表", "model": "deepseek-ai/DeepSeek-R1-0528"},
            ],
            "evaluate": [
                {"name": "技术评估员", "model": "deepseek-ai/DeepSeek-R1-0528"},
                {"name": "商业分析师", "model": "deepseek-ai/DeepSeek-R1-0528"},
                {"name": "风险顾问", "model": "deepseek-ai/DeepSeek-R1-0528"},
            ]
        }
    
    def _get_model_config(self, model_id: str) -> Dict:
        """从MODEL_CHAIN获取模型配置"""
        for m in self.models:
            if m.get("model_id") == model_id:
                return m
        return self.models[0] if self.models else {}
    
    def call_model(self, prompt: str, model_id: str = None, max_tokens: int = 800) -> SymphonyResult:
        """调用单个模型"""
        if model_id is None:
            model_id = self.models[0].get("model_id", "deepseek-ai/DeepSeek-R1-0528")
        
        model_cfg = self._get_model_config(model_id)
        
        if not model_cfg:
            return SymphonyResult(success=False, model_name=model_id, error="Model not found")
        
        # 使用config.py中的配置
        base_url = model_cfg.get("base_url", "")
        api_key = model_cfg.get("api_key", "")
        api_type = model_cfg.get("api_type", "openai-completions")
        
        try:
            start_time = time.time()
            
            if "anthropic" in api_type:
                url = f"{base_url}/v1/messages"
                headers = {"x-api-key": api_key, "Content-Type": "application/json", "anthropic-version": "2023-06-01"}
                data = {"model": model_id, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
            else:  # openai
                url = f"{base_url}/chat/completions"
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                data = {"model": model_id, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
            
            response = requests.post(url, headers=headers, json=data, timeout=90)
            latency = time.time() - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                if "anthropic" in api_type:
                    content = result_data["content"][0]["text"]
                else:
                    content = result_data["choices"][0]["message"]["content"]
                
                usage = result_data.get("usage", {})
                tokens = usage.get("total_tokens", usage.get("input_tokens", 0) + usage.get("output_tokens", 0))
                
                return SymphonyResult(
                    success=True,
                    model_name=model_id,
                    response=content,
                    tokens=tokens,
                    latency=latency
                )
            else:
                return SymphonyResult(
                    success=False,
                    model_name=model_id,
                    error=f"HTTP {response.status_code}: {response.text[:100]}",
                    latency=latency
                )
        except Exception as e:
            return SymphonyResult(success=False, model_name=model_id, error=str(e))
    
    def discuss(self, topic: str, mode: str = "brainstorm", num_experts: int = 3) -> Dict:
        """多模型讨论"""
        roles = self.roles_config.get(mode, self.roles_config["brainstorm"])[:num_experts]
        results = []
        
        print(f"\n=== {mode} 模式 ===")
        print(f"主题: {topic}")
        print(f"专家数量: {len(roles)}")
        print()
        
        for role in roles:
            print(f"[{role['name']}] 思考中...")
            result = self.call_model(f"你是{role['name']}。请针对以下主题发表你的观点：{topic}")
            
            results.append({
                "role": role["name"],
                "model": result.model_name,
                "success": result.success,
                "response": result.response if result.success else result.error,
                "tokens": result.tokens,
                "latency": result.latency
            })
            
            if result.success:
                print(f"  -> 成功 ({result.tokens} tokens, {result.latency:.1f}s)")
            else:
                print(f"  -> 失败: {result.error}")
        
        # 汇总
        total_tokens = sum(r["tokens"] for r in results)
        total_latency = sum(r["latency"] for r in results)
        
        return {
            "topic": topic,
            "mode": mode,
            "results": results,
            "total_tokens": total_tokens,
            "total_latency": total_latency
        }


def main():
    """测试"""
    print("=" * 60)
    print("BrainstormPanel v2.2.0 - 直接使用config.py")
    print("=" * 60)
    
    panel = BrainstormPanel()
    
    print(f"\n已加载模型数: {len(panel.models)}")
    for m in panel.models:
        print(f"  - {m.get('model_id')} ({m.get('provider')})")
    
    # 测试调用
    result = panel.call_model("hello", max_tokens=50)
    
    print(f"\n测试结果:")
    print(f"  成功: {result.success}")
    print(f"  模型: {result.model_name}")
    print(f"  延迟: {result.latency:.1f}s")
    if result.success:
        print(f"  回复: {result.response[:100]}...")


if __name__ == "__main__":
    main()
