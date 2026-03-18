#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境调度工作流
通过序境系统调度subagent
"""
import json
from dispatcher import Dispatcher

class Workflow:
    """序境工作流"""
    
    def __init__(self):
        self.dispatcher = Dispatcher()
        self.history = []
        self.streaming_enabled = True  # 流式输出默认启用
    
    def enable_streaming(self):
        """启用流式输出"""
        self.streaming_enabled = True
        print("流式输出已启用")
    
    def disable_streaming(self):
        """禁用流式输出"""
        self.streaming_enabled = False
        print("流式输出已禁用")
    
    def analyze(self, task: str) -> dict:
        """分析任务"""
        roles = self.dispatcher.select_roles_by_task(task)
        return {
            "task": task,
            "matched_roles": len(roles),
            "roles": roles
        }
    
    def dispatch(self, task: str, mode: str = "collab") -> dict:
        """
        调度任务
        mode: collab(协作) / concurrent(并发) / queue(排队)
        """
        analysis = self.analyze(task)
        
        result = {
            "workflow": "序境系统",
            "mode": mode,
            "task": task,
            "streaming": self.streaming_enabled,
            "analysis": analysis,
            "status": "pending_dispatch"
        }
        
        self.history.append(result)
        return result
    
    def get_status(self) -> dict:
        """获取调度状态"""
        return {
            "total_dispatched": len(self.history),
            "modes_used": list(set([h["mode"] for h in self.history]))
        }

if __name__ == "__main__":
    wf = Workflow()
    
    # 演示调度流程
    result = wf.dispatch("分析代码问题", mode="collab")
    print(json.dumps(result, ensure_ascii=False, indent=2))
