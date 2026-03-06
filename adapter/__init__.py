#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony 通用适配器层 - v1.0.0
用于与OpenClaw集成的适配器

文件路径: C:\\Users\\Administrator\\.openclaw\\workspace\\skills\\symphony\\adapter\\
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, asdict


# ============================================================
# 1. 事件总线核心 (Event Bus Core)
# ============================================================

class EventBus:
    """事件总线 - 发布/订阅模式"""
    
    def __init__(self):
        self._subscribers: Dict[str, list] = {}
        self._event_history: list = []
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """订阅事件"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def publish(self, event_type: str, data: Dict[str, Any]) -> None:
        """发布事件"""
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "source": "Symphony",
            "timestamp": datetime.now().isoformat(),
            "payload": data
        }
        
        self._event_history.append(event)
        
        # 调用订阅者
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Event callback error: {e}")
    
    def get_history(self, event_type: Optional[str] = None, limit: int = 10) -> list:
        """获取事件历史"""
        if event_type:
            return [e for e in self._event_history if e["event_type"] == event_type][-limit:]
        return self._event_history[-limit:]


# 全局事件总线
_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """获取全局事件总线"""
    return _event_bus


# ============================================================
# 2. OpenClaw适配器 (OpenClaw Adapter)
# ============================================================

class OpenClawAdapter:
    """OpenClaw适配器 - 桥梁模式"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or r"C:\Users\Administrator\.openclaw\openclaw.cherry.json"
        self.event_bus = get_event_bus()
        self._session_context: Dict[str, Any] = {}
    
    def load_config(self) -> Dict[str, Any]:
        """加载OpenClaw配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}
    
    def set_session_context(self, session_id: str, context: Dict[str, Any]) -> None:
        """设置会话上下文"""
        self._session_context[session_id] = context
        self.event_bus.publish("session.context.updated", {
            "session_id": session_id,
            "context": context
        })
    
    def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话上下文"""
        return self._session_context.get(session_id)
    
    def send_to_openclaw(self, message: str, message_type: str = "info") -> bool:
        """发送消息到OpenClaw"""
        self.event_bus.publish(f"openclaw.message.{message_type}", {
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        return True
    
    def validate_input(self, input_data: Dict[str, Any], schema_name: str) -> tuple[bool, Optional[str]]:
        """验证输入（使用JSON Schema）"""
        # 简化验证
        required_fields = {
            "brainstorm": ["topic"],
            "debate": ["topic"],
            "evaluate": ["topic"]
        }
        
        fields = required_fields.get(schema_name, [])
        for field in fields:
            if field not in input_data:
                return False, f"Missing required field: {field}"
        
        return True, None


# ============================================================
# 3. JSON Schema验证器 (Schema Validator)
# ============================================================

class SchemaValidator:
    """JSON Schema验证器"""
    
    def __init__(self):
        self.schemas: Dict[str, Dict] = {}
    
    def load_schema(self, name: str, schema: Dict) -> None:
        """加载Schema"""
        self.schemas[name] = schema
    
    def validate(self, data: Dict, schema_name: str) -> tuple[bool, Optional[str]]:
        """验证数据"""
        if schema_name not in self.schemas:
            return True, None  # 没有Schema则跳过
        
        schema = self.schemas[schema_name]
        properties = schema.get("properties", {})
        
        # 检查必填字段
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                return False, f"Required field missing: {field}"
        
        # 检查类型
        for field, value in data.items():
            if field in properties:
                expected_type = properties[field].get("type")
                if expected_type and not self._check_type(value, expected_type):
                    return False, f"Invalid type for {field}: expected {expected_type}"
        
        return True, None
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """检查类型"""
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        return isinstance(value, type_map.get(expected_type, object))


# ============================================================
# 4. 适配器管理器 (Adapter Manager)
# ============================================================

class AdapterManager:
    """适配器管理器 - 统一入口"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.event_bus = get_event_bus()
        self.openclaw_adapter = OpenClawAdapter()
        self.validator = SchemaValidator()
        self._initialized = True
        
        # 注册默认事件处理器
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """注册默认事件处理器"""
        self.event_bus.subscribe("symphony.start", self._on_symphony_start)
        self.event_bus.subscribe("symphony.complete", self._on_symphony_complete)
        self.event_bus.subscribe("symphony.error", self._on_symphony_error)
    
    def _on_symphony_start(self, event):
        """交响开始事件处理"""
        print(f"🎼 Symphony started: {event['payload'].get('topic')}")
    
    def _on_symphony_complete(self, event):
        """交响完成事件处理"""
        print(f"✅ Symphony completed: {event['payload'].get('summary', '')}")
    
    def _on_symphony_error(self, event):
        """交响错误事件处理"""
        print(f"❌ Symphony error: {event['payload'].get('error')}")
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行适配器流程"""
        # 1. 验证输入
        mode = input_data.get("mode", "brainstorm")
        valid, error = self.validator.validate(input_data, mode)
        if not valid:
            return {"success": False, "error": error}
        
        # 2. 发布开始事件
        self.event_bus.publish("symphony.start", {
            "topic": input_data.get("topic"),
            "mode": mode,
            "timestamp": datetime.now().isoformat()
        })
        
        # 3. 设置会话上下文
        session_id = input_data.get("session_id", str(uuid.uuid4()))
        self.openclaw_adapter.set_session_context(session_id, input_data)
        
        # 4. 返回处理结果
        return {
            "success": True,
            "session_id": session_id,
            "message": "Input validated and processed"
        }


# ============================================================
# 5. 导出接口
# ============================================================

def create_adapter_manager() -> AdapterManager:
    """创建适配器管理器"""
    return AdapterManager()


def get_adapter_manager() -> AdapterManager:
    """获取适配器管理器（单例）"""
    return AdapterManager()


# ============================================================
# 6. 使用示例
# ============================================================

if __name__ == "__main__":
    # 创建适配器管理器
    manager = get_adapter_manager()
    
    # 测试执行
    result = manager.execute({
        "mode": "brainstorm",
        "topic": "测试主题",
        "session_id": "test-001"
    })
    
    print("\n执行结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
