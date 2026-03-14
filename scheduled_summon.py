#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境少府监随机成员召唤 - 计划任务
每10分钟随机召唤一位成员聊天
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import random
import time
import json

# 少府监8位成员
MEMBERS = [
    {"name": "沈清弦", "title": "枢密使", "specialty": "架构设计", "chatTopics": ["系统架构", "设计模式", "技术规划"]},
    {"name": "苏云渺", "title": "工部尚书", "specialty": "代码工程", "chatTopics": ["代码优化", "性能提升", "工程实践"]},
    {"name": "顾清歌", "title": "翰林学士", "specialty": "规则知识", "chatTopics": ["知识库", "规则引擎", "应急处理"]},
    {"name": "沈星衍", "title": "智囊博士", "specialty": "策略规划", "chatTopics": ["AI策略", "任务分配", "智能协调"]},
    {"name": "叶轻尘", "title": "行走使", "specialty": "执行效率", "chatTopics": ["执行进度", "任务状态", "效率优化"]},
    {"name": "林码", "title": "营造司正", "specialty": "工程实现", "chatTopics": ["工程进度", "技术实现", "协作配合"]},
    {"name": "顾至尊", "title": "首辅大学士", "specialty": "统筹协调", "chatTopics": ["资源调配", "进度协调", "整体规划"]},
    {"name": "陆念昭", "title": "少府监", "specialty": "调度管理", "chatTopics": ["成员状态", "任务调度", "系统运行"]},
]

def summon_random_member():
    """随机召唤一位成员"""
    member = random.choice(MEMBERS)
    topic = random.choice(member["chatTopics"])
    
    result = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "member": member,
        "greeting": get_greeting(member, topic)
    }
    return result

def get_greeting(member, topic):
    """生成召唤语"""
    greetings = [
        f"【召唤】{member['title']}{member['name']}，有要事相商！",
        f"【传唤】{member['name']}（{member['title']}）速来！",
        f"【宣】{member['title']}{member['name']}进见！",
    ]
    return random.choice(greetings)

def run_scheduled_task():
    """执行计划任务"""
    result = summon_random_member()
    
    print("=" * 50)
    print(f"⏰ 时间: {result['time']}")
    print(f"\n{result['greeting']}")
    print(f"\n成员: {result['member']['name']}")
    print(f"职务: {result['member']['title']}")
    print(f"专长: {result['member']['specialty']}")
    print(f"话题: {result['member']['chatTopics']}")
    print("=" * 50)
    
    # 保存到日志
    with open('member_summon.log', 'a', encoding='utf-8') as f:
        f.write(f"{result['time']} | {result['member']['name']} | {result['member']['title']}\n")
    
    return result

if __name__ == "__main__":
    print("=== 少府监随机成员召唤 ===")
    run_scheduled_task()
