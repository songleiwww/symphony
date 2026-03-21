# -*- coding: utf-8 -*-
"""
首辅大学士顾至尊 - 序境系统决策机要
阶段一P0任务：统一决策层核心框架

核心职责：
1. Agent任务调度中枢 - 统一入口
2. 整合现有combo_skill/adaptive_combo模块
3. 感知-决策-执行闭环
"""

import json
import time
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DecisionLevel(Enum):
    """决策层级"""
    STRATEGIC = "strategic"     # 战略层 - 大方向
    TACTICAL = "tactical"        # 战术层 - 具体策略
    EXECUTION = "execution"     # 执行层 - 任务执行


class TaskSource(Enum):
    """任务来源"""
    USER = "user"               # 用户输入
    SCHEDULED = "scheduled"      # 定时任务
    WEBHOOK = "webhook"         # Webhook触发
    HEARTBEAT = "heartbeat"     # 心跳触发
    SYSTEM = "system"           # 系统触发


class PerceptionEvent(Enum):
    """感知事件类型"""
    USER_INPUT = "user_input"           # 用户输入
    TASK_COMPLETE = "task_complete"      # 任务完成
    TASK_FAILED = "task_failed"          # 任务失败
    MODULE_STATUS = "module_status"      # 模块状态变化
    HEALTH_ALERT = "health_alert"        # 健康告警
    SCHEDULE_TRIGGER = "schedule_trigger" # 定时触发


@dataclass
class PerceptionData:
    """感知数据"""
    event_type: PerceptionEvent
    source: TaskSource
    content: Any
    context: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class Decision:
    """决策结果"""
    level: DecisionLevel
    action: str
    target: str
    priority: int = 5
    params: Dict = field(default_factory=dict)
    reasoning: str = ""
    confidence: float = 0.8


@dataclass
class ExecutionResult:
    """执行结果"""
    success: bool
    output: Any = None
    error: Optional[str] = None
    metrics: Dict = field(default_factory=dict)
    duration: float = 0


class PerceptionModule:
    """
    感知模块
    负责收集外部输入和内部状态
    """
    
    def __init__(self):
        self.event_history: List[PerceptionData] = []
        self.module_states: Dict[str, Dict] = {}
        self._max_history = 100
    
    def perceive(self, event_type: PerceptionEvent, source: TaskSource, 
                content: Any, context: Dict = None) -> PerceptionData:
        """感知输入"""
        data = PerceptionData(
            event_type=event_type,
            source=source,
            content=content,
            context=context or {},
            timestamp=time.time()
        )
        
        self.event_history.append(data)
        if len(self.event_history) > self._max_history:
            self.event_history.pop(0)
        
        logger.info(f"[感知] {event_type.value} <- {source.value}")
        return data
    
    def update_module_state(self, module_name: str, state: Dict):
        """更新模块状态"""
        self.module_states[module_name] = {
            "state": state,
            "updated_at": time.time()
        }
    
    def get_recent_events(self, event_type: PerceptionEvent = None, 
                         limit: int = 10) -> List[PerceptionData]:
        """获取最近事件"""
        events = self.event_history
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return events[-limit:]


