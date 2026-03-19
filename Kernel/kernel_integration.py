# -*- coding: utf-8 -*-
"""
序境内核 - 集成实时进度功能
将progress模块集成到内核
"""
import sys
import os

# 添加内核路径
kernel_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, kernel_path)

# 导入动态调度器
try:
    from dispatcher.dynamic_dispatcher import DynamicDispatcher
    DYNAMIC_DISPATCHER_AVAILABLE = True
except ImportError:
    # 如果dynamic_dispatcher在上一级目录
    sys.path.insert(0, os.path.join(kernel_path, '..'))
    try:
        from dynamic_dispatcher import DynamicDispatcher
        DYNAMIC_DISPATCHER_AVAILABLE = True
    except ImportError:
        DYNAMIC_DISPATCHER_AVAILABLE = False
        print('[内核] 动态调度器未找到')

# 导入进度模块
from progress.realtime_progress import (
    MultiModelExecutorWithProgress,
    ProgressReporter,
    ProgressStage,
    ResultAggregator
)

# 导入调度器
from dispatcher_multiprovider import MultiProviderDispatcher

# 导入会话管理
from session.task_manager import TaskManager
from session.session_manager import SessionManager

# 导入自我自适应模块
from rules.self_adaptive import (
    SelfAdaptiveRuleManager,
    RuleComplianceChecker, 
    check_before,
    add_rule
)

# 导入任务控制模块
from control.task_controller import (
    TaskController,
    InterruptibleExecutor,
    TaskState,
    get_task_controller
)

# 导入健康检查模块
from health.kernel_health import (
    KernelHealthChecker,
    KernelDefenseSystem
)

# 导入多Agent协作模块
from multi_agent.xujing_multi_agent import (
    XujingAgent,
    ControllerAgent,
    ExecutorAgent,
    KnowledgeAgent,
    MetaAgent,
    EnsembleAgent,
    MultiAgentSystem,
    get_multi_agent_system
)

# 导入检测后组队模块
from multi_agent.detect_then_team import (
    ModelHealthDetector,
    SmartTeamBuilder,
    DetectThenTeamSystem,
    get_detect_then_team_system
)

# 导入接管技能模块
from skills.takeover_skill import (
    XujingTakeover,
    TakeoverSkill,
    get_takeover_skill,
    takeover
)

# 导入对话接管器
from dialog_takeover import (
    XujingDialogHandler,
    get_dialog_handler,
    intercept_message
)

# 导入备份模块
from backup.backup_system import (
    XujingBackup,
    get_backup_system
)

# 导入进化团队模块
from evolution.team_selector import (
    EvolutionTeam,
    get_evolution_team,
    dispatch_team
)

# 导入统一模块加载器
from kernel_loader import (
    ModuleLoader,
    get_module_loader,
    lazy_load
)

# 导入版本管理
from version import (
    VERSION,
    get_version,
    get_changelog
)

__all__ = [
    # 执行器
    'MultiModelExecutorWithProgress',
    'ProgressReporter', 
    'ProgressStage',
    'ResultAggregator',
    'MultiProviderDispatcher',
    'TaskManager',
    'SessionManager',
    'EvolutionDispatcher',
    'AdaptiveDispatcher',
    
    # 动态调度器
    'DynamicDispatcher',
    'DYNAMIC_DISPATCHER_AVAILABLE',
    
    # 统一入口
    'get_kernel_executor',
    'get_evolution_executor',
    'create_executor_with_callback',
    'get_dynamic_dispatcher',
    
    # 自我自适应
    'SelfAdaptiveRuleManager',
    'RuleComplianceChecker', 
    'check_before',
    'add_rule',
    'evolve_dispatcher',
    
    # 任务控制
    'TaskController',
    'InterruptibleExecutor',
    'TaskState',
    'get_task_controller',
    
    # 健康检查
    'KernelHealthChecker',
    'KernelDefenseSystem',
    
    # 多Agent协作
    'XujingAgent',
    'ControllerAgent',
    'ExecutorAgent',
    'KnowledgeAgent',
    'MetaAgent',
    'EnsembleAgent',
    'MultiAgentSystem',
    'get_multi_agent_system',
    
    # 检测后组队
    'ModelHealthDetector',
    'SmartTeamBuilder',
    'DetectThenTeamSystem',
    'get_detect_then_team_system',
    
    # 接管技能
    'XujingTakeover',
    'TakeoverSkill',
    'get_takeover_skill',
    'takeover',
    
    # 对话接管器
    'XujingDialogHandler',
    'get_dialog_handler',
    'intercept_message',
    
    # 备份系统
    'XujingBackup',
    'get_backup_system',
    
    # 进化团队
    'EvolutionTeam',
    'get_evolution_team',
    'dispatch_team',
    
    # 统一加载器
    'ModuleLoader',
    'get_module_loader',
    'lazy_load',
    
    # 版本管理
    'VERSION',
    'get_version',
    'get_changelog'
]

