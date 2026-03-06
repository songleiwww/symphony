#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型限流替补调度器 - FallbackModelCaller
当遇到限流等错误时，自动切换到备用模型
"""

import time
import json
import requests
from pathlib import Path
from typing import Optional, List, Dict, Any
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


class FallbackModelCaller:
    """
    模型限流替补调度器
    
    特性：
    - 自动检测限流错误（429, 500, 502, 503, 504）
    - 自动切换到备用模型
    - 指数退避重试
    - 最多重试次数限制
    """
    
    # 可重试的错误码
    RETRYABLE_CODES = {429, 500, 502, 503, 504}
    
    # 配额用完的错误码（不可重试，需要等待或充值）
    QUOTA_EXCEEDED_CODES = {"AccountQuotaExceeded", "insufficient_quota", "monthly_limit"}
    
    def __init__(self):
        """初始化 - 直接使用config.py"""
        # 直接从config.py加载MODEL_CHAIN
        from config import MODEL_CHAIN
        self.models = MODEL_CHAIN
        
        # 模型优先级列表（按顺序尝试）- 从MODEL_CHAIN构建
        self.model_priority = self._build_priority_from_config()
        
        # 当前使用的模型索引
        self.current_index = 0
        
        # 重试配置
        self.max_retries = 2
        self.base_delay = 1.5
        self.max_delay = 15.0
    
    def _build_priority_from_config(self):
        """从MODEL_CHAIN构建优先级列表"""
        priority_list = []
        for m in self.models:
            if m.get("enabled", True):
                priority_list.append({
                    "provider": m.get("provider", ""),
                    "model": m.get("model_id", m.get("model", "")),
                    "base_url": m.get("base_url", ""),
                    "api_key": m.get("api_key", ""),
                    "api_type": m.get("api_type", "openai-completions")
                })
        return priority_list
    
    def _load_config(self) -> Dict:
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _get_provider_config(self, provider: str) -> Optional[Dict]:
        """获取提供商配置"""
        providers = self.config.get("models", {}).get("providers", {})
        return providers.get(provider)
    
    def _is_retryable(self, status_code: int, error_msg: str = "") -> bool:
        """判断是否可重试"""
        # 检查是否是配额用完（不可重试）
        for quota_key in self.QUOTA_EXCEEDED_CODES:
            if quota_key.lower() in error_msg.lower():
                print(f"  检测到配额用完: {quota_key}，无法重试")
                return False
        
        if status_code in self.RETRYABLE_CODES:
            return True
        
        # 检查错误信息中的限流关键词
        retry_keywords = ["rate", "limit", "quota", "too many", "overloaded"]
        error_lower = error_msg.lower()
        return any(kw in error_lower for kw in retry_keywords)
    
    def _calculate_delay(self, attempt: int) -> float:
        """计算退避延迟（指数退避）"""
        delay = self.base_delay * (2 ** attempt)
        return min(delay, self.max_delay)
    
    def _call_api(
        self,
        provider: str,
        model: str,
        prompt: str,
        max_tokens: int = 800,
        temperature: float = 0.7
    ) -> ModelCallResult:
        """调用单个模型API"""
        provider_config = self._get_provider_config(provider)
        
        if not provider_config:
            return ModelCallResult(
                success=False,
                model_name=model,
                error=f"找不到提供商配置: {provider}"
            )
        
        api_key = provider_config.get("apiKey", "")
        base_url = provider_config.get("baseUrl", "")
        api_type = provider_config.get("api", "openai-completions")
        
        if api_type == "openai-completions":
            url = f"{base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
        else:
            # Anthropic messages API
            url = f"{base_url}/v1/messages"
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens
            }
        
        try:
            start_time = time.time()
            response = requests.post(url, headers=headers, json=data, timeout=90)
            latency = time.time() - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                
                if api_type == "openai-completions":
                    content = result_data["choices"][0]["message"]["content"]
                    usage = result_data.get("usage", {})
                else:
                    content = result_data["content"][0]["text"]
                    usage = result_data.get("usage", {})
                
                return ModelCallResult(
                    success=True,
                    model_name=model,
                    response=content,
                    prompt_tokens=usage.get("input_tokens", 0),
                    completion_tokens=usage.get("output_tokens", 0),
                    total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
                    latency=latency
                )
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                return ModelCallResult(
                    success=False,
                    model_name=model,
                    error=error_msg,
                    latency=latency
                )
                
        except Exception as e:
            return ModelCallResult(
                success=False,
                model_name=model,
                error=str(e)
            )
    
    def call(
        self,
        prompt: str,
        max_tokens: int = 800,
        temperature: float = 0.7,
        preferred_model: str = None
    ) -> ModelCallResult:
        """
        调用模型（带自动替补）
        
        Args:
            prompt: 提示词
            max_tokens: 最大生成token数
            temperature: 温度参数
            preferred_model: 首选模型（格式：provider/model）
        
        Returns:
            ModelCallResult: 调用结果
        """
        # 确定模型优先级
        if preferred_model:
            # 将首选模型移到最前面
            provider, model = preferred_model.split("/", 1)
            sorted_models = [
                {"provider": provider, "model": model}
            ] + [m for m in self.model_priority 
                 if m["provider"] != provider or m["model"] != model]
        else:
            sorted_models = self.model_priority
        
        last_error = ""
        
        # 尝试每个模型
        for attempt in range(self.max_retries):
            for i, model_cfg in enumerate(sorted_models):
                result = self._call_api(
                    model_cfg["provider"],
                    model_cfg["model"],
                    prompt,
                    max_tokens,
                    temperature
                )
                
                if result.success:
                    result.used_fallback = i > 0
                    return result
                
                last_error = result.error
                
                # 检查是否可重试
                status_code = 0
                if "HTTP" in result.error:
                    try:
                        status_code = int(result.error.split()[0].replace("HTTP", ""))
                    except:
                        pass
                
                if not self._is_retryable(status_code, result.error):
                    # 不可重试的错误，直接返回
                    return result
                
                print(f"  模型 {model_cfg['provider']}/{model_cfg['model']} 限流，尝试下一个...")
            
            # 所有模型都失败，等待后重试
            if attempt < self.max_retries - 1:
                delay = self._calculate_delay(attempt)
                print(f"  等待 {delay:.1f}秒后重试...")
                time.sleep(delay)
        
        # 所有重试都失败
        return ModelCallResult(
            success=False,
            model_name=sorted_models[-1]["model"],
            error=f"所有模型都失败: {last_error}"
        )


# ============================================================
# 使用示例
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("模型限流替补调度器测试")
    print("=" * 60)
    
    caller = FallbackModelCaller()
    
    # 测试调用
    prompt = "用一句话介绍你自己"
    
    print(f"\n调用模型...")
    print(f"提示词: {prompt}")
    print()
    
    result = caller.call(prompt, max_tokens=100)
    
    print("\n结果:")
    print(f"  成功: {result.success}")
    print(f"  模型: {result.model_name}")
    print(f"  使用替补: {result.used_fallback}")
    print(f"  延迟: {result.latency:.2f}秒")
    print(f"  Tokens: {result.total_tokens}")
    
    if result.success:
        print(f"\n回复: {result.response[:200]}")
    else:
        print(f"\n错误: {result.error}")
