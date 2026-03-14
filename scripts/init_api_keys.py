# -*- coding: utf-8 -*-
"""
API Key 初始化脚本
用法: python scripts/init_api_keys.py
"""
import sqlite3
import os

# 配置
TEMPLATE_DB = 'data/symphony_template.db'
LOCAL_DB = 'data/symphony.db'

def init_keys():
    """初始化API Keys"""
    
    print("="*60)
    print("序境交响 - API Key 初始化")
    print("="*60)
    
    # 检查模板数据库
    if not os.path.exists(TEMPLATE_DB):
        print(f"❌ 模板数据库不存在: {TEMPLATE_DB}")
        print("请从GitHub克隆项目获取模板")
        return False
    
    # 复制模板
    if not os.path.exists(LOCAL_DB):
        import shutil
        shutil.copy(TEMPLATE_DB, LOCAL_DB)
        print(f"✅ 已创建本地数据库: {LOCAL_DB}")
    
    # 提示用户配置
    print("\n⚠️ 请配置以下服务商的API Key:")
    print("-"*40)
    
    providers = [
        ('火山引擎', 'https://ark.cn-beijing.volces.com/api/coding/v3'),
        ('硅基流动', 'https://api.siliconflow.cn/v1'),
        ('英伟达', 'https://integrate.api.nvidia.com/v1'),
        ('魔搭', 'https://api-inference.modelscope.cn/v1'),
    ]
    
    for name, url in providers:
        print(f"  • {name}: {url}")
    
    print("\n📝 配置方法:")
    print(f"  1. 编辑数据库: sqlite3 {LOCAL_DB}")
    print(f"  2. 执行: UPDATE 模型配置表 SET key = '你的Key' WHERE 服务商='服务商名';")
    print(f"  3. 或运行: python scripts/update_keys.py")
    
    return True


if __name__ == "__main__":
    init_keys()
