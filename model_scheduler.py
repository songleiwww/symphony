#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
Symphony 模型自动调度系统 v1.0
============================================================================
根据讨论决议实现：
1. 任务-模型映射规则
2. 动态负载均衡
3. 失败熔断降级
4. 策略优化
============================================================================
"""

import time
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

# ==================== 任务类型定义 ====================

class TaskType(Enum):
    """任务类型"""
    TEXT_GENERATION = "text_generation"    # 文本生成
    CODE_GENERATION = "code_generation"    # 代码生成
    REASONING = "reasoning"                # 推理
    MULTIMODAL = "multimodal"              # 多模态
    EMBEDDING = "embedding"                # 向量嵌入
    RERANK = "rerank"                      # 重排序
    CHAT = "chat"                          # 对话


# ==================== 模型定义 ====================

@dataclass
class Model:
    """模型定义"""
    model_id: str
    name: str
    provider: str
    task_types: List[TaskType]
    weight: int = 10          # 调度权重
    priority: int = 1         # 优先级（1-10）
    max_rps: int = 100        # 最大每秒请求
    current_rps: float = 0.0  # 当前RPS
    latency_ms: float = 0.0    # 平均延迟
    error_rate: float = 0.0    # 错误率
    available: bool = True    # 是否可用
    consecutive_failures: int = 0  # 连续失败次数


# ==================== 任务分类器 ====================

class TaskClassifier:
    """任务分类器 - 根据输入识别任务类型"""
    
    def __init__(self):
        # 关键词到任务类型的映射
        self.keyword_map = {
            TaskType.CODE_GENERATION: [
                "代码", "编程", "function", "def ", "class ", "import ",
                "实现", "算法", "debug", "修复", "开发"
            ],
            TaskType.REASONING: [
                "分析", "推理", "为什么", "逻辑", "思考", "原因",
                "证明", "推导", "计算"
            ],
            TaskType.EMBEDDING: [
                "向量", "embedding", "相似度", "检索", "搜索"
            ],
            TaskType.RERANK: [
                "排序", "rerank", "重排", "相关性"
            ],
            TaskType.MULTIMODAL: [
                "图片", "图像", "视频", "audio", "vision"
            ],
            TaskType.TEXT_GENERATION: [
                "生成", "写作", "创作", "文章", "摘要"
            ],
        }
    
    def classify(self, prompt: str) -> TaskType:
        """根据提示词分类任务类型"""
        prompt_lower = prompt.lower()
        
        scores = {}
        for task_type, keywords in self.keyword_map.items():
            score = sum(1 for kw in keywords if kw in prompt_lower)
            if score > 0:
                scores[task_type] = score
        
        if scores:
            # 返回得分最高的类型
            return max(scores, key=scores.get)
        
        # 默认返回对话类型
        return TaskType.CHAT


# ==================== 负载均衡器 ====================

class LoadBalancer:
    """负载均衡器 - 加权最少连接"""
    
    def __init__(self):
        self.models: Dict[str, Model] = {}
    
    def add_model(self, model: Model):
        """添加模型"""
        self.models[model.model_id] = model
    
    def select_model(self, task_type: TaskType) -> Optional[Model]:
        """选择最佳模型（加权最少连接）"""
        candidates = [
            m for m in self.models.values()
            if task_type in m.task_types and m.available
        ]
        
        if not candidates:
            return None
        
        # 计算得分：权重越高、负载越低、延迟越低、错误率越低越好
        scored = []
        for m in candidates:
            load_factor = 1.0 / (m.current_rps + 1)
            latency_factor = 1.0 / (m.latency_ms + 100)
            error_factor = 1.0 - m.error_rate
            score = m.weight * load_factor * latency_factor * error_factor
            scored.append((m, score))
        
        # 返回得分最高的模型
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[0][0]
    
    def update_stats(self, model_id: str, success: bool, latency: float):
        """更新模型统计"""
        if model_id not in self.models:
            return
        
        m = self.models[model_id]
        
        # 更新延迟
        m.latency_ms = m.latency_ms * 0.9 + latency * 0.1
        
        # 更新错误率
        if not success:
            m.error_rate = m.error_rate * 0.9 + 0.1
            m.consecutive_failures += 1
        else:
            m.error_rate = m.error_rate * 0.9
            m.consecutive_failures = 0
        
        # 检查是否需要熔断
        if m.consecutive_failures >= 3:
            m.available = False
        elif m.consecutive_failures == 0 and m.error_rate < 0.1:
            m.available = True
    
    def get_available_models(self, task_type: TaskType) -> List[Model]:
        """获取可用模型列表"""
        return [
            m for m in self.models.values()
            if task_type in m.task_types and m.available
        ]


# ==================== 熔断器 ====================

class CircuitBreaker:
    """熔断器 - 失败时自动切换"""
    
    def __init__(self):
        self.failure_threshold = 3      # 失败阈值
        self.recovery_timeout = 60      # 恢复超时（秒）
        self.circuits: Dict[str, Dict] = defaultdict(lambda: {
            'failures': 0,
            'last_failure_time': 0,
            'state': 'closed'  # closed, open, half-open
        })
    
    def record_failure(self, model_id: str) -> bool:
        """记录失败，返回是否需要切换"""
        circuit = self.circuits[model_id]
        circuit['failures'] += 1
        circuit['last_failure_time'] = time.time()
        
        if circuit['failures'] >= self.failure_threshold:
            circuit['state'] = 'open'
            return True
        
        return False
    
    def record_success(self, model_id: str):
        """记录成功"""
        circuit = self.circuits[model_id]
        circuit['failures'] = 0
        circuit['state'] = 'closed'
    
    def should_try(self, model_id: str) -> bool:
        """检查是否应该尝试"""
        circuit = self.circuits[model_id]
        
        if circuit['state'] == 'closed':
            return True
        
        if circuit['state'] == 'open':
            # 检查是否超过恢复超时
            if time.time() - circuit['last_failure_time'] > self.recovery_timeout:
                circuit['state'] = 'half-open'
                return True
            return False
        
        # half-open状态，允许尝试
        return True


# ==================== 模型调度器 ====================

class ModelScheduler:
    """模型调度器 - 统一调度入口"""
    
    def __init__(self):
        self.classifier = TaskClassifier()
        self.load_balancer = LoadBalancer()
        self.circuit_breaker = CircuitBreaker()
        self.task_history: List[Dict] = []
    
    def register_model(self, model: Model):
        """注册模型"""
        self.load_balancer.add_model(model)
    
    def dispatch(self, prompt: str, context: Dict = None) -> Dict:
        """调度模型"""
        # 1. 任务分类
        task_type = self.classifier.classify(prompt)
        
        # 2. 选择模型
        model = self.load_balancer.select_model(task_type)
        
        if not model:
            return {
                'success': False,
                'error': 'No available model',
                'task_type': task_type.value
            }
        
        # 3. 记录调度
        dispatch_result = {
            'success': True,
            'model_id': model.model_id,
            'model_name': model.name,
            'provider': model.provider,
            'task_type': task_type.value,
            'timestamp': time.time()
        }
        
        # 更新统计
        self.task_history.append(dispatch_result)
        if len(self.task_history) > 1000:
            self.task_history = self.task_history[-500:]
        
        return dispatch_result
    
    def report_result(self, model_id: str, success: bool, latency: float):
        """报告执行结果"""
        # 更新负载均衡器
        self.load_balancer.update_stats(model_id, success, latency)
        
        # 更新熔断器
        if success:
            self.circuit_breaker.record_success(model_id)
        else:
            self.circuit_breaker.record_failure(model_id)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'total_tasks': len(self.task_history),
            'models': {
                m_id: {
                    'name': m.name,
                    'provider': m.provider,
                    'available': m.available,
                    'latency_ms': round(m.latency_ms, 2),
                    'error_rate': round(m.error_rate, 3),
                    'current_rps': round(m.current_rps, 2)
                }
                for m_id, m in self.load_balancer.models.items()
            }
        }


# ==================== 预设模型配置 ====================

def get_default_scheduler() -> ModelScheduler:
    """获取默认调度器"""
    scheduler = ModelScheduler()
    
    # 注册模型
    models = [
        Model("ark-code-latest", "Ark Code", "doubao", 
              [TaskType.TEXT_GENERATION, TaskType.CODE_GENERATION, TaskType.CHAT], 
              weight=10, priority=10),
        Model("doubao-seed-2.0-code", "Doubao Seed", "doubao",
              [TaskType.CODE_GENERATION, TaskType.REASONING],
              weight=8, priority=9),
        Model("glm-4.7", "GLM-4.7", "zhipu",
              [TaskType.TEXT_GENERATION, TaskType.CODE_GENERATION],
              weight=7, priority=8),
        Model("kimi-k2.5", "Kimi K2.5", "doubao",
              [TaskType.TEXT_GENERATION, TaskType.CHAT],
              weight=6, priority=7),
        Model("deepseek-v3.2", "DeepSeek V3.2", "nvidia",
              [TaskType.REASONING, TaskType.CODE_GENERATION],
              weight=9, priority=9),
        Model("MiniMax-M2.5", "MiniMax M2.5", "modelscope",
              [TaskType.TEXT_GENERATION, TaskType.MULTIMODAL],
              weight=5, priority=6),
    ]
    
    for model in models:
        scheduler.register_model(model)
    
    return scheduler


# ==================== 测试 ====================

if __name__ == "__main__":
    print("="*60)
    print("Symphony Model Scheduler Test")
    print("="*60)
    
    # 创建调度器
    scheduler = get_default_scheduler()
    
    # 测试任务
    test_prompts = [
        "帮我写一个Python函数实现快速排序",
        "分析一下为什么太阳是圆的",
        "写一篇关于春天的文章",
        "帮我搜索相似的内容",
        "今天天气怎么样",
    ]
    
    print("\n--- Dispatch Test ---")
    for prompt in test_prompts:
        result = scheduler.dispatch(prompt)
        print(f"\nPrompt: {prompt[:20]}...")
        print(f"  Task Type: {result['task_type']}")
        print(f"  Model: {result.get('model_name', 'None')}")
        print(f"  Provider: {result.get('provider', 'None')}")
    
    print("\n--- Stats ---")
    stats = scheduler.get_stats()
    print(f"Total Tasks: {stats['total_tasks']}")
    for model_id, info in stats['models'].items():
        print(f"  {info['name']}: {info['provider']}, lat={info['latency_ms']}ms, err={info['error_rate']}")
