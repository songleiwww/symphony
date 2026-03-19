# -*- coding: utf-8 -*-
"""
接管历史记录管理
记录每次接管的详细信息，实现状态持续化
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

HISTORY_FILE = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\takeover_history.json'

def load_history() -> List[Dict]:
    """加载接管历史"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_history(history: List[Dict]):
    """保存接管历史"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def add_takeover_record(
    user_message: str, 
    intent: str, 
    status: str = "success",
    response_length: int = 0
) -> Dict:
    """
    添加接管记录
    
    参数:
        user_message: 用户原始消息
        intent: 识别到的意图
        status: 处理状态
        response_length: 响应长度
    
    返回:
        记录字典
    """
    history = load_history()
    
    record = {
        "id": len(history) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_message": user_message[:100],  # 截取前100字符
        "intent": intent,
        "status": status,
        "response_length": response_length
    }
    
    history.append(record)
    save_history(history)
    
    return record

def get_recent_takeovers(limit: int = 10) -> List[Dict]:
    """获取最近的接管记录"""
    history = load_history()
    return history[-limit:] if history else []

def get_today_count() -> int:
    """获取今日接管次数"""
    today = datetime.now().strftime("%Y-%m-%d")
    history = load_history()
    count = 0
    for record in history:
        if record.get("timestamp", "").startswith(today):
            count += 1
    return count

def clear_history():
    """清空历史记录"""
    save_history([])

if __name__ == '__main__':
    # 测试
    print("=== 接管历史测试 ===")
    print(f"今日接管次数: {get_today_count()}")
    print(f"\n最近接管记录:")
    for r in get_recent_takeovers(5):
        print(f"  [{r['timestamp']}] {r['intent']} - {r['status']}")
