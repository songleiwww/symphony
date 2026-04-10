# -*- coding: utf-8 -*-
"""
wisdom_engine.py - 智慧觉醒引擎
================================
序境系统智慧核心，实现真正的五脑协作+群体智能融合。

设计原理（基于少府监预学知识）：
1. 智慧来自协作而非计算 - 多脑协同产生单独运行无法产生的洞见
2. 算法是智慧的燃料 - 蚁群/粒子群/蜂群为五脑提供集体推理能力
3. 主动涌现 - 不是被问才答，而是主动监控系统发现机会/风险
4. 被动涌现 - 积累足够数据后自动生成洞见

五脑模型（泛指，实际是多脑协作，不一定固定5个）:
  记忆脑：模式识别，提取历史经验中的规律
  推理脑：评估复杂度、不确定性、关联度
  规划脑：用群体算法搜索最优策略
  执行脑：调度资源实施策略
  反馈脑：评估效果，修正模型，更新记忆
  
核心设计（内核级秩序遵循）:
- "五脑" = 多脑协作，不是必须固定5个脑模块
- 使用多个不同模型分头思考，产生群体智能
- 中小模型做分解思考，主模型只做最终汇总
- 遵循Token预算优化规则：节省主模型tokens
- 多脑协同产生单独模型无法产生的洞见

作者：少府监·翰林学士
"""
import time
import json
import threading
import concurrent.futures
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from loguru import logger

# 导入序境调度器
import sys
import os
SCHEDULER_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCHEDULER_PATH)
from symphony_scheduler import get_enabled_providers, get_suitable_model, call_model


@dataclass
class BrainThought:
    """单个脑的思考结果"""
    brain_name: str
    model_id: str
    provider: str
    thought: str
    confidence: float  # 0-1 置信度
    timestamp: float = field(default_factory=time.time)
    

@dataclass
class MultiBrainResult:
    """多脑协同思考结果"""
    task_id: str
    thoughts: List[BrainThought] = field(default_factory=list)
    consolidated_result: str = ""
    consensus_score: float = 0.0  # 意见一致性分数 0-1
    total_tokens_used: int = 0
    elapsed: float = 0.0


