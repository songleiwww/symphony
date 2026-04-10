# -*- coding: utf-8 -*-
"""
序境系统 - 故障检测与自动转移模块
实现模型调用失败时的自动故障转移
"""
import sqlite3
import time
from datetime import datetime, timedelta

class FaultDetector:
    """故障检测器"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.failure_threshold = 3  # 连续失败次数阈值
        self.cooldown_seconds = 300  # 冷却时间5分钟
    
    def record_failure(self, model_id, error_type):
        """记录失败"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 创建故障记录表
        c.execute('''
            CREATE TABLE IF NOT EXISTS 模型故障记录 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                模型id TEXT,
                错误类型 TEXT,
                失败次数 INTEGER DEFAULT 1,
                最后失败时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                状态 TEXT DEFAULT 'active'
            )
        ''')
        
        # 检查是否已有记录
        c.execute('SELECT id, 失败次数 FROM 模型故障记录 WHERE 模型id=? AND 状态="active"', 
                 (str(model_id),))
        row = c.fetchone()
        
        if row:
            # 更新失败次数
            new_count = row[1] + 1
            c.execute('UPDATE 模型故障记录 SET 失败次数=?, 最后失败时间=CURRENT_TIMESTAMP WHERE id=?',
                     (new_count, row[0]))
        else:
            # 新增记录
            c.execute('INSERT INTO 模型故障记录 (模型id, 错误类型, 失败次数) VALUES (?, ?, 1)',
                     (str(model_id), error_type))
        
        conn.commit()
        conn.close()
    
    def should_disable(self, model_id):
        """检查模型是否应该被禁用"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''SELECT 失败次数, 最后失败时间 FROM 模型故障记录 
                     WHERE 模型id=? AND 状态="active"''', 
                 (str(model_id),))
        row = c.fetchone()
        
        if not row:
            conn.close()
            return False
        
        failures = row[0]
        last_failure = datetime.fromisoformat(row[1])
        
        # 检查是否超过阈值
        if failures >= self.failure_threshold:
            # 检查是否在冷却期内
            if datetime.now() - last_failure < timedelta(seconds=self.cooldown_seconds):
                conn.close()
                return True
        
        conn.close()
        return False
    
    def find_backup_model(self, original_model_id, preferred_tags=None):
        """查找备份模型"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 获取原始模型的服务商
        c.execute('SELECT 服务商 FROM 模型配置表 WHERE id=?', (str(original_model_id),))
        row = c.fetchone()
        if not row:
            conn.close()
            return None
        
        original_provider = row[0]
        
        # 尝试在同一服务商内找其他模型
        c.execute('''SELECT id, 模型名称 FROM 模型配置表 
                     WHERE 服务商=? AND id != ? AND 是否启用="启用"
                     LIMIT 5''', 
                 (original_provider, str(original_model_id)))
        backups = c.fetchall()
        
        if backups:
            conn.close()
            return backups[0][0]  # 返回第一个备份模型ID
        
        # 跨服务商找模型
        c.execute('''SELECT id, 模型名称 FROM 模型配置表 
                     WHERE id != ? AND 是否启用="启用"
                     LIMIT 5''', 
                 (str(original_model_id),))
        backups = c.fetchall()
        
        conn.close()
        return backups[0][0] if backups else None
    
    def clear_failures(self, model_id):
        """清除故障记录"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('UPDATE 模型故障记录 SET 状态="recovered" WHERE 模型id=?',
                 (str(model_id),))
        conn.commit()
        conn.close()


if __name__ == '__main__':
    detector = FaultDetector('C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db')
    
    # 测试查找备份模型
    backup = detector.find_backup_model(3)
    print(f"模型3的备份: {backup}")
