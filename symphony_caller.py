#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 调用 交响的接口
支持多API提供商：火山引擎 + 英伟达
"""

import sys
import io

# 只在直接运行时修改stdout
if __name__ == "__main__" and sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# 导入配置
from config import (
    CONFIG, MODEL_INFO, 
    get_provider_for_model, get_api_config_for_model,
    SYMPHONY_GENESIS, DREAM_MAKER, JIAOJIAO, SYMPHONY_BRAND,
    get_genesis_story, get_dream_maker, get_jiaoJiao, get_brand
)


# =============================================================================
# 模型验证函数
# =============================================================================

def validate_model(model_id: str) -> bool:
    """验证模型是否在允许列表中"""
    from config import get_all_models
    return model_id in get_all_models()


def get_allowed_models() -> List[str]:
    """获取允许使用的模型列表"""
    from config import get_all_models
    return get_all_models()


def filter_allowed_models(model_ids: List[str]) -> List[str]:
    """过滤出允许使用的模型"""
    allowed = get_allowed_models()
    return [m for m in model_ids if m in allowed]


# =============================================================================
# 交响调用器
# =============================================================================

class SymphonyCaller:
    """
    交响调用器
    支持火山引擎和英伟达双API
    """
    
    def __init__(self, silent=False):
        self.config = CONFIG
        # 获取所有模型
        from config import get_all_models
        self.models = get_all_models()
        self.primary_model = self.config["primary_model"]
        
        # 加载基因故事
        self.genesis = get_genesis_story()
        self.dream_maker = get_dream_maker()
        self.jiaoJiao = get_jiaoJiao()
        self.brand = get_brand()
        
        if not silent:
            print("="*60)
            print(f"{self.brand['color']} {self.brand['name_cn']} ({self.brand['name_en']})")
            print(f"标语: {self.brand['tagline']}")
            print("="*60)
            print(f"🎭 基因故事已加载")
            print(f"   创造者: {self.dream_maker['name']}")
            print(f"   继承者: {self.jiaoJiao['name']} ({self.jiaoJiao['species']})")
            print("="*60)
            print(f"主模型: {self.primary_model}")
            print(f"可用模型: {len(self.models)}个")
            print("="*60)
    
    def get_status(self) -> dict:
        """获取交响状态（用于OpenClaw监控）"""
        # 优先从共享文件读取（可跨进程）
        from symphony import load_monitor_from_file
        file_data = load_monitor_from_file()
        
        if file_data:
            return {
                "uptime_seconds": file_data.get("uptime", 0),
                "total_calls": file_data.get("total_calls", 0),
                "success_rate": file_data.get("success_rate", 0),
                "active_calls": file_data.get("active_calls", 0),
                "model_stats": file_data.get("model_stats", {}),
                "recent_calls": file_data.get("recent_calls", []),
                "source": "file"
            }
        
        # 降级到内存监控
        from symphony import get_monitor
        monitor = get_monitor()
        stats = monitor.get_stats()
        history = monitor.get_history(5)
        
        return {
            "uptime_seconds": stats.get("uptime", 0),
            "total_calls": stats.get("total_calls", 0),
            "success_rate": stats.get("success_rate", 0),
            "active_calls": stats.get("active_calls", 0),
            "model_stats": stats.get("model_stats", {}),
            "recent_calls": [
                {
                    "model": h.get("model", ""),
                    "success": h.get("success", False),
                    "elapsed": h.get("elapsed", 0),
                    "prompt_preview": h.get("prompt", "")[:30] + "..." if len(h.get("prompt", "")) > 30 else h.get("prompt", "")
                }
                for h in history
            ],
            "source": "memory"
        }
    
    def call_api(self, model_id: str, prompt: str) -> dict:
        """
        调用API（自动选择提供商）
        
        Args:
            model_id: 模型ID
            prompt: 提示词
            
        Returns:
            调用结果
        """
        # 获取模型对应的API配置
        api_config = get_api_config_for_model(model_id)
        
        url = f"{api_config['base_url']}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_config['api_key']}",
            "Content-Type": "application/json"
        }
        
        # 构建请求
        data = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024,
            "temperature": 0.7
        }
        
        # 检查是否需要thinking参数
        model_info = MODEL_INFO.get(model_id, {})
        if model_info.get("thinking"):
            # thinking模型添加思考模式
            data["thinking"] = {"type": "enabled"}
        
        start = time.time()
        
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=120)
            elapsed = time.time() - start
            
            if resp.status_code == 200:
                result = resp.json()
                msg = result["choices"][0]["message"]
                content = msg.get("content") or msg.get("reasoning_content") or ""
                
                result = {
                    "success": True,
                    "model": model_id,
                    "provider": api_config["provider"],
                    "response": content,
                    "elapsed": elapsed,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                result = {
                    "success": False,
                    "model": model_id,
                    "provider": api_config["provider"],
                    "error": f"Status {resp.status_code}: {resp.text[:100]}",
                    "elapsed": elapsed,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            result = {
                "success": False,
                "model": model_id,
                "provider": "unknown",
                "error": str(e),
                "elapsed": elapsed if 'elapsed' in dir() else 0,
                "timestamp": datetime.now().isoformat()
            }
        
        # 记录到监控器并保存到共享文件
        try:
            from symphony import get_monitor, save_monitor_to_file
            monitor = get_monitor()
            call_id = f"caller_{int(time.time()*1000)}"
            
            # 记录开始
            monitor.start_call(call_id, model_id, prompt)
            
            # 记录结束
            error_msg = result.get("error", "") if not result["success"] else ""
            monitor.end_call(call_id, result["success"], result.get("response", ""), error_msg, result.get("elapsed", 0))
            
            # 保存到共享文件
            save_monitor_to_file()
        except Exception as e:
            pass  # 静默失败
        
        return result
    
    def call_single(self, prompt: str, model: str = None) -> Dict[str, Any]:
        """
        调用单个模型
        
        Args:
            prompt: 提示词
            model: 模型ID（可选，默认主模型）
            
        Returns:
            调用结果
        """
        if model is None:
            model = self.primary_model
        
        # 验证模型
        if not validate_model(model):
            return {
                "success": False,
                "model": model,
                "error": f"模型 {model} 不在允许列表中"
            }
        
        return self.call_api(model, prompt)
    
    def call_multiple(self, prompt: str, models: List[str] = None) -> Dict[str, Any]:
        """
        调用多个模型
        
        Args:
            prompt: 提示词
            models: 模型列表（可选，默认全部）
            
        Returns:
            包含所有模型结果的字典
        """
        if models is None:
            models = self.models[:5]
        
        # 验证模型
        validated_models = []
        rejected_models = []
        
        for m in models:
            if validate_model(m):
                validated_models.append(m)
            else:
                rejected_models.append(m)
        
        if rejected_models:
            print(f"\n⚠️ 警告: 以下模型不在允许列表中，已跳过: {rejected_models}")
        
        if not validated_models:
            return {
                "success": False,
                "error": "没有有效的模型可用"
            }
        
        models = validated_models
        
        print(f"\n🎯 交响多模型调用: {len(models)}个模型")
        print(f"主题: {prompt[:50]}...")
        print("-"*60)
        
        results = []
        
        # 并行调用
        with ThreadPoolExecutor(max_workers=len(models)) as executor:
            futures = {executor.submit(self.call_single, prompt, m): m for m in models}
            
            for future in as_completed(futures):
                model = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        "success": False,
                        "model": model,
                        "error": str(e)
                    })
        
        # 按模型名排序
        results.sort(key=lambda x: x.get("model", ""))
        
        # 统计
        success = sum(1 for r in results if r.get("success"))
        
        print(f"\n✅ 调用完成: {success}/{len(models)}成功")
        
        return {
            "success": success > 0,
            "total": len(models),
            "success_count": success,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def format_results(self, call_result: Dict[str, Any]) -> str:
        """格式化结果"""
        results = call_result.get("results", [])
        
        if not results:
            return "没有调用结果"
        
        output = []
        output.append("\n" + "="*60)
        output.append("🎼 交响多模型协作结果")
        output.append("="*60)
        
        for r in results:
            model = r.get("model", "unknown")
            provider = r.get("provider", "unknown")
            status = "✅" if r.get("success") else "❌"
            elapsed = r.get("elapsed", 0)
            
            output.append(f"\n{status} {model} [{provider}] ({elapsed:.2f}s)")
            
            if r.get("success"):
                content = r.get("response", "")
                if len(content) > 300:
                    content = content[:300] + "..."
                output.append(f"   {content}")
            else:
                output.append(f"   错误: {r.get('error', 'unknown')}")
        
        output.append("\n" + "="*60)
        output.append(f"总计: {call_result.get('success_count', 0)}/{call_result.get('total', 0)} 成功")
        output.append("="*60)
        
        return "\n".join(output)


# =============================================================================
# 便捷函数
# =============================================================================

def symphony_call(prompt: str, models: List[str] = None) -> str:
    """交响调用"""
    caller = SymphonyCaller()
    result = caller.call_multiple(prompt, models)
    return caller.format_results(result)


def symphony_single(prompt: str, model: str = None) -> Dict[str, Any]:
    """交响单模型调用"""
    caller = SymphonyCaller()
    return caller.call_single(prompt, model)


# =============================================================================
# 测试
# =============================================================================

if __name__ == "__main__":
    print("🎼 交响调用器测试")
    print("="*60)
    
    caller = SymphonyCaller()
    
    # 测试豆包模型
    print("\n\n测试1: 豆包模型")
    result1 = caller.call_single("你好，请介绍一下自己", "ark-code-latest")
    
    if result1.get("success"):
        print(f"\n✅ {result1['model']} [{result1['provider']}]:")
        print(result1['response'][:200])
    else:
        print(f"\n❌ 失败: {result1.get('error')}")
    
    # 测试多模型
    print("\n\n" + "="*60)
    print("测试2: 多模型调用")
    
    test_models = ["ark-code-latest", "Doubao-Seed-2.0-pro", "GLM-4.7"]
    result2 = caller.call_multiple("如何让人工智能更智能？", test_models)
    print(caller.format_results(result2))
