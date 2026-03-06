#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BrainstormPanel v2.3.0 - 真实模型调用 + 视觉推理支持
直接使用config.py配置，不再依赖openclaw.cherry.json
"""

import time
import base64
import requests
from typing import Dict, List, Any, Union
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


class BrainstormPanel:
    """
    多模型协作工具 v2.3.0
    直接使用config.py配置
    支持视觉推理
    """
    
    def __init__(self):
        self.name = "brainstorm_panel"
        self.version = "2.3.0"
        
        # 直接从config.py加载MODEL_CHAIN
        self.models = MODEL_CHAIN
        
        # 角色配置 - 使用MODEL_CHAIN中的模型
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
    
    def _get_model_config(self, model_id: str) -> Dict:
        """从MODEL_CHAIN获取模型配置"""
        for m in self.models:
            if m.get("model_id") == model_id:
                return m
        return self.models[0] if self.models else {}
    
    def _is_vision_model(self, model_cfg: Dict) -> bool:
        """判断是否是视觉模型"""
        return model_cfg.get("is_vision", False)
    
    def call_model(
        self, 
        prompt: str, 
        model_id: str = None, 
        max_tokens: int = 800,
        image: str = None  # 图片路径或base64
    ) -> SymphonyResult:
        """
        调用单个模型
        
        Args:
            prompt: 提示词
            model_id: 模型ID
            max_tokens: 最大token数
            image: 图片路径或base64字符串（视觉模型用）
        """
        if model_id is None:
            model_id = self.models[0].get("model_id", "glm-4-flash")
        
        model_cfg = self._get_model_config(model_id)
        
        if not model_cfg:
            return SymphonyResult(success=False, model_name=model_id, error="Model not found")
        
        # 使用config.py中的配置
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
                
                # 处理图片
                content_list = []
                
                # 添加文本
                content_list.append({"type": "text", "text": prompt})
                
                # 添加图片
                if image:
                    if Path(image).exists():
                        # 文件路径
                        with open(image, 'rb') as f:
                            img_b64 = base64.b64encode(f.read()).decode('utf-8')
                        content_list.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img_b64}"}
                        })
                    elif image.startswith('data:') or len(image) > 1000:
                        # 已经是base64
                        content_list.append({
                            "type": "image_url",
                            "image_url": {"url": image}
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
    
    def call_vision(
        self, 
        prompt: str, 
        image: str,
        model_id: str = None
    ) -> SymphonyResult:
        """
        调用视觉模型分析图片
        
        Args:
            prompt: 提示词
            image: 图片路径或base64
            model_id: 视觉模型ID（默认使用配置中的第一个视觉模型）
        """
        # 查找视觉模型
        if model_id is None:
            for m in self.models:
                if m.get("is_vision", False) and m.get("enabled", True):
                    model_id = m.get("model_id")
                    break
        
        if model_id is None:
            # 使用默认模型尝试
            model_id = self.models[0].get("model_id") if self.models else "glm-4.1v-thinking-flash"
        
        return self.call_model(prompt, model_id=model_id, image=image)
    
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
                    "is_reasoning": m.get("is_reasoning", False),
                    "context_window": m.get("context_window")
                }
                models.append(info)
        return models


def main():
    """测试"""
    print("=" * 60)
    print("BrainstormPanel v2.3.0 - 视觉推理支持")
    print("=" * 60)
    
    panel = BrainstormPanel()
    
    print(f"\n已加载模型数: {len(panel.models)}")
    for m in panel.models:
        vision_tag = " [视觉]" if m.get("is_vision") else ""
        reasoning_tag = " [推理]" if m.get("is_reasoning") else ""
        print(f"  - {m.get('model_id')} ({m.get('provider')}){vision_tag}{reasoning_tag}")
    
    # 测试文本调用
    print("\n--- 文本调用测试 ---")
    result = panel.call_model("hello", max_tokens=50)
    print(f"  成功: {result.success}")
    print(f"  模型: {result.model_name}")
    print(f"  延迟: {result.latency:.1f}s")
    
    # 测试视觉调用
    print("\n--- 视觉调用测试 ---")
    # 尝试找图片
    test_images = [
        r"C:\Users\Administrator\.openclaw\workspace\avatars\openclaw.png",
        r"C:\Users\Administrator\.openclaw\openclaw.png"
    ]
    
    vision_result = None
    for img_path in test_images:
        if Path(img_path).exists():
            print(f"  找到测试图片: {img_path}")
            vision_result = panel.call_vision("描述这张图片", img_path)
            break
    
    if vision_result:
        print(f"  成功: {vision_result.success}")
        print(f"  模型: {vision_result.model_name}")
        print(f"  延迟: {vision_result.latency:.1f}s")
    else:
        print("  未找到测试图片，跳过视觉测试")


if __name__ == "__main__":
    main()
