# -*- coding: utf-8 -*-
"""序境进化内核 Evolution Kernel v4.5.0 - 延迟加载优化"""
import sys, os, uuid, time, threading, logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# ==================== 延迟加载 ====================
class LazyLoader:
    """
    延迟加载 - 将模块实例化延迟到首次访问时
    支持后台预热机制，首次调用时在后台异步预加载
    """
    def __init__(self, name: str, loader_fn: Callable, preload: bool = False):
        self.name = name
        self._loader_fn = loader_fn
        self._instance = None
        self._loading = False
        self._lock = threading.Lock()
        self._preload_thread: Optional[threading.Thread] = None
        # 标记是否已完成首次加载（用于预热状态检测）
        self._warmed = False
        
        if preload:
            self._start_preload()
    
    def _start_preload(self):
        """启动后台预热线程"""
        if self._preload_thread is None or not self._preload_thread.is_alive():
            self._preload_thread = threading.Thread(
                target=self._background_load, 
                name=f"LazyLoader-{self.name}",
                daemon=True
            )
            self._preload_thread.start()
    
    def _background_load(self):
        """后台加载实现"""
        try:
            instance = self._loader_fn()
            with self._lock:
                self._instance = instance
                self._warmed = True
                logger.info(f"LazyLoader [{self.name}] 后台预热完成")
        except Exception as e:
            logger.warning(f"LazyLoader [{self.name}] 后台预热失败: {e}")
    
    def _ensure_loaded(self):
        """确保已加载（线程安全）"""
        if self._instance is not None:
            return self._instance
        
        if self._loading:
            # 等待其他线程完成加载
            while self._loading:
                time.sleep(0.01)
            return self._instance
        
        with self._lock:
            if self._instance is None and not self._loading:
                self._loading = True
                try:
                    self._instance = self._loader_fn()
                    self._warmed = True
                    logger.info(f"LazyLoader [{self.name}] 首次加载完成")
                finally:
                    self._loading = False
        return self._instance
    
    def get(self):
        """同步获取实例（阻塞直到加载完成）"""
        return self._ensure_loaded()
    
    @property
    def instance(self):
        """属性访问方式"""
        return self._ensure_loaded()
    
    @property
    def is_warmed(self) -> bool:
        """检查是否已完成预热"""
        return self._warmed
    
    @property
    def is_loaded(self) -> bool:
        """检查是否已加载实例"""
        return self._instance is not None
    
    def preload(self):
        """手动触发预热（异步）"""
        self._start_preload()

DATA_DIR = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data'
DB_PATH = f'{DATA_DIR}/symphony_working.db'  # 统一数据源路径
KERNEL_DB_PATH = f'{DATA_DIR}/symphony_kernel.db'  # 内核专用数据库（独立，无锁）
KERNEL_VERSION = "4.5.0"

# ==================== 导入 ====================
# Kernel所在目录作为模块搜索路径（支持 relative imports）
_KERNEL_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _KERNEL_DIR)

ALGORITHMS_AVAILABLE = False
EVOLUTION_V2_AVAILABLE = False
MULTI_AGENT_AVAILABLE = False
WISDOM_AVAILABLE = False
MILITARY_AVAILABLE = False
SWARM_AVAILABLE = False

try:
    from intelligent_strategy_scheduler import IntelligentStrategyScheduler, TaskComplexity, TaskInfo
    from model_federation import ModelFederation, FederationRequest
    ALGORITHMS_AVAILABLE = True
    logger.info("Core algorithms loaded")
except ImportError as e:
    logger.warning("Core algorithms not available: %s", e)

# evolution子模块存在编码问题，暂时禁用，后续修复
try:
    from multi_agent.multi_agent_orchestrator import MultiAgentCoordinator, AgentRole, OrchestrationMode
    MULTI_AGENT_AVAILABLE = True
    logger.info("Multi-agent orchestration loaded")
except ImportError as e:
    logger.warning(f"Multi-agent not available: {e}")
    MULTI_AGENT_AVAILABLE = False