class DecisionModule:
    """
    决策模块
    负责分析感知数据并做出决策
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path
        self.decision_rules: List[Dict] = []
        self.decision_history: List[Decision] = []
        self._load_rules()
    
    def _load_rules(self):
        """加载决策规则"""
        # 从数据库加载
        if self.db_path:
            try:
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                
                # 尝试查找规则表
                c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%规则%'")
                tables = c.fetchall()
                
                if tables:
                    rule_table = tables[0][0]
                    c.execute(f'SELECT * FROM "{rule_table}" LIMIT 20')
                    rules = c.fetchall()
                    
                    for rule in rules:
                        self.decision_rules.append({
                            "id": rule[0] if len(rule) > 0 else "",
                            "name": rule[1] if len(rule) > 1 else "",
                            "content": rule[2] if len(rule) > 2 else "",
                        })
                    
                    logger.info(f"已加载 {len(self.decision_rules)} 条规则")
                
                conn.close()
            except Exception as e:
                logger.warning(f"加载规则失败: {e}")
    
    def decide(self, perception: PerceptionData) -> Decision:
        """决策入口"""
        # 简单规则匹配
        for rule in self.decision_rules:
            if self._match_rule(perception, rule):
                decision = self._apply_rule(perception, rule)
                self.decision_history.append(decision)
                logger.info(f"[决策] {decision.action} -> {decision.target}")
                return decision
        
        # 默认决策
        default = self._default_decision(perception)
        self.decision_history.append(default)
        return default
    
    def _match_rule(self, perception: PerceptionData, rule: Dict) -> bool:
        """匹配规则"""
        # 简单关键词匹配
        content_str = str(perception.content)
        rule_content = rule.get("content", "")
        
        keywords = ["接管", "决策", "调度", "健康", "监控"]
        return any(k in content_str or k in rule_content for k in keywords)
    
    def _apply_rule(self, perception: PerceptionData, rule: Dict) -> Decision:
        """应用规则"""
        return Decision(
            level=DecisionLevel.TACTICAL,
            action="delegate",
            target="adaptive_scheduler",
            reasoning=f"规则匹配: {rule.get('name', '未知')}"
        )
    
    def _default_decision(self, perception: PerceptionData) -> Decision:
        """默认决策"""
        # 根据感知类型决定
        if perception.event_type == PerceptionEvent.USER_INPUT:
            return Decision(
                level=DecisionLevel.EXECUTION,
                action="process_input",
                target="unified_scheduler",
                reasoning="用户输入 -> 统一调度"
            )
        elif perception.event_type == PerceptionEvent.HEALTH_ALERT:
            return Decision(
                level=DecisionLevel.TACTICAL,
                action="handle_alert",
                target="health_monitor",
                reasoning="健康告警 -> 监控处理"
            )
        else:
            return Decision(
                level=DecisionLevel.EXECUTION,
                action="log",
                target="system",
                reasoning="未知事件 -> 记录"
            )


class ExecutionModule:
    """
    执行模块
    负责执行决策并返回结果
    """
    
    def __init__(self):
        self.execution_handlers: Dict[str, Callable] = {}
        self.execution_history: List[ExecutionResult] = []
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """注册默认处理器"""
        self.execution_handlers = {
            "delegate": self._delegate_to_scheduler,
            "process_input": self._process_input,
            "handle_alert": self._handle_alert,
            "log": self._log_event,
        }
    
    def execute(self, decision: Decision, context: Dict = None) -> ExecutionResult:
        """执行入口"""
        start_time = time.time()
        
        handler = self.execution_handlers.get(decision.action)
        if handler:
            try:
                result = handler(decision, context or {})
                result.duration = time.time() - start_time
                self.execution_history.append(result)
                logger.info(f"[执行] {decision.action} -> {'成功' if result.success else '失败'}")
                return result
            except Exception as e:
                result = ExecutionResult(
                    success=False,
                    error=str(e),
                    duration=time.time() - start_time
                )
                self.execution_history.append(result)
                return result
        else:
            return ExecutionResult(
                success=False,
                error=f"未知动作: {decision.action}",
                duration=time.time() - start_time
            )
    
    def _delegate_to_scheduler(self, decision: Decision, context: Dict) -> ExecutionResult:
        """委托给调度器"""
        try:
            from skills.symphony.Kernel.core.unified_scheduler import (
                get_unified_scheduler, 
                DispatchRequest,
                DispatchMode
            )
            
            scheduler = get_unified_scheduler()
            request = DispatchRequest(
                task_type=decision.target,
                complexity=decision.priority,
                keywords=context.get("keywords", []),
                context=context
            )
            
            dispatch_result = scheduler.dispatch(request)
            
            return ExecutionResult(
                success=True,
                output={
                    "model": dispatch_result.primary_model,
                    "mode": dispatch_result.mode.value,
                    "reasoning": dispatch_result.reasoning
                }
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e))
    
    def _process_input(self, decision: Decision, context: Dict) -> ExecutionResult:
        """处理输入"""
        return ExecutionResult(
            success=True,
            output={"status": "input_processed"}
        )
    
    def _handle_alert(self, decision: Decision, context: Dict) -> ExecutionResult:
        """处理告警"""
        return ExecutionResult(
            success=True,
            output={"alert_handled": True}
        )
    
    def _log_event(self, decision: Decision, context: Dict) -> ExecutionResult:
        """记录事件"""
        return ExecutionResult(
            success=True,
            output={"logged": True}
        )


class AgentTaskCoordinator:
    """
    Agent任务调度中枢
    整合感知-决策-执行闭环
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
        
        # 初始化三大模块
        self.perception = PerceptionModule()
        self.decision = DecisionModule(self.db_path)
        self.execution = ExecutionModule()
        
        # 协调状态
        self.coordination_history: List[Dict] = []
        self.is_running = False
        
        logger.info("[首辅] 顾至尊 - 任务调度中枢已初始化")
    
    def process(self, event_type: PerceptionEvent, source: TaskSource,
               content: Any, context: Dict = None) -> ExecutionResult:
        """
        完整的感知-决策-执行闭环
        
        Args:
            event_type: 感知事件类型
            source: 任务来源
            content: 输入内容
            context: 上下文
        
        Returns:
            执行结果
        """
        # 阶段1: 感知
        perception_data = self.perception.perceive(event_type, source, content, context)
        
        # 阶段2: 决策
        decision = self.decision.decide(perception_data)
        
        # 阶段3: 执行
        result = self.execution.execute(decision, context or {})
        
        # 记录协调历史
        self.coordination_history.append({
            "timestamp": time.time(),
            "event": event_type.value,
            "decision": decision.action,
            "success": result.success
        })
        
        return result
    
    def get_status(self) -> Dict:
        """获取协调器状态"""
        return {
            "is_running": self.is_running,
            "perception_events": len(self.perception.event_history),
            "module_states": len(self.perception.module_states),
            "decisions": len(self.decision.decision_history),
            "executions": len(self.execution.execution_history),
            "coordination_rounds": len(self.coordination_history)
        }
    
    def get_health_summary(self) -> Dict:
        """获取健康摘要"""
        recent = self.coordination_history[-10:] if self.coordination_history else []
        success_count = sum(1 for r in recent if r.get("success"))
        
        return {
            "total_rounds": len(self.coordination_history),
            "recent_success_rate": success_count / len(recent) if recent else 0,
            "module_status": {
                "perception": "healthy",
                "decision": "healthy" if self.decision.decision_rules else "limited",
                "execution": "healthy"
            }
        }


