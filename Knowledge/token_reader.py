
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any

class TokenManager:
    """Token管理类 - 负责从symphony.db读取和验证Token"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """连接数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
    
    def disconnect(self):
        """断开数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def get_token_usage_records(self, limit: int = 100) -&gt; List[Dict[str, Any]]:
        """
        从Token使用记录表获取记录
        
        Args:
            limit: 返回记录数量限制
            
        Returns:
            Token使用记录列表
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM Token使用记录表 ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        
        records = []
        for row in rows:
            record = dict(row)
            records.append(record)
        
        return records
    
    def get_token_auth_records(self) -&gt; List[Dict[str, Any]]:
        """
        从Token认证表获取记录
        
        Returns:
            Token认证记录列表
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Token认证表 WHERE is_active = 1")
        rows = cursor.fetchall()
        
        records = []
        for row in rows:
            record = dict(row)
            records.append(record)
        
        return records
    
    def verify_token_source(self, token_id: str) -&gt; Dict[str, Any]:
        """
        验证Token来源可靠性
        
        Args:
            token_id: Token ID
            
        Returns:
            验证结果字典
        """
        if not self.conn:
            self.connect()
        
        result = {
            "token_id": token_id,
            "is_valid": False,
            "is_active": False,
            "has_quota": False,
            "source_verified": False,
            "message": ""
        }
        
        # 检查Token认证表
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Token认证表 WHERE token_id = ?", (token_id,))
        row = cursor.fetchone()
        
        if row:
            record = dict(row)
            result["is_valid"] = True
            result["is_active"] = bool(record["is_active"])
            
            # 检查配额
            if record["quota"] &gt; 0:
                result["has_quota"] = record["usage_count"] &lt; record["quota"]
            
            # 检查是否过期
            if record["expires_at"]:
                try:
                    expires_at = datetime.fromisoformat(record["expires_at"])
                    if datetime.now() &lt; expires_at:
                        result["source_verified"] = True
                        result["message"] = "Token来源验证通过"
                    else:
                        result["message"] = "Token已过期"
                except:
                    result["message"] = "Token过期时间格式错误"
            else:
                result["source_verified"] = True
                result["message"] = "Token无过期时间限制"
        else:
            result["message"] = "Token不存在"
        
        return result
    
    def get_model_configs(self, online_only: bool = True) -&gt; List[Dict[str, Any]]:
        """
        获取模型配置
        
        Args:
            online_only: 是否只获取在线模型
            
        Returns:
            模型配置列表
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        if online_only:
            cursor.execute("SELECT * FROM 模型配置表 WHERE 在线状态 = 'online'")
        else:
            cursor.execute("SELECT * FROM 模型配置表")
        
        rows = cursor.fetchall()
        
        configs = []
        for row in rows:
            config = dict(row)
            configs.append(config)
        
        return configs

def main():
    """测试Token管理器"""
    db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
    
    manager = TokenManager(db_path)
    manager.connect()
    
    print("=== Token使用记录 ===")
    usage_records = manager.get_token_usage_records(10)
    for i, record in enumerate(usage_records, 1):
        print(f"{i}. {json.dumps(record, ensure_ascii=False, indent=2)}")
    
    print("\n=== Token认证记录 ===")
    auth_records = manager.get_token_auth_records()
    for i, record in enumerate(auth_records, 1):
        print(f"{i}. {json.dumps(record, ensure_ascii=False, indent=2)}")
    
    print("\n=== 在线模型配置 ===")
    models = manager.get_model_configs(online_only=True)
    print(f"找到 {len(models)} 个在线模型")
    for i, model in enumerate(models[:5], 1):
        print(f"{i}. {model['模型名称']} ({model['服务商']}) - {model['在线状态']}")
    
    manager.disconnect()

if __name__ == "__main__":
    main()

