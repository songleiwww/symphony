# -*- coding: utf-8 -*-
"""
序境系统 - 统一调度入口 (P1修复)
解决 scheduler.py 与 adaptive_scheduler.py 的冲突
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DispatchMode(Enum):
    """调度模式"""
    BASIC = "basic"           # 基础模式 - 单模型选择
    ADAPTIVE = "adaptive"     # 自适应模式 - 任务分解+多模型协同
    AUTO = "auto"             # 自动模式 - 根据复杂度自动选择


class TaskComplexity(Enum):
    """任务复杂度"""
    SIMPLE = 1      # 简单 - 单模型
    NORMAL = 5      # 普通 - 基础调度
    COMPLEX = 10    # 复杂 - 多模型协同


@dataclass
class DispatchRequest:
    """调度请求"""
    task_type: str
    complexity: int = 5
    keywords: List[str] = None
    context: Dict = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.context is None:
            self.context = {}


@dataclass
class DispatchResult:
    """调度结果"""
    mode: DispatchMode
    primary_model: str = None
    secondary_models: List[str] = None
    agents: List[Dict] = None
    reasoning: str = ""
    
    def __post_init__(self):
        if self.secondary_models is None:
            self.secondary_models = []
        if self.agents is None:
            self.agents = []


class UnifiedScheduler:
    """
    统一调度入口
    解决 scheduler.py vs adaptive_scheduler.py 冲突
    
    P1修复:
    - 统一返回值格式
    - 自动模式选择
    - 兼容历史接口
    """
    
    def __init__(self):
        self.mode = DispatchMode.AUTO
        self._basic_scheduler = None  # 延迟加载
        self._adaptive_scheduler = None  # 延迟加载
        self._load_schedulers()
    
    def _load_schedulers(self):
        """延迟加载调度器"""
        try:
            from core.scheduler import Scheduler
            self._basic_scheduler = Scheduler()
            logger.info("基础调度器已加载")
        except Exception as e:
            logger.warning(f"基础调度器加载失败: {e}")
        
        try:
            from dispatcher.adaptive_scheduler import AdaptiveScheduler
            self._adaptive_scheduler = AdaptiveScheduler()
            logger.info("自适应调度器已加载")
        except Exception as e:
            logger.warning(f"自适应调度器加载失败: {e}")
    
    def _detect_mode(self, request: DispatchRequest) -> DispatchMode:
        """自动检测调度模式"""
        # 复杂度判断
        if request.complexity >= 7:
            return DispatchMode.ADAPTIVE
        
        # 关键词判断
        complex_keywords = ["进化", "升级", "架构", "集成", "优化", "分析", "团队", "多模型"]
        if any(k in request.keywords for k in complex_keywords):
            return DispatchMode.ADAPTIVE
        
        # 任务类型判断
        complex_types = ["evolution", "self_adaptive", "integration"]
        if request.task_type in complex_types:
            return DispatchMode.ADAPTIVE
        
        return DispatchMode.BASIC
    
    def dispatch(self, request: DispatchRequest) -> DispatchResult:
        """
        统一调度入口
        
        Args:
            request: 调度请求
        
        Returns:
            调度结果
        """
        # 自动选择模式
        if self.mode == DispatchMode.AUTO:
            mode = self._detect_mode(request)
        else:
            mode = self.mode
        
        if mode == DispatchMode.ADAPTIVE:
            return self._dispatch_adaptive(request)
        else:
            return self._dispatch_basic(request)
    
    def _dispatch_basic(self, request: DispatchRequest) -> DispatchResult:
        """基础调度"""
        if self._basic_scheduler:
            model = self._basic_scheduler.select_model()
            if model:
                return DispatchResult(
                    mode=DispatchMode.BASIC,
                    primary_model=model.model_id,
                    reasoning=f"基础调度: 选择模型 {model.model_name}"
                )
        
        # 回退
        return DispatchResult(
            mode=DispatchMode.BASIC,
            primary_model="ark-code-latest",
            reasoning="基础调度: 使用默认模型"
        )
    
    def _dispatch_adaptive(self, request: DispatchRequest) -> DispatchResult:
        """自适应调度"""
        # 团队选择
        try:
            from evolution.team_selector import get_evolution_team
            team_system = get_evolution_team()
            team_result = team_system.select_team(request.task_type)
            
            return DispatchResult(
                mode=DispatchMode.ADAPTIVE,
                primary_model=team_result["team"]["primary"],
                secondary_models=[
                    team_result["team"]["secondary"],
                    team_result["team"]["support"]
                ],
                agents=[
                    {"role": role, "model": team_result["team"]["primary"]}
                    for role in team_result["team"]["roles"]
                ],
                reasoning=f"自适应调度: {team_result['team']['name']}"
            )
        except Exception as e:
            logger.warning(f"自适应调度失败: {e}")
            return self._dispatch_basic(request)
    
    def set_mode(self, mode: DispatchMode):
        """设置调度模式"""
        self.mode = mode
        logger.info(f"调度模式已设置为: {mode.value}")
    
    def get_status(self) -> Dict:
        """获取调度器状态"""
        return {
            "mode": self.mode.value,
            "basic_scheduler_loaded": self._basic_scheduler is not None,
            "adaptive_scheduler_loaded": self._adaptive_scheduler is not None
        }


# 全局统一调度器
_unified_scheduler: Optional[UnifiedScheduler] = None


def get_unified_scheduler() -> UnifiedScheduler:
    """获取统一调度器"""
    global _unified_scheduler
    if _unified_scheduler is None:
        _unified_scheduler = UnifiedScheduler()
    return _unified_scheduler


def dispatch(request: DispatchRequest) -> DispatchResult:
    """
    便捷调度函数
    
    Usage:
        result = dispatch(DispatchRequest(
            task_type="evolution",
            complexity=8,
            keywords=["系统升级"]
        ))
    """
    scheduler = get_unified_scheduler()
    return scheduler.dispatch(request)


# 导出
__all__ = [
    'DispatchMode',
    'TaskComplexity',
    'DispatchRequest',
    'DispatchResult',
    'UnifiedScheduler',
    'get_unified_scheduler',
    'dispatch'
]


if __name__ == '__main__':
    print("=== 统一调度入口测试 ===\n")
    
    scheduler = get_unified_scheduler()
    print(f"状态: {scheduler.get_status()}\n")
    
    # 测试不同任务
    tests = [
        DispatchRequest(task_type="takeover", complexity=3, keywords=["接管"]),
        DispatchRequest(task_type="evolution", complexity=8, keywords=["系统升级"]),
        DispatchRequest(task_type="integration", complexity=5, keywords=["冲突解决"]),
    ]
    
    for req in tests:
        result = scheduler.dispatch(req)
        print(f"任务: {req.task_type}")
        print(f"  模式: {result.mode.value}")
        print(f"  主模型: {result.primary_model}")
        print(f"  推理: {result.reasoning}")
        print()
