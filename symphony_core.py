#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎼 Symphony - 统一调度核心
整合模型管理器、故障处理系统、技能管理器、MCP管理器
实现智能任务调度和多Agent协作
"""

import time
import logging
import threading
from enum import Enum
from typing import (
    Any, Callable, Dict, List, Optional, Tuple, Type, Union
)
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
import json

# 导入现有模块
try:
    from model_manager import (
        ModelManager, ModelWrapper, ModelConfig,
        ModelStatus, ModelHealth, NoAvailableModelError,
        CircuitBreakerOpenError, setup_logging
    )
except ImportError:
    ModelManager = None
    ModelWrapper = None

try:
    from fault_tolerance import (
        SmartClient, Retrier, CircuitBreaker, FallbackManager,
        FailoverManager, HealthChecker,
        RetryConfig, CircuitBreakerConfig, HealthCheckConfig,
        ModelConfig as FTModelConfig,
        with_retry, with_circuit_breaker,
        ErrorType, HealthStatus, NoHealthyModelError
    )
except ImportError:
    SmartClient = None

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SymphonyCore")


# =============================================================================
# 枚举定义
# =============================================================================

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"          # 待处理
    QUEUED = "queued"            # 已排队
    RUNNING = "running"          # 运行中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"            # 失败
    CANCELLED = "cancelled"      # 已取消
    RETRYING = "retrying"        # 重试中


class SkillType(Enum):
    """技能类型"""
    BUILTIN = "builtin"          # 内置技能
    MCP = "mcp"                  # MCP技能
    CUSTOM = "custom"             # 自定义技能
    AGENT = "agent"               # Agent技能


class ExecutionMode(Enum):
    """执行模式"""
    SEQUENTIAL = "sequential"     # 顺序执行
    PARALLEL = "parallel"         # 并行执行
    PIPELINE = "pipeline"         # 流水线执行
    WORKFLOW = "workflow"         # 工作流执行


# =============================================================================
# 数据类定义
# =============================================================================

@dataclass
class Task:
    """任务数据类"""
    task_id: str
    name: str
    description: str = ""
    skill_name: Optional[str] = None
    model_name: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "skill_name": self.skill_name,
            "model_name": self.model_name,
            "parameters": self.parameters,
            "status": self.status.value,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "dependencies": self.dependencies,
            "tags": self.tags,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """从字典创建"""
        return cls(
            task_id=data["task_id"],
            name=data["name"],
            description=data.get("description", ""),
            skill_name=data.get("skill_name"),
            model_name=data.get("model_name"),
            parameters=data.get("parameters", {}),
            status=TaskStatus(data.get("status", "pending")),
            priority=data.get("priority", 0),
            created_at=datetime.fromisoformat(data["created_at"]),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            result=data.get("result"),
            error=data.get("error"),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            dependencies=data.get("dependencies", []),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )


@dataclass
class Skill:
    """技能定义"""
    name: str
    skill_type: SkillType
    description: str = ""
    version: str = "1.0.0"
    handler: Optional[Callable] = None
    parameters_schema: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    tags: List[str] = field(default_factory=list)


@dataclass
class MCPTool:
    """MCP工具定义"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    server_name: str = "default"
    version: str = "1.0.0"


@dataclass
class WorkflowStep:
    """工作流步骤"""
    step_id: str
    name: str
    task: Task
    condition: Optional[Callable] = None
    on_success: Optional[str] = None
    on_failure: Optional[str] = None
    timeout: Optional[float] = None