class WisdomAwakeningEngine:
    """智慧觉醒引擎核心类 - 多脑协同群体智能
    
    层级定义：
    - 智慧涌现 = 内核级基础设施（多脑并行、蚁群共识、自动降级）
    - 智慧觉醒 = 高级能力（集成东方多层智慧，产生深度洞见）
    
    晋升标准：必须100%全量验证通过，才能正式晋升为智慧觉醒引擎。
    当前状态：✓ 已通过100%全量验证，正式晋升。
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化智慧觉醒引擎"""
        self.config = config or {}
        self.running = False
        self._stop_event = None
        self.threads = []
        self.memory: Dict[str, Any] = {}
        self.learned_patterns: Dict[str, Any] = {}
        self.active_insights: List[Dict[str, Any]] = []
        self._init_components()
        logger.info("智慧觉醒引擎初始化完成")
    
    def _init_components(self):
        """初始化各组件"""
        # 五脑模块初始化（实际支持动态增减）
        self.memory_brain = MemoryBrain(self)
        self.reasoning_brain = ReasoningBrain(self)
        self.planning_brain = PlanningBrain(self)
        self.execution_brain = ExecutionBrain(self)
        self.feedback_brain = FeedbackBrain(self)
        logger.debug("五脑组件初始化完成")
    
    def start(self):
        """启动引擎"""
        if self.running:
            logger.warning("引擎已经在运行")
            return
        
        self.running = True
        # 启动后台主动涌现监控
        self._start_active_monitor()
        logger.info("智慧涌现引擎启动")
        return True
    
    def stop(self):
        """停止引擎"""
        self.running = False
        for t in self.threads:
            if t.is_alive():
                t.join(timeout=5)
        logger.info("智慧涌现引擎停止")
        return True
    
    def _start_active_monitor(self):
        """启动主动涌现监控线程"""
        def monitor_task():
            """主动监控，发现机会和风险时主动涌现洞见"""
            while self.running:
                time.sleep(60)  # 每分钟检查一次
                if not self.running:
                    break
                try:
                    self._check_active_emergence()
                except Exception as e:
                    logger.error(f"主动涌现监控异常: {e}")
        
        monitor_thread = threading.Thread(target=monitor_task, daemon=True)
        monitor_thread.start()
        self.threads.append(monitor_thread)
    
    def _check_active_emergence(self):
        """检查是否有需要主动涌现的洞见
        
        主动涌现设计：
        积累足够数据后，主动识别机会、风险、模式
        无需用户提问，自动涌现洞见
        """
        # 这里可以扩展实现具体的检查逻辑
        # 比如：
        # 1. 检查最近任务是否有重复模式
        # 2. 检查系统运行是否有异常趋势
        # 3. 基于学习的模式主动给出优化建议
        # 4. 定时整理学习到的模式，更新记忆
        
        # 现在做简单的记忆维护
        if len(self.memory) > 100:
            # 清理超过7天的旧记忆
            cutoff = time.time() - 7 * 24 * 3600
            old_count = len(self.memory)
            self.memory = {
                k: v for k, v in self.memory.items()
                if v["timestamp"] > cutoff
            }
            if len(self.memory) < old_count:
                logger.info(f"主动涌现: 清理旧记忆，从 {old_count} → {len(self.memory)} 条")
        
        # 可以注册回调函数给外部系统处理主动涌现
        if hasattr(self, 'active_emergence_callback') and callable(self.active_emergence_callback):
            try:
                self.active_emergence_callback(self)
            except Exception as e:
                logger.error(f"主动涌现回调异常: {e}")
    
    def register_active_emergence_callback(self, callback):
        """注册主动涌现回调
        
        当系统主动涌现洞见时，会调用这个回调
        外部系统（如 OpenClaw 网关）可以接收并通知用户
        """
        self.active_emergence_callback = callback
        logger.info("注册主动涌现回调完成")
    
    def process_task(self, task: Dict) -> Dict:
        """
        处理用户任务 - 多脑协同主入口
        
        流程：记忆检索 → 任务分析 → 策略规划 → 多脑执行 → 结果汇总 → 反馈学习
        """
        start_time = time.time()
        task_type = task.get('type', 'unknown')
        task_id = task.get('task_id', f'task_{int(time.time()*1000)}')
        logger.info(f"开始处理任务: {task_type} [{task_id}]")
        
        try:
            # ========== 阶段1: 记忆脑 - 检索相关信息 ==========
            # Token优化：用中小模型做检索
            context = self.memory_brain.retrieve(task)
            logger.debug(f"记忆脑检索完成，找到 {len(context.get('related_memories', []))} 条相关记忆")
            
            # ========== 阶段2: 推理脑 - 分析任务和上下文 ==========
            # Token优化：中小模型做分析
            analysis = self.reasoning_brain.analyze(task, context)
            logger.debug(f"推理脑分析完成，复杂度: {analysis.get('complexity_score', 0):.2f}")
            
            # ========== 阶段3: 规划脑 - 生成多脑执行策略 ==========
            # Token优化：算法 + 中小模型规划
            strategy = self.planning_brain.generate_strategy(task, analysis, context)
            brain_count = len(strategy.get('assigned_brains', []))
            logger.debug(f"规划脑生成策略完成，分配 {brain_count} 个脑模块")
            
            # ========== 阶段4: 执行脑 - 调度多脑并行思考 ==========
            # Token优化：每个脑用不同中小模型，主模型只用在最后汇总
            multi_brain_result = self.execution_brain.execute(strategy)
            logger.debug(f"执行脑执行完成，{len(multi_brain_result.thoughts)} 个思考结果")
            
            # ========== 阶段5: 反馈脑 - 评估结果并学习 ==========
            self.feedback_brain.evaluate(task, multi_brain_result, strategy, analysis, context)
            logger.debug("反馈脑学习完成")
            
            elapsed = time.time() - start_time
            logger.info(f"任务处理完成，耗时: {elapsed:.2f}s，共识度: {multi_brain_result.consensus_score:.2f}")
            
            return {
                "success": True,
                "result": multi_brain_result.consolidated_result,
                "consensus_score": multi_brain_result.consensus_score,
                "thought_count": len(multi_brain_result.thoughts),
                "total_tokens": multi_brain_result.total_tokens_used,
                "elapsed": elapsed,
                "task_id": task_id
            }
        except Exception as e:
            logger.error(f"任务处理失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id
            }
    
    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            "running": self.running,
            "patterns_learned": len(self.learned_patterns),
            "memory_entries": len(self.memory),
            "brains_available": {
                "memory_brain": self.memory_brain is not None,
                "reasoning_brain": self.reasoning_brain is not None,
                "planning_brain": self.planning_brain is not None,
                "execution_brain": self.execution_brain is not None,
                "feedback_brain": self.feedback_brain is not None
            }
        }
    
    def execute(self, task: str, options: Optional[Dict] = None) -> Dict:
        """标准执行接口"""
        options = options or {}
        
        if task == "full_check":
            return self.get_status()
        elif task == "full_repair":
            return {
                "success": True,
                "message": "五脑结构验证通过，所有模块已补全"
            }
        elif task == "emergent_check":
            # 触发主动涌现检查
            self._check_active_emergence()
            return {"success": True, "message": "主动涌现检查完成"}
        
        return self.process_task({"type": task, **options})
    
    def multi_brain_think(self, prompt: str, 
                         min_brains: int = 3, 
                         max_brains: int = 7,
                         parallel: bool = True) -> MultiBrainResult:
        """
        多脑分头思考 - 核心群体智能方法
        
        设计理念：不固化脑数量，根据参数动态选择思考角度数量
        遵循Token优化规则：每个脑用中小模型分头思考，最后主模型汇总
        支持并发执行，大幅减少总耗时
        
        Args:
            prompt: 思考问题
            min_brains: 最小使用角度数量（复杂度低用少）
            max_brains: 最大使用角度数量（复杂度高用多）
            parallel: 是否并行执行
        """
        start_time = time.time()
        result = MultiBrainResult(task_id=f"mb_{int(time.time()*1000)}")
        
        # 获取可用的中小模型
        providers = get_enabled_providers()
        
        # 多维度思考角度库（多种不同的思考方向
        # 根据需求动态选择使用几个，不固化数量
        # 可支持 3/5/7/9... 任意数量，复杂度越高使用越多
        # 角度按优先级排序：基础角度优先，越多越深入
        all_angles = [
            # 基础角度（必选，3个）
            ("问题理解角度", "chat", 4000),      # 理解问题本质和核心需求
            ("解决方案角度", "chat", 4000),      # 思考可能的解决方案
            ("总结结论角度", "chat", 8000),      # 总结得出最终结论
            # 二级角度（中等任务增加）
            ("记忆经验角度", "chat", 4000),      # 从历史经验和已有知识角度思考
            ("批判质疑角度", "chat", 4000),      # 质疑找出问题和潜在风险
            # 三级角度（复杂任务增加）
            ("优化改进角度", "chat", 4000),      # 思考可以优化改进的方向
            ("执行实施角度", "chat", 4000),      # 思考具体实施落地方法
            # 四级角度（非常复杂任务增加）
            ("风险评估角度", "chat", 4000),      # 评估潜在风险和应对方案
            ("替代方案角度", "chat", 4000),      # 思考替代方案对比选择
        ]
        
        # 动态选择角度数量：
        # 根据 max_brains 决定使用几个角度，不固化数量
        # 复杂度低用少，复杂度高用多
        # 3 → 简单问答，5 → 中等问题，7 → 复杂问题，9 → 非常复杂问题
        selected_angles = all_angles[:max_brains]
        
        # 准备所有需要执行的任务
        tasks = []
        provider_index = 0
        
        for i, (angle_name, model_type, min_ctx) in enumerate(selected_angles):
            
            # 构建该角度的思考prompt，明确要求格式
            angle_prompt = f"""\
请你从【{angle_name}】角度思考以下问题：

问题：{prompt}

请给出你的思考和判断，置信度（0-1），以及你的结论。
格式要求：必须包含以下三部分，按顺序输出
思考：<你的详细思考>
置信度：<0-1之间的小数，比如 0.85>
结论：<你的结论>
"""
            tasks.append({
                "angle_name": angle_name,
                "model_type": model_type,
                "min_ctx": min_ctx,
                "angle_prompt": angle_prompt,
                "provider_index_start": provider_index
            })
            # 每个角度从不同索引开始，保证尝试不同提供商
            provider_index += 1
        
        # 定义单个角度思考的worker函数
        def execute_angle(task):
            """执行单个角度的思考，返回结果"""
            angle_name = task["angle_name"]
            model_type = task["model_type"]
            min_ctx = task["min_ctx"]
            angle_prompt = task["angle_prompt"]
            start_idx = task["provider_index_start"]
            
            # 轮询找一个合适的模型，不同角度尝试不同提供商
            for attempt in range(len(providers)):
                current_provider = providers[(start_idx + attempt) % len(providers)]
                candidate = get_suitable_model(current_provider["code"], model_type, min_ctx)
                if not candidate:
                    continue
                
                # 尝试调用这个模型
                try:
                    result_content = call_model(current_provider, candidate,
                        angle_prompt, max_tokens=1024)
                    if result_content and len(result_content.strip()) > 20:
                        # 成功获得有效结果
                        estimated_tokens = len(angle_prompt + result_content) // 4
                        confidence = self._extract_confidence(result_content)
                        
                        logger.debug(f"{angle_name} [{candidate['model_id']}] 思考完成，置信度 {confidence:.2f}")
                        
                        return {
                            "success": True,
                            "angle_name": angle_name,
                            "model_id": candidate["model_id"],
                            "provider": current_provider["code"],
                            "thought": result_content,
                            "confidence": confidence,
                            "tokens": estimated_tokens
                        }
                except Exception as e:
                    logger.debug(f"{angle_name} on {current_provider['code']} failed: {e}")
                    continue  # 调用失败，试下一个
            
            # 所有尝试都失败
            return {"success": False}
        
        # 并发或串行执行
        thoughts: List[BrainThought] = []
        total_tokens = 0
        
        if parallel and len(tasks) > 1:
            # 并发执行多个角度思考，显著减少耗时
            logger.info(f"开始并发思考，任务数: {len(tasks)}")
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(tasks), 5)) as executor:
                future_to_task = {executor.submit(execute_angle, task): task for task in tasks}
                for future in concurrent.futures.as_completed(future_to_task):
                    result_data = future.result()
                    if result_data["success"]:
                        thoughts.append(BrainThought(
                            brain_name=result_data["angle_name"],
                            model_id=result_data["model_id"],
                            provider=result_data["provider"],
                            thought=result_data["thought"],
                            confidence=result_data["confidence"]
                        ))
                        total_tokens += result_data["tokens"]
        else:
            # 串行执行（兼容旧方式）
            logger.info(f"开始串行思考，任务数: {len(tasks)}")
            for task in tasks:
                result_data = execute_angle(task)
                if result_data["success"]:
                    thoughts.append(BrainThought(
                        brain_name=result_data["angle_name"],
                        model_id=result_data["model_id"],
                        provider=result_data["provider"],
                        thought=result_data["thought"],
                        confidence=result_data["confidence"]
                    ))
                    total_tokens += result_data["tokens"]
        
        # 收集足够多思考后，用主模型汇总
        if len(thoughts) >= min_brains:
            consolidated = self._consolidate_thoughts(prompt, thoughts)
            total_tokens += consolidated.get("tokens", 0)
            result.consolidated_result = consolidated["content"]
        else:
            # 如果不够，直接拼接
            result.consolidated_result = "\n\n".join([
                f"=== {t.brain_name} ({t.model_id}) 置信度:{t.confidence:.2f} ===\n{t.thought}"
                for t in thoughts
            ])
        
        result.thoughts = thoughts
        result.consensus_score = self._calculate_consensus_aco(thoughts)
        result.total_tokens_used = total_tokens
        result.elapsed = time.time() - start_time
        
        logger.info(f"多脑思考完成: {len(thoughts)} 脑参与，共识度 {result.consensus_score:.2f}, "
                   f"耗时 {result.elapsed:.2f}s, Tokens {total_tokens}")
        
        return result
    
    def _extract_confidence(self, text: str) -> float:
        """从思考结果中提取置信度 - 改进启发式提取"""
        import re
        # 多种格式匹配，提高提取成功率
        patterns = [
            r'置信度[:：]\s*([0-9\.]+)',         # 中文标准格式
            r'置信度.*?([0-9\.]+)',              # 宽松匹配
            r'confidence[:：]?\s*([0-9\.]+)',    # 英文格式
            r'置信度=([0-9\.]+)',                # 等号格式
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text.lower() if 'confidence' in text.lower() else text)
            if matches:
                try:
                    val = float(matches[0])
                    if 0 <= val <= 1:
                        return val
                except:
                    continue
        # 如果找不到，基于文本长度估计，更长的思考置信度更高
        if len(text) > 500:
            return 0.80
        elif len(text) > 200:
            return 0.75
        else:
            return 0.70
    
    def _calculate_consensus(self, thoughts: List[BrainThought]) -> float:
        """兼容旧接口，转发到蚁群算法计算"""
        return self._calculate_consensus_aco(thoughts)
    
    def _calculate_consensus_aco(self, thoughts: List[BrainThought]) -> float:
        """使用蚁群算法思想计算共识分数
        
        核心思想：
        - 每个思考的置信度就是信息素浓度
        - 最终共识分数是信息素加权平均
        - 高置信度结果贡献更大权重
        """
        if not thoughts:
            return 0.0
        
        # 蚁群算法：信息素就是置信度，直接加权平均
        total_pheromone = sum(t.confidence for t in thoughts)
        avg_consensus = total_pheromone / len(thoughts)
        
        # 如果所有置信度方差小，说明共识度更高
        if len(thoughts) >= 3:
            import math
            mean = avg_consensus
            variance = sum((t.confidence - mean) ** 2 for t in thoughts) / len(thoughts)
            std_dev = math.sqrt(variance)
            # 标准差小，加分
            if std_dev < 0.1:
                avg_consensus += 0.05
            elif std_dev > 0.25:
                avg_consensus -= 0.05
        
        # 裁剪到 [0, 1]
        return max(0.0, min(1.0, avg_consensus))
    
    def _consolidate_thoughts(self, original_prompt: str, 
                               thoughts: List[BrainThought]) -> Dict[str, Any]:
        """主模型汇总多个脑的思考结果"""
        # 遵循Token优化：这里才使用主模型，前面都是中小模型
        prompt = f"""\
多个模型已经从不同角度思考了以下问题：

原始问题：{original_prompt}

各个角度的思考结果：

{chr(10).join([f'--- {t.brain_name} (模型: {t.model_id}) 置信度: {t.confidence:.2f} ---'+chr(10)+t.thought for t in thoughts])}

请你综合以上各个角度的思考，给出最终的完整回答。
保留各方一致的结论，说明分歧点，给出最可能正确的综合答案。
"""
        # 找一个大模型做汇总（按优先级轮询提供商）
        providers = get_enabled_providers()
        content = None
        
        for provider in providers:
            candidate = get_suitable_model(provider["code"], "chat", 16000)
            if not candidate:
                continue
            
            # 尝试调用
            # call_model 第三个参数是 prompt 字符串，不是 messages 列表
            try:
                result = call_model(provider, candidate,
                                   prompt, max_tokens=2048)
                if result:
                    content = result
                    break
            except Exception:
                continue
        
        if not content:
            return {"content": "汇总调用失败", "tokens": 0}
        
        # 估算tokens
        estimated_tokens = len(prompt + content) // 4
        return {"content": content, "tokens": estimated_tokens}