# 内核执行器缓存
_kernel_executor = None

def get_kernel_executor(db_path: str, user_id: str = None, message_callback = None):
    """
    获取内核执行器(带进度反馈)

    参数:
        db_path: 数据库路径
        user_id: 用户ID
        message_callback: 消息回调函数(用于发送进度到对话框)

    返回:
        MultiModelExecutorWithProgress实例
    """
    global _kernel_executor

    if _kernel_executor is None:
        dispatcher = MultiProviderDispatcher(db_path)
        _kernel_executor = MultiModelExecutorWithProgress(
            dispatcher,
            user_id=user_id,
            message_callback=message_callback
        )

    return _kernel_executor


def create_executor_with_callback(db_path: str, user_id: str, callback_func):
    """
    创建带飞书回调的执行器

    示例:
        def my_callback(report):
            message(action='send', message=report['message'], ...)

        executor = create_executor_with_callback(db_path, user_id, my_callback)
        result = executor.execute_with_progress("你好", model_count=3)
    """
    dispatcher = MultiProviderDispatcher(db_path)
    return MultiModelExecutorWithProgress(
        dispatcher,
        user_id=user_id,
        message_callback=callback_func
    )


# 进化调度器
_evolution_dispatcher = None

def get_evolution_executor(db_path: str):
    """
    获取进化调度器(带自适应学习能力)

    特性:
    1. 模型权重动态调整
    2. 成功率追踪
    3. 故障预测
    4. 用户偏好学习
    """
    global _evolution_dispatcher

    if _evolution_dispatcher is None:
        from dispatcher_evolution import EvolutionDispatcher
        _evolution_dispatcher = EvolutionDispatcher(db_path)

    return _evolution_dispatcher


# 动态调度器
_dynamic_dispatcher = None

def get_dynamic_dispatcher(db_path: str = None):
    """
    获取动态调度器(根据任务动态选择最佳模型)
    
    特性:
    1. 任务分析 - 分析任务类型和复杂度
    2. 动态评分 - 根据历史表现评分
    3. 失败淘汰 - 失败3次自动降权
    4. 智能路由 - 根据任务匹配最佳模型
    
    参数:
        db_path: 数据库路径，默认使用symphony.db
    
    返回:
        DynamicDispatcher实例
    """
    global _dynamic_dispatcher
    
    if db_path is None:
        # 使用默认数据库路径
        import os
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data', 'symphony.db'
        )
    
    if _dynamic_dispatcher is None:
        if DYNAMIC_DISPATCHER_AVAILABLE:
            _dynamic_dispatcher = DynamicDispatcher(db_path)
        else:
            raise ImportError('动态调度器未正确加载')
    
    return _dynamic_dispatcher


def evolve_dispatcher(db_path: str):
    """
    执行调度器自我进化
    分析历史数据，调整策略
    """
    dispatcher = get_evolution_executor(db_path)
    dispatcher.evolve()
    return "进化完成"


# ============================================================================
# 消息预处理 - 集成接管检测
# ============================================================================

def preprocess_message(user_message: str, context: dict = None) -> dict:
    """
    消息预处理函数 - 在处理消息前先检查是否需要接管
    """
    try:
        from dialog_takeover import intercept_message, get_dialog_handler
        
        takeover_result = intercept_message(user_message, context)
        
        if takeover_result.get('taken_over'):
            handler = get_dialog_handler()
            signed_response = handler.add_takeover_signature(takeover_result.get('response', ''))
            takeover_result['response'] = signed_response
            
            return {
                'should_takeover': True,
                'takeover_result': takeover_result,
                'original_result': None
            }
        else:
            return {
                'should_takeover': False,
                'takeover_result': None,
                'original_result': None
            }
    except Exception as e:
        print(f'[预处理] 接管检测失败: {e}')
        return {
            'should_takeover': False,
            'takeover_result': None,
            'original_result': None
        }


def process_with_takeover(user_message: str, context: dict = None, normal_handler=None):
    """
    带接管检测的消息处理函数
    """
    preprocess_result = preprocess_message(user_message, context)
    
    if preprocess_result['should_takeover']:
        return preprocess_result['takeover_result']
    else:
        if normal_handler:
            return normal_handler(user_message, context)
        return None
