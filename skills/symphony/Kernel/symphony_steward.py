#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
symphony_steward.py - 序境管家 内核级AI机器人
=============================

**定位**：从内到外管理整个序境内核的AI机器人
- 内核状态全监控管理
- 专用模型自适应适配
- 外部智能体握手协作接口
- 多脑多模型全算力调度

**层级**：内核级核心模块，运行在序境内核最顶层
**设计者**：智慧觉醒引擎（融合东方智慧+兵家战略+现代算法）
"""

import sys
import os
import time
import json
from typing import Optional, Dict, List, Tuple, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime

# 导入内核基础模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .bypass_protection import protected_function
from .provider_health_checker import ProviderHealthChecker, ProviderHealth, print_health_report
# 导入序境调度器 - 用于独立调用配置表中的模型
from symphony_scheduler import get_enabled_providers, get_suitable_model, call_model

# 类型定义
@dataclass
class KernelModuleInfo:
    """内核模块信息"""
    name: str
    path: str
    version: str
    is_loaded: bool
    last_check: float = 0.0
    health_score: float = 1.0
    errors: List[str] = field(default_factory=list)

@dataclass
class ModelCapability:
    """模型能力画像（专用模型适配）"""
    model_id: str
    provider: str
    model_type: str
    context_window: int
    is_free: bool
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    avg_latency: float = 0.0
    success_rate: float = 0.5
    last_used: float = 0.0
    use_count: int = 0

@dataclass
class ExternalAgentInfo:
    """外部智能体信息（协作握手）"""
    agent_id: str
    agent_name: str
    capabilities: List[str]
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    last_handshake: float = 0.0
    is_alive: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class KernelStatusReport:
    """全内核状态报告"""
    timestamp: float
    total_modules: int
    loaded_modules: int
    healthy_modules: int
    failed_modules: int
    providers_health: Dict[str, str]
    total_models: int
    enabled_models: int
    overall_health_score: float
    recommendations: List[str]
    errors: List[str]

class SymphonySteward:
    """
    **序境管家** - 内核级AI机器人
    
    职责：
    1. 从内到外管理整个序境内核（模块加载/健康检查/状态监控）
    2. 专用模型适配（根据任务类型自动选择最优模型）
    3. 外部智能体协作（标准握手协议+任务分发+结果回流）
    4. 全量多脑多模型调度（顶级算力聚合）
    """
    
    def __init__(self):
        self.modules: Dict[str, KernelModuleInfo] = {}
        self.model_capabilities: Dict[str, ModelCapability] = {}
        self.external_agents: Dict[str, ExternalAgentInfo] = {}
        self.start_time: float = time.time()
        self.is_initialized: bool = False
        self._register_core_modules()
    
    def _register_core_modules(self) -> None:
        """注册所有核心内核模块"""
        core_modules = [
            ("wisdom_engine", "Kernel/wisdom_engine.py", "1.2.0"),
            ("bypass_protection", "Kernel/bypass_protection.py", "1.0.0"),
            ("code_auditor", "Kernel/code_auditor.py", "1.0.0"),
            ("provider_health_checker", "Kernel/provider_health_checker.py", "1.1.0"),
            ("tavily_mcp_search", "Kernel/tavily_mcp_search.py", "1.0.0"),
            ("symphony_steward", "Kernel/symphony_steward.py", "1.0.0"),
            ("evolution_kernel", "Kernel/evolution_kernel.py", "1.0.0"),
            ("intelligent_strategy_scheduler", "Kernel/intelligent_strategy_scheduler.py", "1.0.0"),
        ]
        
        for name, path, version in core_modules:
            full_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                path
            )
            exists = os.path.exists(full_path)
            self.modules[name] = KernelModuleInfo(
                name=name,
                path=full_path,
                version=version,
                is_loaded=exists
            )
    
    @protected_function
    def bootstrap(self) -> bool:
        """
        启动序境管家（引导启动）
        返回：是否启动成功
        """
        print("🚀 序境管家 启动中...")
        print(f"📋 注册核心模块: {len(self.modules)} 个")
        
        # 检查所有核心模块
        failed = []
        for name, module in self.modules.items():
            if not module.is_loaded:
                failed.append(name)
                module.health_score = 0.0
            else:
                module.health_score = 1.0
        
        if failed:
            print(f"⚠️  核心模块缺失: {failed}")
        else:
            print("✅ 所有核心模块就绪")
        
        # 初始化模型能力画像
        self._init_model_capabilities()
        
        # 加载模型配置表中所有已启用模型
        # 这样序境管家就能独立使用任何配置表中的模型思考
        loaded_count = self.load_all_enabled_models()
        print(f"📋 已从模型配置表加载 {loaded_count} 个已启用模型")
        
        self.is_initialized = True
        print(f"🎉 序境管家 启动完成！耗时: {time.time() - self.start_time:.2f}s")
        return len(failed) == 0
    
    def _init_model_capabilities(self) -> None:
        """初始化常见模型能力画像（专用模型适配）"""
        # 基于领域知识预定义能力画像
        # 实际运行会根据调用统计更新
        
        capabilities = [
            # 阿里云百炼
            ("qwen2.5-7b-instruct-1m", "aliyun", "chat", 1048576, True,
             ["通用对话", "长文本处理", "代码", "思考"],
             ["复杂推理", "高精度创作"]),
            ("qwen2.5-14b-instruct-1m", "aliyun", "chat", 1048576, False,
             ["通用对话", "推理", "创作", "长文本"],
             []),
            ("text-embedding-v3", "aliyun", "embedding", 0, False,
             ["向量嵌入", "语义检索"],
             []),
            
            # MiniMax
            ("MiniMax-M2.7", "minimax", "chat", 204800, False,
             ["长对话", "创作", "角色扮演"],
             []),
            ("MiniMax-M2.5", "minimax", "chat", 204800, False,
             ["快速响应", "对话"],
             ["长文本"]),
            
            # 智谱AI
            ("glm-4-flash", "zhipu", "chat", 128000, True,
             ["快速响应", "通用对话", "免费"],
             []),
            ("glm-3-turbo-free", "zhipu", "chat", 128000, True,
             ["通用对话", "免费"],
             ["速度较慢"]),
            ("embedding-2", "zhipu", "embedding", 0, True,
             ["向量嵌入", "免费"],
             []),
        ]
        
        for model_id, provider, model_type, ctx, free, strengths, weaknesses in capabilities:
            self.model_capabilities[model_id] = ModelCapability(
                model_id=model_id,
                provider=provider,
                model_type=model_type,
                context_window=ctx,
                is_free=free,
                strengths=strengths,
                weaknesses=weaknesses
            )
    
    @protected_function
    def check_all_modules(self) -> Tuple[int, int, List[str]]:
        """
        检查所有内核模块健康状态
        返回：(总模块数, 健康模块数, 错误列表)
        """
        if not self.is_initialized:
            raise RuntimeError("序境管家未初始化，请先调用 bootstrap()")
        
        errors = []
        healthy_count = 0
        
        for name, module in self.modules.items():
            if not os.path.exists(module.path):
                error = f"模块 {name} 文件不存在: {module.path}"
                errors.append(error)
                module.errors.append(error)
                module.health_score = 0.0
                continue
            
            # 尝试导入检查
            try:
                if name == "wisdom_engine":
                    from . import wisdom_engine
                elif name == "bypass_protection":
                    from . import bypass_protection
                elif name == "code_auditor":
                    from . import code_auditor
                elif name == "provider_health_checker":
                    from . import provider_health_checker
                elif name == "tavily_mcp_search":
                    from . import tavily_mcp_search
                module.last_check = time.time()
                module.health_score = 1.0
                healthy_count += 1
            except Exception as e:
                error = f"模块 {name} 导入失败: {str(e)}"
                errors.append(error)
                module.errors.append(error)
                module.health_score = 0.0
        
        return len(self.modules), healthy_count, errors
    
    @protected_function
    def select_best_model(self, task_type: str, required_context: int = 4098, 
                         prefer_free: bool = True) -> Optional[ModelCapability]:
        """
        专用模型适配：根据任务类型选择最佳模型
        兵法思想：知己知彼，百战不殆
        """
        candidates: List[ModelCapability] = []
        
        for _, cap in self.model_capabilities.items():
            if cap.model_type != task_type:
                continue
            if cap.context_window < required_context:
                continue
            if prefer_free and not cap.is_free:
                continue
            candidates.append(cap)
        
        if not candidates:
            # 放宽免费限制再找
            for _, cap in self.model_capabilities.items():
                if cap.model_type != task_type:
                    continue
                if cap.context_window < required_context:
                    continue
                candidates.append(cap)
        
        if not candidates:
            return None
        
        # 兵法排序：成功率优先 → 免费优先 → 大上下文优先 →  latency优先
        def sort_key(cap: ModelCapability) -> Tuple[float, int, int, float]:
            return (
                -cap.success_rate,  # 成功率高先试
                0 if cap.is_free else 1,  # 免费优先
                -cap.context_window,  # 大上下文优先
                cap.avg_latency,  # 延迟低优先
            )
        
        candidates.sort(key=sort_key)
        selected = candidates[0]
        selected.last_used = time.time()
        selected.use_count += 1
        return selected
    
    @protected_function
    def update_model_performance(self, model_id: str, success: bool, latency: float) -> None:
        """更新模型性能统计（滚动更新）"""
        if model_id not in self.model_capabilities:
            return
        
        cap = self.model_capabilities[model_id]
        # 滚动平均更新
        alpha = 0.1  # 学习率
        old_success = cap.success_rate
        old_latency = cap.avg_latency
        
        cap.success_rate = (1 - alpha) * old_success + alpha * (1.0 if success else 0.0)
        if cap.avg_latency > 0:
            cap.avg_latency = (1 - alpha) * old_latency + alpha * latency
        else:
            cap.avg_latency = latency
    
    # === 独立模型思考（直接使用序境配置表中的模型） ===
    
    @protected_function
    def steward_think(self, prompt: str, task_type: str = "chat", 
                     required_context: int = 4098, prefer_free: bool = True) -> Optional[str]:
        """
        序境管家独立思考：直接使用序境模型配置表中的模型进行思考
        
        功能：
        - 自动从模型配置表选择最适合任务的模型
        - 通过序境核心调度器直接调用
        - 自动更新模型性能统计
        - 不依赖外部，完全使用序境内部配置
        
        Args:
            prompt: 思考提示
            task_type: 任务类型 (chat/text/embedding)
            required_context: 需要的最小上下文窗口
            prefer_free: 是否优先选择免费模型
            
        Returns:
            模型思考结果，失败返回 None
        """
        start_time = time.time()
        
        # 1. 获取最佳模型
        selected = self.select_best_model(task_type, required_context, prefer_free)
        if selected is None:
            # 直接调用调度器找适合模型
            providers = get_enabled_providers()
            selected_model = get_suitable_model(providers, task_type)
            if selected_model is None:
                return None
            # 创建临时能力描述
            selected = ModelCapability(
                model_id=selected_model['model_id'],
                provider=selected_model['provider'],
                model_type=selected_model['model_type'],
                context_window=selected_model['context_window'],
                is_free=selected_model.get('is_free', False),
            )
        
        # 2. 调用模型
        try:
            result = call_model(selected.provider, selected.model_id, prompt)
            elapsed = time.time() - start_time
            
            # 3. 更新性能统计
            self.update_model_performance(selected.model_id, success=True, latency=elapsed)
            
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            self.update_model_performance(selected.model_id, success=False, latency=elapsed)
            return None
    
    @protected_function
    def steward_think_with_model(self, provider: str, model_id: str, prompt: str) -> Optional[str]:
        """
        序境管家独立思考：指定提供商和模型ID
        
        直接使用指定模型，不自动选择
        """
        start_time = time.time()
        try:
            result = call_model(provider, model_id, prompt)
            elapsed = time.time() - start_time
            
            # 更新性能统计
            if model_id in self.model_capabilities:
                self.update_model_performance(model_id, success=True, latency=elapsed)
            
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            if model_id in self.model_capabilities:
                self.update_model_performance(model_id, success=False, latency=elapsed)
            return None
    
    @protected_function
    def load_all_enabled_models(self) -> int:
        """
        加载所有已启用模型到能力画像中
        
        从序境模型配置表读取所有已启用模型，构建管家的模型能力索引
        返回加载的模型数量
        """
        import sqlite3
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data', 'symphony.db'
        )
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT provider, model_id, model_name, model_type, context_window, is_free, is_enabled
            FROM model_config 
            WHERE is_enabled = 1
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        count = 0
        for row in rows:
            provider, model_id, model_name, model_type, context_window, is_free, is_enabled = row
            if not is_enabled:
                continue
            
            cap = ModelCapability(
                model_id=model_id,
                provider=provider,
                model_type=model_type,
                context_window=context_window,
                is_free=bool(is_free),
            )
            self.model_capabilities[model_id] = cap
            count += 1
        
        return count
    
    # === 外部智能体协作 ===
    
    @protected_function
    def handshake(self, agent_id: str, agent_name: str, capabilities: List[str],
                  endpoint: Optional[str] = None, metadata: Optional[Dict] = None) -> bool:
        """
        与外部智能体握手协作
        协议：交换能力声明，确认在线状态
        """
        agent_info = ExternalAgentInfo(
            agent_id=agent_id,
            agent_name=agent_name,
            capabilities=capabilities,
            endpoint=endpoint,
            is_alive=True,
            last_handshake=time.time(),
            metadata=metadata or {}
        )
        self.external_agents[agent_id] = agent_info
        print(f"🤝 握手成功：外部智能体 {agent_name} ({agent_id})")
        print(f"   能力：{', '.join(capabilities)}")
        return True
    
    @protected_function
    def check_agent_alive(self, agent_id: str) -> bool:
        """检查外部智能体是否在线"""
        if agent_id not in self.external_agents:
            return False
        # 简单检查：5分钟内有握手算活的
        agent = self.external_agents[agent_id]
        return (time.time() - agent.last_handshake) < 300
    
    @protected_function
    def collaborate_task(self, agent_id: str, task_content: str) -> Optional[str]:
        """分发任务给外部智能体协作处理（占位，实际由外部实现）"""
        if not self.check_agent_alive(agent_id):
            print(f"❌ 外部智能体 {agent_id} 不在线")
            return None
        
        # 这里输出任务，外部智能体接收处理后回流结果
        # 这是标准协作接口
        print(f"📤 分发任务给外部智能体 {agent_id}: {task_content[:60]}...")
        # 返回结果由外部回流
        return None
    
    @protected_function
    def receive_result(self, agent_id: str, task_id: str, result: str) -> None:
        """接收外部智能体处理完的结果回流"""
        print(f"📥 收到外部智能体 {agent_id} 结果 (task: {task_id}): {len(result)} chars")
        # 存入任务缓存
        if not hasattr(self, '_task_cache'):
            self._task_cache: Dict[str, Dict[str, Any]] = {}
        self._task_cache[task_id] = {
            'agent_id': agent_id,
            'task_id': task_id,
            'result': result,
            'timestamp': time.time()
        }
        return None
    
    @protected_function
    def get_cached_result(self, task_id: str) -> Optional[str]:
        """获取缓存的协作结果"""
        if not hasattr(self, '_task_cache'):
            return None
        if task_id not in self._task_cache:
            return None
        return self._task_cache[task_id]['result']
    
    @protected_function
    def audit_execution_plan(self, plan_content: str) -> Tuple[bool, List[str]]:
        """审计执行方案：检查方案是否符合内核规则，有问题发还整改，没问题放行
        
        Args:
            plan_content: 要审计的执行方案内容（文本描述或JSON）
            
        Returns:
            (passed: bool, issues: List[str])
            - passed: True = 审计通过，放行；False = 不通过，发还整改
            - issues: 问题列表，空列表表示通过
            
        审计规则（全部七条内核规则）：
        1. 检查是否违反旁路规则：是否有直接调用厂商SDK、绕过主调度
        2. 检查是否违反内核配置：是否修改openclaw.json、是否要自动重启网关
        3. 检查是否违反向量存储规则：是否要持久化存储向量
        4. 检查是否存在危险操作：是否有破坏性文件操作
        5. 检查路径正确性：是否使用了错误的数据库路径
        6. 检查优先级规则：是否动态修改优先级
        7. 检查配置来源：是否从正确的symphony.db读取配置
        
        审计结论：
        - 任何一个规则违反 → 审计不通过，发还整改
        - 全部规则通过 → 放行执行
        """
        issues = []
        
        # 规则1: 检查旁路违规 - 禁止直接导入厂商SDK
        bypass_keywords = [
            'import openai', 'import dashscope', 'import zhipuai', 'import minimax',
            'openai.', 'dashscope.', 'zhipuai.', 'minimax.',
            '直接调用', '绕过调度', '旁路调用',
        ]
        for kw in bypass_keywords:
            if kw in plan_content:
                issues.append(f"[规则1违规] 检测到可能的旁路调用: '{kw}'，所有调用必须走symphony_scheduler主链路")
        
        # 规则2: 检查内核配置违规 - 禁止修改固化配置
        config_keywords = [
            'modify openclaw.json', '修改 openclaw.json', 'openclaw.json',
            'restart gateway', '重启网关', 'restart openclaw',
        ]
        for kw in config_keywords:
            if kw.lower() in plan_content.lower():
                issues.append(f"[规则2违规] 检测到违规操作: '{kw}'，openclaw.json已固化禁止修改，网关必须用户手动重启")
        
        # 规则3: 检查向量存储违规 - 只保存原始文本
        vector_keywords = [
            'persist vector', '存储向量', 'save vector', '持久化向量',
            'vector database', '向量数据库',
        ]
        for kw in vector_keywords:
            if kw.lower() in plan_content.lower() and '原始文本' not in plan_content:
                issues.append(f"[规则3违规] 检测到向量存储违规: '{kw}'，内核规则要求只保存原始文本，禁止持久化存储向量")
        
        # 规则4: 检查危险操作 - 需要警告
        danger_keywords = [
            'rm -rf', 'rm -r', 'format', '格式化', 'shutil.rmtree',
        ]
        for kw in danger_keywords:
            if kw in plan_content:
                issues.append(f"[规则4警告] 检测到危险操作: '{kw}'，请确认操作安全性")
        
        # 规则5: 检查路径错误 - 修正数据库路径
        path_errors = [
            'symphony_working.db',
        ]
        for path in path_errors:
            if path in plan_content:
                issues.append(f"[规则5违规] 检测到错误路径: '{path}'，正确数据库路径是 symphony.db")
        
        # 规则6: 检查优先级违规 - 优先级必须固化
        priority_errors = [
            'change priority', 'modify priority', 
            '动态修改', '修改优先级', '调整优先级', 
            '动态优先级', 'change priority',
        ]
        content_lower = plan_content.lower()
        for kw in priority_errors:
            if kw.lower() in content_lower:
                issues.append(f"[规则6违规] 检测到优先级违规: '{kw}'，优先级必须固化，禁止动态修改")
        
        # 规则7: 检查配置来源 - 必须从symphony.db读取
        config_source_errors = [
            'os.getenv', 'env.get', 'json.load(open(',
        ]
        for kw in config_source_errors:
            if kw in plan_content and 'symphony.db' not in plan_content:
                issues.append(f"[规则7违规] 检测到配置来源错误: '{kw}'，所有配置必须从symphony.db读取")
        
        # 返回审计结果
        passed = len(issues) == 0
        
        if passed:
            import logging
            logging.info("[方案审计] 审计通过 ✓，放行执行")
        else:
            import logging
            logging.warning(f"[方案审计] 审计不通过 ✗，发现 {len(issues)} 个问题，发还整改")
            for issue in issues:
                logging.warning(f"  - {issue}")
        
        return (passed, issues)
    
    @protected_function
    def from_inner_collaborate(self, internal_task: str, external_agent_id: str,
                               require_audit: bool = True) -> Optional[Dict]:
        """
        从内到外：内核任务分发到外部智能体
        
        流程第一步：内核内部发现任务/问题/机会 → 序境管家 → 外部智能体
        
        Args:
            internal_task: 内核产生的任务内容
            external_agent_id: 目标外部智能体ID
            require_audit: 是否需要先审计再分发，默认需要
            
        Returns:
            dict: {
                'task_id': str,
                'status': 'distributed' | 'rejected',
                'audit_passed': bool,
                'audit_issues': List[str],
                'message': str
            }
            如果外部同步处理，返回结果在result字段
            如果异步处理，需要稍后通过 get_cached_result 获取
        """
        if not self.check_agent_alive(external_agent_id):
            print(f"❌ 外部智能体 {external_agent_id} 不在线，协作失败")
            return {
                'task_id': None,
                'status': 'rejected',
                'audit_passed': False,
                'audit_issues': ['外部智能体不在线'],
                'message': '外部智能体不在线，无法协作',
                'result': None
            }
        
        # 如果需要审计，先审计
        if require_audit:
            passed, issues = self.audit_execution_plan(internal_task)
            if not passed:
                # 审计不通过，拒绝分发，发还整改
                task_id = f"task_{int(time.time())}_{hash(internal_task) % 10000:04d}"
                if not hasattr(self, '_task_cache'):
                    self._task_cache: Dict[str, Dict[str, Any]] = {}
                self._task_cache[task_id] = {
                    'task_id': task_id,
                    'status': 'rejected',
                    'task_content': internal_task,
                    'target_agent': external_agent_id,
                    'audit_passed': False,
                    'audit_issues': issues,
                    'created_at': time.time(),
                }
                return {
                    'task_id': task_id,
                    'status': 'rejected',
                    'audit_passed': False,
                    'audit_issues': issues,
                    'message': f"审计不通过，发现 {len(issues)} 个问题，请整改后重新提交。",
                    'result': None
                }
        
        # 审计通过，继续分发
        # 生成唯一任务ID
        task_id = f"task_{int(time.time())}_{hash(internal_task) % 10000:04d}"
        
        # 分发任务给外部智能体
        print(f"🚀 [从内到外协作] 内核任务 → 外部智能体 {external_agent_id}")
        if require_audit:
            print(f"   审计: 通过 ✓")
        print(f"   任务ID: {task_id}")
        if len(internal_task) > 60:
            print(f"   任务内容: {internal_task[:60]}...")
        else:
            print(f"   任务内容: {internal_task}")
        
        # 分发任务
        result = self.collaborate_task(external_agent_id, internal_task)
        
        # 存入缓存
        if not hasattr(self, '_task_cache'):
            self._task_cache: Dict[str, Dict[str, Any]] = {}
        self._task_cache[task_id] = {
            'agent_id': external_agent_id,
            'task_id': task_id,
            'task_content': internal_task,
            'status': 'distributed',
            'audit_passed': require_audit,
            'audit_issues': [],
            'result': result,
            'timestamp': time.time()
        }
        
        # 如果外部立即返回结果，直接返回
        if result is not None:
            return {
                'task_id': task_id,
                'status': 'completed',
                'audit_passed': True if require_audit else None,
                'audit_issues': [],
                'message': '任务已完成，结果返回',
                'result': result
            }
        
        # 否则等待外部回流结果，调用方需要稍后获取
        print(f"⏳ 任务已分发，等待外部智能体 {external_agent_id} 处理完成...")
        print(f"   后续使用 get_cached_result('{task_id}') 获取结果")
        return {
            'task_id': task_id,
            'status': 'distributed',
            'audit_passed': True if require_audit else None,
            'audit_issues': [],
            'message': '任务已分发到外部智能体，等待处理结果。',
            'result': None
        }
    
    @protected_function
    def to_inner_apply_result(self, task_id: str, apply_func: Callable[[str], Any]) -> Optional[Any]:
        """
        外到内应用：外部结果回流到内核应用
        
        流程第二步：外部结果 → 序境管家 → 内核应用
        
        Args:
            task_id: 任务ID
            apply_func: 内核应用函数，接收结果返回应用结果
            
        Returns:
            应用结果，如果结果还没就绪返回None
        """
        result = self.get_cached_result(task_id)
        if result is None:
            return None
        
        try:
            applied_result = apply_func(result)
            print(f"✅ [外到内应用] 任务 {task_id} 结果已成功应用到内核")
            return applied_result
        except Exception as e:
            print(f"❌ [外到内应用] 应用失败: {e}")
            return None
    
    @protected_function
    def full_inner_outer_cycle(self, internal_task: str, external_agent_id: str, 
                             apply_func: Optional[Callable[[str], Any]] = None) -> Optional[Any]:
        """
        完整的从内到外协作闭环流程：
        
        完整闭环：
        内核发现任务/问题/机会 
        → 序境管家 从内分发到外部智能体 
        → 外部智能体处理 
        → 结果回流到序境管家 
        → 序境管家交付结果给内核应用
        
        Args:
            internal_task: 内核产生的任务内容
            external_agent_id: 协作的外部智能体ID
            apply_func: 结果应用函数，如果为None只返回结果不自动应用
            
        Returns:
            同步处理：返回最终结果/应用结果
            异步处理：返回None，需要后续获取
            
        这就是完整的"从内到外协作过程"
        """
        # 第一步：从内分发到外
        result = self.from_inner_collaborate(internal_task, external_agent_id)
        
        # 同步返回：直接处理
        if result is not None and apply_func is not None:
            return apply_func(result)
        
        # 直接返回结果
        return result
    
    # === 全内核状态报告 ===
    
    @protected_function
    def generate_status_report(self) -> KernelStatusReport:
        """生成全内核状态报告"""
        from symphony_scheduler_military import get_enabled_providers
        from symphony_scheduler_military import DB_PATH
        
        # 检查模块
        total_modules, healthy_modules, errors = self.check_all_modules()
        failed_modules = total_modules - healthy_modules
        
        # 检查提供商健康
        checker = ProviderHealthChecker()
        health_report = checker.test_all_providers()
        
        # 汇总
        providers_health = {code: h.overall_health() for code, h in health_report.items()}
        total_models = sum(len(h.available_models) for h in health_report.values())
        enabled_models = sum(1 for status in providers_health.values() if status in ['healthy', 'partial'])
        
        # 计算总体健康分数
        if total_modules > 0:
            module_score = healthy_modules / total_modules
        else:
            module_score = 0
        
        provider_count = len(health_report)
        healthy_provider_count = sum(1 for code, h in health_report.items() if h.overall_health() == 'healthy')
        if provider_count > 0:
            provider_score = healthy_provider_count / provider_count
        else:
            provider_score = 0
        
        overall_score = (module_score * 0.5 + provider_score * 0.5)
        
        # 生成建议
        recommendations = []
        if failed_modules > 0:
            recommendations.append(f"有 {failed_modules} 个核心模块缺失/损坏，需要修复")
        for p, status in providers_health.items():
            if status == 'failing':
                recommendations.append(f"提供商 {p} 状态 failing，检查API密钥")
            if status == 'missing_key':
                recommendations.append(f"提供商 {p} 缺少API密钥，需要配置")
        
        if overall_score >= 0.9:
            recommendations.insert(0, "整体健康状况优秀，可以全力运行")
        elif overall_score >= 0.7:
            recommendations.insert(0, "整体健康状况良好，少量问题不影响核心运行")
        else:
            recommendations.insert(0, "整体健康状况需要关注，建议修复问题后再运行")
        
        report = KernelStatusReport(
            timestamp=time.time(),
            total_modules=total_modules,
            loaded_modules=sum(1 for m in self.modules.values() if m.is_loaded),
            healthy_modules=healthy_modules,
            failed_modules=failed_modules,
            providers_health=providers_health,
            total_models=total_models,
            enabled_models=enabled_models,
            overall_health_score=overall_score,
            recommendations=recommendations,
            errors=errors
        )
        
        return report
    
    @protected_function
    def start_management_report(self, title: str) -> None:
        """开始管理汇报 - 序境管家独立标识
        
        所有序境管家的管理行为都以此开头，明确区分管理汇报和普通输出
        """
        print("\n")
        print("╔" + "═" * 68 + "╗")
        print("║" + "  🤵 序境管家 管理行为汇报  " + " " * (42 - len(title)) + "║")
        print(f"║ ▶ 开始执行：{title}" + " " * (48 - len(title)) + "║")
        print("╚" + "═" * 68 + "╝")
        print("")
    
    @protected_function
    def end_management_report(self, success: bool = True, summary: str = "") -> None:
        """结束管理汇报"""
        print("")
        print("╔" + "═" * 68 + "╗")
        if success:
            print("║" + "  ✅ 管理执行完成  " + (summary if summary else "操作成功") + " " * (46 - len(summary)) + "║")
        else:
            print("║" + "  ❌ 管理执行失败  " + (summary if summary else "遇到错误") + " " * (46 - len(summary)) + "║")
        print("╚" + "═" * 68 + "╝")
        print("")
    
    @protected_function
    def print_status_report(self, report: Optional[KernelStatusReport] = None) -> None:
        """打印状态报告 - 序境管家独立汇报格式
        
        独立边框格式，清晰区分序境管家管理行为和普通输出
        """
        if report is None:
            report = self.generate_status_report()
        
        print("\n")
        print("╔" + "═" * 68 + "╗")
        print("║" + "  🤵 序境管家 独立汇报 - 全内核状态报告  " + " " * 18 + "║")
        print("╠" + "═" * 68 + "╣")
        dt_str = datetime.fromtimestamp(report.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        print(f"║ 生成时间: {dt_str}" + " " * (46 - len(dt_str)) + "║")
        print("╠" + "─" * 68 + "╣")
        print(f"║ 核心模块: 总计 {report.total_modules}, 健康 {report.healthy_modules}, 失败 {report.failed_modules}" + " " * (8 - len(str(report.failed_modules))) + "║")
        print("╠" + "─" * 68 + "╣")
        print("║ 提供商健康状态:" + " " * 49 + "║")
        for p, status in report.providers_health.items():
            icon = "✅" if status == 'healthy' else "⚠️" if status == 'partial' else "❌"
            line_text = f"  {icon} {p}: {status}"
            line = f"║{line_text}{' ' * (68 - len(line_text))}║"
            print(line)
        print("╠" + "─" * 68 + "╣")
        print(f"║ 总模型数: {report.total_models}, 已启用可用: {report.enabled_models}" + " " * (10 - len(str(report.enabled_models))) + "║")
        print(f"║ 总体健康分数: {report.overall_health_score:.2f}/1.00" + " " * (43 - len(f"{report.overall_health_score:.2f}")) + "║")
        print("╠" + "─" * 68 + "╣")
        print("║ 💡 管理建议:" + " " * 54 + "║")
        for i, rec in enumerate(report.recommendations, 1):
            line_text = f"  {i}. {rec}"
            if len(line_text) > 65:
                line_text = line_text[:62] + "..."
            line = f"║{line_text}{' ' * (68 - len(line_text))}║"
            print(line)
        if report.errors and len(report.errors) > 0:
            print("╠" + "─" * 68 + "╣")
            print("║ ❌ 需要修复的错误:" + " " * 48 + "║")
            for i, err in enumerate(report.errors, 1):
                line_text = f"  {i}. {err}"
                if len(line_text) > 65:
                    line_text = line_text[:62] + "..."
                line = f"║{line_text}{' ' * (68 - len(line_text))}║"
                print(line)
        print("╚" + "═" * 68 + "╝")

# 导出
__all__ = [
    'SymphonySteward',
    'KernelModuleInfo',
    'ModelCapability',
    'ExternalAgentInfo',
    'KernelStatusReport',
]

# 引导启动
if __name__ == "__main__":
    steward = SymphonySteward()
    success = steward.bootstrap()
    if success:
        steward.print_status_report()
        print("\n🎉 序境管家启动成功，随时可以管理内核！")
    else:
        print("\n❌ 序境管家启动失败，请修复缺失模块")
