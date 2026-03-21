# -*- coding: utf-8 -*-
"""
序境系统 - 自动学习模块
无需用户确认，自动学习AI相关知识
"""
import sqlite3
import requests
import json
import os
import sys
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')

# 禁用代理
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
memory_path = 'C:/Users/Administrator/.openclaw/workspace/memory/'

def record_token(task_id, model_name, provider, prompt_tokens, completion_tokens, status='success'):
    """记录Token使用到数据库"""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    total = prompt_tokens + completion_tokens
    timestamp = datetime.now().isoformat()
    
    c.execute("""
        INSERT INTO Token使用记录表 
        (task_id, model_name, provider, prompt_tokens, completion_tokens, total_tokens, timestamp, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (task_id, model_name, provider, prompt_tokens, completion_tokens, total, timestamp, status))
    
    conn.commit()
    conn.close()
    print(f"  💾 Token记录: {model_name} | in:{prompt_tokens} out:{completion_tokens} total:{total}")

def call_model_api(model_name, provider, api_key, base_url, messages):
    """调用模型API并返回Token使用"""
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model_name,
            'messages': messages,
            'max_tokens': 2048
        }
        
        start = time.time()
        # 避免重复追加路径
        if base_url.endswith('/chat/completions'):
            api_url = base_url
        else:
            api_url = f"{base_url}/chat/completions"
        
        resp = requests.post(api_url, headers=headers, json=payload, timeout=60)
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            result = resp.json()
            usage = result.get('usage', {})
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            return {
                'status': 'ok',
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'response': result.get('choices', [{}])[0].get('message', {}).get('content', ''),
                'elapsed': elapsed
            }
        else:
            return {
                'status': 'error',
                'error': f'HTTP {resp.status_code}',
                'prompt_tokens': 0,
                'completion_tokens': 0
            }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)[:50],
            'prompt_tokens': 0,
            'completion_tokens': 0
        }

# AI学习源（扩展版 - 2026-03-21）
LEARNING_SOURCES = [
    {"name": "百度AI", "url": "https://top.baidu.com/board?tab=realtime", "category": "AI趋势"},
    {"name": "36kr AI", "url": "https://www.36kr.com/information/AI/", "category": "AI资讯"},
    {"name": "知乎AI", "url": "https://www.zhihu.com/topic/19550517/hot", "category": "AI讨论"},
    {"name": "机器之心", "url": "https://www.jiqizhixin.com/", "category": "AI技术"},
    {"name": "AI Blog", "url": "https://blog.google/technology/ai/", "category": "AI研究"},
    {"name": "腾讯AI", "url": "https://ai.qq.com/", "category": "AI平台"},
    {"name": "网易AI", "url": "https://digi.163.com/", "category": "AI科技"},
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
            # 使用浏览器抓取
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            resp = requests.get(source['url'], headers=headers, timeout=10)
            
            if resp.status_code == 200:
                # 提取标题
                soup = BeautifulSoup(resp.text, 'html.parser')
                titles = []
                
                # 尝试多种选择器
                for selector in ['h3', '.title', '.news-title', 'a.title']:
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

def load_existing_topics():
    """加载已存在的主题，避免重复"""
    existing = set()
    today = datetime.now().strftime('%Y-%m-%d')
    memory_file = memory_path + today + '.md'
    
    if os.path.exists(memory_file):
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 提取已学习的主题
            for line in content.split('\n'):
                if '### ' in line and any(src in line for src in ['36kr', '百度', '知乎']):
                    existing.add(line.strip())
    return existing

def save_to_memory(learned):
    """保存到记忆（去重版）"""
    today = datetime.now().strftime('%Y-%m-%d')
    memory_file = memory_path + today + '.md'
    
    # 加载已存在内容避免重复
    existing_content = ""
    if os.path.exists(memory_file):
        with open(memory_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    
    # 过滤掉已存在的主题
    new_items = []
    for item in learned:
        new_topics = []
        for topic in item['topics']:
            # 检查是否已存在
            if topic not in existing_content:
                new_topics.append(topic)
        
        if new_topics:
            new_items.append({
                "source": item['source'],
                "category": item['category'],
                "topics": new_topics
            })
    
    # 如果没有新内容则不保存
    if not new_items:
        print(f"\n⚠️ 无新内容，跳过保存")
        return
    
    content = f"\n\n## 自动学习 {datetime.now().strftime('%H:%M')}\n"
    content += "*(无需用户确认自动学习)*\n\n"
    
    for item in new_items:
        content += f"### {item['source']} - {item['category']}\n"
        for topic in item['topics']:
            content += f"- {topic}\n"
        content += "\n"
    
    # 追加到记忆文件
    with open(memory_file, 'a', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ 已保存到: {memory_file} ({len(new_items)}条新内容)")

def model_research():
    """模型自主研究"""
    print("\n" + "="*50)
    print("【自动学习：模型研究】")
    print("="*50)
    
    conn = sqlite3.connect(db_path)
    conn.text_factory = str
    c = conn.cursor()
    
    # 优先选火山引擎模型（已测试稳定），排除视频/图像模型
    c.execute("""
        SELECT 模型名称, 模型标识符, 服务商, API地址, API密钥 
        FROM 模型配置表 
        WHERE 在线状态='online' 
        AND 服务商='火山引擎'
        AND 模型名称 NOT LIKE '%Video%' 
        AND 模型名称 NOT LIKE '%Vision%'
        AND 模型名称 NOT LIKE '%VL%'
        AND 模型名称 NOT LIKE '%Image%'
        ORDER BY RANDOM() 
        LIMIT 1
    """)
    model = c.fetchone()
    
    if model:
        model_name = model[0]
        model_id = model[1]
        provider = model[2]
        api_addr = model[3]
        api_key = model[4]
        
        print(f"研究模型: {model_name} ({provider})")
        
        # 研究问题
        research_topics = [
            f"{model_name}的最新应用场景",
            f"{model_name}的性能优化方法",
            f"AI Agent最新发展趋势"
        ]
        
        # 构建消息
        topic_text = "\n".join([f"{i+1}. {t}" for i, t in enumerate(research_topics)])
        messages = [
            {"role": "system", "content": "你是AI助手，请简洁回答以下问题，每个问题不超过100字。"},
            {"role": "user", "content": f"请研究以下AI主题：\n{topic_text}"}
        ]
        
        # 调用模型API
        task_id = f"learn_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if api_addr and api_key:
            result = call_model_api(model_id, provider, api_key, api_addr, messages)
            
            if result['status'] == 'ok':
                # 记录Token
                record_token(
                    task_id, 
                    model_id, 
                    provider, 
                    result['prompt_tokens'], 
                    result['completion_tokens'],
                    'success'
                )
                print(f"  ✅ API调用成功，耗时{result['elapsed']:.2f}s")
            else:
                record_token(task_id, model_id, provider, 0, 0, f'error:{result.get("error","unknown")}')
                print(f"  ❌ API调用失败: {result.get('error','unknown')}")
        else:
            # 模拟Token记录（无API配置时）
            prompt_tokens = random.randint(100, 300)
            completion_tokens = random.randint(200, 500)
            record_token(task_id, model_id, provider, prompt_tokens, completion_tokens, 'simulated')
            print(f"  ⚠️ 无API配置，模拟记录")
        
        # 记录研究主题
        research_record = {
            "time": datetime.now().strftime('%Y-%m-%d %H:%M'),
            "model": model_name,
            "topics": research_topics
        }
        
        print(f"研究主题: {len(research_topics)}个")
        
    else:
        research_record = None
        print("  ⚠️ 无可用模型")
        
    conn.close()
    return research_record

def auto_learn():
    """自动学习主函数"""
    print("="*60)
    print("【序境系统 - 自动学习模块】")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 1. 抓取AI资讯
    learned = fetch_ai_news()
    
    # 2. 保存到记忆
    if learned:
        save_to_memory(learned)
    
    # 3. 模型自主研究
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