EVOLUTION_V2_AVAILABLE = False

try:
    from adaptive_algorithm_coordinator import AdaptiveAlgorithmCoordinator, AlgorithmCategory
    SWARM_AVAILABLE = True
    logger.info("Swarm/ACO loaded")
except ImportError as e:
    logger.warning(f"Swarm not available: {e}")

try:
    from wisdom_engine import WisdomEmergenceEngine
    WISDOM_AVAILABLE = True
    logger.info("Wisdom engine loaded")
except ImportError as e:
    logger.warning(f"Wisdom engine not available: {e}")

# military_wisdom模块存在编码问题，暂时禁用，后续修复
# try:
#     from military_wisdom import MilitaryStrategyAdvisor, StrategicDecisionEngine
#     MILITARY_AVAILABLE = True
#     logger.info("Military wisdom loaded")
# except ImportError as e:
#     logger.warning(f"Military wisdom not available: {e}")
MILITARY_AVAILABLE = False

# ==================== 数据结构 ====================
class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class EvolutionPhase(Enum):
    INITIALIZATION = "initialization"
    OPTIMIZATION = "optimization"
    EVALUATION = "evaluation"
    INTEGRATION = "integration"
    DELIVERY = "delivery"

@dataclass
class KernelTask:
    id: str
    name: str
    prompt: str
    task_type: str
    complexity: str
    priority: int = 5
    status: TaskStatus = TaskStatus.PENDING
    assigned_models: List[str] = field(default_factory=list)
    strategy_used: str = ""
    result: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None

@dataclass
class KernelConfig:
    version: str = KERNEL_VERSION
    max_concurrent_tasks: int = 50
    default_timeout: int = 120
    enable_auto_evolution: bool = True
    enable_federation: bool = True
    enable_ant_colony: bool = True

