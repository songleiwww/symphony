#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
"""
青丘模型配置引导系统 v3.9.11
检测模型可用性，如果没有可用模型则引导用户配置
"""
import requests
import json
import time
from datetime import datetime

# 读取配置
def load_config():
    """加载配置文件"""
    try:
        import sys
        sys.path.insert(0, 'C:\\Users\\Administrator\\.openclaw\\workspace\\skills\\symphony')
        from config import MODEL_CHAIN
        return MODEL_CHAIN
    except Exception as e:
        return []

# 测试模型可用性
def test_model(model_config):
    """测试单个模型是否可用"""
    try:
        url = model_config.get('base_url', '') + '/chat/completions'
        headers = {
            'Authorization': f"Bearer {model_config.get('api_key', '')}",
            'Content-Type': 'application/json'
        }
        data = {
            'model': model_config.get('model_id', ''),
            'messages': [{'role': 'user', 'content': 'Hi'}],
            'max_tokens': 10
        }
        
        r = requests.post(url, headers=headers, json=data, timeout=10)
        return r.status_code == 200
    except Exception:
        return False

# 主程序
def main():
    print("="*60)
    print("青丘模型配置引导系统 v3.9.11")
    print("检测模型可用性")
    print("="*60)
    print()
    
    # 加载配置
    models = load_config()
    
    if not models:
        print("❌ 未找到模型配置")
        print()
        print_guide()
        return
    
    print(f"📋 检测到 {len(models)} 个模型配置")
    print()
    
    available_models = []
    unavailable_models = []
    
    for model in models:
        name = model.get('name', 'unknown')
        alias = model.get('alias', name)
        api_key = model.get('api_key', '')
        
        # 检查API Key
        if not api_key or 'YOUR_' in api_key:
            print(f"⚠️  {alias}: 需要配置API Key")
            unavailable_models.append(name)
            continue
        
        # 测试模型
        print(f"🔄 测试 {alias}...", end=" ")
        if test_model(model):
            print("✅ 可用")
            available_models.append(name)
        else:
            print("❌ 不可用")
            unavailable_models.append(name)
    
    print()
    print("="*60)
    print("检测结果")
    print("="*60)
    print(f"✅ 可用模型: {len(available_models)}")
    print(f"❌ 不可用模型: {len(unavailable_models)}")
    print()
    
    if len(available_models) == 0:
        print_guide()
    else:
        print("✅ 模型配置正常，可以使用！")

def print_guide():
    """打印配置引导"""
    print("="*60)
    print("📌 模型配置引导")
    print("="*60)
    print()
    print("步骤1: 复制配置模板")
    print("  cp config.template.py config.py")
    print()
    print("步骤2: 编辑config.py，填写API Key")
    print("  api_key = 'YOUR_NVIDIA_API_KEY'")
    print("  api_key = 'YOUR_MINIMAX_API_KEY'")
    print("  api_key = 'YOUR_ZHIPU_API_KEY'")
    print()
    print("步骤3: 获取API Key")
    print("  NVIDIA: https://build.nvidia.com/")
    print("  MiniMax: https://platform.minimaxi.com/")
    print("  智谱: https://open.bigmodel.cn/")
    print()
    print("="*60)

if __name__ == '__main__':
    main()
