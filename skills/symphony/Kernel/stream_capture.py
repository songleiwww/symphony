# -*- coding: utf-8 -*-
"""
SSE流式输出捕获模块
实现Server-Sent Events的实时流式输出回??"""

import re
import time
import threading
import json
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class SSECallbackState(Enum):
    IDLE = "idle"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECEIVING = "receiving"
    DISCONNECTED = "disconnected"
    ERROR = "error"


@dataclass
class SSEvent:
    """SSE事件"""
    event_type: str = "message"
    data: str = ""
    id: Optional[str] = None
    retry: Optional[int] = None
    comment: Optional[str] = None
    
    @property
    def is_heartbeat(self) -> bool:
        """判断是否为心跳事??"""
        return self.data == "" and self.event_type == "message"


@dataclass 
class StreamCallbacks:
    """流式输出回调集合"""
    on_start: Optional[Callable[[], None]] = None
    on_message: Optional[Callable[[SSEvent], None]] = None
    on_heartbeat: Optional[Callable[[], None]] = None
    on_error: Optional[Callable[[Exception], None]] = None
    on_end: Optional[Callable[[], None]] = None
    on_reconnect: Optional[Callable[[int], None]] = None


class SSELineParser:
    """SSE行解析器"""
    
    # SSE字段正则
    FIELD_PATTERN = re.compile(r'^([^:]*)(?:: ?(.*))?$')
    
    @staticmethod
    def parse_line(line: str) -> Optional[tuple]:
        """解析单行数据
        Returns: (field, value) or None for empty lines
        """
        line = line.rstrip('\r\n')
        
        if not line:
            return None
            
        # 注释??        if line.startswith(':'):
            return ('_comment', line[1:].strip())
            
        match = SSELineParser.FIELD_PATTERN.match(line)
        if match:
            return (match.group(1), match.group(2) or "")
        return None
    
    @staticmethod
    def parse_event(lines: list) -> SSEvent:
        """解析一个完整事件（一组lines??"""
        event = SSEvent()
        
        for line in lines:
            parsed = SSELineParser.parse_line(line)
            if parsed is None:
                continue
                
            field, value = parsed
            
            if field == '_comment':
                event.comment = value
            elif field == 'event':
                event.event_type = value
            elif field == 'data':
                event.data = value
            elif field == 'id':
                event.id = value
            elif field == 'retry':
                try:
                    event.retry = int(value)
                except ValueError:
                    pass
                    
        return event


class SSEParser:
    """SSE消息解析??"""
    
    # 双换行分隔事??    EVENT_SEPARATOR = re.compile(r'\n\n|\r\n\r\n')
    # 单换行处理field continuation
    TRAILING_SPACE = re.compile(r'[ \t]+$')
    
    def __init__(self):
        self.buffer = ""
        
    def feed(self, chunk: str) -> list:
        """接收数据块，解析并返回事件列??"""
        self.buffer += chunk
        events = []
        
        # 分割事件
        parts = self.EVENT_SEPARATOR.split(self.buffer)
        
        # 最后一个可能是不完整的，留到下??        self.buffer = parts[-1]
        
        for part in parts[:-1]:
            if not part.strip():
                continue
                
            lines = part.split('\n')
            # 处理continuation行（以空格或tab开头）
            merged_lines = []
            for line in lines:
                if line.startswith(' ') or line.startswith('\t'):
                    if merged_lines:
                        merged_lines[-1] += line[1:]
                else:
                    merged_lines.append(line.rstrip('\r'))
                    
            event = SSELineParser.parse_event(merged_lines)
            events.append(event)
            
        return events
        
    def feed_line(self, line: str) -> Optional[SSEvent]:
        """单行输入模式"""
        lines = [line]
        return SSELineParser.parse_event(lines)
    
    def reset(self):
        """重置解析器状??"""
        self.buffer = ""