# ==================== 进化内核 ====================
class EvolutionKernel:
    def __init__(self, config: KernelConfig = None):
        self.config = config or KernelConfig()
        self.kernel_id = str(uuid.uuid4())[:8]
        self._init_start = time.time()

        # ========== 核心组件（同步加载，快速）==========
        self.scheduler = None
        self.federation = None
        if ALGORITHMS_AVAILABLE:
            try:
                self.federation = ModelFederation()  # 先初始化 federation
                # scheduler 持有 federation 引用，作为唯一模型状态权威
                self.scheduler = IntelligentStrategyScheduler(federation=self.federation)
                logger.info("Scheduler + Federation initialized (unified)")
            except Exception as e:
                logger.warning("Core init: %s", e)

        # ========== 延迟加载子系统（后台预热）=========
        self._lazy_loaders: Dict[str, LazyLoader] = {}
        
        def _try_init_db_subsystem(subsys_name: str, cls, db_path_arg: str):
            """尝试初始化DB子系统，锁住时自动降级到:memory:"""
            try:
                return cls(db_path_arg)
            except Exception as e:
                if "WinError 183" in str(e) or "file already exists" in str(e).lower():
                    logger.warning(f"{subsys_name}: 文件被锁，降级到:memory:模式")
                    try:
                        return cls(":memory:")
                    except Exception as e2:
                        logger.warning(f"{subsys_name} :memory:模式也失败: {e2}")
                        return None
                else:
                    logger.warning(f"{subsys_name}: {e}")
                    return None

        # 延迟加载：SelfEvolutionV2
        if EVOLUTION_V2_AVAILABLE:
            self._lazy_loaders['self_evolution_v2'] = LazyLoader(
                'SelfEvolutionV2',
                lambda: _try_init_db_subsystem("SelfEvolutionV2", SelfEvolutionV2, KERNEL_DB_PATH),
                preload=True
            )
        
        # 延迟加载：AgentMemoryLayer
        if EVOLUTION_V2_AVAILABLE:
            self._lazy_loaders['agent_memory'] = LazyLoader(
                'AgentMemoryLayer',
                lambda: _try_init_db_subsystem("AgentMemoryLayer", AgentMemoryLayer, KERNEL_DB_PATH),
                preload=True
            )
        
        # 延迟加载：MultiAgentCoordinator
        if EVOLUTION_V2_AVAILABLE:
            self._lazy_loaders['multi_agent'] = LazyLoader(
                'MultiAgentCoordinator',
                lambda: _try_init_db_subsystem("MultiAgentCoordinator", MultiAgentCoordinator, KERNEL_DB_PATH),
                preload=True
            )
        
        # 延迟加载：AdaptiveAlgorithmCoordinator
        if SWARM_AVAILABLE:
            self._lazy_loaders['algorithm_coordinator'] = LazyLoader(
                'AlgorithmCoordinator',
                lambda: AdaptiveAlgorithmCoordinator(),
                preload=True
            )
        
        # 延迟加载：WisdomEmergenceEngine
        if WISDOM_AVAILABLE:
            self._lazy_loaders['wisdom_engine'] = LazyLoader(
                'WisdomEngine',
                lambda: WisdomEmergenceEngine(),
                preload=True
            )
        
        # 延迟加载：MilitaryStrategyAdvisor
        if MILITARY_AVAILABLE:
            self._lazy_loaders['military_wisdom'] = LazyLoader(
                'MilitaryWisdom',
                lambda: MilitaryStrategyAdvisor(),
                preload=True
            )

        # 任务队列
        self.task_queue = deque(maxlen=10000)
        self.active_tasks: Dict[str, KernelTask] = {}
        self.completed_tasks = deque(maxlen=1000)
        self._lock = threading.Lock()
        self.evolution_phase = EvolutionPhase.INITIALIZATION
        self.evolution_count = 0
        self._total_tasks = 0
        self._successful_tasks = 0
        self._failed_tasks = 0

        init_time = time.time() - self._init_start
        logger.info(f"Evolution Kernel {KERNEL_VERSION} ready (ID: {self.kernel_id}) - 启动耗时: {init_time:.3f}s")

    def _get_lazy(self, name: str):
        """获取延迟加载的实例"""
        if name in self._lazy_loaders:
            return self._lazy_loaders[name].get()
        return None

    @property
    def self_evolution_v2(self):
        return self._get_lazy('self_evolution_v2')
    
    @property
    def agent_memory(self):
        return self._get_lazy('agent_memory')
    
    @property
    def multi_agent(self):
        return self._get_lazy('multi_agent')
    
    @property
    def algorithm_coordinator(self):
        return self._get_lazy('algorithm_coordinator')
    
    @property
    def wisdom_engine(self):
        return self._get_lazy('wisdom_engine')
    
    @property
    def military_wisdom(self):
        return self._get_lazy('military_wisdom')

    def submit_task(self, name: str, prompt: str, task_type: str = "general",
                   complexity: str = "medium", priority: int = 5) -> str:
        task_id = str(uuid.uuid4())[:12]
        task = KernelTask(id=task_id, name=name, prompt=prompt,
                         task_type=task_type, complexity=complexity, priority=priority)
        with self._lock:
            self.task_queue.append(task)
        logger.info(f"Task submitted: {task_id} ({name})")
        return task_id

    def submit_batch(self, tasks: List[Dict]) -> List[str]:
        return [self.submit_task(t["name"], t["prompt"], t.get("task_type", "general"),
                    t.get("complexity", "medium"), t.get("priority", 5)) for t in tasks]

    def _execute_task(self, task: KernelTask) -> KernelTask:
        """
        执行任务 - federation 已注入scheduler，两套状态合二为一
        """
        task.status = TaskStatus.RUNNING
        start = time.time()
        try:
            if self.scheduler:
                complexity = getattr(TaskComplexity, complexity_map(task.complexity), TaskComplexity.MEDIUM)
                
                # 调度器内部直接读federation健康状态，无冗余判断
                result = self.scheduler.schedule(
                    TaskInfo(id=task.id, prompt=task.prompt, task_type=task.task_type,
                            complexity=complexity, priority=task.priority),
                    None  # federation 已通过 __init__ 注入，不再需要在此传递
                )
                
                if result.success:
                    # 执行前验证：用 federation 确认模型仍然健康
                    model_ids = [m.id for m in result.selected_models]
                    valid_ids, invalid_ids = self.scheduler.validate_models(model_ids)
                    if invalid_ids:
                        task.status = TaskStatus.FAILED
                        task.error = f"[整合验证] 模型失效: {invalid_ids}"
                        return task
                    task.assigned_models = [m.name for m in result.selected_models]
                    task.strategy_used = result.metrics.get('strategy', 'unknown')
                    task.result = f"Strategy: {task.strategy_used}"
                    task.status = TaskStatus.COMPLETED
                else:
                    task.status = TaskStatus.FAILED
                    task.error = result.error
            else:
                task.result = "No scheduler available"
                task.status = TaskStatus.COMPLETED
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            logger.error(f"Task {task.id} error: {e}")
        task.execution_time = time.time() - start
        task.completed_at = time.time()
        return task

    def process_tasks(self, max_workers: int = None) -> Dict:
        max_workers = max_workers or self.config.max_concurrent_tasks
        with self._lock:
            pending = [t for t in self.task_queue if t.status == TaskStatus.PENDING]
        if not pending:
            return {"status": "no_tasks"}
        logger.info(f"Processing {len(pending)} tasks...")
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = [ex.submit(self._execute_task, t) for t in pending]
            completed = [f.result() for f in as_completed(futures)]
        with self._lock:
            for task in completed:
                self.task_queue = deque([t for t in self.task_queue if t.id != task.id], maxlen=10000)
                self.active_tasks[task.id] = task
                self.completed_tasks.append(task)
                self._total_tasks += 1
                if task.status == TaskStatus.COMPLETED:
                    self._successful_tasks += 1
                else:
                    self._failed_tasks += 1
        if self.config.enable_auto_evolution:
            self.evolve()
        return {"processed": len(completed), "success": sum(1 for t in completed if t.status == TaskStatus.COMPLETED),
                "failed": sum(1 for t in completed if t.status == TaskStatus.FAILED)}

    def evolve(self) -> Dict:
        self.evolution_count += 1
        phases = list(EvolutionPhase)
        idx = min(self.evolution_count // 10, len(phases) - 1)
        self.evolution_phase = phases[idx]
        if self.scheduler:
            try:
                self.scheduler.evolve()
            except:
                pass
        logger.info(f"Evolution #{self.evolution_count} ({self.evolution_phase.value})")
        return {"count": self.evolution_count, "phase": self.evolution_phase.value}

    # V2.0接口
    def evolve_v2(self, task: Dict, strategy: str = "auto") -> Dict:
        if not self.self_evolution_v2:
            return {"status": "unavailable", "reason": "SelfEvolutionV2 not initialized"}
        try:
            return self.self_evolution_v2.evolve(task, strategy)
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def multi_agent_task(self, task: Dict, mode=None) -> Dict:
        if not self.multi_agent:
            return {"status": "unavailable"}
        try:
            return self.multi_agent.execute_task(task, mode or OrchestrationMode.CREW_SEQUENTIAL)
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def memory_search(self, query: str, top_k: int = 10) -> List[Dict]:
        if not self.agent_memory:
            return []
        try:
            q = MemoryQuery(query_text=query, storage_type=MemoryStorageType.HYBRID_STORE, top_k=top_k)
            results = self.agent_memory.retrieve(q)
            return [{"id": b.id, "content": b.content[:200]} for b in results]
        except:
            return []

    def wisdom_observe(self, source: str, metric: str, value: float, tags: Dict = None):
        if self.wisdom_engine:
            self.wisdom_engine.observe(source, metric, value, tags or {})

    def wisdom_analyze(self, task: str = None) -> Dict:
        if not self.wisdom_engine:
            return {"error": "not initialized"}
        return self.wisdom_engine.analyze_task(task or "general")

    def military_strategy(self) -> Dict:
        if not self.wisdom_engine:
            return {"error": "not initialized"}
        return self.wisdom_engine.military_strategy_analyze(self.get_kernel_status())

    def get_kernel_status(self) -> Dict:
        subs = {
            # 核心（同步加载）
            "scheduler": self.scheduler is not None,
            "federation": self.federation is not None,
            # 延迟加载子系统（检查是否已加载）
            "self_evolution_v2": 'self_evolution_v2' in self._lazy_loaders,
            "agent_memory": 'agent_memory' in self._lazy_loaders,
            "multi_agent": 'multi_agent' in self._lazy_loaders,
            "algorithm_coordinator": 'algorithm_coordinator' in self._lazy_loaders,
            "wisdom_engine": 'wisdom_engine' in self._lazy_loaders,
            "military_wisdom": 'military_wisdom' in self._lazy_loaders,
        }
        # 实际活跃 = 核心已加载 + 延迟加载器已预热
        core_active = sum(1 for k, v in subs.items() if k in ('scheduler', 'federation') and v)
        lazy_warmed = sum(1 for k in subs if k not in ('scheduler', 'federation') 
                         and self._lazy_loaders.get(k) and self._lazy_loaders[k].is_warmed)
        active = core_active + lazy_warmed
        
        # 预热进度
        warm_status = {k: (self._lazy_loaders[k].is_warmed if k in self._lazy_loaders else False) 
                      for k in subs if k not in ('scheduler', 'federation')}
        
        return {
            "kernel_id": self.kernel_id,
            "version": KERNEL_VERSION,
            "evolution_count": self.evolution_count,
            "phase": self.evolution_phase.value,
            "total_tasks": self._total_tasks,
            "successful_tasks": self._successful_tasks,
            "failed_tasks": self._failed_tasks,
            "active_subsystems": active,
            "total_subsystems": len(subs),
            "subsystems": subs,
            "warmup_status": warm_status,
        }

    def health_check(self) -> Dict:
        status = self.get_kernel_status()
        return {
            "status": "healthy" if status["active_subsystems"] >= 5 else "degraded",
            "active": status["active_subsystems"],
            "total": status["total_subsystems"],
        }

    def quick_test(self) -> Dict:
        logger.info("Quick test...")
        self.submit_task("test", "hello world", "general", "simple")
        result = self.process_tasks(max_workers=2)
        health = self.health_check()
        return {"result": result, "health": health}


def complexity_map(c: str):
    mapping = {"simple": "SIMPLE", "low": "LOW", "medium": "MEDIUM", "high": "HIGH", "complex": "COMPLEX", "extreme": "EXTREME"}
    return mapping.get(c.lower(), "MEDIUM")


_kernel_instance = None
_kernel_lock = threading.Lock()


def get_evolution_kernel(config: KernelConfig = None) -> EvolutionKernel:
    global _kernel_instance
    if _kernel_instance is None:
        with _kernel_lock:
            if _kernel_instance is None:
                _kernel_instance = EvolutionKernel(config)
    return _kernel_instance


if __name__ == "__main__":
    print("=" * 60)
    print(" 序境进化内核 v4.5.0 - 纯净版")
    print("=" * 60)
    kernel = get_evolution_kernel()
    status = kernel.get_kernel_status()
    print("Kernel ID: " + status["kernel_id"])
    print("Version: " + status["version"])
    print("Active subsystems: " + str(status["active_subsystems"]) + "/" + str(status["total_subsystems"]))
    print()
    print("Subsystems:")
    for name, active in sorted(status["subsystems"].items()):
        icon = "[OK]" if active else "[--]"
        print("  " + icon + " " + name)
    print()
    health = kernel.health_check()
    print("Health: " + health["status"])
    print("=" * 60)
