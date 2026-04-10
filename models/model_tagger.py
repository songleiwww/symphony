# -*- coding: utf-8 -*-
"""
序境系统 - 模型分类标签模块 v2
为模型添加能力分类标签
"""
import sqlite3

def add_model_tags():
    """为模型添加分类标签"""
    conn = sqlite3.connect('C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db')
    c = conn.cursor()
    
    # 创建模型标签表
    c.execute('''
        CREATE TABLE IF NOT EXISTS 模型标签表 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            模型id TEXT,
            标签 TEXT,
            权重 INTEGER DEFAULT 1,
            创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 定义模型分类规则 - 使用索引位置
    # 列: id, 模型名称, 模型标识, 模型类型, 服务商, API地址, API密钥...
    
    # 获取所有模型
    c.execute('SELECT * FROM 模型配置表')
    rows = c.fetchall()
    
    tagged_count = 0
    for row in rows:
        model_id = row[0]      # id
        model_name = row[1]    # 模型名称
        model标识 = row[2] or ''  # 模型标识
        
        # 根据名称和标识添加标签
        search_text = (model_name + ' ' + model标识).lower()
        
        # 标签规则
        tag_rules = [
            ('code', ['code', 'coder', 'python', 'java', 'coding', '编程']),
            ('chat', ['chat', 'gpt', 'claude', '对话', '聊天']),
            ('reasoning', ['reason', 'think', '推理', 'o1', 'o3', 'r1']),
            ('vision', ['vision', '视觉', 'image', '图片', 'vision']),
            ('math', ['math', '数学', 'math']),
            ('cn', ['cn', 'chinese', '中文', 'glm', '千问', '豆包', 'doubao']),
            ('en', ['llama', 'claude', 'gpt', 'english']),
            ('large', ['70b', '90b', '100b', 'large', 'super']),
            ('small', ['1b', '3b', '7b', '8b', 'small']),
        ]
        
        for tag, keywords in tag_rules:
            for kw in keywords:
                if kw.lower() in search_text:
                    # 检查是否已存在
                    c.execute('SELECT COUNT(*) FROM 模型标签表 WHERE 模型id=? AND 标签=?', 
                             (str(model_id), tag))
                    if c.fetchone()[0] == 0:
                        c.execute('INSERT INTO 模型标签表 (模型id, 标签) VALUES (?, ?)',
                                 (str(model_id), tag))
                        tagged_count += 1
                    break
    
    conn.commit()
    print(f"已添加 {tagged_count} 个标签")
    
    # 显示统计
    c.execute('SELECT 标签, COUNT(*) FROM 模型标签表 GROUP BY 标签')
    print("\n标签统计:")
    for r in c.fetchall():
        print(f"  {r[0]}: {r[1]}")
    
    conn.close()

if __name__ == '__main__':
    add_model_tags()
