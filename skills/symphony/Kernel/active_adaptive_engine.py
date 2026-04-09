# -*- coding: utf-8 -*-
"""
序境系统 - 主被动自使用 + 泛处理触??+ 内协??+ 自适配 核心引擎
Active Adaptive Engine v1.0.0
"""
import os, sys, time, re, threading, json, logging
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# ==================== 枚举定义 ====================
class TriggerSource(Enum):
    PASSIVE_DIRECT = "passive_direct"       # 被动直接指令
    PASSIVE_CONTEXT = "passive_context"     # 被动上下文触??    ACTIVE_SENSE = "active_sense"           # 主动感知触发
    ACTIVE_SERVICE = "active_service"       # 主动服务触发

class TaskCategory(Enum):
    GENERAL = "general"
    CODE_DEVELOPMENT = "code_development"
    RESEARCH = "research"
    STRATEGY = "strategy"
    DATA_ANALYSIS = "data_analysis"
    CREATIVE = "creative"
    # 皇权专属任务类别
    IMPERIAL_DECREE = "imperial_decree"          # 圣旨/诏令处理
    IMPERIAL_GOVERNMENT = "imperial_government"  # 官署行政/政务处理
    IMPERIAL_HAREM = "imperial_harem"            # 后宫事务
    IMPERIAL_HISTORY = "imperial_history"        # 历史考据/礼制
    IMPERIAL_MILITARY = "imperial_military"      # 军事调度/战略
    IMPERIAL_CULTURE = "imperial_culture"        # 文化/教育/科举

class ResourcePriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

# ==================== 数据结构 ====================
@dataclass
class TriggerContext:
    source: TriggerSource
    text: str
    user_id: Optional[str] = None
    channel: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TriggerResult:
    should_trigger: bool
    confidence: float
    trigger_reason: str
    suggested_task_category: TaskCategory
    suggested_priority: ResourcePriority
    suggested_models: List[str] = field(default_factory=list)

@dataclass
class AdaptationPlan:
    task_category: TaskCategory
    priority: ResourcePriority
    selected_models: List[str]
    brain_group_size: int
    timeout: int
    strategy: str
    cost_estimate: float