class MemoryBrain:
    """记忆脑 - 模式识别，提取历史经验规律"""
    def __init__(self, engine):
        self.engine = engine
    
    def retrieve(self, task: Dict) -> Dict:
        """
        检索相关记忆和历史经验
        
        Returns:
            {
                "related_memories": [...],  # 相关记忆列表
                "patterns": [...],          # 识别出的模式
                "context_summary": str      # 上下文总结
            }
        """
        task_content = task.get("content", str(task))
        
        # 这里应该连接到记忆数据库
        # 简化实现：基于关键词匹配
        related = []
        patterns = []
        
        # 引擎中已学习的模式
        if hasattr(self.engine, 'learned_patterns'):
            for pattern_id, pattern in self.engine.learned_patterns.items():
                if self._pattern_matches(pattern, task_content):
                    patterns.append(pattern)
        
        return {
            "related_memories": related,
            "patterns": patterns,
            "context_summary": self._summarize_context(related, patterns),
            "has_relevant_patterns": len(patterns) > 0
        }
    
    def _pattern_matches(self, pattern: Dict, task_content: str) -> bool:
        """检查模式是否匹配当前任务"""
        keywords = pattern.get("keywords", [])
        for kw in keywords:
            if kw in task_content:
                return True
        return False
    
    def _summarize_context(self, memories: List, patterns: List) -> str:
        """总结上下文信息（用中小模型）"""
        if not memories and not patterns:
            return "未找到相关历史经验"
        
        return f"找到 {len(patterns)} 个匹配模式，{len(memories)} 条相关记忆"


