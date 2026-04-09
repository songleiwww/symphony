# -*- coding: utf-8 -*-
"""
FineGrainedWorkflow - 细粒度工作流引擎
========================================
全链路分解 → 验证 → 归一 → 成功

设计原则：
- 思考层：每步推理可验证
- 执行层：每个操作原子化
- 验证层：每步有检查点
- 输出层：归一化+最终验证

防止 token 浪费：按需分配、提前截止、结果导向
"""

import json
import time
import sqlite3
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'


class StepStatus(Enum):
    """步骤状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """工作流步骤 - 原子化操作单元"""
    step_id: str
    step_type: str  # "reasoning" | "tool_call" | "merge" | "verify"
    name: str
    input: Dict[str, Any] = field(default_factory=dict)
    output: Any = None
    status: StepStatus = StepStatus.PENDING
    error: str = None
    latency_ms: int = 0
    token_used: int = 0
    retries: int = 0
    max_retries: int = 3


@dataclass
class WorkflowResult:
    """工作流执行结果"""
    success: bool = False
    output: Any = None
    steps: List[WorkflowStep] = field(default_factory=list)
    total_tokens: int = 0
    total_latency_ms: int = 0
    errors: List[str] = field(default_factory=list)


class FineGrainedWorkflow:
    """
    细粒度工作流引擎
    
    三层架构：
    1. Thinking Layer - 推理分解
    2. Execution Layer - 工具执行
    3. Output Layer - 归一验证
    """
    
    def __init__(self, task: str, config: Dict = None):
        self.task = task
        self.config = config or self._default_config()
        self.steps: List[WorkflowStep] = []
        self.step_handlers = {
            'reasoning': self._think_step,
            'tool_call': self._tool_step,
            'merge': self._merge_step,
            'verify': self._verify_step,
        }
    
    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            'max_tokens_per_step': 2000,
            'max_total_tokens': 10000,
            'timeout_per_step': 30,
            'verify_after_each_step': True,
            'early_stop_on_error': True,
        }
    
    def add_step(self, step_type: str, name: str, input: Dict = None) -> str:
        """添加工作流步骤"""
        step_id = f"step_{len(self.steps) + 1}_{step_type}"
        step = WorkflowStep(
            step_id=step_id,
            step_type=step_type,
            name=name,
            input=input or {}
        )
        self.steps.append(step)
        return step_id
    
    def execute(self) -> WorkflowResult:
        """执行工作流"""
        result = WorkflowResult()
        start_time = time.time()
        
        print(f"[FineGrainedWorkflow] 任务: {self.task}")
        print(f"[FineGrainedWorkflow] 总步骤: {len(self.steps)}")
        
        accumulated_context = {"task": self.task, "history": []}
        
        for i, step in enumerate(self.steps):
            print(f"\n[Step {i+1}] {step.step_type}: {step.name}")
            
            # 超时检查
            elapsed = (time.time() - start_time) * 1000
            if elapsed > self.config.get('timeout_per_step', 30) * 1000:
                step.status = StepStatus.FAILED
                step.error = "Timeout"
                if self.config['early_stop_on_error']:
                    break
            
            # Token 预算检查
            if result.total_tokens > self.config['max_total_tokens']:
                print(f"[TokenBudget] 超过预算 {self.config['max_total_tokens']}，提前截止")
                step.status = StepStatus.SKIPPED
                break
            
            # 执行步骤
            try:
                step_start = time.time()
                step.input['context'] = accumulated_context
                
                handler = self.step_handlers.get(step.step_type)
                if handler:
                    step.output = handler(step)
                    step.status = StepStatus.SUCCESS
                else:
                    step.status = StepStatus.FAILED
                    step.error = f"Unknown step type: {step.step_type}"
                
                step.latency_ms = int((time.time() - step_start) * 1000)
                
                # 更新上下文
                accumulated_context['history'].append({
                    'step': step.name,
                    'output': step.output,
                    'status': step.status.value
                })
                
                # 验证（可选）
                if self.config['verify_after_each_step'] and step.status == StepStatus.SUCCESS:
                    if not self._verify_step_output(step):
                        step.status = StepStatus.FAILED
                        step.error = "Verification failed"
                
                print(f"[Step {i+1}] 状态: {step.status.value}, 耗时: {step.latency_ms}ms")
                
            except Exception as e:
                step.status = StepStatus.FAILED
                step.error = str(e)
                print(f"[Step {i+1}] 错误: {e}")
                
                if self.config['early_stop_on_error']:
                    break
            
            result.steps.append(step)
        
        # 归一化输出
        result.total_latency_ms = int((time.time() - start_time) * 1000)
        result.success = all(s.status == StepStatus.SUCCESS for s in self.steps)
        result.output = self._normalize_output(accumulated_context)
        result.errors = [s.error for s in self.steps if s.error]
        
        print(f"\n[Workflow] 完成: {result.success}, 总耗时: {result.total_latency_ms}ms")
        
        return result
    
    def _think_step(self, step: WorkflowStep) -> str:
        """
        思考步骤 - 分解推理过程
        每步只做一件事，防止 token 浪费
        """
        context = step.input.get('context', {})
        prompt = f"""任务: {context.get('task', '')}

