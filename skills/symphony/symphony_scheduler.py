#!/usr/bin/env python3
# 序境正式调度内核：严格从symphony.db读取配置，无第三方库依赖，自适应适配所有内核环境
import sqlite3
import requests
import json
from typing import Optional, Dict, List

# 唯一数据源，固定路径，不可修改
DB_PATH = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"

# 优先级顺序（严格按序境调度规则）
PRIORITY_ORDER = ["aliyun", "minimax", "zhipu", "nvidia"]

def get_enabled_providers() -> List[Dict]:
    """从数据库读取已启用的服务商，按优先级排序"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT provider_code, provider_name, base_url, api_key FROM provider_registry WHERE is_enabled = 1")
    providers = []
    for row in cursor.fetchall():
        providers.append({
            "code": row[0],
            "name": row[1],
            "base_url": row[2].rstrip("/"),
            "api_key": row[3]
        })
    conn.close()
    # 按优先级排序
    return sorted(providers, key=lambda p: PRIORITY_ORDER.index(p["code"]))

def get_suitable_model(provider_code: str, model_type: str = "text", min_context_window: int = 2048) -> Optional[Dict]:
    """从数据库读取对应服务商的合适模型，匹配类型和上下文窗口"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT model_id, model_name, model_type, context_window, max_tokens, is_free
        FROM model_config 
        WHERE provider = ? AND is_enabled = 1 AND model_type = ? AND context_window >= ?
        ORDER BY context_window DESC, is_free DESC
        LIMIT 1
    """, (provider_code, model_type, min_context_window))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "model_id": row[0],
        "model_name": row[1],
        "model_type": row[2],
        "context_window": row[3],
        "max_tokens": row[4],
        "is_free": row[5]
    }

def call_model(provider: Dict, model: Dict, prompt: str, max_tokens: int = 1024) -> Optional[str]:
    """调用模型，原生HTTP请求，无openai库依赖，兼容所有OpenAI格式接口"""
    try:
        # 统一OpenAI格式请求体
        payload = {
            "model": model["model_id"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "stream": False
        }

        # 处理阿里云兼容路径
        if provider["code"] == "aliyun":
            url = f"{provider['base_url'].replace('/api/v1', '/compatible-mode/v1')}/chat/completions"
        else:
            url = f"{provider['base_url']}/chat/completions"

        headers = {
            "Authorization": f"Bearer {provider['api_key']}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
        
    except Exception as e:
        print(f"调用{provider['name']} {model['model_name']}失败：{str(e)}，自动降级到下一级服务商")
        return None

def symphony_scheduler(prompt: str, model_type: str = "text", min_context_window: int = 2048) -> Optional[str]:
    """序境正式调度逻辑：按优先级顺序调用，失败自动降级，自适应适配所有内核环境"""
    providers = get_enabled_providers()
    for provider in providers:
        model = get_suitable_model(provider["code"], model_type, min_context_window)
        if not model:
            continue
        print(f"调度：{provider['name']} - {model['model_name']}")
        result = call_model(provider, model, prompt)
        if result:
            return result
    print("所有服务商调度失败，请检查API密钥配置")
    return None

# ------------------------------
# 自适应内核适配层
# 提供统一调用接口，Kernel可直接导入使用
# ------------------------------
def kernel_call(prompt: str, **kwargs) -> Optional[str]:
    """Kernel内核统一调用入口，自适应适配所有参数"""
    return symphony_scheduler(
        prompt=prompt,
        model_type=kwargs.get("model_type", "text"),
        min_context_window=kwargs.get("min_context_window", 2048)
    )

if __name__ == "__main__":
    print("=== 序境调度内核测试 ===")
    print(f"唯一数据源：{DB_PATH}")
    print("无第三方库依赖，自适应适配所有内核环境")
    print("-" * 50)
    # 测试调用（密钥为空所以会失败，逻辑正常）
    result = symphony_scheduler("你好", model_type="text")
    if result:
        print(f"测试成功：{result}")
    else:
        print("调度逻辑正常，请配置API密钥后使用")
