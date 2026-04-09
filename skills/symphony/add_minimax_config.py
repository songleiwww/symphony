import sys
import os
import sqlite3
sys.path.insert(0, os.path.dirname(__file__))
from db.database import SymphonyDatabase

db = SymphonyDatabase()

# 添加Minimax官方服务商配置
result = db.add_provider(
    provider_code="minimax",
    provider_name="MiniMax AI",
    base_url="https://api.minimax.chat/v1",
    api_key="sk-cp-jLVIwvegv9hZpQwkQsujGrTGbh7MH3vzWEaIt6lNRVhIzeF7l71kZp1ObWs2QCH8HAbLH96SH6EXDxSqMhTX61D9wwGVFdJp6jZwxh94KOHxH1eF-48FiH8",
    is_enabled=True
)

if result:
    print("MiniMax AI服务商配置添加成功！")
    # 查询验证
    conn = db.get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM provider_registry WHERE provider_code=?", ("minimax",))
    provider = dict(cursor.fetchone())
    conn.close()
    print(f"服务商编码：{provider['provider_code']}")
    print(f"服务商名称：{provider['provider_name']}")
    print(f"API网关：{provider['base_url']}")
    print(f"状态：已启用")
    print("API密钥已安全存储到统一密钥管理器，调度时自动读取")
else:
    print("添加失败")