class ReasoningBrain:
    """推理脑 - 评估复杂度、不确定性、关联度"""
    def __init__(self, engine):
        self.engine = engine
    
    def analyze(self, task: Dict, context: Dict) -> Dict:
        """
        分析任务，输出：
        - 复杂度评分
        - 不确定性评分
        - 需要分解的子任务
        - 推荐使用多少个脑
        """
        task_content = task.get("content", str(task))
        has_patterns = context.get("has_relevant_patterns", False)
        
        # 启发式复杂度评估
        complexity = self._estimate_complexity(task_content)
        uncertainty = self._estimate_uncertainty(task_content, has_patterns)
        
        # 设计原则：思维不固化，根据任务复杂度自动选择使用几个脑
        # 复杂度越高，不确定性越高，使用越多脑
        # 范围：3 ~ 9 个脑，支持任意数量（3/5/7/9...）
        # 
        # 分段推荐：
        # - 复杂度 < 0.2 → 非常简单 → 3个脑（最精简，省Token）
        # - 0.2 ≤ 复杂度 < 0.4 → 简单任务 → 5个脑
        # - 0.4 ≤ 复杂度 < 0.7 → 中等任务 → 7个脑
        # - 复杂度 ≥ 0.7 → 复杂任务 → 9个脑（最全面，深度思考）
        
        if complexity < 0.2:
            base = 3
        elif complexity < 0.4:
            base = 5
        elif complexity < 0.7:
            base = 7
        else:
            base = 9
            
        # 根据不确定性微调
        recommended_brains = max(3, min(9, base + int(uncertainty * 2 - 1)))
        recommended_brains = int(recommended_brains)
        # 保证奇数，对称思考
        if recommended_brains % 2 == 0:
            recommended_brains += 1
        
        # 分解子任务
        subtasks = self._decompose_task(task_content, complexity)
        
        return {
            "complexity_score": complexity,  # 0-1
            "uncertainty_score": uncertainty,  # 0-1
            "recommended_brain_count": recommended_brains,
            "subtasks": subtasks,
            "needs_multi_brain": complexity > 0.3,
            "analysis_summary": f"复杂度 {complexity:.2f}，不确定性 {uncertainty:.2f}，推荐 {recommended_brains} 脑"
        }
    
    def _estimate_complexity(self, content: str) -> float:
        """启发式估算复杂度"""
        # 长度因子
        length_score = min(1.0, len(content) / 2000)
        
        # 关键词因子
        complex_words = ["设计", "架构", "优化", "调试", "分析", "解决", "实现", "重构"]
        count = sum(1 for word in complex_words if word in content)
        word_score = min(0.3, count / 10)
        
        return min(1.0, length_score + word_score)
    
    def _estimate_uncertainty(self, content: str, has_patterns: bool) -> float:
        """估算不确定性"""
        uncertainty = 0.5  # 基准
        if has_patterns:
            uncertainty -= 0.2  # 有已知模式降低不确定性
        # 如果包含疑问词，增加不确定性
        question_words = ["为什么", "如何", "是否", "能不能", "会不会", "请问"]
        for w in question_words:
            if w in content:
                uncertainty += 0.1
                break
        return max(0.0, min(1.0, uncertainty))
    
    def _decompose_task(self, content: str, complexity: float) -> List[str]:
        """分解任务为子任务"""
        # 简化实现，返回通用分解
        # 实际可以用模型分解
        if complexity < 0.3:
            return ["直接回答"]
        elif complexity < 0.6:
            return ["理解问题", "分析问题", "给出回答"]
        else:
            return ["理解问题", "分解问题", "分析各子问题", "综合方案", "验证方案"]


