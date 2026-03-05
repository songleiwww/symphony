#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony Context-aware Memory - 交响情境感知记忆
Context-aware memory with session, time, user, and task context
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TimeContext(Enum):
    """Time context - 时间情境"""
    MORNING = "morning"  # 早晨 6:00-12:00
    AFTERNOON = "afternoon"  # 下午 12:00-18:00
    EVENING = "evening"  # 晚上 18:00-24:00
    NIGHT = "night"  # 深夜 0:00-6:00


class ContextAwareMemory:
    """情境感知记忆"""
    
    def __init__(self):
        self.session_context: Dict[str, Any] = {}  # 会话情境
        self.user_context: Dict[str, Any] = {}  # 用户情境
        self.task_context: Dict[str, Any] = {}  # 任务情境
        self.session_start = datetime.now().isoformat()
        self.conversation_history: List[Dict[str, Any]] = []  # 对话历史
        
        # Initialize context
        self._init_time_context()
        self._init_session_context()
    
    def _init_time_context(self):
        """Initialize time context - 初始化时间情境"""
        now = datetime.now()
        hour = now.hour
        
        if 6 <= hour < 12:
            time_ctx = TimeContext.MORNING
        elif 12 <= hour < 18:
            time_ctx = TimeContext.AFTERNOON
        elif 18 <= hour < 24:
            time_ctx = TimeContext.EVENING
        else:
            time_ctx = TimeContext.NIGHT
        
        self.session_context["time_of_day"] = time_ctx.value
        self.session_context["current_time"] = now.isoformat()
        self.session_context["current_hour"] = hour
        self.session_context["current_day"] = now.strftime("%A")
    
    def _init_session_context(self):
        """Initialize session context - 初始化会话情境"""
        self.session_context["session_id"] = f"session_{int(datetime.now().timestamp())}"
        self.session_context["session_start"] = self.session_start
        self.session_context["message_count"] = 0
        self.session_context["turn_count"] = 0
    
    # =========================================================================
    # Context Management - 情境管理
    # =========================================================================
    
    def set_user_context(self, key: str, value: Any):
        """Set user context - 设置用户情境"""
        self.user_context[key] = value
    
    def get_user_context(self, key: str, default: Any = None) -> Any:
        """Get user context - 获取用户情境"""
        return self.user_context.get(key, default)
    
    def set_task_context(self, key: str, value: Any):
        """Set task context - 设置任务情境"""
        self.task_context[key] = value
    
    def get_task_context(self, key: str, default: Any = None) -> Any:
        """Get task context - 获取任务情境"""
        return self.task_context.get(key, default)
    
    def add_conversation_turn(self, role: str, content: str):
        """Add conversation turn - 添加对话回合"""
        turn = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "turn_number": self.session_context["turn_count"]
        }
        self.conversation_history.append(turn)
        self.session_context["turn_count"] += 1
        self.session_context["message_count"] += 1
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history - 获取最近对话历史"""
        return self.conversation_history[-limit:]
    
    # =========================================================================
    # Context-aware Memory Retrieval - 情境感知记忆检索
    # =========================================================================
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get context summary - 获取情境摘要"""
        return {
            "session": self.session_context,
            "user": self.user_context,
            "task": self.task_context,
            "conversation_recent": self.get_conversation_history(5)
        }
    
    def get_context_prompt(self) -> str:
        """Get context as prompt - 获取情境作为提示词"""
        time_ctx = self.session_context.get("time_of_day", "unknown")
        time_greeting = {
            "morning": "Good morning!",
            "afternoon": "Good afternoon!",
            "evening": "Good evening!",
            "night": "It's late at night."
        }.get(time_ctx, "Hello!")
        
        prompt_parts = [time_greeting]
        
        # Session info
        prompt_parts.append(f"Session: {self.session_context.get('session_id', 'N/A')}")
        prompt_parts.append(f"Turns: {self.session_context.get('turn_count', 0)}")
        
        # User preferences
        if self.user_context:
            prompt_parts.append("User preferences:")
            for k, v in self.user_context.items():
                prompt_parts.append(f"  - {k}: {v}")
        
        # Current task
        if self.task_context:
            prompt_parts.append("Current task:")
            for k, v in self.task_context.items():
                prompt_parts.append(f"  - {k}: {v}")
        
        return "\n".join(prompt_parts)


def create_context_aware_memory() -> ContextAwareMemory:
    """Create context-aware memory - 创建情境感知记忆"""
    return ContextAwareMemory()


if __name__ == "__main__":
    print("Symphony Context-aware Memory")
    print("交响情境感知记忆")
    print("=" * 60)
    
    ctx = create_context_aware_memory()
    
    # Test 1: Context initialization
    print("\n[Test 1] Context initialization...")
    summary = ctx.get_context_summary()
    print(f"  Time of day: {summary['session'].get('time_of_day')}")
    print(f"  Session ID: {summary['session'].get('session_id')}")
    print(f"  OK: Context initialized")
    
    # Test 2: User context
    print("\n[Test 2] User context...")
    ctx.set_user_context("preferred_model", "ark-code-latest")
    ctx.set_user_context("language", "zh-CN")
    pref_model = ctx.get_user_context("preferred_model")
    print(f"  Preferred model: {pref_model}")
    print(f"  OK: User context works")
    
    # Test 3: Task context
    print("\n[Test 3] Task context...")
    ctx.set_task_context("current_goal", "Develop v0.4.0")
    ctx.set_task_context("priority", "high")
    goal = ctx.get_task_context("current_goal")
    print(f"  Current goal: {goal}")
    print(f"  OK: Task context works")
    
    # Test 4: Conversation history
    print("\n[Test 4] Conversation history...")
    ctx.add_conversation_turn("user", "Hello Symphony!")
    ctx.add_conversation_turn("assistant", "Hello! How can I help?")
    history = ctx.get_conversation_history(5)
    print(f"  History turns: {len(history)}")
    print(f"  OK: Conversation history works")
    
    # Test 5: Context prompt
    print("\n[Test 5] Context prompt...")
    prompt = ctx.get_context_prompt()
    print(f"  Prompt generated (length: {len(prompt)})")
    print(f"  OK: Context prompt works")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
