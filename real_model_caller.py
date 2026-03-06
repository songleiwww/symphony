#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实模型调用器 - Real Model Caller
从OpenClaw配置加载真实模型和API Key，进行真实的模型调用
"""

import sys
import io

# 修复Windows编码问题（只在stdout未被包装时）
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        if hasattr(sys.stderr, 'buffer') and not isinstance(sys.stderr, io.TextIOWrapper):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except Exception:
        pass  # 忽略IO错误

import json
import time
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from openclaw_config_loader import OpenClawConfigLoader


@dataclass
class ModelCallResult:
    """模型调用结果"""
    success: bool
    model_name: str
    model_alias: str
    provider: str
    prompt: str
    response: str = ""
    error: str = ""
    latency: float = 0.0
    timestamp: datetime = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class RealModelCaller:
    """真实模型调用器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化真实模型调用器
        
        Args:
            config_path: OpenClaw配置文件路径
        """
        self.loader = OpenClawConfigLoader(config_path)
        self.models = self.loader.get_models()
        self.call_history: List[ModelCallResult] = []
        
        print("=" * 80)
        print("🤖 真实模型调用器 - Real Model Caller")
        print("=" * 80)
        print(f"\n✅ 已加载 {len(self.models)} 个模型")
        print(f"✅ 提供商数量: {len(self.loader.get_providers())}")
        
        # 按提供商分组显示
        provider_models: Dict[str, List] = {}
        for model in self.models:
            p = model["provider"]
            if p not in provider_models:
                provider_models[p] = []
            provider_models[p].append(model)
        
        print("\n📋 可用模型:")
        for provider_name, provider_models_list in provider_models.items():
            print(f"\n  {provider_name}:")
            for i, model in enumerate(provider_models_list, 1):
                print(f"    {model['priority']}. {model['alias']}")
        
        print("\n" + "=" * 80)
    
    def call_model(
        self,
        prompt: str,
        priority: int = 1,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> ModelCallResult:
        """
        调用指定优先级的模型
        
        Args:
            prompt: 提示词
            priority: 模型优先级（1开始）
            max_tokens: 最大生成token数
            temperature: 温度参数
        
        Returns:
            模型调用结果
        """
        # 获取模型配置
        model_config = self.loader.get_model_by_priority(priority)
        if not model_config:
            return ModelCallResult(
                success=False,
                model_name=f"priority_{priority}",
                model_alias=f"Priority {priority}",
                provider="unknown",
                prompt=prompt,
                error=f"找不到优先级为 {priority} 的模型"
            )
        
        print(f"\n🔄 正在调用模型: {model_config['alias']}")
        print(f"   提供商: {model_config['provider']}")
        print(f"   优先级: {priority}")
        
        start_time = time.time()
        
        try:
            # 根据API类型调用
            if model_config["api_type"] == "openai-completions":
                result = self._call_openai_completions(
                    model_config, prompt, max_tokens, temperature
                )
            elif model_config["api_type"] == "anthropic-messages":
                result = self._call_anthropic_messages(
                    model_config, prompt, max_tokens, temperature
                )
            else:
                result = ModelCallResult(
                    success=False,
                    model_name=model_config["name"],
                    model_alias=model_config["alias"],
                    provider=model_config["provider"],
                    prompt=prompt,
                    error=f"不支持的API类型: {model_config['api_type']}"
                )
        except Exception as e:
            result = ModelCallResult(
                success=False,
                model_name=model_config["name"],
                model_alias=model_config["alias"],
                provider=model_config["provider"],
                prompt=prompt,
                error=f"调用异常: {str(e)}"
            )
        
        result.latency = time.time() - start_time
        result.timestamp = datetime.now()
        
        # 记录历史
        self.call_history.append(result)
        
        # 显示结果
        self._display_result(result)
        
        return result
    
    def _call_openai_completions(
        self,
        model_config: Dict,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> ModelCallResult:
        """
        调用OpenAI兼容的API
        
        Args:
            model_config: 模型配置
            prompt: 提示词
            max_tokens: 最大token数
            temperature: 温度参数
        
        Returns:
            调用结果
        """
        url = f"{model_config['base_url']}/chat/completions"
        headers = {
            "Authorization": f"Bearer {model_config['api_key']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model_config["model_id"],
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=model_config["timeout"]
        )
        
        if response.status_code == 200:
            result_data = response.json()
            return ModelCallResult(
                success=True,
                model_name=model_config["name"],
                model_alias=model_config["alias"],
                provider=model_config["provider"],
                prompt=prompt,
                response=result_data["choices"][0]["message"]["content"],
                prompt_tokens=result_data.get("usage", {}).get("prompt_tokens", 0),
                completion_tokens=result_data.get("usage", {}).get("completion_tokens", 0),
                total_tokens=result_data.get("usage", {}).get("total_tokens", 0)
            )
        else:
            return ModelCallResult(
                success=False,
                model_name=model_config["name"],
                model_alias=model_config["alias"],
                provider=model_config["provider"],
                prompt=prompt,
                error=f"HTTP {response.status_code}: {response.text}"
            )
    
    def _call_anthropic_messages(
        self,
        model_config: Dict,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> ModelCallResult:
        """
        调用Anthropic Messages API
        
        Args:
            model_config: 模型配置
            prompt: 提示词
            max_tokens: 最大token数
            temperature: 温度参数
        
        Returns:
            调用结果
        """
        url = f"{model_config['base_url']}/v1/messages"
        headers = {
            "x-api-key": model_config["api_key"],
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": model_config["model_id"],
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=model_config["timeout"]
        )
        
        if response.status_code == 200:
            result_data = response.json()
            return ModelCallResult(
                success=True,
                model_name=model_config["name"],
                model_alias=model_config["alias"],
                provider=model_config["provider"],
                prompt=prompt,
                response=result_data["content"][0]["text"],
                prompt_tokens=result_data.get("usage", {}).get("input_tokens", 0),
                completion_tokens=result_data.get("usage", {}).get("output_tokens", 0),
                total_tokens=result_data.get("usage", {}).get("input_tokens", 0) + 
                             result_data.get("usage", {}).get("output_tokens", 0)
            )
        else:
            return ModelCallResult(
                success=False,
                model_name=model_config["name"],
                model_alias=model_config["alias"],
                provider=model_config["provider"],
                prompt=prompt,
                error=f"HTTP {response.status_code}: {response.text}"
            )
    
    def _display_result(self, result: ModelCallResult):
        """
        显示调用结果
        
        Args:
            result: 调用结果
        """
        print("\n" + "=" * 80)
        if result.success:
            print(f"✅ 调用成功 - {result.model_alias}")
            print("=" * 80)
            print(f"\n⏱️  延迟: {result.latency:.2f}秒")
            if result.total_tokens > 0:
                print(f"📊 Token统计:")
                print(f"   提示词: {result.prompt_tokens}")
                print(f"   生成: {result.completion_tokens}")
                print(f"   总计: {result.total_tokens}")
            print(f"\n💬 响应:")
            print("-" * 80)
            print(result.response[:500])
            if len(result.response) > 500:
                print("... (截断显示，完整响应已保存)")
        else:
            print(f"❌ 调用失败 - {result.model_alias}")
            print("=" * 80)
            print(f"\n⏱️  延迟: {result.latency:.2f}秒")
            print(f"\n❌ 错误: {result.error}")
        print("=" * 80)
    
    def multi_model_call(
        self,
        prompt: str,
        priorities: Optional[List[int]] = None,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> List[ModelCallResult]:
        """
        多模型并行调用
        
        Args:
            prompt: 提示词
            priorities: 优先级列表，默认前3个
            max_tokens: 最大token数
            temperature: 温度参数
        
        Returns:
            调用结果列表
        """
        if priorities is None:
            priorities = [1, 2, 3]
        
        print(f"\n" + "=" * 80)
        print(f"🎭 多模型协作调用 - {len(priorities)} 个模型")
        print("=" * 80)
        
        results = []
        for priority in priorities:
            result = self.call_model(prompt, priority, max_tokens, temperature)
            results.append(result)
        
        # 汇总结果
        print(f"\n" + "=" * 80)
        print("📊 多模型调用汇总")
        print("=" * 80)
        
        success_count = sum(1 for r in results if r.success)
        total_tokens = sum(r.total_tokens for r in results)
        total_latency = sum(r.latency for r in results)
        
        print(f"\n✅ 成功: {success_count}/{len(results)}")
        print(f"📊 总Token: {total_tokens}")
        print(f"⏱️  总延迟: {total_latency:.2f}秒")
        
        if success_count > 0:
            print(f"\n💬 成功的模型:")
            for i, result in enumerate(results, 1):
                if result.success:
                    print(f"  {i}. {result.model_alias} - {result.total_tokens} tokens")
        
        print("=" * 80)
        
        return results
    
    def print_history(self):
        """打印调用历史"""
        print(f"\n" + "=" * 80)
        print("📜 调用历史")
        print("=" * 80)
        
        if not self.call_history:
            print("\n暂无调用历史")
        else:
            print(f"\n共 {len(self.call_history)} 次调用:")
            for i, result in enumerate(self.call_history, 1):
                status = "✅" if result.success else "❌"
                print(f"\n{i}. {status} {result.model_alias} ({result.provider})")
                print(f"   时间: {result.timestamp.strftime('%H:%M:%S')}")
                print(f"   延迟: {result.latency:.2f}秒")
                if result.success:
                    print(f"   Token: {result.total_tokens}")
        
        print("=" * 80)


if __name__ == "__main__":
    # 测试
    caller = RealModelCaller()
    
    # 简单测试（不实际调用，避免消耗）
    print("\n⚠️  注意：实际调用会消耗API额度")
    print("   使用 call_model() 或 multi_model_call() 进行真实调用")
    print("\n示例:")
    print("  caller.call_model('你好', priority=1)")
    print("  caller.multi_model_call('你好', priorities=[1, 2, 3])")
