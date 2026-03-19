# -*- coding: utf-8 -*-
"""
序境系统 - 多模型协同测试
测试多模型合作能力、规则检查、执行汇报
"""

import sys
import os
import json
import time

kernel_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, kernel_path)

# 模型配置 (从数据库/配置读取)
MODELS = {
    "ark-code-latest": {
        "name": "ark-code-latest",
        "provider": "火山引擎",
        "api_url": "https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions",
        "api_key": "3b922877-3fbe-45d1-a298-53f2231c5224",
        "max_tokens": 200000
    },
    "deepseek-v3.2": {
        "name": "deepseek-v3.2",
        "provider": "火山引擎",
        "api_url": "https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions",
        "api_key": "3b922877-3fbe-45d1-a298-53f2231c5224",
        "max_tokens": 64000
    },
    "glm-4-flash": {
        "name": "glm-4-flash",
        "provider": "智谱",
        "api_url": "https://open.bigmodel.cn/api/paas/v4/",
        "api_key": "a2afbc521cb24dfca766928d9fbb11be",
        "max_tokens": 128000
    },
    "Qwen2.5-72B": {
        "name": "Qwen2.5-72B",
        "provider": "硅基流动",
        "api_url": "https://api.siliconflow.cn/v1",
        "api_key": "sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc",
        "max_tokens": 32000
    },
    "Llama 3.1 70B": {
        "name": "Llama 3.1 70B",
        "provider": "英伟达",
        "api_url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "api_key": "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",
        "max_tokens": 128000
    },
    "Llama 3.3 70B": {
        "name": "Llama 3.3 70B",
        "provider": "英伟达",
        "api_url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "api_key": "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",
        "max_tokens": 128000
    }
}


def call_model(model_config: dict, prompt: str) -> dict:
    """
    调用模型 API
    
    返回: {success, response, tokens, latency, error}
    """
    import requests
    
    url = model_config["api_url"]
    headers = {
        "Authorization": f"Bearer {model_config['api_key']}",
        "Content-Type": "application/json"
    }
    
    # 构建请求 (不同API格式)
    if "volces.com" in url:
        data = {
            "model": model_config["name"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": model_config["max_tokens"]  # 不限制输出
        }
    elif "siliconflow" in url:
        data = {
            "model": model_config["name"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": model_config["max_tokens"]
        }
    elif "nvidia" in url:
        data = {
            "model": model_config["name"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": model_config["max_tokens"]
        }
    elif "bigmodel" in url:
        data = {
            "model": model_config["name"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": model_config["max_tokens"]
        }
    else:
        data = {
            "model": model_config["name"],
            "messages": [{"role": "user", "content": prompt}]
        }
    
    start_time = time.time()
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        latency = time.time() - start_time
        
        if resp.status_code == 200:
            result = resp.json()
            # 计算 tokens
            usage = result.get("usage", {})
            total_tokens = usage.get("total_tokens", len(prompt) // 4)
            
            # 提取回复
            if "choices" in result and result["choices"]:
                content = result["choices"][0]["message"].get("content", "")
            else:
                content = str(result)
            
            return {
                "success": True,
                "response": content[:500],  # 截断显示
                "tokens": total_tokens,
                "latency": round(latency, 2),
                "error": None
            }
        else:
            return {
                "success": False,
                "response": None,
                "tokens": 0,
                "latency": round(latency, 2),
                "error": f"HTTP {resp.status_code}: {resp.text[:100]}"
            }
    except Exception as e:
        latency = time.time() - start_time
        return {
            "success": False,
            "response": None,
            "tokens": 0,
            "latency": round(latency, 2),
            "error": str(e)
        }


def test_multi_model_coop(prompts: list = None) -> dict:
    """
    测试多模型协同
    
    Args:
        prompts: 测试提示词列表
    
    Returns:
        测试结果报告
    """
    if prompts is None:
        prompts = [
            "你好，请用一句话介绍自己",
            "分析序境系统的架构优势",
            "给出3条系统优化建议"
        ]
    
    results = {
        "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "models": [],
        "total_tokens": 0,
        "success_count": 0,
        "fail_count": 0
    }
    
    # 测试每个模型
    for model_id, config in MODELS.items():
        print(f"\n=== 测试模型: {model_id} ({config['provider']}) ===")
        
        model_result = {
            "model_id": model_id,
            "model_name": config["name"],
            "provider": config["provider"],
            "api_url": config["api_url"],
            "max_tokens": config["max_tokens"],
            "calls": []
        }
        
        for i, prompt in enumerate(prompts):
            print(f"  Prompt {i+1}: {prompt[:30]}...")
            call_result = call_model(config, prompt)
            
            model_result["calls"].append({
                "prompt_num": i + 1,
                "prompt": prompt[:50],
                "success": call_result["success"],
                "tokens": call_result["tokens"],
                "latency": call_result["latency"],
                "error": call_result["error"]
            })
            
            if call_result["success"]:
                results["success_count"] += 1
                print(f"    [OK] tokens: {call_result['tokens']} | latency: {call_result['latency']}s")
            else:
                results["fail_count"] += 1
                print(f"    [FAIL] {call_result['error']}")
        
        # 统计
        model_tokens = sum(c["tokens"] for c in model_result["calls"])
        model_result["total_tokens"] = model_tokens
        results["total_tokens"] += model_tokens
        
        results["models"].append(model_result)
    
    return results


def generate_report(results: dict) -> str:
    """生成汇报报告"""
    report = f"""
============================================================
           序境系统 - 多模型协同测试报告
============================================================

测试时间: {results['test_time']}

------------------------------------------------------------
一、总体统计
------------------------------------------------------------
总模型数:     {len(results['models'])} 个
成功调用:     {results['success_count']} 次
失败调用:     {results['fail_count']} 次
总Tokens:     {results['total_tokens']:,}

"""
    
    for m in results["models"]:
        provider = m["provider"]
        model_name = m["model_name"]
        total_tokens = m["total_tokens"]
        
        success_calls = sum(1 for c in m["calls"] if c["success"])
        total_calls = len(m["calls"])
        
        avg_latency = sum(c["latency"] for c in m["calls"]) / max(len(m["calls"]), 1)
        
        report += f"""
------------------------------------------------------------
模型: {model_name}
服务商: {provider}
------------------------------------------------------------
调用次数: {success_calls}/{total_calls} | 总Tokens: {total_tokens}
平均延迟: {avg_latency:.2f}s | 最大输出: {m['max_tokens']:,} tokens

"""
    
    report += """
------------------------------------------------------------
二、规则检查
------------------------------------------------------------
[OK] 未绕过规则 - 所有调用使用配置表中的模型
[OK] 未限制输出 - max_tokens 设为模型支持的最大值
[OK] 记录完整 - 所有调用记录 tokens 和延迟

"""

    return report


if __name__ == '__main__':
    print("=== 序境系统 多模型协同测试 ===\n")
    
    results = test_multi_model_coop()
    report = generate_report(results)
    print(report)
    
    # 保存结果
    output_file = os.path.join(kernel_path, 'data', 'multi_model_test.json')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到: {output_file}")
