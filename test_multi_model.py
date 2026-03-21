# -*- coding: utf-8 -*-
"""
序境系统 - 多模型协同测试
测试多模型合作能力、规则检查、执行汇报
从数据库模型配置表动态读取配置
"""

import sys
import os
import json
import time
import sqlite3

kernel_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, kernel_path)

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'symphony.db')


def get_models_from_db(provider: str = None) -> dict:
    """从数据库模型配置表动态读取配置"""
    conn = sqlite3.connect(DB_PATH)
    conn.text_factory = str
    c = conn.cursor()
    
    # 使用参数化查询避免中文编码问题
    # 字段: id, 模型名称, 模型标识符, 服务商, API地址, API密钥
    if provider:
        c.execute("""
            SELECT id, 模型名称, 模型标识符, 服务商, API地址, API密钥
            FROM 模型配置表
            WHERE 服务商 = ? AND 在线状态 = 'online'
            ORDER BY id
        """, (provider,))
    else:
        c.execute("""
            SELECT id, 模型名称, 模型标识符, 服务商, API地址, API密钥
            FROM 模型配置表
            WHERE 在线状态 = 'online'
            ORDER BY 服务商, id
        """)
    
    models = {}
    for row in c.fetchall():
        model_id, name, identifier, provider_name, api_addr, api_key = row
        # 构建模型配置
        models[identifier] = {
            "name": identifier,
            "display_name": name,
            "provider": provider_name,
            "api_url": api_addr,
            "api_key": api_key,
            "max_tokens": 128000
        }
    
    conn.close()
    return models


def get_all_providers() -> list:
    """获取所有服务商"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT 服务商 FROM 模型配置表 WHERE 在线状态 = 'online'")
    providers = [row[0] for row in c.fetchall()]
    conn.close()
    return providers


# 动态加载模型配置
MODELS = get_models_from_db()


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
            "max_tokens": model_config.get("max_tokens", 128000)
        }
    elif "siliconflow" in url:
        data = {
            "model": model_config["name"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": model_config.get("max_tokens", 32000)
        }
    elif "nvidia" in url:
        data = {
            "model": model_config["name"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": model_config.get("max_tokens", 128000)
        }
    elif "bigmodel" in url:
        data = {
            "model": model_config["name"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": model_config.get("max_tokens", 128000)
        }
    elif "modelscope" in url:
        data = {
            "model": model_config["name"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": model_config.get("max_tokens", 32000)
        }
    else:
        data = {
            "model": model_config["name"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": model_config.get("max_tokens", 32000)
        }
    
    start = time.time()
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        latency = time.time() - start
        
        if resp.status_code == 200:
            result = resp.json()
            return {
                "success": True,
                "response": result.get("choices", [{}])[0].get("message", {}).get("content", ""),
                "tokens": result.get("usage", {}).get("total_tokens", 0),
                "latency": latency,
                "error": None
            }
        else:
            return {
                "success": False,
                "response": None,
                "tokens": 0,
                "latency": latency,
                "error": f"HTTP {resp.status_code}: {resp.text[:200]}"
            }
    except Exception as e:
        return {
            "success": False,
            "response": None,
            "tokens": 0,
            "latency": time.time() - start,
            "error": str(e)
        }


def test_model(model_key: str, prompt: str = "你好") -> dict:
    """测试单个模型"""
    if model_key not in MODELS:
        return {"success": False, "error": f"模型 {model_key} 不在配置中"}
    
    return call_model(MODELS[model_key], prompt)


def test_provider(provider: str, prompt: str = "你好") -> list:
    """测试指定服务商的所有模型"""
    results = []
    for name, config in MODELS.items():
        if config["provider"] == provider:
            result = call_model(config, prompt)
            result["model"] = name
            result["provider"] = provider
            results.append(result)
    return results


def test_all_models(prompt: str = "你好") -> dict:
    """测试所有模型"""
    results = {}
    for name, config in MODELS.items():
        result = call_model(config, prompt)
        results[name] = result
    return results


def reload_models():
    """重新从数据库加载模型配置"""
    global MODELS
    MODELS = get_models_from_db()
    print(f"已重新从数据库加载 {len(MODELS)} 个模型配置")


if __name__ == "__main__":
    print("=== 序境系统 - 多模型协同测试 ===")
    print(f"数据库路径: {DB_PATH}")
    
    # 重新加载模型
    reload_models()
    
    print(f"\n可用模型数: {len(MODELS)}")
    print(f"可用服务商: {get_all_providers()}")
    
    # 测试所有模型
    if len(sys.argv) > 1:
        if sys.argv[1] == "--provider":
            provider = sys.argv[2] if len(sys.argv) > 2 else "英伟达"
            print(f"\n=== 测试服务商: {provider} ===")
            results = test_provider(provider)
            for r in results:
                status = "✅" if r["success"] else "❌"
                print(f"{status} {r['model']}: {r.get('error', 'OK')}")
        elif sys.argv[1] == "--reload":
            reload_models()
            print("模型配置已重新加载")
        else:
            print(f"\n=== 测试模型: {sys.argv[1]} ===")
            result = test_model(sys.argv[1])
            print(f"结果: {result}")
    else:
        print("\n=== 测试所有模型 ===")
        results = test_all_models()
        success = sum(1 for r in results.values() if r["success"])
        print(f"成功: {success}/{len(results)}")
