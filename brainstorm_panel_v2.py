#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BrainstormPanel v2.4.0 - 真实模型调用 + 视觉/图像/视频支持
直接使用config.py配置
"""

import time
import base64
import requests
import threading
from typing import Dict, List, Any, Union, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

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


@dataclass
class GenerationResult:
    """生成结果（图像/视频）"""
    success: bool
    model_name: str
    url: str = ""
    error: str = ""
    latency: float = 0.0
    is_async: bool = False
    task_id: str = ""


class BrainstormPanel:
    """
    多模型协作工具 v2.4.0
    直接使用config.py配置
    支持：文本、视觉、图像生成、视频生成
    """
    
    def __init__(self):
        self.name = "brainstorm_panel"
        self.version = "2.4.0"
        
        # 直接从config.py加载MODEL_CHAIN
        self.models = MODEL_CHAIN
        
        # 角色配置
        self.roles_config = {
            "debate": [
                {"name": "正方专家", "model": "glm-4-flash"},
                {"name": "反方专家", "model": "glm-4-flash"},
                {"name": "调解员", "model": "glm-4-flash"},
            ],
            "brainstorm": [
                {"name": "创意专家", "model": "glm-4-flash"},
                {"name": "行业专家", "model": "glm-4-flash"},
                {"name": "用户代表", "model": "glm-4-flash"},
            ],
            "evaluate": [
                {"name": "技术评估员", "model": "glm-4-flash"},
                {"name": "商业分析师", "model": "glm-4-flash"},
                {"name": "风险顾问", "model": "glm-4-flash"},
            ]
        }
        
        # 异步任务结果存储
        self._async_tasks: Dict[str, GenerationResult] = {}
    
    def _get_model_config(self, model_id: str) -> Dict:
        """从MODEL_CHAIN获取模型配置"""
        for m in self.models:
            if m.get("model_id") == model_id:
                return m
        return self.models[0] if self.models else {}
    
    def _is_vision_model(self, model_cfg: Dict) -> bool:
        """判断是否是视觉模型"""
        return model_cfg.get("is_vision", False)
    
    def _is_image_gen_model(self, model_cfg: Dict) -> bool:
        """判断是否是图像生成模型"""
        return model_cfg.get("is_image_gen", False)
    
    def _is_video_gen_model(self, model_cfg: Dict) -> bool:
        """判断是否是视频生成模型"""
        return model_cfg.get("is_video_gen", False)
    
    def call_model(
        self, 
        prompt: str, 
        model_id: str = None, 
        max_tokens: int = 800,
        image: str = None  # 图片路径或base64
    ) -> SymphonyResult:
        """调用单个模型"""
        if model_id is None:
            model_id = self.models[0].get("model_id", "glm-4-flash")
        
        model_cfg = self._get_model_config(model_id)
        
        if not model_cfg:
            return SymphonyResult(success=False, model_name=model_id, error="Model not found")
        
        base_url = model_cfg.get("base_url", "")
        api_key = model_cfg.get("api_key", "")
        api_type = model_cfg.get("api_type", "openai-completions")
        
        try:
            start_time = time.time()
            
            # 判断是否是视觉模型
            is_vision = self._is_vision_model(model_cfg) or image is not None
            
            if is_vision:
                # 视觉模型调用
                url = f"{base_url}/chat/completions"
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                
                content_list = [{"type": "text", "text": prompt}]
                
                if image:
                    if Path(image).exists():
                        with open(image, 'rb') as f:
                            img_b64 = base64.b64encode(f.read()).decode('utf-8')
                        content_list.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img_b64}"}
                        })
                
                data = {
                    "model": model_id,
                    "messages": [{"role": "user", "content": content_list}],
                    "max_tokens": max_tokens
                }
            else:
                # 普通文本模型调用
                if "anthropic" in api_type:
                    url = f"{base_url}/v1/messages"
                    headers = {"x-api-key": api_key, "Content-Type": "application/json", "anthropic-version": "2023-06-01"}
                    data = {"model": model_id, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
                else:
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
    
    def call_vision(
        self, 
        prompt: str, 
        image: str,
        model_id: str = None
    ) -> SymphonyResult:
        """调用视觉模型分析图片"""
        if model_id is None:
            for m in self.models:
                if m.get("is_vision", False) and m.get("enabled", True):
                    model_id = m.get("model_id")
                    break
        
        if model_id is None:
            model_id = self.models[0].get("model_id") if self.models else "glm-4.1v-thinking-flash"
        
        return self.call_model(prompt, model_id=model_id, image=image)
    
    def generate_image(
        self, 
        prompt: str, 
        model_id: str = None
    ) -> GenerationResult:
        """
        调用图像生成模型
        
        Args:
            prompt: 图像描述
            model_id: 图像生成模型ID
        """
        if model_id is None:
            for m in self.models:
                if m.get("is_image_gen", False) and m.get("enabled", True):
                    model_id = m.get("model_id")
                    break
        
        if model_id is None:
            return GenerationResult(
                success=False,
                model_name="",
                error="No image generation model available"
            )
        
        model_cfg = self._get_model_config(model_id)
        
        if not model_cfg:
            return GenerationResult(success=False, model_name=model_id, error="Model not found")
        
        base_url = model_cfg.get("base_url", "")
        api_key = model_cfg.get("api_key", "")
        
        try:
            start_time = time.time()
            
            # 使用chat completions接口生成图像
            url = f"{base_url}/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {
                "model": model_id,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=90)
            latency = time.time() - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                content = result_data["choices"][0]["message"]["content"]
                
                # 解析返回的图像URL
                image_url = ""
                if isinstance(content, list):
                    for item in content:
                        if item.get("type") == "image_url":
                            image_url = item.get("image_url", {}).get("url", "")
                            break
                
                return GenerationResult(
                    success=True,
                    model_name=model_id,
                    url=image_url,
                    latency=latency
                )
            else:
                return GenerationResult(
                    success=False,
                    model_name=model_id,
                    error=f"HTTP {response.status_code}: {response.text[:100]}",
                    latency=latency
                )
        except Exception as e:
            return GenerationResult(success=False, model_name=model_id, error=str(e))
    
    def generate_video(
        self, 
        prompt: str, 
        model_id: str = None,
        callback: callable = None
    ) -> GenerationResult:
        """
        调用视频生成模型（异步）
        
        Args:
            prompt: 视频描述
            model_id: 视频生成模型ID
            callback: 完成后回调函数
        """
        if model_id is None:
            for m in self.models:
                if m.get("is_video_gen", False) and m.get("enabled", True):
                    model_id = m.get("model_id")
                    break
        
        if model_id is None:
            return GenerationResult(
                success=False,
                model_name="",
                error="No video generation model available",
                is_async=False
            )
        
        model_cfg = self._get_model_config(model_id)
        
        if not model_cfg:
            return GenerationResult(success=False, model_name=model_id, error="Model not found", is_async=False)
        
        base_url = model_cfg.get("base_url", "")
        api_key = model_cfg.get("api_key", "")
        
        try:
            start_time = time.time()
            
            # 尝试使用异步任务API
            # 首先尝试直接调用（某些模型可能支持同步）
            url = f"{base_url}/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {
                "model": model_id,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=90)
            latency = time.time() - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                content = result_data["choices"][0]["message"]["content"]
                
                # 解析返回的视频URL
                video_url = ""
                if isinstance(content, list):
                    for item in content:
                        if item.get("type") == "video_url":
                            video_url = item.get("video_url", {}).get("url", "")
                            break
                
                return GenerationResult(
                    success=True,
                    model_name=model_id,
                    url=video_url,
                    latency=latency,
                    is_async=False
                )
            elif response.status_code == 400:
                error_msg = response.text
                if "不支持SYNC" in error_msg or "async" in error_msg.lower():
                    # 异步模型，需要返回task_id让用户轮询
                    return GenerationResult(
                        success=False,
                        model_name=model_id,
                        error="Video generation requires async API. Use async_task_id to poll results.",
                        latency=latency,
                        is_async=True,
                        task_id=f"async_{int(time.time())}"
                    )
                else:
                    return GenerationResult(
                        success=False,
                        model_name=model_id,
                        error=f"HTTP 400: {response.text[:100]}",
                        latency=latency
                    )
            else:
                return GenerationResult(
                    success=False,
                    model_name=model_id,
                    error=f"HTTP {response.status_code}: {response.text[:100]}",
                    latency=latency
                )
        except Exception as e:
            return GenerationResult(success=False, model_name=model_id, error=str(e), is_async=False)
    
    def discuss(self, topic: str, mode: str = "brainstorm", num_experts: int = 3) -> Dict:
        """多模型讨论"""
        roles = self.roles_config.get(mode, self.roles_config["brainstorm"])[:num_experts]
        results = []
        
        print(f"\n=== {mode} 模式 ===")
        print(f"主题: {topic}")
        print(f"专家数量: {len(roles)}")
        
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
        
        total_tokens = sum(r["tokens"] for r in results)
        total_latency = sum(r["latency"] for r in results)
        
        return {
            "topic": topic,
            "mode": mode,
            "results": results,
            "total_tokens": total_tokens,
            "total_latency": total_latency
        }
    
    def list_models(self) -> List[Dict]:
        """列出所有可用模型"""
        models = []
        for m in self.models:
            if m.get("enabled", True):
                info = {
                    "model_id": m.get("model_id"),
                    "alias": m.get("alias", m.get("model_id")),
                    "provider": m.get("provider"),
                    "is_vision": m.get("is_vision", False),
                    "is_image_gen": m.get("is_image_gen", False),
                    "is_video_gen": m.get("is_video_gen", False),
                    "is_reasoning": m.get("is_reasoning", False),
                    "context_window": m.get("context_window")
                }
                models.append(info)
        return models


def main():
    """测试"""
    print("=" * 60)
    print("BrainstormPanel v2.4.0 - 图像/视频生成支持")
    print("=" * 60)
    
    panel = BrainstormPanel()
    
    print(f"\n已加载模型数: {len(panel.models)}")
    for m in panel.models:
        tags = []
        if m.get("is_vision"): tags.append("[视觉]")
        if m.get("is_image_gen"): tags.append("[图像]")
        if m.get("is_video_gen"): tags.append("[视频]")
        if m.get("is_reasoning"): tags.append("[推理]")
        tag_str = " ".join(tags) if tags else ""
        print(f"  - {m.get('model_id')} ({m.get('provider')}) {tag_str}")
    
    # 测试文本调用
    print("\n--- 文本调用测试 ---")
    result = panel.call_model("hello", max_tokens=50)
    print(f"  成功: {result.success}")
    print(f"  模型: {result.model_name}")
    print(f"  延迟: {result.latency:.1f}s")
    
    # 测试图像生成
    print("\n--- 图像生成测试 ---")
    img_result = panel.generate_image("一只可爱的蓝色小猫")
    print(f"  成功: {img_result.success}")
    print(f"  模型: {img_result.model_name}")
    if img_result.success:
        print(f"  URL: {img_result.url[:80]}...")
    else:
        print(f"  错误: {img_result.error}")
    print(f"  延迟: {img_result.latency:.1f}s")
    
    # 测试视频生成
    print("\n--- 视频生成测试 ---")
    vid_result = panel.generate_video("一只可爱的小猫")
    print(f"  成功: {vid_result.success}")
    print(f"  模型: {vid_result.model_name}")
    print(f"  异步: {vid_result.is_async}")
    if vid_result.is_async:
        print(f"  Task ID: {vid_result.task_id}")
    print(f"  错误: {vid_result.error}")
    print(f"  延迟: {vid_result.latency:.1f}s")


if __name__ == "__main__":
    main()
