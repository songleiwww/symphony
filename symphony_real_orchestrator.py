#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony Real Orchestrator
交响真实模型编排器
根据用户方法开发：运行脚本 -> 输出到JSON -> 读取结果
"""

import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class SymphonyRealOrchestrator:
    """交响真实模型编排器"""
    
    def __init__(self, workspace: str = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony"):
        self.workspace = Path(workspace)
        self.output_dir = self.workspace / "outputs"
        self.output_dir.mkdir(exist_ok=True)
        
        self.config = self._load_openclaw_config()
    
    def _load_openclaw_config(self) -> Dict[str, Any]:
        """加载OpenClaw配置"""
        config_path = Path(r"C:\Users\Administrator\.openclaw\openclaw.cherry.json")
        if not config_path.exists():
            return {}
        return json.loads(config_path.read_text(encoding='utf-8'))
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """获取可用模型列表"""
        models = []
        providers = self.config.get("models", {}).get("providers", {})
        
        for provider_name, provider_config in providers.items():
            for model in provider_config.get("models", []):
                models.append({
                    "provider": provider_name,
                    "model_id": model["id"],
                    "name": model.get("name", model["id"]),
                    "context_window": model.get("contextWindow", 128000),
                    "api_key": provider_config.get("apiKey", ""),
                    "base_url": provider_config.get("baseUrl", "")
                })
        
        return models
    
    def call_model(
        self,
        provider: str,
        model_id: str,
        prompt: str,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """
        调用真实模型
        
        方法：
        1. 创建临时调用脚本
        2. 运行脚本，输出到JSON
        3. 读取JSON结果
        
        Args:
            provider: 提供商名称
            model_id: 模型ID
            prompt: 提示词
            max_tokens: 最大Token数
            
        Returns:
            模型调用结果
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_path = self.workspace / f"temp_call_{timestamp}.py"
        output_path = self.output_dir / f"result_{timestamp}.json"
        
        providers = self.config.get("models", {}).get("providers", {})
        if provider not in providers:
            return {
                "success": False,
                "error": f"Provider not found: {provider}",
                "timestamp": datetime.now().isoformat()
            }
        
        provider_config = providers[provider]
        api_key = provider_config.get("apiKey", "")
        base_url = provider_config.get("baseUrl", "")
        
        # 创建临时调用脚本
        script_content = f'''#!/usr/bin/env python3
import json
import time
import requests
from datetime import datetime
from pathlib import Path

result = {{
    "success": False,
    "model_name": "{model_id}",
    "provider": "{provider}",
    "prompt": {json.dumps(prompt, ensure_ascii=False)},
    "response": "",
    "error": "",
    "latency": 0.0,
    "timestamp": datetime.now().isoformat(),
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
}}

start_time = time.time()

try:
    headers = {{
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }}
    
    payload = {{
        "model": "{model_id}",
        "messages": [{{"role": "user", "content": {json.dumps(prompt, ensure_ascii=False)}}}],
        "max_tokens": {max_tokens}
    }}
    
    if "/v1" in "{base_url}":
        url = f"{base_url}/chat/completions"
    else:
        url = f"{base_url}/chat/completions"
    
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    
    latency = time.time() - start_time
    result["latency"] = latency
    
    if response.status_code == 200:
        data = response.json()
        result["success"] = True
        result["response"] = data["choices"][0]["message"]["content"]
        
        if "usage" in data:
            result["prompt_tokens"] = data["usage"].get("prompt_tokens", 0)
            result["completion_tokens"] = data["usage"].get("completion_tokens", 0)
            result["total_tokens"] = data["usage"].get("total_tokens", 0)
    else:
        result["error"] = f"HTTP {{response.status_code}}: {{response.text}}"

except Exception as e:
    latency = time.time() - start_time
    result["latency"] = latency
    result["error"] = str(e)

Path({json.dumps(str(output_path), ensure_ascii=False)}).write_text(
    json.dumps(result, indent=2, ensure_ascii=False),
    encoding='utf-8'
)
'''
        
        script_path.write_text(script_content, encoding='utf-8')
        
        # 运行脚本
        try:
            subprocess.run(
                ["python", str(script_path)],
                cwd=str(self.workspace),
                capture_output=True,
                text=True,
                timeout=120
            )
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Call timeout",
                "timestamp": datetime.now().isoformat()
            }
        
        # 读取结果
        if output_path.exists():
            result = json.loads(output_path.read_text(encoding='utf-8'))
        else:
            result = {
                "success": False,
                "error": "Output file not found",
                "timestamp": datetime.now().isoformat()
            }
        
        # 清理临时文件
        script_path.unlink(missing_ok=True)
        if output_path.exists():
            output_path.unlink(missing_ok=True)
        
        return result
    
    def call_multiple_models(
        self,
        model_specs: List[Dict[str, str]],
        prompt: str
    ) -> List[Dict[str, Any]]:
        """
        调用多个模型（串行）
        
        Args:
            model_specs: 模型规格列表 [{"provider": ..., "model_id": ...}]
            prompt: 提示词
            
        Returns:
            所有模型的结果
        """
        results = []
        for spec in model_specs:
            result = self.call_model(
                spec["provider"],
                spec["model_id"],
                prompt
            )
            results.append(result)
        return results


def main():
    """测试"""
    print("=" * 80)
    print("Symphony Real Orchestrator - Test")
    print("=" * 80)
    
    orchestrator = SymphonyRealOrchestrator()
    
    print("\nAvailable models:")
    models = orchestrator.get_available_models()
    for i, model in enumerate(models[:6], 1):
        print(f"  {i}. {model['provider']}/{model['model_id']}")
    
    print("\nTesting single model call...")
    result = orchestrator.call_model(
        "cherry-doubao",
        "ark-code-latest",
        "Hello, please introduce yourself briefly in Chinese"
    )
    
    if result["success"]:
        print(f"\nSuccess!")
        print(f"  Model: {result['provider']}/{result['model_name']}")
        print(f"  Latency: {result['latency']:.2f}s")
        print(f"  Tokens: {result['prompt_tokens']}+{result['completion_tokens']}={result['total_tokens']}")
        print(f"  Response: {result['response']}")
    else:
        print(f"\nFailed: {result['error']}")
    
    print("\n" + "=" * 80)
    print("Done!")
    print("=" * 80)


if __name__ == "__main__":
    main()