# ==================== 核心引擎实现 ====================
class ActiveAdaptiveEngine:
    def __init__(self, kernel):
        self.kernel = kernel
        self.config = self._load_config()
        
        # 泛处理触发模??        self.vectorizer = TfidfVectorizer(stop_words=["??, "??, "??, "??, "??, "??, "??, "??, "??])
        self._init_trigger_corpus()
        
        # 主动感知线程
        self._active_sense_thread = None
        self._stop_event = threading.Event()
        self._context_history = []
        self._max_context_history = 100
        
        # 内协调状??        self._subsystem_load = defaultdict(float)
        self._last_coordination_time = 0
        
        # 自适配统计
        self._model_performance = {}
        self._cost_history = []
        
        # 启动主动感知
        if self.config.get("enable_active_sensing", True):
            self._start_active_sensing()
        
        logger.info("Active Adaptive Engine initialized successfully")

    def _load_config(self) -> Dict:
        """加载引擎配置"""
        default_config = {
            "trigger_threshold": 0.65,              # 触发置信度阈??            "enable_active_sensing": True,          # 启用主动感知
            "active_sensing_interval": 30,          # 主动感知间隔（秒??            "max_concurrent_tasks": 10,             # 最大并发任务数
            "qps_limit": 2,                         # QPS限制
            "cost_priority": True,                  # 成本优先模式
            "enable_logging": True,                 # 全链路日??            "default_timeout": 300,                 # 默认超时
            "min_brain_size": 1,                    # 最小脑群规??            "max_brain_size": 10,                   # 最大脑群规??        }
        config_path = os.path.join(os.path.dirname(__file__), "../config/adaptive_engine.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config, using defaults: {e}")
        return default_config

    def _init_trigger_corpus(self):
        """初始化泛触发语料??- 覆盖所有序境系统相关场??"""
        self.trigger_corpus = [
            # 系统调用相关
            "用序??, "调用序境", "序境系统", "symphony", "序境内核",
            # 能力相关
            "多智能体", "脑群协同", "群智能算??, "蚁群算法", "蜂群算法", "智慧涌现",
            # 任务场景
            "开发代??, "写代??, "debug", "代码审计", "查问??, "解决bug",
            "研究", "调研", "查资??, "分析数据", "写报??, "战略分析",
            "军事咨询", "战略规划", "方案设计", "优化", "决策支持",
            # 主动服务场景
            "提醒", "通知", "帮我", "需??, "想要", "有没??, "能不??,
            "为什??, "怎么", "如何", "是什??, "推荐", "建议",
            # 领域相关
            "唐朝", "历史", "古籍", "文学", "艺术", "哲学", "军事",
            # 皇权专属触发??            "皇帝", "皇上", "陛下", "圣旨", "诏令", "敕令", "奏折", "奏章",
            "内阁", "六部", "吏部", "户部", "礼部", "兵部", "刑部", "工部",
            "尚书", "侍郎", "巡抚", "总督", "知府", "知县", "官员", "大臣",
            "后宫", "皇后", "贵妃", "嫔妃", "太后", "太监", "宫女", "内务??,
            "科举", "殿试", "状元", "礼制", "祭祀", "宗庙", "上朝", "听政",
            "军事调度", "出征", "粮草", "边关", "海防", "屯田", "赋税", "徭役"
        ]
        self.corpus_vectors = self.vectorizer.fit_transform(self.trigger_corpus)

    # ==================== 1. 泛处理触发能??====================
    def check_trigger(self, context: TriggerContext) -> TriggerResult:
        """基于语义相似度判断是否需要触发序境系统能??"""
        # 预处理输入文??        text_clean = re.sub(r'[^\w\s\u4e00-\u9fff]', '', context.text.lower())
        
        # 计算语义相似??        input_vector = self.vectorizer.transform([text_clean])
        similarities = cosine_similarity(input_vector, self.corpus_vectors)[0]
        max_similarity = np.max(similarities)
        
        # 上下文匹配增??        context_score = self._calculate_context_score(context)
        final_confidence = min(max_similarity * 0.7 + context_score * 0.3, 1.0)
        
        # 判断是否触发
        if final_confidence >= self.config["trigger_threshold"]:
            # 识别任务类别
            task_category = self._identify_task_category(text_clean)
            # 计算优先??            priority = self._calculate_priority(context, final_confidence)
            
            return TriggerResult(
                should_trigger=True,
                confidence=final_confidence,
                trigger_reason=f"语义相似??{max_similarity:.2f} + 上下文匹??{context_score:.2f} = 总置信度 {final_confidence:.2f}",
                suggested_task_category=task_category,
                suggested_priority=priority
            )
        else:
            return TriggerResult(
                should_trigger=False,
                confidence=final_confidence,
                trigger_reason=f"置信??{final_confidence:.2f} 低于阈??{self.config['trigger_threshold']}",
                suggested_task_category=TaskCategory.GENERAL,
                suggested_priority=ResourcePriority.LOW
            )

    def _calculate_context_score(self, context: TriggerContext) -> float:
        """计算上下文匹配得??"""
        score = 0.0
        
        # 直接@或提及关键词加分
        if any(k in context.text for k in ["交交", "序境", "symphony"]):
            score += 0.4
        
        # 历史上下文相关加??        for hist in self._context_history[-5:]:
            if any(w in hist.text for w in context.text.split()[:10]):
                score += 0.2
                break
        
        # 主动感知场景加分
        if context.source == TriggerSource.ACTIVE_SENSE:
            score += 0.1
        
        return min(score, 1.0)

    def _identify_task_category(self, text: str) -> TaskCategory:
        """识别任务类别"""
        category_keywords = {
            TaskCategory.CODE_DEVELOPMENT: ["代码", "开??, "编程", "写程??, "debug", "bug", "函数", "??, "脚本", "部署"],
            TaskCategory.RESEARCH: ["研究", "调研", "查资??, "学习", "论文", "文献", "分析", "报告", "总结"],
            TaskCategory.STRATEGY: ["战略", "规划", "方案", "决策", "军事", "策略", "布局", "咨询"],
            TaskCategory.DATA_ANALYSIS: ["数据", "统计", "可视??, "报表", "图表", "计算", "分析"],
            TaskCategory.CREATIVE: ["??, "创作", "设计", "文案", "故事", "诗歌", "创意"],
            # 皇权专属类别
            TaskCategory.IMPERIAL_DECREE: ["圣旨", "诏令", "敕令", "陛下", "皇帝", "皇上", "上谕"],
            TaskCategory.IMPERIAL_GOVERNMENT: ["内阁", "六部", "吏部", "户部", "礼部", "兵部", "刑部", "工部",
                                               "尚书", "侍郎", "巡抚", "总督", "知府", "知县", "官员", "大臣",
                                               "赋税", "徭役", "赈灾", "政务", "行政", "奏折", "奏章"],
            TaskCategory.IMPERIAL_HAREM: ["后宫", "皇后", "贵妃", "嫔妃", "太后", "太监", "宫女", "内务??, "选秀"],
            TaskCategory.IMPERIAL_HISTORY: ["礼制", "祭祀", "宗庙", "科举", "殿试", "状元", "历史考据", "古籍", "典章"],
            TaskCategory.IMPERIAL_MILITARY: ["军事调度", "出征", "粮草", "边关", "海防", "屯田", "军队", "士兵", "将军"],
            TaskCategory.IMPERIAL_CULTURE: ["文化", "教育", "书院", "修史", "编书", "艺术", "礼乐"],
        }
        
        for category, keywords in category_keywords.items():
            if any(k in text for k in keywords):
                return category
        
        return TaskCategory.GENERAL

    def _calculate_priority(self, context: TriggerContext, confidence: float) -> ResourcePriority:
        """计算任务优先??"""
        if confidence >= 0.9:
            return ResourcePriority.CRITICAL
        elif confidence >= 0.8:
            return ResourcePriority.HIGH
        elif confidence >= 0.7:
            return ResourcePriority.MEDIUM
        else:
            return ResourcePriority.LOW

    # ==================== 2. 主被动自使用能力 ====================
    def process_passive_request(self, text: str, user_id: str = None, channel: str = None, metadata: Dict = None) -> Optional[Dict]:
        """处理被动请求（用户直??间接指令??"""
        context = TriggerContext(
            source=TriggerSource.PASSIVE_DIRECT if "@" in text or "交交" in text else TriggerSource.PASSIVE_CONTEXT,
            text=text,
            user_id=user_id,
            channel=channel,
            metadata=metadata or {}
        )
        
        trigger_result = self.check_trigger(context)
        if not trigger_result.should_trigger:
            logger.debug(f"Request not triggered: {trigger_result.trigger_reason}")
            return None
        
        # 保存上下??        self._context_history.append(context)
        if len(self._context_history) > self._max_context_history:
            self._context_history.pop(0)
        
        # 生成适配计划
        adaptation_plan = self.generate_adaptation_plan(trigger_result, context)
        
        # 提交任务到内??        task_id = self.kernel.submit_task(
            name=f"AutoTask_{int(time.time())}",
            prompt=text,
            task_type=trigger_result.suggested_task_category.value,
            complexity=self._map_priority_to_complexity(trigger_result.suggested_priority),
            priority=trigger_result.suggested_priority.value
        )
        
        # 协调内部模块执行
        coordination_result = self.coordinate_subsystems(task_id, adaptation_plan)
        
        return {
            "task_id": task_id,
            "trigger_confidence": trigger_result.confidence,
            "adaptation_plan": adaptation_plan.__dict__,
            "coordination_result": coordination_result
        }

    def _start_active_sensing(self):
        """启动主动感知线程"""
        def _sense_loop():
            last_qps_check = time.time()
            request_count = 0
            
            while not self._stop_event.is_set():
                try:
                    # QPS限流
                    now = time.time()
                    if now - last_qps_check >= 1:
                        request_count = 0
                        last_qps_check = now
                    if request_count >= self.config["qps_limit"]:
                        time.sleep(0.1)
                        continue
                    
                    # 主动感知逻辑
                    self._run_active_sense_cycle()
                    
                    request_count += 1
                    time.sleep(self.config["active_sensing_interval"])
                except Exception as e:
                    logger.error(f"Active sense error: {e}")
                    time.sleep(10)
        
        self._active_sense_thread = threading.Thread(target=_sense_loop, daemon=True)
        self._active_sense_thread.start()
        logger.info("Active sensing thread started")

    def _run_active_sense_cycle(self):
        """执行一次主动感知周??"""
        # 检查内存中的未处理上下??        for context in self._context_history[-3:]:
            if time.time() - context.timestamp < 300:  # 5分钟内的上下??                # 检查是否有未满足的潜在需??                potential_tasks = self._identify_potential_tasks(context)
                for task in potential_tasks:
                    trigger_result = self.check_trigger(TriggerContext(
                        source=TriggerSource.ACTIVE_SERVICE,
                        text=task["prompt"],
                        user_id=context.user_id,
                        channel=context.channel
                    ))
                    if trigger_result.should_trigger and trigger_result.confidence >= 0.75:
                        # 触发主动服务
                        logger.info(f"Active service triggered: {task['prompt']}")
                        self.process_passive_request(task["prompt"], context.user_id, context.channel)
        
        # 检查系统状态，主动优化
        if time.time() - self._last_coordination_time > 300:
            self.auto_optimize_subsystems()
            self._last_coordination_time = time.time()

    def _identify_potential_tasks(self, context: TriggerContext) -> List[Dict]:
        """识别潜在的用户需求，主动提供服务"""
        potential_tasks = []
        
        # 示例：用户提到了某个技术问题，主动查最新解决方??        if "问题" in context.text and "解决" not in context.text:
            potential_tasks.append({
                "prompt": f"帮我查找最新的关于[{context.text}]的解决方??,
                "type": "research"
            })
        
        # 示例：用户提到了待办事项，主动提??        if "明天" in context.text and "?? in context.text:
            potential_tasks.append({
                "prompt": f"帮我设置明天的提醒：{context.text}",
                "type": "reminder"
            })
        
        return potential_tasks

    # ==================== 3. 内协调能??====================
    def coordinate_subsystems(self, task_id: str, plan: AdaptationPlan) -> Dict:
        """协调内部各模块执行任??"""
        logger.info(f"Coordinating subsystems for task {task_id}")
        
        # 1. 检查各子系统负??        subsystems = self._get_available_subsystems(plan.task_category)
        
        # 2. 任务分配
        assignments = {}
        if plan.task_category in [TaskCategory.CODE_DEVELOPMENT, TaskCategory.RESEARCH]:
            if self.kernel.multi_agent:
                assignments["multi_agent"] = {"task": "orchestrate", "agents": plan.brain_group_size}
            if self.kernel.algorithm_coordinator:
                assignments["algorithm_coordinator"] = {"algorithm": "ant_colony", "task": "optimize_path"}
        elif plan.task_category == TaskCategory.STRATEGY:
            if self.kernel.wisdom_engine:
                assignments["wisdom_engine"] = {"task": "analyze_strategy"}
            if self.kernel.military_wisdom:
                assignments["military_wisdom"] = {"task": "evaluate_risk"}
        # 皇权任务专属协同逻辑
        elif plan.task_category.name.startswith("IMPERIAL_"):
            # 所有皇权任务都启用多脑协同
            if self.kernel.multi_agent:
                assignments["multi_agent"] = {"task": "imperial_orchestrate", "agents": plan.brain_group_size}
            # 政务类任务启用蚁群算法优化流??            if plan.task_category == TaskCategory.IMPERIAL_GOVERNMENT and self.kernel.algorithm_coordinator:
                assignments["algorithm_coordinator"] = {"algorithm": "ant_colony", "task": "optimize_administrative_process"}
            # 军事类任务启用军事智慧引??蜂群算法
            if plan.task_category == TaskCategory.IMPERIAL_MILITARY:
                if self.kernel.military_wisdom:
                    assignments["military_wisdom"] = {"task": "evaluate_military_risk"}
                if self.kernel.algorithm_coordinator:
                    assignments["algorithm_coordinator"] = {"algorithm": "bee_colony", "task": "optimize_military_deployment"}
            # 历史/文化类任务启用智慧引??            if plan.task_category in [TaskCategory.IMPERIAL_HISTORY, TaskCategory.IMPERIAL_CULTURE] and self.kernel.wisdom_engine:
                assignments["wisdom_engine"] = {"task": "verify_historical_facts"}
            # 诏令类任务启用全链路校验
            if plan.task_category == TaskCategory.IMPERIAL_DECREE:
                if self.kernel.wisdom_engine:
                    assignments["wisdom_engine"] = {"task": "validate_decree_propriety"}
                if self.kernel.multi_agent:
                    assignments["multi_agent"] = {"task": "cross_verify_decree", "agents": max(plan.brain_group_size, 8)}
        
        # 3. 资源调度（严格遵守QPS??限制??        resource_allocation = {
            "models": plan.selected_models,
            "timeout": plan.timeout,
            "priority": plan.priority.value,
            "qps_limit": min(self.config["qps_limit"], 2),  # 强制QPS不超??
            "cost_priority": self.config["cost_priority"],
            "enable_logging": self.config["enable_logging"]  # 全链路日志留??        }
        
        # 4. 流程衔接
        execution_flow = [
            "preprocess: model_federation.check_models",
            "execute: assigned_subsystems.run",
            "postprocess: wisdom_engine.optimize_result",
            "log: full_chain_logging.save_result",  # 强制全链路日??            "deliver: return_result"
        ]
        
        # 更新子系统负??        for subsys in assignments.keys():
            self._subsystem_load[subsys] += 0.1
        
        return {
            "status": "coordinated",
            "subsystems_assigned": list(assignments.keys()),
            "resource_allocation": resource_allocation,
            "execution_flow": execution_flow
        }

    def _get_available_subsystems(self, task_category: TaskCategory) -> List[str]:
        """获取可用的子系统列表"""
        available = []
        status = self.kernel.get_kernel_status()["subsystems"]
        for subsys, active in status.items():
            if active and self._subsystem_load[subsys] < 0.8:  # 负载低于80%可用
                available.append(subsys)
        return available

    def auto_optimize_subsystems(self) -> Dict:
        """自动优化内部子系统负载和配置"""
        logger.info("Running auto optimization for subsystems")
        
        # 重置过载的子系统负载
        for subsys, load in self._subsystem_load.items():
            if load > 0.9:
                self._subsystem_load[subsys] = 0.3
                logger.info(f"Reset load for {subsys}")
        
        # 触发内核进化
        if self.kernel.config.enable_auto_evolution:
            self.kernel.evolve()
        
        return {"status": "optimized", "subsystems_optimized": len([k for k, v in self._subsystem_load.items() if v < 0.5])}

    # ==================== 4. 自适配能力 ====================
    def generate_adaptation_plan(self, trigger_result: TriggerResult, context: TriggerContext) -> AdaptationPlan:
        """生成自适应执行计划"""
        task_category = trigger_result.suggested_task_category
        priority = trigger_result.suggested_priority
        
        # 1. 选择模型（成本优先）
        selected_models = self._select_optimal_models(task_category, priority)
        
        # 2. 确定脑群规模
        brain_size = self._calculate_brain_group_size(task_category, priority)
        
        # 3. 确定超时时间
        timeout = self._calculate_timeout(task_category, priority)
        
        # 4. 选择执行策略
        strategy = self._select_execution_strategy(task_category, priority)
        
        # 5. 估算成本
        cost_estimate = self._estimate_cost(selected_models, brain_size, timeout)
        
        return AdaptationPlan(
            task_category=task_category,
            priority=priority,
            selected_models=selected_models,
            brain_group_size=brain_size,
            timeout=timeout,
            strategy=strategy,
            cost_estimate=cost_estimate
        )

    def _select_optimal_models(self, task_category: TaskCategory, priority: ResourcePriority) -> List[str]:
        """选择最优模型（成本优先 + 皇权官署匹配??"""
        # 成本优先排序：免费模??> 低成本模??> 高成本模??        model_preferences = {
            TaskCategory.CODE_DEVELOPMENT: ["deepseek-ai/deepseek-v3.2", "qwen/qwen2.5-72b-instruct", "glm-4-flash"],
            TaskCategory.RESEARCH: ["qwen/qwen2.5-72b-instruct", "meta/llama3.1-70b-instruct", "glm-4-flash"],
            TaskCategory.STRATEGY: ["meta/llama3.1-405b-instruct", "deepseek-ai/deepseek-v3.2", "glm-4-flash"],
            TaskCategory.GENERAL: ["glm-4-flash", "deepseek-ai/deepseek-v3", "qwen/qwen2.5-72b-instruct"],
            # 皇权专属模型匹配规则（官署对应专业模型）
            TaskCategory.IMPERIAL_DECREE: ["meta/llama3.1-405b-instruct", "deepseek-ai/deepseek-v3.2"],  # 诏令用最高精度模??            TaskCategory.IMPERIAL_GOVERNMENT: ["qwen/qwen2.5-72b-instruct", "glm-4-flash"],  # 政务用中文优化模??            TaskCategory.IMPERIAL_HAREM: ["glm-4-flash", "qwen/qwen2.5-72b-instruct"],  # 后宫事务优先低成??            TaskCategory.IMPERIAL_HISTORY: ["qwen/qwen2.5-72b-instruct", "meta/llama3.1-70b-instruct"],  # 历史考据用专业大模型
            TaskCategory.IMPERIAL_MILITARY: ["meta/llama3.1-405b-instruct", "deepseek-ai/deepseek-v3.2"],  # 军事用高精度战略模型
            TaskCategory.IMPERIAL_CULTURE: ["deepseek-ai/deepseek-v3.2", "qwen/qwen2.5-72b-instruct"],  # 文化用创??中文模型
        }
        
        preferred = model_preferences.get(task_category, model_preferences[TaskCategory.GENERAL])
        
        # 只返回在线的模型
        online_models = [m["name"] for m in self.kernel._get_online_models_from_federation()]
        selected = [m for m in preferred if m in online_models]
        
        # 兜底用免费模??        if not selected:
            selected = ["glm-4-flash"]
        
        return selected[:2]  # 最多??个模??符合QPS??限制

    def _calculate_brain_group_size(self, task_category: TaskCategory, priority: ResourcePriority) -> int:
        """计算脑群规模"""
        base_size = {
            ResourcePriority.LOW: 1,
            ResourcePriority.MEDIUM: 2,
            ResourcePriority.HIGH: 4,
            ResourcePriority.CRITICAL: 8
        }[priority]
        
        # 复杂任务增加规模
        if task_category in [TaskCategory.STRATEGY, TaskCategory.CODE_DEVELOPMENT]:
            base_size = min(base_size * 1.5, self.config["max_brain_size"])
        
        return int(base_size)

    def _calculate_timeout(self, task_category: TaskCategory, priority: ResourcePriority) -> int:
        """计算任务超时时间"""
        base_timeout = {
            ResourcePriority.LOW: 60,
            ResourcePriority.MEDIUM: 120,
            ResourcePriority.HIGH: 300,
            ResourcePriority.CRITICAL: 600
        }[priority]
        
        # 研究类任务增加超??        if task_category == TaskCategory.RESEARCH:
            base_timeout *= 2
        
        return base_timeout

    def _select_execution_strategy(self, task_category: TaskCategory, priority: ResourcePriority) -> str:
        """选择执行策略"""
        if priority >= ResourcePriority.HIGH:
            return "parallel"  # 高优先级并行执行
        elif task_category in [TaskCategory.CODE_DEVELOPMENT, TaskCategory.RESEARCH]:
            return "sequential_validation"  # 开??研究类顺序验??        else:
            return "fast_response"  # 其他快速响??
    def _estimate_cost(self, models: List[str], brain_size: int, timeout: int) -> float:
        """估算任务成本"""
        # 简化成本计算：0.001??1000token 基础??        model_cost_multipliers = {
            "glm-4-flash": 0,  # 免费
            "deepseek-ai/deepseek-v3": 0.5,
            "qwen/qwen2.5-72b-instruct": 0.8,
            "meta/llama3.1-70b-instruct": 1.0,
            "meta/llama3.1-405b-instruct": 2.5,
        }
        
        total = 0.0
        for model in models:
            total += model_cost_multipliers.get(model, 0.5)
        
        total *= brain_size * (timeout / 60) * 0.01
        return round(total, 4)

    def _map_priority_to_complexity(self, priority: ResourcePriority) -> str:
        """将优先级映射为任务复杂度"""
        mapping = {
            ResourcePriority.LOW: "simple",
            ResourcePriority.MEDIUM: "medium",
            ResourcePriority.HIGH: "high",
            ResourcePriority.CRITICAL: "complex"
        }
        return mapping[priority]

    # ==================== 工具方法 ====================
    def get_engine_status(self) -> Dict:
        """获取引擎状??"""
        return {
            "version": "1.0.0",
            "config": self.config,
            "active_sensing_running": self._active_sense_thread is not None and self._active_sense_thread.is_alive(),
            "context_history_count": len(self._context_history),
            "subsystem_load": dict(self._subsystem_load),
            "trigger_threshold": self.config["trigger_threshold"],
            "qps_limit": self.config["qps_limit"]
        }

    def stop(self):
        """停止引擎"""
        self._stop_event.set()
        if self._active_sense_thread:
            self._active_sense_thread.join(timeout=5)
        logger.info("Active Adaptive Engine stopped")