# 全局协调器实例
_coordinator: Optional[AgentTaskCoordinator] = None


def get_coordinator(db_path: str = None) -> AgentTaskCoordinator:
    """获取全局协调器"""
    global _coordinator
    if _coordinator is None:
        _coordinator = AgentTaskCoordinator(db_path)
    return _coordinator


def process_task(event_type: PerceptionEvent, source: TaskSource,
                content: Any, context: Dict = None) -> ExecutionResult:
    """便捷任务处理函数"""
    coordinator = get_coordinator()
    return coordinator.process(event_type, source, content, context)


# 导出
__all__ = [
    'DecisionLevel',
    'TaskSource',
    'PerceptionEvent',
    'PerceptionData',
    'Decision',
    'ExecutionResult',
    'PerceptionModule',
    'DecisionModule',
    'ExecutionModule',
    'AgentTaskCoordinator',
    'get_coordinator',
    'process_task'
]


# 测试
if __name__ == '__main__':
    print("=== 首辅大学士顾至尊 - 决策机要测试 ===\n")
    
    # 初始化
    coordinator = get_coordinator()
    print(f"协调器状态: {coordinator.get_status()}\n")
    
    # 测试场景1: 用户输入
    print("--- 场景1: 用户输入 ---")
    result = process_task(
        event_type=PerceptionEvent.USER_INPUT,
        source=TaskSource.USER,
        content="帮我分析序境系统性能",
        context={"keywords": ["分析", "性能"]}
    )
    print(f"结果: success={result.success}, output={result.output}")
    
    # 测试场景2: 健康告警
    print("\n--- 场景2: 健康告警 ---")
    result = process_task(
        event_type=PerceptionEvent.HEALTH_ALERT,
        source=TaskSource.SYSTEM,
        content={"alert": "cpu_high", "value": 95},
        context={}
    )
    print(f"结果: success={result.success}, output={result.output}")
    
    # 最终状态
    print(f"\n最终状态: {coordinator.get_status()}")
    print(f"健康摘要: {coordinator.get_health_summary()}")
