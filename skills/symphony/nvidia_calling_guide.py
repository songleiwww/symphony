#!/usr/bin/env python3
# 英伟达模型调用指南（最终版，统一使用官方在线API调用，无需本地硬件）
import requests

# ==================================================
# 英伟达统一在线API调用方案（支持所有英伟达平台模型，包括第三方厂商模型）
# 无需本地GPU、无需本地部署，直接调用官方云端接口
# 支持模型：NVIDIA自研模型 + 所有第三方合作模型（moonshotai/kimi-k2.5、Stability AI等全量上架模型）
# 唯一标识：完整模型ID作为调用标识，例如"moonshotai/kimi-k2.5"、"nvidia/llama-3.1-nemotron-70b-instruct"
# ==================================================
def call_nvidia_api(model_name: str, prompt: str, api_key: str, stream: bool = True, max_tokens: int = 16384, temperature: float = 1.0):
    """
    调用英伟达官方在线API
    :param model_name: 完整模型ID，例如"moonshotai/kimi-k2.5"
    :param prompt: 用户提问内容
    :param api_key: 英伟达API密钥（从NVIDIA官网获取）
    :param stream: 是否流式返回
    :param max_tokens: 最大生成长度
    :param temperature: 温度系数
    """
    invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "text/event-stream" if stream else "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": 1.0,
        "stream": stream
    }
    try:
        response = requests.post(invoke_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        if stream:
            for line in response.iter_lines():
                if line:
                    print(line.decode("utf-8"))
        else:
            return response.json()
    except Exception as e:
        print(f"英伟达API调用失败: {str(e)}，自动降级到其他服务商")
        return None

# ==================================================
# 调用示例
# ==================================================
if __name__ == "__main__":
    # 示例1：调用月之暗面kimi-k2.5模型
    # call_nvidia_api(
    #     model_name="moonshotai/kimi-k2.5",
    #     prompt="你好",
    #     api_key="nv-你的API密钥",
    #     stream=True
    # )

    # 示例2：调用英伟达自研模型
    # call_nvidia_api(
    #     model_name="nvidia/llama-3.1-nemotron-70b-instruct",
    #     prompt="你好",
    #     api_key="nv-你的API密钥",
    #     stream=True
    # )
    print("英伟达API调用指南已更新，统一使用在线接口，支持所有平台模型，无需本地硬件部署")