class StreamCapture:
    """
    SSE流式输出捕获??    支持实时回调、断线重??    """
    
    def __init__(
        self,
        callbacks: Optional[StreamCallbacks] = None,
        heartbeat_interval: float = 15.0,
        max_reconnect_attempts: int = 5,
        reconnect_delay: float = 1.0
    ):
        self.callbacks = callbacks or StreamCallbacks()
        self.heartbeat_interval = heartbeat_interval
        self.max_reconnect_attempts = max_reconnect_attempts
        self.reconnect_delay = reconnect_delay
        
        self.parser = SSEParser()
        self.state = SSECallbackState.IDLE
        self.last_event_id: Optional[str] = None
        self.reconnect_count = 0
        
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
    @property
    def is_connected(self) -> bool:
        return self.state == SSECallbackState.CONNECTED
    
    def _notify_start(self):
        """通知连接开??"""
        if self.callbacks.on_start:
            try:
                self.callbacks.on_start()
            except Exception as e:
                pass
                
    def _notify_message(self, event: SSEvent):
        """通知消息接收"""
        if self.callbacks.on_message:
            try:
                self.callbacks.on_message(event)
            except Exception as e:
                pass
                
    def _notify_heartbeat(self):
        """通知心跳"""
        if self.callbacks.on_heartbeat:
            try:
                self.callbacks.on_heartbeat()
            except Exception:
                pass
                
    def _notify_error(self, error: Exception):
        """通知错误"""
        if self.callbacks.on_error:
            try:
                self.callbacks.on_error(error)
            except Exception:
                pass
                
    def _notify_end(self):
        """通知结束"""
        if self.callbacks.on_end:
            try:
                self.callbacks.on_end()
            except Exception:
                pass
                
    def _notify_reconnect(self, attempt: int):
        """通知重连"""
        if self.callbacks.on_reconnect:
            try:
                self.callbacks.on_reconnect(attempt)
            except Exception:
                pass
    
    def process_chunk(self, chunk: str) -> list:
        """
        处理接收到的数据??        这是外部调用者接收数据后需要调用的方法
        
        Returns: 解析出的事件列表
        """
        events = self.parser.feed(chunk)
        
        for event in events:
            # 更新last_event_id
            if event.id:
                self.last_event_id = event.id
                
            # 心跳事件
            if event.is_heartbeat:
                self._notify_heartbeat()
            else:
                self._notify_message(event)
                
        return events
    
    def process_line(self, line: str) -> Optional[SSEvent]:
        """处理单行数据（实时模式）"""
        event = self.parser.feed_line(line)
        if event:
            if event.id:
                self.last_event_id = event.id
            if event.is_heartbeat:
                self._notify_heartbeat()
            else:
                self._notify_message(event)
        return event
    
    def set_state(self, new_state: SSECallbackState):
        """更新连接状??"""
        with self._lock:
            self.state = new_state
            
    def get_state(self) -> SSECallbackState:
        """获取当前状??"""
        with self._lock:
            return self.state
            
    def should_reconnect(self) -> bool:
        """判断是否应该重连"""
        return (
            self.state == SSECallbackState.DISCONNECTED or
            self.state == SSECallbackState.ERROR
        ) and self.reconnect_count < self.max_reconnect_attempts
    
    def increment_reconnect(self) -> int:
        """增加重连计数"""
        self.reconnect_count += 1
        return self.reconnect_count
        
    def reset_reconnect(self):
        """重置重连计数"""
        self.reconnect_count = 0
        
    def close(self):
        """关闭连接"""
        self._running = False
        self.set_state(SSECallbackState.IDLE)
        self.parser.reset()
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


class ReconnectingSSEClient(StreamCapture):
    """
    支持自动重连的SSE客户??    适用于WebSocket等长连接场景
    """
    
    def __init__(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        callbacks: Optional[StreamCallbacks] = None,
        heartbeat_interval: float = 15.0,
        max_reconnect_attempts: int = 5,
        reconnect_base_delay: float = 1.0,
        reconnect_max_delay: float = 30.0
    ):
        super().__init__(
            callbacks=callbacks,
            heartbeat_interval=heartbeat_interval,
            max_reconnect_attempts=max_reconnect_attempts
        )
        
        self.url = url
        self.headers = headers or {}
        self.reconnect_base_delay = reconnect_base_delay
        self.reconnect_max_delay = reconnect_max_delay
        
        self._stop_event = threading.Event()
        
    def _calculate_delay(self, attempt: int) -> float:
        """计算重连延迟（指数退避）"""
        delay = self.reconnect_base_delay * (2 ** (attempt - 1))
        return min(delay, self.reconnect_max_delay)
        
    def connect(self):
        """建立连接"""
        self.set_state(SSECallbackState.CONNECTING)
        self._notify_start()
        self.set_state(SSECallbackState.CONNECTED)
        self.reset_reconnect()
        
    def disconnect(self):
        """断开连接"""
        self.set_state(SSECallbackState.DISCONNECTED)
        self._notify_end()
        
    def attempt_reconnect(self) -> bool:
        """尝试重连"""
        if not self.should_reconnect():
            return False
            
        attempt = self.increment_reconnect()
        delay = self._calculate_delay(attempt)
        
        self._notify_reconnect(attempt)
        self.set_state(SSECallbackState.CONNECTING)
        
        # 等待延迟
        time.sleep(delay)
        
        self.connect()
        return True
        
    def stop(self):
        """停止客户??"""
        self._stop_event.set()
        self.close()
        

def create_stream_capture(
    on_message: Optional[Callable[[SSEvent], None]] = None,
    on_error: Optional[Callable[[Exception], None]] = None,
    on_heartbeat: Optional[Callable[[], None]] = None
) -> StreamCapture:
    """创建流捕获器的便捷工厂函??"""
    callbacks = StreamCallbacks(
        on_message=on_message,
        on_error=on_error,
        on_heartbeat=on_heartbeat
    )
    return StreamCapture(callbacks=callbacks)


# 示例用法
if __name__ == "__main__":
    import sys
    
    messages = []
    
    def on_message(event: SSEvent):
        print(f"[收到事件] type={event.event_type}, data={event.data[:50] if event.data else '(empty)'}...")
        messages.append(event.data)
        
    def on_heartbeat():
        print("[心跳]")
        
    def on_error(e: Exception):
        print(f"[错误] {e}")
        
    capture = create_stream_capture(
        on_message=on_message,
        on_heartbeat=on_heartbeat,
        on_error=on_error
    )
    
    # 模拟SSE数据
    test_data = """event: message
id: 1
data: {"content": "Hello"}

event: message
id: 2
data: {"content": "World"}

"""
    
    print("=== 测试SSE解析 ===")
    events = capture.process_chunk(test_data)
    print(f"解析??{len(events)} 个事??)
    print(f"消息内容: {messages}")

