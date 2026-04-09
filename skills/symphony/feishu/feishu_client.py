# -*- coding: utf-8 -*-
"""
飞书客户端模�?
用于实际的飞书消息发�?
"""

import requests
import json
from typing import Dict, Any, Optional

class FeishuClient:
    """
    飞书客户�?
    用于发送消息到飞书
    """
    
    def __init__(self, app_id: str, app_secret: str):
        """
        初始化飞书客户端
        
        Args:
            app_id: 飞书应用ID
            app_secret: 飞书应用密钥
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.token_expire_time = 0
    
    def _get_access_token(self) -> str:
        """
        获取访问令牌
        
        Returns:
            访问令牌
        """
        import time
        current_time = time.time()
        
        # 检查令牌是否有�?
        if self.access_token and current_time < self.token_expire_time:
            return self.access_token
        
        # 获取新令�?
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                self.access_token = result.get("tenant_access_token")
                self.token_expire_time = current_time + result.get("expire", 7200) - 300  # 提前5分钟刷新
                return self.access_token
            else:
                raise Exception(f"获取访问令牌失败: {result.get('msg')}")
                
        except Exception as e:
            raise Exception(f"获取访问令牌失败: {str(e)}")
    
    def send(self, receive_id: str, message: Dict[str, Any], receive_id_type: str = "user_id") -> Dict[str, Any]:
        """
        发送消�?
        
        Args:
            receive_id: 接收者ID
            message: 消息内容
            receive_id_type: 接收者ID类型，默认为user_id
            
        Returns:
            发送结�?
        """
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._get_access_token()}"
        }
        data = {
            "receive_id_type": receive_id_type,
            "receive_id": receive_id,
            **message
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"发送消息失�? {str(e)}")
    
    def send_text(self, receive_id: str, text: str, receive_id_type: str = "user_id") -> Dict[str, Any]:
        """
        发送文本消�?
        
        Args:
            receive_id: 接收者ID
            text: 文本内容
            receive_id_type: 接收者ID类型，默认为user_id
            
        Returns:
            发送结�?
        """
        message = {
            "msg_type": "text",
            "content": json.dumps({"text": text})
        }
        return self.send(receive_id, message, receive_id_type)
    
    def send_card(self, receive_id: str, card: Dict[str, Any], receive_id_type: str = "user_id") -> Dict[str, Any]:
        """
        发送卡片消�?
        
        Args:
            receive_id: 接收者ID
            card: 卡片内容
            receive_id_type: 接收者ID类型，默认为user_id
            
        Returns:
            发送结�?
        """
        message = {
            "msg_type": "interactive",
            "content": json.dumps(card)
        }
        return self.send(receive_id, message, receive_id_type)
    
    def update_card(self, message_id: str, card: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新卡片消息
        
        Args:
            message_id: 消息ID
            card: 卡片内容
            
        Returns:
            更新结果
        """
        url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._get_access_token()}"
        }
        data = {
            "content": json.dumps(card)
        }
        
        try:
            response = requests.patch(url, headers=headers, json=data, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"更新卡片失败: {str(e)}")


class MockFeishuClient:
    """
    模拟飞书客户�?
    用于测试
    """
    
    def __init__(self):
        """
        初始化模拟客户端
        """
        self.messages = []
    
    def send(self, receive_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        模拟发送消�?
        
        Args:
            receive_id: 接收者ID
            message: 消息内容
            
        Returns:
            发送结�?
        """
        self.messages.append({"receive_id": receive_id, "message": message})
        print(f"[模拟] 发送消息到 {receive_id}: {message.get('msg_type')}")
        return {"message_id": f"test_{len(self.messages)}", "code": 0}
    
    def send_text(self, receive_id: str, text: str) -> Dict[str, Any]:
        """
        模拟发送文本消�?
        
        Args:
            receive_id: 接收者ID
            text: 文本内容
            
        Returns:
            发送结�?
        """
        message = {
            "msg_type": "text",
            "content": {"text": text}
        }
        return self.send(receive_id, message)
    
    def send_card(self, receive_id: str, card: Dict[str, Any]) -> Dict[str, Any]:
        """
        模拟发送卡片消�?
        
        Args:
            receive_id: 接收者ID
            card: 卡片内容
            
        Returns:
            发送结�?
        """
        message = {
            "msg_type": "interactive",
            "content": card
        }
        return self.send(receive_id, message)
    
    def update_card(self, message_id: str, card: Dict[str, Any]) -> Dict[str, Any]:
        """
        模拟更新卡片消息
        
        Args:
            message_id: 消息ID
            card: 卡片内容
            
        Returns:
            更新结果
        """
        print(f"[模拟] 更新卡片 {message_id}")
        return {"code": 0}
    
    def get_sent_messages(self) -> list:
        """
        获取已发送的消息
        
        Returns:
            消息列表
        """
        return self.messages

