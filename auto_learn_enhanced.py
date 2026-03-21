# -*- coding: utf-8 -*-
"""
序境系统 - 自动学习模块(增强版)
无需用户确认，自动学习AI相关知识
"""
import sqlite3
import requests
import json
import os
import sys
from datetime import datetime
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')

# 禁用代理
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
memory_path = 'C:/Users/Administrator/.openclaw/workspace/memory/'

# AI学习源(增强版)
LEARNING_SOURCES = [
    {"name": "百度AI", "url": "https://top.baidu.com/board?tab=realtime", "category": "AI趋势"},
    {"name": "36kr AI", "url": "https://www.36kr.com/information/AI/", "category": "AI资讯"},
    {"name": "腾讯AI", "url": "https://new.qq.com/omn/AI.html", "category": "AI动态"},
    {"name": "网易AI", "url": "https://www.163.com/dy/media/TT1493440062/index.html", "category": "AI科技"},
    {"name": "搜狐AI", "url": "https://www.sohu.com/a/ai", "category": "AI前沿"},
]

def fetch_ai_news():
    """抓取AI资讯"""
    print("="*50)
    print("【自动学习：AI知识抓取】")
    print("="*50)
    
    learned = []
    
    for source in LEARNING_SOURCES:
        print(f"\n学习: {source['name']}...")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            resp = requests.get(source['url'], headers=headers, timeout=10)
            
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                titles = []
                
                for selector in ['h3', '.title', '.news-title', 'a.title', '.text-title']:
                    elements = soup.select(selector)[:5]
                    for el in elements:
                        text = el.get_text().strip()
                        if text and len(text) > 5:
                            titles.append(text)
                
                if titles:
                    learned.append({
                        "source": source['name'],
                        "category": source['category'],
                        "topics": titles[:5]
                    })
                    print(f"  ✅ 获取 {len(titles)} 条")
                else:
                    print(f"  ⚠️ 无内容")
            else:
                print(f"  ❌ HTTP {resp.status_code}")
                
        except Exception as e:
            print(f"  ❌ 错误: {str(e)[:30]}")
    
    return learned

def save_to_memory(learned):
    """保存到记忆"""
    today = datetime.now().strftime('%Y-%m-%d')
    memory_file = memory_path + today + '.md'
    
    content = f"\n\n## 自动学习(增强) {datetime.now().strftime('%H:%M')}\n"
    content += "*(无需用户确认自动学习)*\n\n"
    
    for item in learned:
        content += f"### {item['source']} - {item['category']}\n"
        for topic in item['topics']:
            content += f"- {topic}\n"
        content += "\n"
    
    if os.path.exists(memory_file):
        with open(memory_file, 'r', encoding='utf-8') as f:
            existing = f.read()
        with open(memory_file, 'w', encoding='utf-8') as f:
            f.write(existing + content)
    else:
        with open(memory_file, 'w', encoding='utf-8') as f:
            f.write(f"# {today} 记忆\n")
            f.write(content)
    
    print(f"\n✅ 已保存到: {memory_file}")

def model_research():
    """模型自主研究"""
    print("\n" + "="*50)
    print("【自动学习：模型研究】")
    print("="*50)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("SELECT 模型名称, 模型标识符, 服务商 FROM 模型配置表 WHERE 在线状态='online' ORDER BY RANDOM() LIMIT 1")
    model = c.fetchone()
    
    if model:
        print(f"研究模型: {model[0]} ({model[2]})")
        
        research_topics = [
            f"{model[0]}的最新应用场景",
            f"{model[0]}的性能优化方法",
            f"AI Agent最新发展趋势"
        ]
        
        research_record = {
            "time": datetime.now().strftime('%Y-%m-%d %H:%M'),
            "model": model[0],
            "topics": research_topics
        }
        
        print(f"研究主题: {len(research_topics)}个")
        
    conn.close()
    return research_record if model else None

def auto_learn():
    """自动学习主函数"""
    print("="*60)
    print("【序境系统 - 自动学习模块(增强版)】")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    learned = fetch_ai_news()
    
    if learned:
        save_to_memory(learned)
    
    research = model_research()
    
    print("\n" + "="*60)
    print("【自动学习完成】")
    print("="*60)
    print(f"学习源: {len(learned)}个")
    if research:
        print(f"研究模型: {research['model']}")
    print("*(无需用户确认)*")

if __name__ == "__main__":
    auto_learn()
