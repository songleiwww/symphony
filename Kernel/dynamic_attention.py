#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统 - 动态注意力机制模块
开发者: 李太白 (中书侍郎)
功能: 实现动态注意力机制, 根据上下文动态调整注意力分布
"""

import time
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class AttentionHead:
    """注意力头"""
    head_id: int
    query_dim: int = 64
    key_dim: int = 64
    value_dim: int = 64
    
    # 注意力权重
    weights: np.ndarray = field(init=False)
    
    def __post_init__(self):
        # 初始化随机权重
        self.weights = np.random.randn(self.query_dim, self.key_dim) * 0.1


@dataclass
class AttentionContext:
    """注意力上下文"""
    prompt: str
    tokens: List[str]
    attention_weights: np.ndarray
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)


class DynamicAttention:
    """动态注意力机制"""
    
    def __init__(
        self,
        num_heads: int = 8,
        sparsity: float = 0.7,      # 稀疏度 (0-1)
        update_frequency: int = 100, # 更新频率
        memory_size: int = 1000       # 记忆大小
    ):
        self.num_heads = num_heads
        self.sparsity = sparsity
        self.update_frequency = update_frequency
        self.memory_size = memory_size
        
        # 初始化注意力头
        self.heads = [
            AttentionHead(head_id=i, query_dim=64, key_dim=64, value_dim=64)
            for i in range(num_heads)
        ]
        
        # 上下文记忆
        self.memory: deque = deque(maxlen=memory_size)
        
        # 统计
        self.stats = {
            "total_updates": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_attention_time": 0
        }
        
        # 调度计数器
        self._调度计数 = 0
    
    def _tokenize(self, text: str) -> List[str]:
        """简单分词"""
        # 简单空格分词
        tokens = text.lower().split()
        return tokens
    
    def _compute_attention_scores(
        self, 
        query_tokens: List[str], 
        key_tokens: List[str]
    ) -> np.ndarray:
        """计算注意力分数"""
        # 简化的注意力计算
        seq_len = max(len(query_tokens), len(key_tokens))
        scores = np.zeros((len(query_tokens), len(key_tokens)))
        
        for i, q in enumerate(query_tokens):
            for j, k in enumerate(key_tokens):
                # 基于token重叠计算相似度
                if q == k:
                    scores[i, j] = 1.0
                elif q in k or k in q:
                    scores[i, j] = 0.5
                else:
                    scores[i, j] = 0.1
        
        # 归一化
        if scores.sum() > 0:
            scores = scores / scores.sum(axis=1, keepdims=True)
        
        return scores
    
    def _apply_sparsity(self, attention_weights: np.ndarray) -> np.ndarray:
        """应用稀疏性 - 只保留top-k"""
        if self.sparsity <= 0:
            return attention_weights
        
        sparse_weights = attention_weights.copy()
        k = max(1, int(attention_weights.shape[-1] * (1 - self.sparsity)))
        
        # 对每个query，只保留top-k
        for i in range(sparse_weights.shape[0]):
            indices = np.argsort(sparse_weights[i])[-k:]
            mask = np.zeros_like(sparse_weights[i])
            mask[indices] = 1
            sparse_weights[i] *= mask
        
        # 重新归一化
        row_sums = sparse_weights.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        sparse_weights = sparse_weights / row_sums
        
        return sparse_weights
    
    def compute_attention(
        self, 
        prompt: str,
        context: Optional[str] = None
    ) -> AttentionContext:
        """计算注意力"""
        start_time = time.time()
        
        tokens = self._tokenize(prompt)
        
        # 如果有上下文，合并计算
        if context:
            context_tokens = self._tokenize(context)
            all_tokens = tokens + context_tokens
        else:
            all_tokens = tokens
        
        # 计算注意力分数
        attention_weights = self._compute_attention_scores(tokens, all_tokens)
        
        # 应用稀疏性
        attention_weights = self._apply_sparsity(attention_weights)
        
        # 创建上下文
        ctx = AttentionContext(
            prompt=prompt,
            tokens=tokens,
            attention_weights=attention_weights,
            metadata={"context": context}
        )
        
        # 更新统计
        latency = time.time() - start_time
        self.stats["avg_attention_time"] = (
            0.9 * self.stats["avg_attention_time"] + 0.1 * latency
        )
        
        return ctx
    
    def update_weights(self, context: AttentionContext) -> None:
        """根据上下文更新注意力权重"""
        self._调度计数 += 1
        
        # 更新每个头的权重
        for head in self.heads:
            # 基于上下文的注意力调整
            adjustment = context.attention_weights.mean(axis=0)
            
            # 指数移动平均更新
            head.weights = 0.9 * head.weights + 0.1 * adjustment[:, :head.query_dim]
        
        # 保存到记忆
        self.memory.append(context)
        
        self.stats["total_updates"] += 1
        
        if self._调度计数 % self.update_frequency == 0:
            logger.info(f"注意力权重已更新 {self.stats['total_updates']} 次")
    
    def get_important_tokens(self, prompt: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """获取最重要的token"""
        ctx = self.compute_attention(prompt)
        
        # 计算每个token的平均注意力
        avg_attention = ctx.attention_weights.mean(axis=0)
        
        # 排序
        token_weights = list(zip(ctx.tokens, avg_attention))
        token_weights.sort(key=lambda x: x[1], reverse=True)
        
        return token_weights[:top_k]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = self.stats["cache_hits"] + self.stats["cache_misses"]
        hit_rate = self.stats["cache_hits"] / max(1, total)
        
        return {
            "num_heads": self.num_heads,
            "sparsity": self.sparsity,
            "total_updates": self.stats["total_updates"],
            "cache_hit_rate": hit_rate,
            "avg_attention_time": self.stats["avg_attention_time"],
            "memory_size": len(self.memory)
        }


class AttentionBasedScheduler:
    """基于注意力的调度器"""
    
    def __init__(self, attention: DynamicAttention, router: Any):
        self.attention = attention
        self.router = router
    
    def schedule(self, prompt: str) -> Optional[Any]:
        """基于注意力调度"""
        # 计算注意力
        ctx = self.attention.compute_attention(prompt)
        
        # 获取重要token
        important_tokens = self.attention.get_important_tokens(prompt)
        
        # 基于重要token选择模型
        prompt_with_context = " ".join([t for t, _ in important_tokens])
        
        # 让路由器选择模型
        model = self.router.select_model(prompt_with_context)
        
        return model


# ==================== 测试 ====================

def test_attention():
    """测试动态注意力"""
    attention = DynamicAttention(num_heads=8, sparsity=0.7)
    
    test_prompts = [
        "Python 编程中的列表推导式如何使用",
        "机器学习模型的训练流程",
        "编写一个快速排序算法",
        "深度学习中的注意力机制原理",
        "如何优化SQL查询性能"
    ]
    
    print("=== 动态注意力测试 ===\n")
    
    for prompt in test_prompts:
        # 计算注意力
        ctx = attention.compute_attention(prompt)
        
        # 获取重要token
        important = attention.get_important_tokens(prompt, top_k=3)
        
        print(f"Prompt: {prompt[:30]}...")
        print(f"  Tokens: {ctx.tokens[:5]}...")
        print(f"  重要Token: {important}")
        print(f"  注意力矩阵: {ctx.attention_weights.shape}")
        print()
        
        # 更新权重
        attention.update_weights(ctx)
    
    # 输出统计
    stats = attention.get_stats()
    print("=== 统计信息 ===")
    print(f"  头数: {stats['num_heads']}")
    print(f"  稀疏度: {stats['sparsity']}")
    print(f"  更新次数: {stats['total_updates']}")
    print(f"  平均注意力时间: {stats['avg_attention_time']*1000:.2f}ms")
    print(f"  记忆大小: {stats['memory_size']}")


if __name__ == "__main__":
    test_attention()