@dataclass
class SymphonyMetrics:
    """Symphony指标"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    cancelled_tasks: int = 0
    avg_task_duration: float = 0.0
    total_duration: float = 0.0
    skill_calls: Dict[str, int] = field(default_factory=dict)
    model_calls: Dict[str, int] = field(default_factory=dict)
    error_counts: Dict[str, int] = field(default_factory=dict)


# =============================================================================
# 技能管理器
# =============================================================================

class SkillManager:
    """
    技能管理器
    管理内置技能、MCP技能、自定义技能
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("SkillManager")
        self._skills: Dict[str, Skill] = {}
        self._mcp_tools: Dict[str, MCPTool] = {}
        self._lock = threading.RLock()

    def register_skill(self, skill: Skill) -> bool:
        """
        注册技能

        Args:
            skill: 技能对象

        Returns:
            是否注册成功
        """
        with self._lock:
            if skill.name in self._skills:
                self.logger.warning(f"技能已存在，将被覆盖: {skill.name}")

            self._skills[skill.name] = skill
            self.logger.info(f"已注册技能: {skill.name} ({skill.skill_type.value})")
            return True

    def register_mcp_tool(self, tool: MCPTool) -> bool:
        """
        注册MCP工具

        Args:
            tool: MCP工具对象

        Returns:
            是否注册成功
        """
        with self._lock:
            tool_name = f"mcp.{tool.server_name}.{tool.name}"
            self._mcp_tools[tool_name] = tool

            # 同时注册为技能
            skill = Skill(
                name=tool_name,
                skill_type=SkillType.MCP,
                description=tool.description,
                version=tool.version,
                parameters_schema=tool.input_schema,
                config={"server_name": tool.server_name}
            )
            self._skills[tool_name] = skill

            self.logger.info(f"已注册MCP工具: {tool_name}")
            return True

    def get_skill(self, name: str) -> Optional[Skill]:
        """
        获取技能

        Args:
            name: 技能名称

        Returns:
            技能对象，如果不存在返回None
        """
        with self._lock:
            return self._skills.get(name)

    def list_skills(self, skill_type: Optional[SkillType] = None) -> List[Skill]:
        """
        列出所有技能

        Args:
            skill_type: 可选的技能类型过滤

        Returns:
            技能列表
        """
        with self._lock:
            skills = list(self._skills.values())
            if skill_type:
                skills = [s for s in skills if s.skill_type == skill_type]
            return skills

    def execute_skill(self, skill_name: str, **kwargs) -> Any:
        """
        执行技能

        Args:
            skill_name: 技能名称
            **kwargs: 技能参数

        Returns:
            技能执行结果

        Raises:
            ValueError: 技能不存在或不可用
        """
        skill = self.get_skill(skill_name)
        if not skill:
            raise ValueError(f"技能不存在: {skill_name}")

        if not skill.enabled:
            raise ValueError(f"技能已禁用: {skill_name}")

        if not skill.handler:
            raise ValueError(f"技能没有处理器: {skill_name}")

        self.logger.info(f"执行技能: {skill_name}")
        return skill.handler(**kwargs)

    def unregister_skill(self, name: str) -> bool:
        """
        注销技能

        Args:
            name: 技能名称

        Returns:
            是否注销成功
        """
        with self._lock:
            if name in self._skills:
                del self._skills[name]
                self.logger.info(f"已注销技能: {name}")
                return True
            return False


# =============================================================================
# MCP管理器
# =============================================================================

