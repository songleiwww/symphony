#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境3.0 标准化IPC通信协议
=============================
模块间进程通信的核心数据结构与协议定义

作者：少府监·首辅大学士 顾至尊
版本：3.0.0
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Dict
import uuid
import time


class MessageType(Enum):
    """
    消息类型枚举
    定义四种基础消息类型用于不同通信场景
    """
    REQUEST = "request"    # 请求消息：需要对方响应的调用
    RESPONSE = "response"  # 响应消息：对请求的答复
    EVENT = "event"        # 事件消息：单向通知，无需响应
    ERROR = "error"        # 错误消息：通信过程中出现的异常


class MessagePriority(Enum):
    """
    消息优先级枚举
    用于消息队列排序和调度
    """
    LOW = 0      # 低优先级：后台任务、日志等
    NORMAL = 1   # 普通优先级：常规业务逻辑
    HIGH = 2     # 高优先级：重要回调、紧急通知
    CRITICAL = 3 # 紧急优先级：系统致命错误、需要立即处理


@dataclass
class IPCMessage:
    """
    IPC通信消息数据结构
    ====================
    统一的消息格式，用于所有模块间的通信
    
    属性说明：
        msg_type: 消息类型（REQUEST/RESPONSE/EVENT/ERROR）
        id: 全局唯一消息ID，用于消息追踪和关联
        sender: 发送方模块名称
        receiver: 接收方模块名称
        action: 操作名称/方法名
        payload: 消息载荷，携带业务数据
        timestamp: 时间戳（毫秒）
        priority: 消息优先级
        correlation_id: 关联ID，用于关联请求与响应
        metadata: 扩展元数据
        error_code: 错误码（仅ERROR类型使用）
        error_message: 错误描述（仅ERROR类型使用）
    """
    msg_type: MessageType
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    receiver: str = ""
    action: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: time.time() * 1000)
    priority: MessagePriority = MessagePriority.NORMAL
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """
        初始化后的校验与自动处理
        确保消息ID和关联ID的正确性
        """
        # 如果是响应消息，自动填充关联ID
        if self.msg_type == MessageType.RESPONSE and not self.correlation_id:
            self.correlation_id = self.id
    
    def to_dict(self) -> Dict[str, Any]:
        """
        序列化消息为字典
        
        返回：
            包含所有消息字段的字典
        """
        return {
            "msg_type": self.msg_type.value,
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "action": self.action,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "priority": self.priority.value,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata,
            "error_code": self.error_code,
            "error_message": self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IPCMessage":
        """
        从字典反序列化消息
        
        参数：
            data: 包含消息数据的字典
            
        返回：
            IPCMessage实例
        """
        return cls(
            msg_type=MessageType(data.get("msg_type", "request")),
            id=data.get("id", str(uuid.uuid4())),
            sender=data.get("sender", ""),
            receiver=data.get("receiver", ""),
            action=data.get("action", ""),
            payload=data.get("payload", {}),
            timestamp=data.get("timestamp", time.time() * 1000),
            priority=MessagePriority(data.get("priority", 1)),
            correlation_id=data.get("correlation_id"),
            metadata=data.get("metadata", {}),
            error_code=data.get("error_code"),
            error_message=data.get("error_message")
        )
    
    def create_response(self, payload: Optional[Dict[str, Any]] = None, 
                        success: bool = True) -> "IPCMessage":
        """
        创建响应消息
        
        参数：
            payload: 响应载荷
            success: 是否成功处理
            
        返回：
            新的IPCMessage实例作为响应
        """
        response_data = payload if payload is not None else {}
        
        if not success:
            return IPCMessage(
                msg_type=MessageType.ERROR,
                sender=self.receiver,
                receiver=self.sender,
                action=self.action,
                payload=response_data,
                correlation_id=self.id,
                error_code="PROCESSING_ERROR",
                error_message=response_data.get("error", "Unknown error")
            )
        
        return IPCMessage(
            msg_type=MessageType.RESPONSE,
            sender=self.receiver,
            receiver=self.sender,
            action=self.action,
            payload=response_data,
            correlation_id=self.id
        )
    
    def is_request(self) -> bool:
        """判断是否为请求消息"""
        return self.msg_type == MessageType.REQUEST
    
    def is_response(self) -> bool:
        """判断是否为响应消息"""
        return self.msg_type == MessageType.RESPONSE
    
    def is_event(self) -> bool:
        """判断是否为事件消息"""
        return self.msg_type == MessageType.EVENT
    
    def is_error(self) -> bool:
        """判断是否为错误消息"""
        return self.msg_type == MessageType.ERROR


def create_request(sender: str, receiver: str, action: str, 
                   payload: Optional[Dict[str, Any]] = None,
                   priority: MessagePriority = MessagePriority.NORMAL) -> IPCMessage:
    """
    快速创建请求消息的工厂函数
    
    参数：
        sender: 发送方模块名
        receiver: 接收方模块名
        action: 操作名称
        payload: 请求载荷
        priority: 消息优先级
        
    返回：
        配置好的IPCMessage实例
    """
    return IPCMessage(
        msg_type=MessageType.REQUEST,
        sender=sender,
        receiver=receiver,
        action=action,
        payload=payload or {},
        priority=priority
    )


def create_response(request: IPCMessage, payload: Optional[Dict[str, Any]] = None,
                   success: bool = True) -> IPCMessage:
    """
    快速创建响应消息的工厂函数
    
    参数：
        request: 原始请求消息
        payload: 响应载荷
        success: 是否成功
        
    返回：
        响应IPCMessage实例
    """
    return request.create_response(payload, success)


def create_event(sender: str, receiver: str, action: str,
                payload: Optional[Dict[str, Any]] = None,
                priority: MessagePriority = MessagePriority.NORMAL) -> IPCMessage:
    """
    快速创建事件消息的工厂函数
    
    参数：
        sender: 发送方模块名
        receiver: 接收方模块名（可为空表示广播）
        action: 事件名称
        payload: 事件载荷
        priority: 消息优先级
        
    返回：
        事件IPCMessage实例
    """
    return IPCMessage(
        msg_type=MessageType.EVENT,
        sender=sender,
        receiver=receiver,
        action=action,
        payload=payload or {},
        priority=priority
    )


def create_error(sender: str, receiver: str, error_code: str, 
                error_message: str, action: str = "",
                payload: Optional[Dict[str, Any]] = None) -> IPCMessage:
    """
    快速创建错误消息的工厂函数
    
    参数：
        sender: 发送方模块名
        receiver: 接收方模块名
        error_code: 错误码
        error_message: 错误描述
        action: 关联的操作名称
        payload: 额外的错误数据
        
    返回：
        错误IPCMessage实例
    """
    return IPCMessage(
        msg_type=MessageType.ERROR,
        sender=sender,
        receiver=receiver,
        action=action,
        payload=payload or {},
        error_code=error_code,
        error_message=error_message,
        priority=MessagePriority.HIGH
    )


# 错误码常量定义
class ErrorCode:
    """标准错误码定义"""
    UNKNOWN = "UNKNOWN"
    TIMEOUT = "TIMEOUT"
    MODULE_NOT_FOUND = "MODULE_NOT_FOUND"
    ACTION_NOT_FOUND = "ACTION_NOT_FOUND"
    INVALID_PAYLOAD = "INVALID_PAYLOAD"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    PROCESSING_ERROR = "PROCESSING_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    SERIALIZATION_ERROR = "SERIALIZATION_ERROR"


# 预定义操作常量
class SystemAction:
    """系统级操作名称"""
    PING = "system.ping"
    PONG = "system.pong"
    HEALTH_CHECK = "system.health_check"
    REGISTER_MODULE = "system.register_module"
    UNREGISTER_MODULE = "system.unregister_module"
    GET_MODULES = "system.get_modules"
    SHUTDOWN = "system.shutdown"
