# -*- coding: utf-8 -*-
"""修复 model_federation.py 的DB schema不匹配问题"""
import re

filepath = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\Kernel\model_federation.py"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix PROVIDER_CONFIG - replace Chinese names with English codes
old_provider_config = '''PROVIDER_CONFIG = {
    "智谱": {
        "priority": 1,
        "max_concurrent": 50,
        "timeout": 60,
        "retry": 2,
        "enabled": True,
        "models": "all"
    },
    "英伟达": {
        "priority": 2,
        "max_concurrent": 50,
        "timeout": 60,
        "retry": 2,
        "enabled": True,
        "models": "all"
    },

    "阿里云百炼": {
        "priority": 4,
        "max_concurrent": 30,
        "timeout": 60,
        "retry": 2,
        "enabled": True,
        "models": "all"
    },
    "英伟达超算": {
        "priority": 5,
        "max_concurrent": 50,
        "timeout": 60,
        "retry": 2,
        "enabled": True,
        "models": "all"
    },
    "火山引擎": {
        "priority": 7,
        "max_concurrent": 20,
        "timeout": 60,
        "retry": 2,
        "enabled": False
    }
}'''

new_provider_config = '''PROVIDER_CONFIG = {
    "aliyun": {
        "priority": 1,
        "max_concurrent": 50,
        "timeout": 60,
        "retry": 2,
        "enabled": True,
        "models": "all"
    },
    "minimax": {
        "priority": 2,
        "max_concurrent": 50,
        "timeout": 60,
        "retry": 2,
        "enabled": True,
        "models": "all"
    },
    "zhipu": {
        "priority": 3,
        "max_concurrent": 50,
        "timeout": 60,
        "retry": 2,
        "enabled": True,
        "models": "all"
    },
    "nvidia": {
        "priority": 4,
        "max_concurrent": 50,
        "timeout": 60,
        "retry": 2,
        "enabled": True,
        "models": "all"
    }
}'''

content = content.replace(old_provider_config, new_provider_config)

# 2. Fix _init_db - simplify to not recreate tables
old_init_db = '''    def _init_db(self):
        """初始化数据库"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(\'\'\'
            CREATE TABLE IF NOT EXISTS model_config (
                id TEXT PRIMARY KEY,
                模型名称 TEXT NOT NULL,
                API地址 TEXT NOT NULL,
                API密钥 TEXT NOT NULL,
                服务商 TEXT NOT NULL,
                在线状态 TEXT DEFAULT 'unknown',
                最大并发 INTEGER DEFAULT 10,
                当前并发 INTEGER DEFAULT 0,
                延迟 REAL DEFAULT 0.0,
                成功率 REAL DEFAULT 1.0,
                最后检查 REAL DEFAULT 0.0,
                容量 INTEGER DEFAULT 100,
                更新时间 REAL DEFAULT 0.0
            )
        \'\'\')
        conn.commit()
        conn.close()'''

new_init_db = '''    def _init_db(self):
        """初始化数据库（symphony.db已通过其他脚本初始化，此处仅确保目录存在）"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)'''

content = content.replace(old_init_db, new_init_db)

# 3. Fix _load_all_models - use correct symphony.db column names
old_load_models = '''    def _load_all_models(self):
        """加载所有模型"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(\'\'\'
            SELECT id, 模型名称, API地址, API密钥, 服务商, 在线状态, 
                   最大并发, 当前并发, 延迟, 成功率, 最后检查, 容量
            FROM model_config
            WHERE 在线状态 IN ("online", "unknown")
        \'\'\')
        rows = c.fetchall()
        for row in rows:
            model = ModelEndpoint(
                id=row[0],
                name=row[1],
                api_url=row[2],
                api_key=row[3],
                provider=row[4],
                online_status=row[5],
                max_concurrent=row[6] or 10,
                current_concurrent=row[7] or 0,
                latency=row[8] or 0.0,
                success_rate=row[9] or 1.0,
                last_check=row[10] or 0.0,
                capacity=row[11] or 100
            )
            if model.provider in self.pools and self.pools[model.provider].enabled:
                self.pools[model.provider].models.append(model)
        conn.close()'''

new_load_models = '''    def _load_all_models(self):
        """加载所有模型（适配symphony.db schema）"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # 正确的symphony.db列名：model_id, model_name, provider
        # api_url和api_key从provider_registry获取
        c.execute(\'\'\'
            SELECT m.model_id, m.model_name, m.provider, m.model_type,
                   p.base_url, p.api_key
            FROM model_config m
            LEFT JOIN provider_registry p ON m.provider = p.provider_code
            WHERE m.is_enabled = 1
        \'\'\')
        rows = c.fetchall()
        for row in rows:
            model_id, model_name, provider, model_type, base_url, api_key = row
            if not provider or provider not in self.pools:
                continue
            pool = self.pools[provider]
            if not pool.enabled:
                continue
            model = ModelEndpoint(
                id=model_id,
                name=model_name,
                api_url=base_url or "",
                api_key=api_key or "",
                provider=provider,
                online_status="unknown",
                max_concurrent=10,
                current_concurrent=0,
                latency=0.0,
                success_rate=1.0,
                last_check=0.0,
                capacity=100
            )
            pool.models.append(model)
        conn.close()'''

content = content.replace(old_load_models, new_load_models)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed model_federation.py")
print("- PROVIDER_CONFIG: Chinese names -> English codes")
print("- _init_db: simplified (no table recreation)")
print("- _load_all_models: fixed column names for symphony.db schema")
