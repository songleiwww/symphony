#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境少府监协作系统
包含：协作能力、心情愉悦、文化氛围、智能协调
"""
import json
from threading import Lock
from enum import Enum
from typing import Dict, List, Optional
import time

# ==================== 枚举定义 ====================

class MemberStatus(Enum):
    ONLINE = "在线"
    BUSY = "忙碌"
    AWAY = "离开"
    OFFLINE = "离线"

class AchievementType(Enum):
    TASK_COMPLETE = "任务完成"
    HELP_COLLEAGUE = "帮助同事"
    INNOVATION = "创新贡献"
    MILESTONE = "里程碑"

# ==================== 协作系统类 ====================

class CommunicationSystem:
    """通信机制"""
    def __init__(self):
        self.channels = {
            'general': [],
            'urgent': [],
            'casual': []
        }
        self.lock = Lock()
    
    def send_message(self, channel: str, sender: str, message: str) -> bool:
        with self.lock:
            if channel in self.channels:
                self.channels[channel].append({
                    'sender': sender,
                    'message': message,
                    'timestamp': time.time()
                })
                return True
            return False
    
    def get_messages(self, channel: str, limit: int = 10) -> List:
        with self.lock:
            return self.channels.get(channel, [])[-limit:]


class MoodSystem:
    """心情愉悦系统"""
    def __init__(self):
        self.achievements = []
        self.compliments = []
        self.breaks_count = 0
        self.total_breaks = 0
        self.mood_score = 100  # 0-100
        self.lock = Lock()
    
    def add_achievement(self, member: str, achievement: str, points: int = 10):
        with self.lock:
            self.achievements.append({
                'member': member,
                'achievement': achievement,
                'points': points,
                'timestamp': time.time()
            })
            self.mood_score = min(100, self.mood_score + points)
    
    def compliment(self, from_member: str, to_member: str, message: str):
        with self.lock:
            self.compliments.append({
                'from': from_member,
                'to': to_member,
                'message': message,
                'timestamp': time.time()
            })
            self.mood_score = min(100, self.mood_score + 2)
    
    def remind_break(self):
        with self.lock:
            self.breaks_count += 1
            self.total_breaks += 1
            return f"休息提醒：您已连续工作{self.breaks_count}小时，请适当休息！"
    
    def reset_breaks(self):
        with self.lock:
            self.breaks_count = 0
    
    def get_mood_score(self) -> int:
        return self.mood_score


class CultureSystem:
    """文化氛围系统"""
    def __init__(self):
        self.slogan = "文韵千年，匠心筑梦"
        self.honor_board = []
        self.events = []
        self.lock = Lock()
    
    def add_to_honor(self, member: str, reason: str):
        with self.lock:
            self.honor_board.append({
                'member': member,
                'reason': reason,
                'timestamp': time.time()
            })
    
    def add_event(self, event_name: str):
        with self.lock:
            self.events.append({
                'name': event_name,
                'timestamp': time.time()
            })
    
    def get_slogan(self) -> str:
        return self.slogan


class SmartCoordinator:
    """智能协调系统"""
    def __init__(self):
        self.member_capabilities = {}
        self.task_queue = []
        self.lock = Lock()
    
    def register_member(self, member: str, capability: int):
        with self.lock:
            self.member_capabilities[member] = capability
    
    def assign_task(self, task: str, required_capability: int) -> Optional[str]:
        with self.lock:
            # 能力匹配：选择能力最强的成员
            best_member = None
            best_cap = 0
            for member, cap in self.member_capabilities.items():
                if cap >= required_capability and cap > best_cap:
                    best_member = member
                    best_cap = cap
            
            if best_member:
                self.task_queue.append({
                    'task': task,
                    'assigned_to': best_member,
                    'timestamp': time.time()
                })
                return best_member
            return None
    
    def get_load_balance(self) -> Dict:
        with self.lock:
            task_count = {}
            for t in self.task_queue:
                member = t['assigned_to']
                task_count[member] = task_count.get(member, 0) + 1
            return task_count


class CollaborationHub:
    """协作中心 - 整合所有协作功能"""
    def __init__(self):
        self.communication = CommunicationSystem()
        self.mood = MoodSystem()
        self.culture = CultureSystem()
        self.coordinator = SmartCoordinator()
        self.member_status = {}
        self.lock = Lock()
        
        # 初始化成员状态
        self.member_status = {
            '沈清弦': MemberStatus.ONLINE,
            '苏云渺': MemberStatus.ONLINE,
            '顾清歌': MemberStatus.ONLINE,
            '沈星衍': MemberStatus.ONLINE,
            '叶轻尘': MemberStatus.ONLINE,
            '林码': MemberStatus.ONLINE,
            '顾至尊': MemberStatus.ONLINE,
            '陆念昭': MemberStatus.ONLINE,
        }
        
        # 注册成员能力
        for member in self.member_status:
            self.coordinator.register_member(member, capability=80)
    
    def set_status(self, member: str, status: MemberStatus):
        with self.lock:
            if member in self.member_status:
                self.member_status[member] = status
    
    def get_status(self, member: str) -> Optional[MemberStatus]:
        return self.member_status.get(member)
    
    def get_all_status(self) -> Dict:
        return {m: s.value for m, s in self.member_status.items()}
    
    def send_greeting(self, member: str):
        """成员加入时的欢迎"""
        greeting = f"欢迎{member}加入少府监！"
        self.communication.send_message('general', 'System', greeting)
        self.culture.add_event(f"成员加入: {member}")
    
    def celebrate_achievement(self, member: str, achievement: str):
        """庆祝成就"""
        self.mood.add_achievement(member, achievement, points=10)
        self.culture.add_to_honor(member, achievement)
        msg = f"🎉 恭喜{member}获得成就：{achievement}！"
        self.communication.send_message('general', 'System', msg)
    
    def give_compliment(self, from_member: str, to_member: str, message: str):
        """赞美同事"""
        self.mood.compliment(from_member, to_member, message)
        msg = f"💬 {from_member}赞美{to_member}：{message}"
        self.communication.send_message('general', 'System', msg)
    
    def check_break(self):
        """检查休息"""
        reminder = self.mood.remind_break()
        self.communication.send_message('general', 'System', reminder)
        return reminder
    
    def get_summary(self) -> Dict:
        """获取协作系统摘要"""
        return {
            'slogan': self.culture.get_slogan(),
            'mood_score': self.mood.get_mood_score(),
            'achievements_count': len(self.mood.achievements),
            'compliments_count': len(self.mood.compliments),
            'honor_board_count': len(self.culture.honor_board),
            'member_status': self.get_all_status()
        }


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=== 少府监协作系统 ===\n")
    
    hub = CollaborationHub()
    
    # 测试欢迎
    print("1. 成员加入")
    hub.send_greeting("新成员测试")
    
    # 测试成就
    print("\n2. 成就庆祝")
    hub.celebrate_achievement("沈清弦", "完成重要架构设计")
    
    # 测试赞美
    print("\n3. 同事赞美")
    hub.give_compliment("苏云渺", "顾清歌", "规则设计非常专业！")
    
    # 测试休息提醒
    print("\n4. 休息提醒")
    print(hub.check_break())
    
    # 测试状态查询
    print("\n5. 成员状态")
    for member, status in hub.get_all_status().items():
        print(f"  {member}: {status}")
    
    # 获取摘要
    print("\n6. 系统摘要")
    summary = hub.get_summary()
    print(f"  口号: {summary['slogan']}")
    print(f"  心情指数: {summary['mood_score']}")
    print(f"  成就数: {summary['achievements_count']}")
    print(f"  赞美数: {summary['compliments_count']}")
    
    print("\n=== 协作系统测试通过 ===")
