#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆包模型列表测试
"""

import requests
import json

API_KEY = "3b922877-3fbe-45d1-a298-53f2231c5224"
BASE_URL = "https://ark.cn-beijing.volces.com/api/coding/v3"

# 获取模型列表
headers = {
    "Authorization": f"Bearer {API_KEY}"
}

try:
    response = requests.get(
        f"{BASE_URL}/models",
        headers=headers,
        timeout=30
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
except Exception as e:
    print(f"错误: {e}")