class MCPManager:
    """
    MCP (Model Context Protocol) 管理器
    管理MCP服务器连接和工具调用
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("MCPManager")
        self._servers: Dict[str, Dict[str, Any]] = {}
        self._tools: Dict[str, MCPTool] = {}
        self._lock = threading.RLock()

    def register_server(self, server_name: str, config: Dict[str, Any]) -> bool:
        """
        注册MCP服务器

        Args:
            server_name: 服务器名称
            config: 服务器配置

        Returns:
            是否注册成功
        """
        with self._lock:
            self._servers[server_name] = {
                "name": server_name,
                "config": config,
                "connected": False,
                "tools": []
            }
            self.logger.info(f"已注册MCP服务器: {server_name}")
            return True

    def connect_server(self, server_name: str) -> bool:
        """
        连接MCP服务器

        Args:
            server_name: 服务器名称

        Returns:
            是否连接成功
        """
        with self._lock:
            if server_name not in self._servers:
                self.logger.error(f"MCP服务器不存在: {server_name}")
                return False

            # 这里应该实现实际的连接逻辑
            # 暂时模拟连接成功
            self._servers[server_name]["connected"] = True
            self.logger.info(f"MCP服务器已连接: {server_name}")
            return True

    def disconnect_server(self, server_name: str) -> bool:
        """
        断开MCP服务器

        Args:
            server_name: 服务器名称

        Returns:
            是否断开成功
        """
        with self._lock:
            if server_name in self._servers:
                self._servers[server_name]["connected"] = False
                self.logger.info(f"MCP服务器已断开: {server_name}")
                return True
            return False

    def get_server_tools(self, server_name: str) -> List[MCPTool]:
        """
        获取服务器工具列表

        Args:
            server_name: 服务器名称

        Returns:
            工具列表
        """
        with self._lock:
            if server_name not in self._servers:
                return []

            # 这里应该实现实际的工具发现逻辑
            # 暂时返回空列表
            return self._servers[server_name].get("tools", [])

    def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        server_name: str = "default"
    ) -> Any:
        """
        调用MCP工具

        Args:
            tool_name: 工具名称
            arguments: 工具参数
            server_name: 服务器名称

        Returns:
            工具调用结果

        Raises:
            ValueError: 服务器或工具不存在
        """
        full_tool_name = f"mcp.{server_name}.{tool_name}"

        with self._lock:
            if server_name not in self._servers:
                raise ValueError(f"MCP服务器不存在: {server_name}")

            if not self._servers[server_name]["connected"]:
                raise ValueError(f"MCP服务器未连接: {server_name}")

        # 这里应该实现实际的工具调用逻辑
        # 暂时模拟调用
        self.logger.info(f"调用MCP工具: {full_tool_name}, 参数: {arguments}")

        return {
            "tool": full_tool_name,
            "arguments": arguments,
            "result": "simulated_result",
            "timestamp": datetime.now().isoformat()
        }

    def list_servers(self) -> List[Dict[str, Any]]:
        """
        列出所有服务器

        Returns:
            服务器列表
        """
        with self._lock:
            return list(self._servers.values())


# =============================================================================
# 任务队列
# =============================================================================

class TaskQueue:
    """
    任务队列
    支持优先级和依赖关系
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("TaskQueue")
        self._tasks: Dict[str, Task] = {}
        self._queue: List[Task] = []
        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)

    def add_task(self, task: Task) -> bool:
        """
        添加任务

        Args:
            task: 任务对象

        Returns:
            是否添加成功
        """
        with self._lock:
            if task.task_id in self._tasks:
                self.logger.warning(f"任务已存在: {task.task_id}")
                return False

            self._tasks[task.task_id] = task
            task.status = TaskStatus.QUEUED
            self._queue.append(task)
            self._sort_queue()
            self._condition.notify()

            self.logger.info(f"任务已加入队列: {task.task_id} ({task.name})")
            return True

    def _sort_queue(self):
        """排序队列（按优先级和创建时间）"""
        self._queue.sort(key=lambda t: (-t.priority, t.created_at))

    def get_task(self, timeout: Optional[float] = None) -> Optional[Task]:
        """
        获取下一个任务

        Args:
            timeout: 超时时间（秒）

        Returns:
            任务对象，如果没有可用任务返回None
        """
        with self._condition:
            start_time = time.time()

            while True:
                # 查找可执行的任务
                for i, task in enumerate(self._queue):
                    if self._can_execute_task(task):
                        task = self._queue.pop(i)
                        task.status = TaskStatus.RUNNING
                        task.started_at = datetime.now()
                        self.logger.info(f"任务开始执行: {task.task_id}")
                        return task

                # 等待新任务
                if timeout is None:
                    self._condition.wait()
                else:
                    elapsed = time.time() - start_time
                    if elapsed >= timeout:
                        return None
                    self._condition.wait(timeout - elapsed)

    def _can_execute_task(self, task: Task) -> bool:
        """检查任务是否可以执行（依赖是否完成）"""
        if not task.dependencies:
            return True

        for dep_id in task.dependencies:
            dep_task = self._tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False

        return True

    def complete_task(self, task_id: str, result: Any = None) -> bool:
        """
        完成任务

        Args:
            task_id: 任务ID
            result: 任务结果

        Returns:
            是否成功
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False

            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result

            self.logger.info(f"任务已完成: {task_id}")
            self._condition.notify_all()
            return True

    def fail_task(self, task_id: str, error: str) -> bool:
        """
        任务失败

        Args:
            task_id: 任务ID
            error: 错误信息

        Returns:
            是否成功
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False

            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.error = error

            self.logger.error(f"任务失败: {task_id}, 错误: {error}")
            self._condition.notify_all()
            return True

    def retry_task(self, task_id: str) -> bool:
        """
        重试任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False

            if task.retry_count >= task.max_retries:
                self.logger.warning(f"任务已达到最大重试次数: {task_id}")
                return False

            task.retry_count += 1
            task.status = TaskStatus.RETRYING
            task.error = None
            task.result = None

            # 重新加入队列
            self._queue.append(task)
            self._sort_queue()

            self.logger.info(f"任务重试: {task_id} (第{task.retry_count}次)")
            self._condition.notify_all()
            return True

    def get_task_status(self, task_id: str) -> Optional[Task]:
        """
        获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务对象
        """
        with self._lock:
            return self._tasks.get(task_id)

    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        """
        列出所有任务

        Args:
            status: 可选的状态过滤

        Returns:
            任务列表
        """
        with self._lock:
            tasks = list(self._tasks.values())
            if status:
                tasks = [t for t in tasks if t.status == status]
            return tasks


# =============================================================================
# Symphony 统一调度器
# =============================================================================

class SymphonyCore:
    """
    🎼 Symphony 统一调度核心

    整合：
    - 模型管理器
    - 故障处理系统
    - 技能管理器
    - MCP管理器
    - 任务调度
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化Symphony核心

        Args:
            config: 配置字典
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger("SymphonyCore")
        self.config = config or {}

        # 初始化组件
        self.skill_manager = SkillManager(logger=self.logger)
        self.mcp_manager = MCPManager(logger=self.logger)
        self.task_queue = TaskQueue(logger=self.logger)

        # 模型管理器和故障处理系统（可选）
        self.model_manager: Optional[ModelManager] = None
        self.smart_client: Optional[SmartClient] = None
        self._init_model_components()

        # 工作线程
        self._workers: List[threading.Thread] = []
        self._running = False

        # 指标
        self.metrics = SymphonyMetrics()
        self._metrics_lock = threading.RLock()

        # 任务ID生成
        self._task_counter = 0
        self._task_counter_lock = threading.Lock()

        self.logger.info("🎼 Symphony 统一调度器已初始化")

    def _init_model_components(self):
        """初始化模型相关组件"""
        try:
            if ModelManager:
                self.model_manager = ModelManager(logger=self.logger)
                self.logger.info("模型管理器已加载")

            if SmartClient:
                retrier = Retrier()
                circuit_breaker = CircuitBreaker()
                fallback_manager = FallbackManager()
                failover_manager = FailoverManager()

                self.smart_client = SmartClient(
                    retrier=retrier,
                    circuit_breaker=circuit_breaker,
                    fallback_manager=fallback_manager,
                    failover_manager=failover_manager
                )
                self.logger.info("智能客户端已加载")
        except Exception as e:
            self.logger.warning(f"模型组件初始化失败: {e}")

    def _generate_task_id(self) -> str:
        """生成任务ID"""
        with self._task_counter_lock:
            self._task_counter += 1
            return f"task_{self._task_counter}_{int(time.time())}"

    def start(self, num_workers: int = 4):
        """
        启动调度器

        Args:
            num_workers: 工作线程数量
        """
        if self._running:
            self.logger.warning("调度器已经在运行中")
            return

        self._running = True

        # 启动工作线程
        for i in range(num_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                args=(i,),
                daemon=True,
                name=f"SymphonyWorker-{i}"
            )
            worker.start()
            self._workers.append(worker)

        self.logger.info(f"🎼 Symphony 调度器已启动，{num_workers}个工作线程")

    def stop(self):
        """停止调度器"""
        if not self._running:
            return

        self._running = False

        # 等待工作线程结束
        for worker in self._workers:
            worker.join(timeout=5)

        self._workers.clear()
        self.logger.info("🎼 Symphony 调度器已停止")

    def _worker_loop(self, worker_id: int):
        """工作线程主循环"""
        self.logger.info(f"工作线程 {worker_id} 已启动")

        while self._running:
            try:
                task = self.task_queue.get_task(timeout=1.0)
                if not task:
                    continue

                self._execute_task(task, worker_id)

            except Exception as e:
                self.logger.error(f"工作线程 {worker_id} 发生错误: {e}", exc_info=True)

        self.logger.info(f"工作线程 {worker_id} 已停止")

    def _execute_task(self, task: Task, worker_id: int):
        """
        执行任务

        Args:
            task: 任务对象
            worker_id: 工作线程ID
        """
        start_time = time.time()

        try:
            self.logger.info(f"[{worker_id}] 执行任务: {task.task_id} ({task.name})")

            # 更新指标
            with self._metrics_lock:
                self.metrics.total_tasks += 1

            result = None

            if task.skill_name:
                # 执行技能
                result = self._execute_skill_task(task)
            elif task.model_name:
                # 执行模型调用
                result = self._execute_model_task(task)
            else:
                # 自定义任务处理
                result = self._execute_custom_task(task)

            # 任务完成
            self.task_queue.complete_task(task.task_id, result)

            with self._metrics_lock:
                self.metrics.completed_tasks += 1
                duration = time.time() - start_time
                self.metrics.total_duration += duration
                self.metrics.avg_task_duration = (
                    self.metrics.total_duration / self.metrics.completed_tasks
                )

            self.logger.info(
                f"[{worker_id}] 任务完成: {task.task_id}, "
                f"耗时: {time.time() - start_time:.2f}s"
            )

        except Exception as e:
            error_msg = str(e)
            self.task_queue.fail_task(task.task_id, error_msg)

            with self._metrics_lock:
                self.metrics.failed_tasks += 1
                self.metrics.error_counts[error_msg] = (
                    self.metrics.error_counts.get(error_msg, 0) + 1
                )

            # 检查是否可以重试
            if task.retry_count < task.max_retries:
                self.task_queue.retry_task(task.task_id)

    def _execute_skill_task(self, task: Task) -> Any:
        """执行技能任务"""
        with self._metrics_lock:
            self.metrics.skill_calls[task.skill_name] = (
                self.metrics.skill_calls.get(task.skill_name, 0) + 1
            )

        return self.skill_manager.execute_skill(
            task.skill_name,
            **task.parameters
        )

    def _execute_model_task(self, task: Task) -> Any:
        """执行模型任务"""
        if not self.model_manager:
            raise RuntimeError("模型管理器未初始化")

        with self._metrics_lock:
            self.metrics.model_calls[task.model_name] = (
                self.metrics.model_calls.get(task.model_name, 0) + 1
            )

        # 这里实现模型调用逻辑
        # 暂时模拟
        return {
            "model": task.model_name,
            "parameters": task.parameters,
            "result": "model_response"
        }

    def _execute_custom_task(self, task: Task) -> Any:
        """执行自定义任务"""
        # 可以在这里添加自定义任务处理逻辑
        raise NotImplementedError("自定义任务处理器未实现")

    def submit_task(
        self,
        name: str,
        description: str = "",
        skill_name: Optional[str] = None,
        model_name: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        priority: int = 0,
        max_retries: int = 3,
        dependencies: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        提交任务

        Args:
            name: 任务名称
            description: 任务描述
            skill_name: 技能名称
            model_name: 模型名称
            parameters: 任务参数
            priority: 优先级
            max_retries: 最大重试次数
            dependencies: 依赖的任务ID列表
            tags: 标签列表
            metadata: 元数据

        Returns:
            任务ID
        """
        task_id = self._generate_task_id()

        task = Task(
            task_id=task_id,
            name=name,
            description=description,
            skill_name=skill_name,
            model_name=model_name,
            parameters=parameters or {},
            priority=priority,
            max_retries=max_retries,
            dependencies=dependencies or [],
            tags=tags or [],
            metadata=metadata or {}
        )

        self.task_queue.add_task(task)
        return task_id

    def register_builtin_skills(self):
        """注册内置技能"""
        # 示例：注册一个简单的问候技能
        def greet_skill(name: str = "World") -> str:
            """问候技能"""
            return f"Hello, {name}!"

        skill = Skill(
            name="greet",
            skill_type=SkillType.BUILTIN,
            description="简单的问候技能",
            handler=greet_skill,
            parameters_schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                }
            }
        )
        self.skill_manager.register_skill(skill)

        # 示例：注册一个计算技能
        def calculate_skill(a: float, b: float, op: str = "add") -> float:
            """计算技能"""
            if op == "add":
                return a + b
            elif op == "subtract":
                return a - b
            elif op == "multiply":
                return a * b
            elif op == "divide":
                return a / b
            else:
                raise ValueError(f"未知操作: {op}")

        calculate_skill_obj = Skill(
            name="calculate",
            skill_type=SkillType.BUILTIN,
            description="简单的计算技能",
            handler=calculate_skill,
            parameters_schema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                    "op": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]}
                },
                "required": ["a", "b"]
            }
        )
        self.skill_manager.register_skill(calculate_skill_obj)

        self.logger.info("内置技能已注册")

    def get_metrics(self) -> Dict[str, Any]:
        """获取指标"""
        with self._metrics_lock:
            return {
                "total_tasks": self.metrics.total_tasks,
                "completed_tasks": self.metrics.completed_tasks,
                "failed_tasks": self.metrics.failed_tasks,
                "cancelled_tasks": self.metrics.cancelled_tasks,
                "avg_task_duration": self.metrics.avg_task_duration,
                "total_duration": self.metrics.total_duration,
                "skill_calls": dict(self.metrics.skill_calls),
                "model_calls": dict(self.metrics.model_calls),
                "error_counts": dict(self.metrics.error_counts)
            }

    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "running": self._running,
            "workers": len(self._workers),
            "metrics": self.get_metrics(),
            "tasks": {
                "total": len(self.task_queue.list_tasks()),
                "pending": len(self.task_queue.list_tasks(TaskStatus.PENDING)),
                "queued": len(self.task_queue.list_tasks(TaskStatus.QUEUED)),
                "running": len(self.task_queue.list_tasks(TaskStatus.RUNNING)),
                "completed": len(self.task_queue.list_tasks(TaskStatus.COMPLETED)),
                "failed": len(self.task_queue.list_tasks(TaskStatus.FAILED))
            },
            "skills": {
                "total": len(self.skill_manager.list_skills()),
                "builtin": len(self.skill_manager.list_skills(SkillType.BUILTIN)),
                "mcp": len(self.skill_manager.list_skills(SkillType.MCP)),
                "custom": len(self.skill_manager.list_skills(SkillType.CUSTOM))
            }
        }


# =============================================================================
# 便捷函数
# =============================================================================

def create_symphony(
    config: Optional[Dict[str, Any]] = None,
    register_builtins: bool = True
) -> SymphonyCore:
    """
    创建Symphony实例

    Args:
        config: 配置字典
        register_builtins: 是否注册内置技能

    Returns:
        SymphonyCore实例
    """
    symphony = SymphonyCore(config=config)

    if register_builtins:
        symphony.register_builtin_skills()

    return symphony


# =============================================================================
# 示例用法
# =============================================================================

def example_usage():
    """示例用法"""
    print("=" * 60)
    print("🎼 Symphony 统一调度器 - 示例")
    print("=" * 60)

    # 创建Symphony实例
    symphony = create_symphony()

    try:
        # 启动调度器
        symphony.start(num_workers=2)

        # 提交一些任务
        print("\n📋 提交任务...")

        # 技能任务
        task1_id = symphony.submit_task(
            name="问候任务",
            description="测试问候技能",
            skill_name="greet",
            parameters={"name": "Symphony"},
            priority=1
        )
        print(f"   - 任务1: {task1_id} (问候)")

        # 计算任务
        task2_id = symphony.submit_task(
            name="计算任务",
            description="测试计算技能",
            skill_name="calculate",
            parameters={"a": 10, "b": 5, "op": "multiply"},
            priority=2
        )
        print(f"   - 任务2: {task2_id} (计算)")

        # 等待任务完成
        print("\n⏳ 等待任务完成...")
        time.sleep(2)

        # 检查任务状态
        print("\n📊 任务状态:")
        for task in symphony.task_queue.list_tasks():
            print(f"   - [{task.task_id}] {task.name}: {task.status.value}")
            if task.result:
                print(f"     结果: {task.result}")

        # 显示系统状态
        print("\n🎼 系统状态:")
        status = symphony.get_status()
        print(f"   - 运行中: {status['running']}")
        print(f"   - 工作线程: {status['workers']}")
        print(f"   - 总任务: {status['tasks']['total']}")
        print(f"   - 已完成: {status['tasks']['completed']}")
        print(f"   - 失败: {status['tasks']['failed']}")

        # 显示指标
        print("\n📈 指标:")
        metrics = symphony.get_metrics()
        print(f"   - 技能调用: {metrics['skill_calls']}")
        print(f"   - 平均任务耗时: {metrics['avg_task_duration']:.2f}s")

    finally:
        # 停止调度器
        symphony.stop()
        print("\n" + "=" * 60)
        print("示例完成!")
        print("=" * 60)


if __name__ == "__main__":
    example_usage()
