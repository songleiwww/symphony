#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BrainstormPanel v2.5.0 - 真实模型调用 + 视觉/图像/视频生成 + 智谱SDK支持
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

# 尝试导入智谱SDK
try:
    from zhipuai import ZhipuAI
    ZHIPU_SDK_AVAILABLE = True
except ImportError:
    ZHIPU_SDK_AVAILABLE = False

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
    video_duration: int = 0


@dataclass
class TaskStatusResult:
    """任务状态结果"""
    task_id: str
    status: str  # pending, processing, success, failed
    progress: int = 0
    url: str = ""  # 成功时的URL
    error: str = ""


class BrainstormPanel:
    """
    多模型协作工具 v2.5.0
    直接使用config.py配置
    支持：文本、视觉、图像生成、视频生成（智谱SDK）
    """
    
    def __init__(self):
        self.name = "brainstorm_panel"
        self.version = "2.5.0"
        
        # 直接从config.py加载MODEL_CHAIN
        self.models = MODEL_CHAIN
        
        # 初始化智谱SDK客户端
        self._init_zhipu_client()
        
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
    
    def _init_zhipu_client(self):
        """初始化智谱AI客户端"""
        self.zhipu_client = None
        
        # 从配置中获取智谱API Key
        for m in self.models:
            if m.get("provider") == "zhipu":
                api_key = m.get("api_key")
                if api_key:
                    if ZHIPU_SDK_AVAILABLE:
                        try:
                            self.zhipu_client = ZhipuAI(api_key=api_key)
                            print(f"[智谱SDK] 初始化成功")
                        except Exception as e:
                            print(f"[智谱SDK] 初始化失败: {e}")
                    else:
                        print(f"[智谱SDK] SDK未安装")
                    break
        
        if not self.zhipu_client:
            print(f"[智谱SDK] 未找到有效的API Key")
    
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
            
            # 方式1: 尝试使用智谱SDK
            if self.zhipu_client and "cogview" in model_id:
                try:
                    response = self.zhipu_client.images.generations(
                        model=model_id,
                        prompt=prompt
                    )
                    latency = time.time() - start_time
                    
                    if response.url:
                        return GenerationResult(
                            success=True,
                            model_name=model_id,
                            url=response.url,
                            latency=latency
                        )
                except Exception as e:
                    print(f"[图像生成] SDK调用失败: {e}")
            
            # 方式2: 使用HTTP API
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
        使用智谱SDK进行异步任务提交
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
            return GenerationResult(success=False, model_name=model_id, error="Model not found")
        
        try:
            start_time = time.time()
            
            # 方式1: 使用智谱SDK（推荐）
            if self.zhipu_client:
                try:
                    response = self.zhipu_client.videos.generations(
                        model=model_id,
                        prompt=prompt
                    )
                    latency = time.time() - start_time
                    
                    task_id = response.id
                    print(f"[视频生成] 任务已提交: {task_id}")
                    
                    return GenerationResult(
                        success=True,
                        model_name=model_id,
                        url="",  # 异步任务，没有即时URL
                        latency=latency,
                        is_async=True,
                        task_id=task_id
                    )
                except Exception as e:
                    print(f"[视频生成] SDK调用失败: {e}")
            
            # 方式2: 备用HTTP API（可能不支持）
            base_url = model_cfg.get("base_url", "")
            api_key = model_cfg.get("api_key", "")
            
            url = f"{base_url}/videos/generations"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {
                "model": model_id,
                "prompt": prompt
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=90)
            latency = time.time() - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                task_id = result_data.get("id", "")
                
                return GenerationResult(
                    success=True,
                    model_name=model_id,
                    url="",
                    latency=latency,
                    is_async=True,
                    task_id=task_id
                )
            elif response.status_code == 400:
                error_msg = response.text
                if "不支持SYNC" in error_msg:
                    return GenerationResult(
                        success=False,
                        model_name=model_id,
                        error="Video generation requires async API. Use query_video_task() to poll results.",
                        latency=latency,
                        is_async=True,
                        task_id=f"async_{int(time.time())}"
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
    
    def query_video_task(
        self, 
        task_id: str
    ) -> TaskStatusResult:
        """
        查询视频生成任务状态
        
        Args:
            task_id: 任务ID (generate_video返回的task_id)
            
        Returns:
            TaskStatusResult: 任务状态
        """
        if not task_id:
            return TaskStatusResult(
                task_id="",
                status="failed",
                error="No task_id provided"
            )
        
        # 过滤掉模拟的task_id
        if task_id.startswith("async_"):
            return TaskStatusResult(
                task_id=task_id,
                status="failed",
                error="Invalid task_id (mock ID)"
            )
        
        try:
            # 使用智谱SDK查询任务
            if self.zhipu_client:
                response = self.zhipu_client.videos.retrieve_videos_task(
                    id=task_id
                )
                
                return TaskStatusResult(
                    task_id=task_id,
                    status=response.task_status,
                    progress=response.task_progress or 0,
                    url=response.video_result or "",
                    error=""
                )
            else:
                # 备用HTTP方式
                for m in self.models:
                    if m.get("provider") == "zhipu":
                        api_key = m.get("api_key")
                        break
                
                base_url = "https://open.bigmodel.cn/api/paas/v4"
                url = f"{base_url}/tasks/{task_id}"
                headers = {"Authorization": f"Bearer {api_key}"}
                
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    return TaskStatusResult(
                        task_id=task_id,
                        status=data.get("task_status", "unknown"),
                        progress=data.get("task_progress", 0),
                        url=data.get("video_result", ""),
                        error=""
                    )
                else:
                    return TaskStatusResult(
                        task_id=task_id,
                        status="failed",
                        error=f"HTTP {response.status_code}"
                    )
                    
        except Exception as e:
            return TaskStatusResult(
                task_id=task_id,
                status="failed",
                error=str(e)
            )
    
    def wait_video_task(
        self, 
        task_id: str,
        timeout: int = 300,
        poll_interval: int = 5
    ) -> GenerationResult:
        """
        等待视频生成任务完成（轮询）
        
        Args:
            task_id: 任务ID
            timeout: 超时时间（秒）
            poll_interval: 轮询间隔（秒）
            
        Returns:
            GenerationResult: 最终结果
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.query_video_task(task_id)
            
            print(f"[视频任务] 状态: {status.status}, 进度: {status.progress}%")
            
            if status.status == "success":
                return GenerationResult(
                    success=True,
                    model_name="cogvideox-flash",
                    url=status.url,
                    latency=time.time() - start_time,
                    is_async=False,
                    task_id=task_id
                )
            elif status.status == "failed":
                return GenerationResult(
                    success=False,
                    model_name="cogvideox-flash",
                    error=status.error or "Task failed",
                    latency=time.time() - start_time,
                    is_async=False,
                    task_id=task_id
                )
            else:
                # pending 或 processing，继续等待
                time.sleep(poll_interval)
        
        # 超时
        return GenerationResult(
            success=False,
            model_name="cogvideox-flash",
            error=f"Timeout after {timeout} seconds",
            latency=timeout,
            is_async=False,
            task_id=task_id
        )
    
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
    print("BrainstormPanel v2.5.0 - 智谱SDK视频生成支持")
    print("=" * 60)
    
    panel = BrainstormPanel()
    
    print(f"\n智谱SDK: {'已安装' if ZHIPU_SDK_AVAILABLE else '未安装'}")
    print(f"智谱客户端: {'已初始化' if panel.zhipu_client else '未初始化'}")
    
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
    
    # 测试视频生成（异步）
    print("\n--- 视频生成测试 ---")
    vid_result = panel.generate_video("一只可爱的小猫在草地上奔跑，阳光明媚")
    print(f"  成功: {vid_result.success}")
    print(f"  模型: {vid_result.model_name}")
    print(f"  异步: {vid_result.is_async}")
    print(f"  Task ID: {vid_result.task_id}")
    print(f"  错误: {vid_result.error}")
    print(f"  延迟: {vid_result.latency:.1f}s")
    
    # 如果有task_id，查询状态
    if vid_result.task_id and not vid_result.task_id.startswith("async_"):
        print("\n--- 任务状态查询 ---")
        status = panel.query_video_task(vid_result.task_id)
        print(f"  Task ID: {status.task_id}")
        print(f"  状态: {status.status}")
        print(f"  进度: {status.progress}%")
        if status.url:
            print(f"  视频URL: {status.url}")


if __name__ == "__main__":
    main()
