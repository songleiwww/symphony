#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json

url = 'https://open.bigmodel.cn/dev/guide/model/cogvideo'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json'
}

# 尝试API格式
r = requests.get(url, headers=headers, timeout=30)

# 保存原始内容
with open('cogvideo_doc.html', 'w', encoding='utf-8') as f:
    f.write(r.text)

print(f'Status: {r.status_code}')
print(f'Length: {len(r.text)}')

# 查找API端点
import re
# 查找URL模式
urls = re.findall(r'["\']([^"\']*(?:api|endpoint|url)[^"\']*)["\']', r.text, re.I)
print(f'\nFound URLs: {urls[:10]}')

# 查找JSON数据
jsons = re.findall(r'\{[^{}]*(?:cogvideo|video|async|task)[^{}]*\}', r.text, re.I)
print(f'\nFound JSONs: {jsons[:5]}')

# 打印内容片段
print(f'\n=== Content (first 3000 chars) ===')
print(r.text[:3000])
