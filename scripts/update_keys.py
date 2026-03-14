# -*- coding: utf-8 -*-
"""
API Key 更新脚本
用法: python scripts/update_keys.py --provider 火山引擎 --key 你的Key
"""
import argparse
import sqlite3
import os

DB_PATH = 'data/symphony.db'

def update_key(provider: str, key: str):
    """更新指定服务商的API Key"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ 数据库不存在: {DB_PATH}")
        print("请先运行: python scripts/init_api_keys.py")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 更新
    cursor.execute('UPDATE 模型配置表 SET key = ? WHERE 服务商 = ?', (key, provider))
    
    if cursor.rowcount > 0:
        print(f"✅ 已更新 {provider} 的API Key")
        conn.commit()
    else:
        print(f"❌ 未找到服务商: {provider}")
    
    conn.close()
    return True

def list_providers():
    """列出所有服务商"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ 数据库不存在")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT 服务商, key FROM 模型配置表 GROUP BY 服务商')
    
    print("\n当前配置:")
    print("-"*40)
    for provider, key in cursor.fetchall():
        has_key = "✅ 已配置" if key and key != "YOUR_API_KEY_HERE" else "❌ 未配置"
        print(f"  {provider}: {has_key}")
    
    conn.close()


def main():
    parser = argparse.ArgumentParser(description='更新API Key')
    parser.add_argument('--provider', '-p', help='服务商名称')
    parser.add_argument('--key', '-k', help='API Key')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有服务商')
    
    args = parser.parse_args()
    
    if args.list:
        list_providers()
    elif args.provider and args.key:
        update_key(args.provider, args.key)
    else:
        print("用法:")
        print("  python scripts/update_keys.py --list")
        print("  python scripts/update_keys.py --provider 火山引擎 --key 你的Key")


if __name__ == "__main__":
    main()
