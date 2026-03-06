#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型限流替补调度器 - 智能版
自动排除同API的模型，避免浪费调用
"""

import time
import json
import requests
from pathlib import Path
from typing import Optional, List, Dict, Set
from dataclasses import dataclass
from datetime import datetime


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
    智能模型替补调度器
    
    特性：
    - 自动检测限流错误
    - 排除同API Provider的模型（避免浪费调用）
    - 指数退避重试
    - 详细的失败原因记录
    """
    
    # 可重试的错误码
    RETRYABLE_CODES = {429, 500, 502, 503, 504}
    
    # 配额用完的错误码（不可重试）
    QUOTA_EXCEEDED_CODES = {"AccountQuotaExceeded", "insufficient_quota", "monthly_limit"}
    
    def __init__(self, config_path: str = None):
        """初始化"""
        if config_path is None:
            config_path = r"C:\Users\Administrator\.openclaw\openclaw.cherry.json"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # 按API分组，优先级：不同API > 不同Provider
        # 格式: {api_type: [{"provider": ..., "model": ...}]}
        self._build_model_priority()
        
        # 已失败的Provider（配额用完）
        self.failed_providers: Set[str] = set()
        
        # 重试配置
        self.max_retries = 3
        self.base_delay = 2.0
        self.max_delay = 30.0
    
    def _load_config(self) -> Dict:
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _build_model_priority(self):
        """按API类型分组构建模型优先级"""
        
        # 模型列表（按提供商分组）
        all_models = [
            # Cherry Doubao (火山引擎)
            {"provider": "cherry-doubao", "model": "deepseek-v3.2", "api_type": "openai"},
            {"provider": "cherry-doubao", "model": "kimi-k2.5", "api_type": "openai"},
            {"provider": "cherry-doubao", "model": "glm-4.7", "api_type": "openai"},
            {"provider": "cherry-doubao", "model": "doubao-seed-2.0-code", "api_type": "openai"},
            
            # Cherry Nvidia (NVIDIA NIM)
            {"provider": "cherry-nvidia", "model": "deepseek-ai/deepseek-v3.2", "api_type": "openai"},
            {"provider": "cherry-nvidia", "model": "moonshotai/kimi-k2.5", "api_type": "openai"},
            
            # Cherry Modelscope
            {"provider": "cherry-modelscope", "model": "deepseek-ai/DeepSeek-R1-0528", "api_type": "custom"},
            
            # Cherry Minimax
            {"provider": "cherry-minimax", "model": "MiniMax-M2.5", "api_type": "anthropic"},
        ]
        
        # 按API类型分组：优先使用不同API的模型
        by_api = {}
        for m in all_models:
            api = m["api_type"]
            if api not in by_api:
                by_api[api] = []
            by_api[api].append(m)
        
        # 优先级：custom > anthropic > openai
        # （因为openai和doubao目前都配额用完）
        priority_order = ["anthropic", "custom", "openai"]
        
        self.model_priority = []
        for api in priority_order:
            if api in by_api:
                self.model_priority.extend(by_api[api])
    
    def _get_provider_config(self, provider: str) -> Optional[Dict]:
        """获取提供商配置"""
        providers = self.config.get("models", {}).get("providers", {})
        return providers.get(provider)
    
    def _is_quota_exceeded(self, error_msg: str) -> bool:
        """检查是否是配额用完"""
        for quota_key in self.QUOTA_EXCEEDED_CODES:
            if quota_key.lower() in error_msg.lower():
                return True
        return False
    
    def _is_retryable(self, status_code: int, error_msg: str = "") -> bool:
        """判断是否可重试"""
        # 配额用完不可重试
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
    
    def _call_api(self, provider: str, model: str, prompt: str, max_tokens: int = 800) -> ModelCallResult:
        """调用单个模型API"""
        provider_config = self._get_provider_config(provider)
        
        if not provider_config:
            return ModelCallResult(success=False, model_name=model, error=f"找不到提供商: {provider}")
        
        api_key = provider_config.get("apiKey", "")
        base_url = provider_config.get("baseUrl", "")
        api_type = provider_config.get("api", "openai-completions")
        
        if api_type == "openai-completions":
            url = f"{base_url}/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
        else:  # anthropic-messages
            url = f"{base_url}/v1/messages"
            headers = {"x-api-key": api_key, "Content-Type": "application/json", "anthropic-version": "2023-06-01"}
            data = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
        
        try:
            start_time = time.time()
            response = requests.post(url, headers=headers, json=data, timeout=90)
            latency = time.time() - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                if api_type == "openai-completions":
                    content = result_data["choices"][0]["message"]["content"]
                else:
                    content = result_data["content"][0]["text"]
                
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
                
                # 检查配额用完
                if self._is_quota_exceeded(error_msg):
                    self.failed_providers.add(provider)
                    print(f"  [!] {provider} 配额用完，加入黑名单")
                
                return ModelCallResult(success=False, model_name=model, error=error_msg, latency=latency)
        except Exception as e:
            return ModelCallResult(success=False, model_name=model, error=str(e))
    
    def call(self, prompt: str, max_tokens: int = 800, exclude_providers: List[str] = None) -> ModelCallResult:
        """
        调用模型（智能替补）
        
        Args:
            prompt: 提示词
            max_tokens: 最大生成token
            exclude_providers: 额外要排除的provider
        """
        # 合并排除列表
        exclude_set = set(self.failed_providers)
        if exclude_providers:
            exclude_set.update(exclude_providers)
        
        print(f"\n[智能调度] 排除Provider: {exclude_set if exclude_set else '无'}")
        
        # 过滤模型（排除同API/同Provider）
        available_models = [m for m in self.model_priority if m["provider"] not in exclude_set]
        
        if not available_models:
            return ModelCallResult(success=False, model_name="", error=f"所有Provider都已失败: {self.failed_providers}")
        
        print(f"[智能调度] 可用模型数: {len(available_models)}")
        
        last_error = ""
        
        for attempt in range(self.max_retries):
            for model_cfg in available_models:
                result = self._call_api(
                    model_cfg["provider"],
                    model_cfg["model"],
                    prompt,
                    max_tokens
                )
                
                if result.success:
                    return result
                
                last_error = result.error
                print(f"  -> {model_cfg['provider']}/{model_cfg['model']} 失败: {result.error[:50]}")
                
                # 配额用完，加入黑名单
                if self._is_quota_exceeded(result.error):
                    continue
                
                # 不可重试的错误
                if not self._is_retryable(0, result.error):
                    continue
            
            # 重试
            if attempt < self.max_retries - 1:
                delay = self._calculate_delay(attempt)
                print(f"  等待 {delay:.1f}秒后重试...")
                time.sleep(delay)
        
        return ModelCallResult(success=False, model_name="", error=f"所有模型失败: {last_error}")


if __name__ == "__main__":
    print("=" * 60)
    print("智能模型替补调度器测试")
    print("=" * 60)
    
    caller = SmartFallbackCaller()
    
    prompt = "用一句话介绍你自己"
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
