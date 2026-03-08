#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import math

API_KEY = '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'

def get_embedding(text):
    url = 'https://integrate.api.nvidia.com/v1/embeddings'
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    data = {'model': 'baai/bge-m3', 'input': text, 'encoding_format': 'float'}
    r = requests.post(url, headers=headers, json=data, timeout=30)
    if r.status_code == 200:
        return r.json()['data'][0]['embedding']
    return None

# Test
print("Test embedding API:")
emb1 = get_embedding("hello")
if emb1:
    print(f"Success! Dimension: {len(emb1)}")
    print(f"First 5 values: {emb1[:5]}")