请分解思考这个问题，每步只解决一个小问题：
1. 这个问题需要什么？
2. 有哪些已知条件？
3. 如何验证？

只输出思考步骤，不要多余内容。"""
        
        # 实际调用 LLM（这里用占位）
        return f"[推理] {step.name} 完成"
    
    def _tool_step(self, step: WorkflowStep) -> Any:
        """
        工具步骤 - 原子化执行
        输入 → 工具调用 → 输出验证
        """
        context = step.input.get('context', {})
        tool_name = step.input.get('tool', 'unknown')
        tool_input = step.input.get('input', {})
        
        print(f"[ToolCall] {tool_name}({tool_input})")
        
        # 实际工具调用（集成 MCP 或其他工具）
        # 这里返回占位
        return {"tool": tool_name, "result": "executed"}
    
    def _merge_step(self, step: WorkflowStep) -> Dict:
        """
        合并步骤 - 聚合多个输入
        """
        context = step.input.get('context', {})
        history = context.get('history', [])
        
        return {
            "merged_results": [h.get('output') for h in history],
            "count": len(history)
        }
    
    def _verify_step(self, step: WorkflowStep) -> bool:
        """
        验证步骤 - 检查前序结果
        """
        context = step.input.get('context', {})
        return True  # 占位
    
    def _verify_step_output(self, step: WorkflowStep) -> bool:
        """验证步骤输出"""
        if step.output is None:
            return False
        # 可扩展更多验证逻辑
        return True
    
    def _normalize_output(self, context: Dict) -> Any:
        """归一化输出"""
        history = context.get('history', [])
        if not history:
            return None
        
        # 返回最后一步的成功结果
        for h in reversed(history):
            if h.get('status') == 'success':
                return h.get('output')
        
        return history[-1] if history else None


class WorkflowBuilder:
    """工作流构建器 - 便捷创建工作流"""
    
    @staticmethod
    def text_to_voice_workflow(task: str) -> FineGrainedWorkflow:
        """文字→语音工作流"""
        wf = FineGrainedWorkflow(task)
        
        # 1. 理解任务
        wf.add_step('reasoning', '理解语音任务', {'task': task})
        
        # 2. TTS 合成
        wf.add_step('tool_call', 'TTS合成', {
            'tool': 'edge_tts',
            'input': {'text': task}
        })
        
        # 3. 格式转换
        wf.add_step('tool_call', '转Opus', {
            'tool': 'ffmpeg',
            'input': {'format': 'opus'}
        })
        
        # 4. 发送
        wf.add_step('tool_call', '发送飞书', {
            'tool': 'feishu_send',
            'input': {}
        })
        
        # 5. 归一验证
        wf.add_step('merge', '合并结果', {})
        
        return wf
    
    @staticmethod
    def voice_to_text_workflow(task: str) -> FineGrainedWorkflow:
        """语音→文字工作流"""
        wf = FineGrainedWorkflow(task)
        
        # 1. 接收语音
        wf.add_step('tool_call', '接收语音', {
            'tool': 'feishu_receive',
            'input': {}
        })
        
        # 2. 格式转换
        wf.add_step('tool_call', '转WAV', {
            'tool': 'ffmpeg',
            'input': {'format': 'wav'}
        })
        
        # 3. ASR 识别
        wf.add_step('tool_call', 'Whisper识别', {
            'tool': 'whisper',
            'input': {}
        })
        
        # 4. 验证
        wf.add_step('verify', '验证识别结果', {})
        
        # 5. 归一
        wf.add_step('merge', '合并结果', {})
        
        return wf
    
    @staticmethod
    def code_generation_workflow(task: str) -> FineGrainedWorkflow:
        """代码生成工作流（带自愈）"""
        wf = FineGrainedWorkflow(task)
        
        # 1. 理解需求
        wf.add_step('reasoning', '分析代码需求', {'task': task})
        
        # 2. 生成代码
        wf.add_step('tool_call', '生成代码', {
            'tool': 'llm',
            'input': {'prompt': task, 'max_tokens': 500}
        })
        
        # 3. 验证语法
        wf.add_step('tool_call', '检查语法', {
            'tool': 'syntax_check',
            'input': {}
        })
        
        # 4. 测试执行
        wf.add_step('tool_call', '执行测试', {
            'tool': 'execute',
            'input': {}
        })
        
        # 5. 验证结果
        wf.add_step('verify', '验证输出', {})
        
        # 6. 失败? 重做
        wf.add_step('merge', '最终结果', {})
        
        return wf


# 导出
__all__ = [
    'FineGrainedWorkflow',
    'WorkflowBuilder',
    'WorkflowStep',
    'WorkflowResult',
    'StepStatus'
]
