import sqlite3
import os

# 备份数据库路径
BACKUP_DB = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db.bak_20260407_1505'
# 新生产库路径
PROD_DB = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

def restore_data():
    # 连接备份库
    backup_conn = sqlite3.connect(BACKUP_DB)
    backup_conn.row_factory = sqlite3.Row
    backup_cursor = backup_conn.cursor()
    
    # 连接生产库
    prod_conn = sqlite3.connect(PROD_DB)
    prod_cursor = prod_conn.cursor()
    
    restored = {
        'model_config': 0,
        'provider_registry': 0,
        'task_history': 0,
        'node_registry': 0
    }
    
    # 恢复model_config表数据
    try:
        backup_cursor.execute("SELECT * FROM model_config")
        models = backup_cursor.fetchall()
        for model in models:
            try:
                prod_cursor.execute('''
                    INSERT INTO model_config 
                    (provider, model_id, model_name, model_type, context_window, 
                     max_tokens, pricing, is_free, is_enabled)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    model['provider'], model['model_id'], model['model_name'], 
                    model.get('model_type'), model.get('context_window'),
                    model.get('max_tokens'), model.get('pricing'), 
                    model.get('is_free', 1), model.get('is_enabled', 1)
                ))
                restored['model_config'] += 1
            except Exception as e:
                print(f"跳过模型 {model['provider']}:{model['model_id']}：{str(e)}")
        print(f"成功恢复 {restored['model_config']} 条模型配置")
    except Exception as e:
        print(f"读取备份库model_config失败：{str(e)}")
    
    # 恢复provider_registry表数据
    try:
        backup_cursor.execute("SELECT * FROM provider_registry")
        providers = backup_cursor.fetchall()
        for provider in providers:
            try:
                prod_cursor.execute('''
                    INSERT INTO provider_registry 
                    (provider_code, provider_name, base_url, api_key, is_enabled)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    provider.get('provider_code', provider.get('provider_name')), 
                    provider['provider_name'], provider.get('base_url', provider.get('api_endpoint')),
                    provider.get('api_key'), provider.get('is_enabled', 1)
                ))
                restored['provider_registry'] += 1
            except Exception as e:
                print(f"跳过服务商 {provider.get('provider_name')}：{str(e)}")
        print(f"成功恢复 {restored['provider_registry']} 条服务商配置")
    except Exception as e:
        print(f"读取备份库provider_registry失败：{str(e)}")
    
    prod_conn.commit()
    backup_conn.close()
    prod_conn.close()
    
    print("\n=== 恢复完成 ===")
    for table, count in restored.items():
        print(f"{table}: {count} 条记录")
    print("数据来源：备份库 symphony.db.bak_20260407_1505")

if __name__ == "__main__":
    restore_data()
