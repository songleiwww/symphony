# -*- coding: utf-8 -*-
"""
飞书动画模块 - Phase 2: 卡片动态更新
包含完整的消息卡片构建和更新功能
"""

class FeishuAnimation:
    """飞书动画管理器"""
    
    def __init__(self, message_client):
        self.client = message_client
    
    # ==================== 卡片构建 ====================
    
    def create_loading_card(self, title="处理中", content="正在执行任务..."):
        """创建加载中卡片"""
        return {
            "config": {
                "update_multi": True
            },
            "header": {
                "template": "blue",
                "title": {
                    "tag": "plain_text",
                    "content": f"🔄 {title}"
                }
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": content
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "plain_text",
                        "content": "⏳ 请稍候..."
                    }
                }
            ]
        }
    
    def create_success_card(self, title="完成", content=""):
        """创建成功卡片"""
        return {
            "config": {
                "update_multi": True
            },
            "header": {
                "template": "green",
                "title": {
                    "tag": "plain_text",
                    "content": f"✅ {title}"
                }
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": content
                    }
                }
            ]
        }
    
    def create_error_card(self, title="错误", content=""):
        """创建错误卡片"""
        return {
            "config": {
                "update_multi": True
            },
            "header": {
                "template": "red",
                "title": {
                    "tag": "plain_text",
                    "content": f"❌ {title}"
                }
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": content
                    }
                }
            ]
        }
    
    def create_progress_card(self, title="进度", progress=0, content=""):
        """创建进度卡片"""
        # 进度条
        bar_length = 10
        filled = int(bar_length * progress / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        return {
            "config": {
                "update_multi": True
            },
            "header": {
                "template": "blue",
                "title": {
                    "tag": "plain_text",
                    "content": f"📊 {title}"
                }
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**进度:** {bar} {progress}%\n\n{content}"
                    }
                }
            ]
        }
    
    # ==================== 消息操作 ====================
    
    def send_loading_message(self, receive_id):
        """发送加载消息"""
        card = self.create_loading_card()
        return self.client.send_card(receive_id, card)
    
    def update_to_success(self, message_id, title="完成", content=""):
        """更新为成功状态"""
        card = self.create_success_card(title, content)
        return self.client.update_card(message_id, card)
    
    def update_to_error(self, message_id, title="错误", content=""):
        """更新为错误状态"""
        card = self.create_error_card(title, content)
        return self.client.update_card(message_id, card)
    
    def update_progress(self, message_id, progress, content=""):
        """更新进度"""
        card = self.create_progress_card("处理中", progress, content)
        return self.client.update_card(message_id, card)


# ==================== 动画效果 ====================

class AnimationEffects:
    """动画效果库"""
    
    @staticmethod
    def typing_indicator():
        """打字机效果指示器"""
        return {
            "tag": "div",
            "text": {
                "tag": "plain_text",
                "content": "✍️ 正在输入..."
            }
        }
    
    @staticmethod
    def pulse_indicator():
        """脉冲效果指示器"""
        return {
            "tag": "div",
            "text": {
                "tag": "plain_text",
                "content": "💫 处理中"
            }
        }
    
    @staticmethod
    def progress_bar(percent):
        """进度条"""
        bar = "▓" * (percent // 10) + "░" * (10 - percent // 10)
        return {
            "tag": "div",
            "text": {
                "tag": "plain_text",
                "content": f"{bar} {percent}%"
            }
        }


if __name__ == "__main__":
    print("=== Feishu Animation Module Phase 2 ===")
    fa = FeishuAnimation(None)
    print("1. Loading card ready")
    print("2. Success card ready")
    print("3. Error card ready")
    print("4. Progress card ready")
    print("5. Animation effects ready")
