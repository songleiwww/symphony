#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响模型调用监控集成器
将模型调用自动记录到orchestration_log.json
供symphony.py的监控功能使用
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

# 日志文件路径
LOG_FILE = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\orchestration_log.json"

class OrchestrationMonitor:
    """交响调度监控器"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.log_file = LOG_FILE
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """确保日志文件存在"""
        if not Path(self.log_file).exists():
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False)
    
    def log_dispatch(self, task: str, model: str, status: str = "running", details: str = ""):
        """记录调度事件"""
        events = []
        if Path(self.log_file).exists():
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    events = json.load(f)
            except:
                events = []
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "call" if status == "running" else "complete",
            "workflow": "openclaw_skill",
            "task": task,
            "model": model,
            "status": status,
            "details": details
        }
        events.append(event)
        
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
        
        return event
    
    def log_start(self, task: str, model: str):
        """记录开始调用"""
        return self.log_dispatch(task, model, "running", "模型调用中...")
    
    def log_complete(self, task: str, model: str, success: bool = True, details: str = ""):
        """记录完成"""
        status = "completed" if success else "error"
        return self.log_dispatch(task, model, status, details)
    
    def get_events(self, limit: int = 20) -> list:
        """获取最近的调度事件"""
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                events = json.load(f)
            return events[-limit:] if events else []
        except:
            return []


# 全局实例
_monitor: Optional[OrchestrationMonitor] = None

def get_monitor() -> OrchestrationMonitor:
    """获取监控器实例"""
    global _monitor
    if _monitor is None:
        _monitor = OrchestrationMonitor()
    return _monitor


# 便捷函数
def log_model_call(task: str, model: str):
    """记录模型调用开始"""
    return get_monitor().log_start(task, model)

def log_model_complete(task: str, model: str, success: bool = True, elapsed: float = 0):
    """记录模型调用完成"""
    details = f"成功 | {elapsed:.2f}秒" if success else "失败"
    return get_monitor().log_complete(task, model, success, details)


if __name__ == "__main__":
    # 测试
    print("测试监控器...")
    m = get_monitor()
    
    # 模拟记录
    m.log_start("测试任务", "ark-code-latest")
    time.sleep(1)
    m.log_complete("测试任务", "ark-code-latest", True, "成功 | 1.00秒")
    
    # 读取
    events = m.get_events()
    print(f"记录了 {len(events)} 条事件")
    for e in events[-3:]:
        print(f"  {e['timestamp'][-8:]} | {e['model']} | {e['status']}")