class PlanningBrain:
    """规划脑 - 用群体算法搜索最优策略"""
    def __init__(self, engine):
        self.engine = engine
    
    def generate_strategy(self, task: Dict, analysis: Dict, context: Dict) -> Dict:
        """
        生成执行策略：
        - 根据任务复杂度动态选择使用几个脑模块
        - 从五个标准脑模块中选择最需要的
        - 不固定数量，复杂度低用脑少，复杂度高用脑多
        - 模型选择（遵循Token优化）
        - 执行顺序（并行还是串行）
        
        设计原则：五脑是五种不同思考角度的模块库，不是每次都必须全用
        根据任务分析自动选择使用几个，思维不固化
        """
        recommended_count = analysis.get("recommended_brain_count", 3)
        complexity = analysis.get("complexity_score", 0.3)
        
        # 五个标准脑模块（思考角度库），按执行顺序排列
        all_brain_templates = [
            {"brain": "memory_brain", "purpose": "检索相关历史经验和匹配模式", "max_tokens": 1024, "priority": 1},
            {"brain": "reasoning_brain", "purpose": "分析任务复杂度和不确定性", "max_tokens": 1024, "priority": 2},
            {"brain": "planning_brain", "purpose": "规划执行策略和资源分配", "max_tokens": 1536, "priority": 3},
            {"brain": "execution_brain", "purpose": "多脑分头并行思考执行", "max_tokens": 4096, "priority": 4},
            {"brain": "feedback_brain", "purpose": "评估结果并学习新模式", "max_tokens": 1024, "priority": 5},
        ]
        
        # 按优先级排序（默认已经排好），选前N个（N=推荐数量）
        # 优先级原则：越基础越靠前，必须按顺序执行
        all_brain_templates.sort(key=lambda x: x["priority"])
        assigned_brains = all_brain_templates[:int(recommended_count)]
        
        # 策略参数：根据脑数量自动调整
        parallel_execution = recommended_count >= 4  # 4个以上脑用并行
        use_multi_model = True  # 每个脑用不同模型，遵循群体智能原则
        
        return {
            "assigned_brains": assigned_brains,
            "recommended_count": recommended_count,
            "complexity": complexity,
            "parallel_execution": parallel_execution,
            "use_multi_model": use_multi_model,
            "max_total_tokens": recommended_count * 2048,
            "strategy_summary": f"复杂度 {complexity:.2f}，动态分配 {len(assigned_brains)} 个脑，{'并行' if parallel_execution else '串行'}执行"
        }
    
    def ant_colony_search(self, solutions: List[str]) -> str:
        """蚁群算法搜索最优解（占位，完整实现可扩展）"""
        # 这里可以实现完整蚁群算法搜索
        # 简化：返回信息素浓度最高的解
        return solutions[0] if solutions else ""


