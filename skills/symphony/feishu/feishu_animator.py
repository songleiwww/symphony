# -*- coding: utf-8 -*-
"""
飞书动画功能 - Phase 3: 完整动画整合
将Phase 1和Phase 2整合为完整模�?"""

class FeishuAnimator:
    """
    飞书动画�?- 完整�?    整合文本提示和卡片动�?    """
    
    def __init__(self, feishu_client):
        """
        初始化动画器
        :param feishu_client: 飞书消息客户�?        """
        self.client = feishu_client
        self.active_animations = {}
    
    # ==================== 对话动画 ====================
    
    async def animate_thinking(self, receive_id, task_name="处理任务"):
        """
        思考动�?- 发送加载提�?        :param receive_id: 接收者ID
        :param task_name: 任务名称
        :return: message_id 用于后续更新
        """
        # Phase 1: 文本提示
        text_msg = {
            "msg_type": "text",
            "content": {
                "text": f"🔄 正在{task_name}..."
            }
        }
        result = self.client.send(receive_id, text_msg)
        message_id = result.get("message_id")
        
        if message_id:
            self.active_animations[message_id] = {
                "receive_id": receive_id,
                "task_name": task_name,
                "start_time": self._get_timestamp()
            }
        
        return message_id
    
    async def animate_thinking_card(self, receive_id, task_name="处理任务"):
        """
        卡片思考动�?- 使用卡片
        :param receive_id: 接收者ID
        :param task_name: 任务名称
        :return: message_id
        """
        card = {
            "config": {"update_multi": True},
            "header": {
                "template": "blue",
                "title": {
                    "tag": "plain_text",
                    "content": f"🔄 {task_name}"
                }
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": "正在思考中..."}
                },
                {
                    "tag": "div",
                    "text": {"tag": "plain_text", "content": "�?请稍�?}
                }
            ]
        }
        
        result = self.client.send_card(receive_id, card)
        message_id = result.get("message_id")
        
        if message_id:
            self.active_animations[message_id] = {
                "receive_id": receive_id,
                "type": "card",
                "task_name": task_name
            }
        
        return message_id
    
    async def update_to_success(self, message_id, title="完成", content="", receive_id=None):
        """
        更新为成功状�?        :param message_id: 消息ID
        :param title: 标题
        :param content: 内容
        :param receive_id: 接收者ID（可选，用于删除消息�?        """
        # 优先尝试卡片更新
        if message_id in self.active_animations:
            card = {
                "config": {"update_multi": True},
                "header": {
                    "template": "green",
                    "title": {
                        "tag": "plain_text", 
                        "content": f"�?{title}"
                    }
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {"tag": "lark_md", "content": content}
                    }
                ]
            }
            try:
                return self.client.update_card(message_id, card)
            except:
                pass
        
        # 降级：发送新消息
        return self.client.send_text(receive_id, f"�?{title}\n{content}")
    
    async def update_to_error(self, message_id, title="错误", content="", receive_id=None):
        """
        更新为错误状�?        """
        if message_id in self.active_animations:
            card = {
                "config": {"update_multi": True},
                "header": {
                    "template": "red",
                    "title": {
                        "tag": "plain_text",
                        "content": f"�?{title}"
                    }
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {"tag": "lark_md", "content": content}
                    }
                ]
            }
            try:
                return self.client.update_card(message_id, card)
            except:
                pass
        
        return self.client.send_text(receive_id, f"�?{title}\n{content}")
    
    async def update_progress(self, message_id, percent, status=""):
        """
        更新进度
        :param percent: 百分�?0-100
        :param status: 状态描�?        """
        bar = "�? * (percent // 10) + "�? * (10 - percent // 10)
        
        card = {
            "config": {"update_multi": True},
            "header": {
                "template": "blue",
                "title": {
                    "tag": "plain_text",
                    "content": f"📊 进度 {percent}%"
                }
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": f"**进度�?**\n{bar} {percent}%\n\n{status}"}
                }
            ]
        }
        
        return self.client.update_card(message_id, card)
    
    def cleanup(self, message_id):
        """清理动画状�?""
        if message_id in self.active_animations:
            del self.active_animations[message_id]
    
    def _get_timestamp(self):
        """获取时间�?""
        import time
        return int(time.time())


# ==================== 使用示例 ====================

async def example_usage():
    """使用示例"""
    # 1. 初始�?    # client = FeishuClient(app_id, app_secret)
    animator = FeishuAnimator(None)
    
    # 2. 发送思考动�?    # message_id = await animator.animate_thinking_card("ou_xxx", "分析问题")
    
    # 3. 执行任务...
    
    # 4. 更新结果
    # await animator.update_to_success(message_id, "分析完成", "发现3个关键点")
    
    print("Feishu Animator ready!")
    return True


if __name__ == "__main__":
    print("=== Feishu Animation Phase 3 Complete ===")
    example_usage()

