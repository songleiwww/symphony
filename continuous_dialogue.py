#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境连续对话模拟器
自动模拟用户对话，持续交互
"""
import sys
import os
import time
import json
from datetime import datetime

# 添加路径
KERNEL_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KERNEL_PATH)

from scheduler import get_scheduler
from flow_executor import get_flow_executor


class ContinuousDialogue:
    """连续对话模拟器"""
    
    def __init__(self):
        self.scheduler = get_scheduler()
        self.flow = get_flow_executor()
        self.conversation_id = None
        self.messages = []
        self.running = False
        self.round = 0
        self.max_rounds = 10
    
    def start(self, max_rounds: int = 10):
        """开始连续对话"""
        self.running = True
        self.round = 0
        self.max_rounds = max_rounds
        self.conversation_id = f"conv_{int(time.time())}"
        
        print("=" * 50)
        print("🔮 序境连续对话模式")
        print("=" * 50)
        print(f"会话ID: {self.conversation_id}")
        print(f"最大轮次: {max_rounds}")
        print("=" * 50)
        print()
        
        # 开始对话
        self.conversation_flow()
    
    def conversation_flow(self):
        """对话流程"""
        # 初始问题
        user_message = "你好，请介绍一下序境系统"
        
        while self.running and self.round < self.max_rounds:
            self.round += 1
            
            print(f"【第{self.round}轮】")
            print(f"👤 用户: {user_message}")
            print()
            
            # 调度官员回复
            result = self.scheduler.dispatch('role-1', [
                {"role": "system", "content": "你是陆念昭，序境少府监。请用友好的方式回复。"},
                {"role": "user", "content": user_message}
            ])
            
            if result.get('status') == 'ok':
                assistant_msg = result.get('response', '')
                print(f"🤖 陆念昭: {assistant_msg[:100]}...")
                print()
                print(f"📊 模型: {result.get('model')} | Tokens: {result.get('usage',{}).get('total_tokens')}")
                print()
                
                # 记录消息
                self.messages.append({
                    'round': self.round,
                    'user': user_message,
                    'assistant': assistant_msg,
                    'model': result.get('model'),
                    'tokens': result.get('usage',{}).get('total_tokens')
                })
                
                # 模拟用户追问(自动生成)
                user_message = self.generate_follow_up(assistant_msg)
                
                if not user_message:
                    print("✅ 对话自然结束")
                    break
                
                print("-" * 30)
                print()
            else:
                print(f"❌ 错误: {result.get('message')}")
                break
        
        self.finish()
    
    def generate_follow_up(self, assistant_msg: str) -> str:
        """根据回复生成追问"""
        # 简单的追问生成逻辑
        follow_ups = [
            "关于这个，你能详细说说吗？",
            "还有其他的吗？",
            "可以举个例子吗？",
            "为什么这么说？",
            "然后呢？",
            "具体怎么做？",
            "有什么优势？",
            "需要注意什么？",
        ]
        
        # 随机选择一个问题
        import random
        return random.choice(follow_ups)
    
    def finish(self):
        """结束对话"""
        self.running = False
        
        print()
        print("=" * 50)
        print("📊 对话统计")
        print("=" * 50)
        print(f"会话ID: {self.conversation_id}")
        print(f"对话轮次: {len(self.messages)}")
        
        total_tokens = sum(m.get('tokens', 0) for m in self.messages)
        print(f"总消耗: {total_tokens} tokens")
        
        print()
        print("明细:")
        for m in self.messages:
            print(f"  {m['round']}. {m['model']} - {m['tokens']} tokens")
        
        # 保存对话记录
        self.save_conversation()
        
        print()
        print("✅ 连续对话完成!")
    
    def save_conversation(self):
        """保存对话记录"""
        save_path = os.path.join(KERNEL_PATH, '..', 'data', 'continuous_dialogues')
        os.makedirs(save_path, exist_ok=True)
        
        file_path = os.path.join(save_path, f"{self.conversation_id}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                'conversation_id': self.conversation_id,
                'rounds': len(self.messages),
                'total_tokens': sum(m.get('tokens', 0) for m in self.messages),
                'messages': self.messages,
                'timestamp': str(datetime.now())
            }, f, ensure_ascii=False, indent=2)
        
        print(f"📝 对话已保存: {file_path}")
    
    def stop(self):
        """停止对话"""
        self.running = False


def start_continuous_dialogue(max_rounds: int = 10):
    """启动连续对话"""
    dialog = ContinuousDialogue()
    dialog.start(max_rounds)


if __name__ == "__main__":
    start_continuous_dialogue(5)