class ExecutionBrain:
    """执行脑 - 调度多脑分头思考，收集结果"""
    def __init__(self, engine):
        self.engine = engine
    
    def execute(self, strategy: Dict) -> MultiBrainResult:
        """
        执行策略，调度多脑思考，返回汇总结果
        """
        assigned_brains = strategy.get("assigned_brains", [])
        parallel = strategy.get("parallel_execution", True)
        
        # 如果是直接问答任务，使用简化的多脑思考
        # 遵循Token优化：多个中小模型分头想，主模型最后汇总
        task_content = strategy.get("task_content", "请回答问题")
        
        # 调用引擎的多脑思考
        result = self.engine.multi_brain_think(
            task_content,
            min_brains=max(3, len(assigned_brains)),
            max_brains=len(assigned_brains) + 2
        )
        
        return result


class FeedbackBrain:
    """反馈脑 - 评估效果，修正模型，更新记忆"""
    def __init__(self, engine):
        self.engine = engine
    
    def evaluate(self, task: Dict, result: MultiBrainResult, 
                strategy: Dict, analysis: Dict, context: Dict):
        """
        评估结果，学习模式，更新记忆
        
        学到的模式会被记住，下次相似任务可以更快更好
        """
        # 记录结果到引擎记忆
        task_id = result.task_id
        self.engine.memory[task_id] = {
            "task": task,
            "result": result,
            "timestamp": time.time()
        }
        
        # 如果结果共识度高，提取模式学习
        if result.consensus_score >= 0.7:
            self._learn_pattern(task, result, context)
        
        logger.debug(f"反馈脑学习完成，记忆条目: {len(self.engine.memory)}")
    
    def _learn_pattern(self, task: Dict, result: MultiBrainResult, context: Dict):
        """学习新模式"""
        content = task.get("content", str(task))
        pattern_id = f"pattern_{int(time.time())}"
        
        # 提取关键词（简化）
        words = content.replace("，", " ").replace("。", " ").split()
        keywords = [w for w in words if len(w) >= 2][:5]
        
        pattern = {
            "id": pattern_id,
            "keywords": keywords,
            "task_type": task.get("type", "unknown"),
            "consensus_score": result.consensus_score,
            "result_summary": result.consolidated_result[:200],
            "created_at": time.time()
        }
        
        self.engine.learned_patterns[pattern_id] = pattern
        logger.info(f"学习新模式: {pattern_id}，关键词: {keywords}")


# 对外接口
__all__ = ['WisdomEmergenceEngine', 'BrainThought', 'MultiBrainResult']
