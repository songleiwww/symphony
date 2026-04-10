# -*- coding: utf-8 -*-
"""
序境系统 - 实时进度反馈模块
模型执行过程中可中途发送进度到对话框
"""
import time
import threading
from typing import Dict, List, Optional, Callable
from enum import Enum

class ProgressStage(Enum):
    """任务执行阶段"""
    START = "开始"
    ANALYZING = "分析中"
    DISPATCHING = "调度模型"
    EXECUTING = "执行中"
    PARTIAL_RESULT = "部分完成"
    AGGREGATING = "聚合结果"
    COMPLETED = "完成"
    FAILED = "失败"

class ProgressReporter:
    """
    进度报告器
    
    功能:
    1. 实时报告任务执行进度
    2. 支持多阶段进度更新
    3. 可配置回调函数(飞书/日志等)
    4. 支持进度历史记录
    """
    
    def __init__(self, user_id: str = None, callback: Callable = None):
        self.user_id = user_id
        self.callback = callback  # 回调函数，用于发送消息
        self.progress_history = []
        self.current_stage = None
        self.start_time = None
        self._lock = threading.Lock()
    
    def start_task(self, task_name: str, total_steps: int = 5) -> str:
        """开始任务"""
        self.start_time = time.time()
        self.total_steps = total_steps
        self.task_id = f"task_{int(self.start_time * 1000)}"
        
        self._report(
            stage=ProgressStage.START,
            message=f"🚀 任务开始: {task_name}",
            progress=0,
            details={"task_id": self.task_id, "total_steps": total_steps}
        )
        
        return self.task_id
    
    def update_progress(self, stage: ProgressStage, message: str, 
                       progress: float = None, details: Dict = None):
        """更新进度"""
        if progress is None:
            progress = self._calculate_progress(stage)
        
        self._report(stage, message, progress, details)
    
    def _calculate_progress(self, stage: ProgressStage) -> float:
        """计算进度百分比"""
        stage_order = [
            ProgressStage.START,
            ProgressStage.ANALYZING,
            ProgressStage.DISPATCHING,
            ProgressStage.EXECUTING,
            ProgressStage.PARTIAL_RESULT,
            ProgressStage.AGGREGATING,
            ProgressStage.COMPLETED
        ]
        
        try:
            idx = stage_order.index(stage)
            return (idx + 1) / len(stage_order) * 100
        except:
            return 50.0
    
    def _report(self, stage: ProgressStage, message: str, 
               progress: float, details: Dict = None):
        """发送进度报告"""
        with self._lock:
            self.current_stage = stage
            
            report = {
                "task_id": self.task_id,
                "stage": stage.value,
                "message": message,
                "progress": progress,
                "details": details or {},
                "timestamp": time.time()
            }
            
            self.progress_history.append(report)
            
            # 调用回调函数
            if self.callback:
                try:
                    self.callback(report)
                except Exception as e:
                    print(f"进度报告回调失败: {e}")
    
    def report_model_start(self, model_name: str, provider: str):
        """报告模型开始执行"""
        self.update_progress(
            ProgressStage.EXECUTING,
            f"🔄 调用模型: {model_name} ({provider})",
            details={"model": model_name, "provider": provider}
        )
    
    def report_model_result(self, model_name: str, success: bool, 
                          latency: float = None, tokens: int = None):
        """报告模型执行结果"""
        if success:
            msg = f"✅ {model_name} 执行成功"
            if latency:
                msg += f" ({latency:.2f}s)"
            if tokens:
                msg += f" - {tokens} tokens"
        else:
            msg = f"❌ {model_name} 执行失败"
        
        self.update_progress(
            ProgressStage.EXECUTING,
            msg,
            details={"model": model_name, "success": success, 
                    "latency": latency, "tokens": tokens}
        )
    
    def report_partial_result(self, result_summary: str, models_completed: int):
        """报告部分结果"""
        self.update_progress(
            ProgressStage.PARTIAL_RESULT,
            f"📊 部分完成 ({models_completed}个模型)\n{result_summary[:100]}...",
            details={"models_completed": models_completed}
        )
    
    def report_completion(self, final_result: str = None, 
                         total_models: int = None, success_count: int = None):
        """报告任务完成"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        msg = f"🎉 任务完成! (耗时: {elapsed:.1f}s)"
        
        if total_models and success_count:
            success_rate = success_count / total_models * 100
            msg += f"\n成功率: {success_rate:.0f}% ({success_count}/{total_models})"
        
        if final_result:
            msg += f"\n结果: {final_result[:150]}..."
        
        self.update_progress(
            ProgressStage.COMPLETED,
            msg,
            progress=100,
            details={
                "elapsed": elapsed,
                "total_models": total_models,
                "success_count": success_count
            }
        )
    
    def report_error(self, error_message: str, stage: str = "执行"):
        """报告错误"""
        self.update_progress(
            ProgressStage.FAILED,
            f"⚠️ {stage}失败: {error_message}",
            details={"error": error_message}
        )
    
    def get_history(self) -> List[Dict]:
        """获取进度历史"""
        return self.progress_history.copy()
    
    def clear_history(self):
        """清空历史"""
        self.progress_history = []


class MultiModelExecutorWithProgress:
    """
    带进度反馈的多模型执行器
    
    特点:
    1. 执行过程中实时报告进度
    2. 每个模型开始/完成都通知
    3. 支持部分结果先发
    4. 支持多轮对话
    """
    
    def __init__(self, dispatcher, user_id: str = None, 
                 message_callback: Callable = None):
        self.dispatcher = dispatcher
        self.user_id = user_id
        self.reporter = ProgressReporter(user_id, message_callback)
    
    def execute_with_progress(self, prompt: str, model_count: int = 3) -> Dict:
        """
        带进度的执行
        
        执行流程:
        1. 开始 → 分析任务
        2. 调度模型 → 逐个调用
        3. 每个模型结果实时报告
        4. 部分完成后可先发送
        5. 全部完成 → 聚合结果 → 最终报告
        """
        task_id = self.reporter.start_task("多模型执行", total_steps=model_count + 3)
        
        # 阶段1: 分析任务
        complexity = self.dispatcher.complexity_analyzer.analyze(prompt)
        self.reporter.update_progress(
            ProgressStage.ANALYZING,
            f"📝 任务分析: {complexity['complexity_label']} - {', '.join(complexity['task_types'])}",
            details=complexity
        )
        
        # 阶段2: 获取在线模型
        self.reporter.update_progress(
            ProgressStage.DISPATCHING,
            "🔍 调度模型..."
        )
        
        online = self.dispatcher.get_online_models()
        selected = self._select_models(online, model_count)
        
        if not selected:
            self.reporter.report_error("无可用模型")
            return {"success": False, "error": "无可用模型"}
        
        # 阶段3: 执行模型
        results = []
        for i, model in enumerate(selected):
            self.reporter.report_model_start(model['name'], model['provider'])
            
            result = self.dispatcher._call_api(model, prompt)
            result['model_name'] = model['name']
            result['provider'] = model['provider']
            results.append(result)
            
            # 报告模型结果
            self.reporter.report_model_result(
                model['name'],
                result.get('success', False),
                result.get('latency'),
                result.get('tokens')
            )
            
            # 如果是第2个模型完成，可以先发送部分结果
            if i >= 1 and i < len(selected) - 1:
                partial = self._summarize_partial(results)
                self.reporter.report_partial_result(partial, i + 1)
        
        # 阶段4: 聚合结果
        self.reporter.update_progress(ProgressStage.AGGREGATING, "📦 聚合结果...")
        
        aggregator = ResultAggregator()
        aggregated = aggregator.aggregate_responses(results)
        summary = aggregator.get_execution_summary(results)
        
        # 阶段5: 完成
        self.reporter.report_completion(
            final_result=aggregated[:100],
            total_models=summary['total_models'],
            success_count=summary['success_count']
        )
        
        return {
            "success": summary['success_count'] > 0,
            "task_id": task_id,
            "results": results,
            "aggregated": aggregated,
            "summary": summary,
            "progress_history": self.reporter.get_history()
        }
    
    def _select_models(self, online: Dict, count: int) -> List[Dict]:
        """选择模型"""
        selected = []
        for models in online.values():
            for m in models:
                selected.append(m)
                if len(selected) >= count:
                    return selected
        return selected[:count]
    
    def _summarize_partial(self, results: List[Dict]) -> str:
        """总结部分结果"""
        success = [r for r in results if r.get('success')]
        if not success:
            return "暂无成功结果"
        
        summary = f"{len(success)}个模型已有响应\n"
        for r in success[:2]:
            content = r.get('content', '')[:80]
            summary += f"- {r.get('model_name')}: {content}...\n"
        
        return summary


# 导入需要的类
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dispatcher_multiprovider import MultiProviderDispatcher

# 简单结果聚合器
class ResultAggregator:
    @staticmethod
    def aggregate_responses(results):
        if not results:
            return ""
        successful = [r for r in results if r.get('success')]
        if not successful:
            return "所有模型执行均失败"
        if len(successful) == 1:
            return successful[0].get('response', '')
        aggregated = "【多模型响应汇总】\n\n"
        for i, r in enumerate(successful, 1):
            aggregated += f"--- 模型{i}: {r.get('model_name')} ---\n"
            aggregated += f"{r.get('content', '')}\n\n"
        return aggregated.strip()
    
    @staticmethod
    def get_execution_summary(results):
        total = len(results)
        success = len([r for r in results if r.get('success')])
        failed = total - success
        avg_latency = sum(r.get('latency', 0) for r in results) / total if total > 0 else 0
        total_tokens = sum(r.get('tokens', 0) for r in results)
        return {
            'total_models': total,
            'success_count': success,
            'failed_count': failed,
            'success_rate': f"{(success/total*100):.1f}%" if total > 0 else "0%",
            'avg_latency': f"{avg_latency:.2f}s",
            'total_tokens': total_tokens
        }


# 测试
if __name__ == '__main__':
    from dispatcher_multiprovider import MultiProviderDispatcher
    
    db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
    dispatcher = MultiProviderDispatcher(db_path)
    
    # 测试进度报告
    print("=== 进度报告测试 ===\n")
    
    def test_callback(report):
        print(f"[进度] {report['stage']}: {report['message']}")
        print(f"  进度: {report['progress']:.0f}%\n")
    
    executor = MultiModelExecutorWithProgress(
        dispatcher, 
        user_id="test_user",
        message_callback=test_callback
    )
    
    print("执行带进度的任务...\n")
    result = executor.execute_with_progress("你好，请介绍一下你自己", model_count=2)
    
    print(f"\n最终结果: 成功={result['success']}")
    print(f"摘要: {result['summary']}")
