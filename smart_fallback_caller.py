#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型限流替补调度器 - 智能版
直接从config.py加载配置，不再依赖openclaw.cherry.json
"""

import time
import json
import requests
from pathlib import Path
from typing import Optional, List, Dict, Set
from dataclasses import dataclass
from datetime import datetime

# 直接从config.py加载MODEL_CHAIN
from config import MODEL_CHAIN


@dataclass
class ModelCallResult:
    """模型调用结果"""
    success: bool
    model_name: str
    response: str = ""
    error: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency: float = 0.0
    used_fallback: bool = False


class SmartFallbackCaller:
    """
    智能模型替补调度器 - 直接使用config.py
    
    特性：
    - 直接从config.py的MODEL_CHAIN加载配置
    - 不再依赖openclaw.cherry.json
    - 自动检测限流错误
    - 排除同API Provider的模型
    """
    
    # 可重试的错误码
    RETRYABLE_CODES = {429, 500, 502, 503, 504}
    
    # 配额用完的错误码（不可重试）
    QUOTA_EXCEEDED_CODES = {"AccountQuotaExceeded", "insufficient_quota", "monthly_limit"}
    
    def __init__(self):
        """初始化 - 直接使用config.py"""
        self.models = MODEL_CHAIN
        
        # 构建模型优先级
        self._build_model_priority()
        
        # 已失败的Provider（配额用完）
        self.failed_providers: Set[str] = set()
        
        # 重试配置
        self.max_retries = 2
        self.base_delay = 1.5
        self.max_delay = 15.0
    
    def _build_model_priority(self):
        """从MODEL_CHAIN构建模型优先级"""
        
        # 按API类型分组：优先使用不同API的模型
        by_api = {}
        
        for m in self.models:
            if not m.get("enabled", True):
                continue
            
            provider = m.get("provider", "")
            model_id = m.get("model_id", m.get("model", ""))
            api_type = m.get("api_type", "openai-completions")
            
            # 转换为简化的api_type
            if "anthropic" in api_type:
                simplified_api = "anthropic"
            elif "openai" in api_type:
                simplified_api = "openai"
            else:
                simplified_api = "custom"
            
            model_cfg = {
                "provider": provider,
                "model": model_id,
                "api_type": simplified_api,
                "base_url": m.get("base_url", ""),
                "api_key": m.get("api_key", "")
            }
            
            if simplified_api not in by_api:
                by_api[simplified_api] = []
            by_api[simplified_api].append(model_cfg)
        
        # 优先级：anthropic > openai > custom
        # (因为Doubao配额用完，优先用其他API)
        priority_order = ["anthropic", "openai", "custom"]
        
        self.model_priority = []
        for api in priority_order:
            if api in by_api:
                self.model_priority.extend(by_api[api])
    
    def _get_provider_config(self, provider: str) -> Optional[Dict]:
        """从MODEL_CHAIN中获取提供商配置"""
        for m in self.models:
            if m.get("provider") == provider:
                return {
                    "base_url": m.get("base_url", ""),
                    "api_key": m.get("api_key", ""),
                    "api_type": m.get("api_type", "openai-completions")
                }
        return None
    
    def _is_quota_exceeded(self, error_msg: str) -> bool:
        """检查是否是配额用完"""
        for quota_key in self.QUOTA_EXCEEDED_CODES:
            if quota_key.lower() in error_msg.lower():
                return True
        return False
    
    def _is_retryable(self, status_code: int, error_msg: str = "") -> bool:
        """判断是否可重试"""
        if self._is_quota_exceeded(error_msg):
            return False
        
        if status_code in self.RETRYABLE_CODES:
            return True
        
        retry_keywords = ["rate", "limit", "quota", "too many", "overloaded"]
        error_lower = error_msg.lower()
        return any(kw in error_lower for kw in retry_keywords)
    
    def _calculate_delay(self, attempt: int) -> float:
        """计算退避延迟"""
        delay = self.base_delay * (2 ** attempt)
        return min(delay, self.max_delay)
    
    def _call_api(self, model_cfg: Dict, prompt: str, max_tokens: int = 800) -> ModelCallResult:
        """调用单个模型API"""
        provider = model_cfg["provider"]
        model = model_cfg["model"]
        
        provider_config = self._get_provider_config(provider)
        
        if not provider_config:
            return ModelCallResult(success=False, model_name=model, error=f"找不到提供商: {provider}")
        
        # 使用MODEL_CHAIN中的配置
        api_key = model_cfg.get("api_key", provider_config.get("api_key", ""))
        base_url = model_cfg.get("base_url", provider_config.get("base_url", ""))
        api_type = model_cfg.get("api_type", provider_config.get("api_type", "openai-completions"))
        
        if "anthropic" in api_type:
            url = f"{base_url}/v1/messages"
            headers = {"x-api-key": api_key, "Content-Type": "application/json", "anthropic-version": "2023-06-01"}
            data = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
        else:  # openai-completions
            url = f"{base_url}/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
        
        try:
            start_time = time.time()
            response = requests.post(url, headers=headers, json=data, timeout=90)
            latency = time.time() - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                if "anthropic" in api_type:
                    content = result_data["content"][0]["text"]
                else:
                    content = result_data["choices"][0]["message"]["content"]
                
                usage = result_data.get("usage", {})
                return ModelCallResult(
                    success=True, model_name=model, response=content,
                    prompt_tokens=usage.get("input_tokens", 0),
                    completion_tokens=usage.get("output_tokens", 0),
                    total_tokens=usage.get("total_tokens", usage.get("input_tokens", 0) + usage.get("output_tokens", 0)),
                    latency=latency
                )
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    err_data = response.json()
                    error_msg += f": {err_data.get('error', {}).get('message', response.text[:100])}"
                except:
                    error_msg += f": {response.text[:100]}"
                
                if self._is_quota_exceeded(error_msg):
                    self.failed_providers.add(provider)
                    print(f"  [!] {provider} 配额用完，加入黑名单")
                
                return ModelCallResult(success=False, model_name=model, error=error_msg, latency=latency)
        except Exception as e:
            return ModelCallResult(success=False, model_name=model, error=str(e))
    
    def call(self, prompt: str, max_tokens: int = 800) -> ModelCallResult:
        """
        调用模型（智能替补）
        直接从config.py的MODEL_CHAIN获取配置
        """
        exclude_set = set(self.failed_providers)
        
        print(f"\n[智能调度] 排除Provider: {exclude_set if exclude_set else '无'}")
        
        # 过滤模型（排除已失败的Provider）
        available_models = [m for m in self.model_priority if m["provider"] not in exclude_set]
        
        if not available_models:
            return ModelCallResult(success=False, model_name="", error=f"所有Provider都已失败: {self.failed_providers}")
        
        print(f"[智能调度] 可用模型数: {len(available_models)}")
        
        last_error = ""
        
        for attempt in range(self.max_retries):
            for model_cfg in available_models:
                result = self._call_api(model_cfg, prompt, max_tokens)
                
                if result.success:
                    return result
                
                last_error = result.error
                print(f"  -> {model_cfg['provider']}/{model_cfg['model']} 失败: {result.error[:50]}")
                
                if self._is_quota_exceeded(result.error):
                    continue
            
            if attempt < self.max_retries - 1:
                delay = self._calculate_delay(attempt)
                print(f"  等待 {delay:.1f}秒后重试...")
                time.sleep(delay)
        
        return ModelCallResult(success=False, model_name="", error=f"所有模型失败: {last_error}")


if __name__ == "__main__":
    print("=" * 60)
    print("智能模型替补调度器 - 直接使用config.py")
    print("=" * 60)
    
    caller = SmartFallbackCaller()
    
    prompt = "hello"
    print(f"\n提示词: {prompt}")
    
    result = caller.call(prompt, max_tokens=50)
    
    print("\n结果:")
    print(f"  成功: {result.success}")
    print(f"  模型: {result.model_name}")
    print(f"  延迟: {result.latency:.2f}秒")
    if result.success:
        print(f"  回复: {result.response[:100]}")
    else:
        print(f"  错误: {result.error}")
