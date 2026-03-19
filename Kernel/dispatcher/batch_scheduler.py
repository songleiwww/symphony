#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统 - 批处理优化模块
开发者: 杜子美 (军师参议)
功能: 请求合并机制, 减少GPU Kernel Launch Overhead
目标: 提升并行效率30-50%
"""

import asyncio
import time
import hashlib
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)


@dataclass
class RequestItem:
    """单个请求项"""
    request_id: str
    prompt: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 2000
    callback: Optional[Callable] = None
    metadata: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class BatchRequest:
    """批量请求"""
    batch_id: str
    items: List[RequestItem]
    created_at: float
    deadline: float
    
    def size(self) -> int:
        return len(self.items)


class RequestBuffer:
    """请求缓冲区 - 实现请求合并"""
    
    def __init__(
        self,
        window_ms: int = 100,      # 窗口时间 (毫秒)
        max_batch_size: int = 10,   # 最大批次大小
        max_wait_ms: int = 500       # 最大等待时间
    ):
        self.window_ms = window_ms
        self.max_batch_size = max_batch_size
        self.max_wait_ms = max_wait_ms
        
        # 待处理请求队列
        self.pending: List[RequestItem] = []
        self.lock = asyncio.Lock()
        
        # 调度定时器
        self._scheduler_task: Optional[asyncio.Task] = None
    
    def _compute_similarity(self, prompt1: str, prompt2: str) -> float:
        """计算两个prompt的相似度"""
        # 简单实现: 基于关键词重叠
        words1 = set(prompt1.lower().split())
        words2 = set(prompt2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0.0
    
    def _group_similar_requests(self, items: List[RequestItem]) -> List[List[RequestItem]]:
        """将相似请求分组"""
        if len(items) <= 1:
            return [items]
        
        groups = []
        used = set()
        
        for i, item in enumerate(items):
            if i in used:
                continue
            
            group = [item]
            used.add(i)
            
            for j, other in enumerate(items):
                if j in used:
                    continue
                if item.model == other.model:  # 相同模型
                    similarity = self._compute_similarity(item.prompt, other.prompt)
                    if similarity > 0.3:  # 相似度阈值
                        group.append(other)
                        used.add(j)
            
            groups.append(group)
        
        return groups
    
    async def add(self, item: RequestItem) -> None:
        """添加请求到缓冲区"""
        async with self.lock:
            self.pending.append(item)
            logger.debug(f"添加请求 {item.request_id}, 当前队列: {len(self.pending)}")
    
    async def flush(self) -> List[BatchRequest]:
        """刷新缓冲区, 返回可处理的批次"""
        async with self.lock:
            if not self.pending:
                return []
            
            current_time = time.time()
            deadline = current_time + (self.max_wait_ms / 1000)
            
            # 按模型分组
            model_groups = defaultdict(list)
            for item in self.pending:
                model_groups[item.model].append(item)
            
            batches = []
            
            for model, items in model_groups.items():
                # 进一步按相似度分组
                groups = self._group_similar_requests(items)
                
                for group in groups:
                    batch_items = group[:self.max_batch_size]
                    batch_id = hashlib.md5(
                        f"{time.time()}_{model}".encode()
                    ).hexdigest()[:12]
                    
                    batch = BatchRequest(
                        batch_id=batch_id,
                        items=batch_items,
                        created_at=current_time,
                        deadline=deadline
                    )
                    batches.append(batch)
                    
                    # 从pending中移除已批处理的请求
                    for item in batch_items:
                        self.pending.remove(item)
            
            logger.info(f"生成 {len(batches)} 个批次, 处理 {sum(b.size() for b in batches)} 个请求")
            return batches


class BatchScheduler:
    """批处理调度器 - 核心调度逻辑"""
    
    def __init__(
        self,
        api_executor: Callable,  # API执行函数
        window_ms: int = 100,
        max_batch_size: int = 10,
        max_workers: int = 4
    ):
        self.api_executor = api_executor
        self.buffer = RequestBuffer(
            window_ms=window_ms,
            max_batch_size=max_batch_size
        )
        self.max_workers = max_workers
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "total_batches": 0,
            "avg_batch_size": 0,
            "total_latency": 0,
            "success_count": 0,
            "fail_count": 0
        }
        
        # 启动调度循环
        self._running = False
    
    async def submit(self, prompt: str, model: str, **kwargs) -> str:
        """提交请求, 返回request_id"""
        request_id = hashlib.md5(
            f"{time.time()}_{prompt}".encode()
        ).hexdigest()[:16]
        
        item = RequestItem(
            request_id=request_id,
            prompt=prompt,
            model=model,
            **kwargs
        )
        
        await self.buffer.add(item)
        self.stats["total_requests"] += 1
        
        return request_id
    
    async def _execute_batch(self, batch: BatchRequest) -> List[Dict]:
        """执行单个批次"""
        logger.info(f"执行批次 {batch.batch_id}, 包含 {batch.size()} 个请求")
        
        start_time = time.time()
        results = []
        
        # 串行执行 (可优化为并行)
        for item in batch.items:
            try:
                result = await self.api_executor(
                    prompt=item.prompt,
                    model=item.model,
                    temperature=item.temperature,
                    max_tokens=item.max_tokens
                )
                results.append({
                    "request_id": item.request_id,
                    "success": True,
                    "result": result
                })
                self.stats["success_count"] += 1
            except Exception as e:
                logger.error(f"请求 {item.request_id} 失败: {e}")
                results.append({
                    "request_id": item.request_id,
                    "success": False,
                    "error": str(e)
                })
                self.stats["fail_count"] += 1
        
        latency = time.time() - start_time
        self.stats["total_latency"] += latency
        self.stats["total_batches"] += 1
        self.stats["avg_batch_size"] = (
            self.stats["total_requests"] / max(1, self.stats["total_batches"])
        )
        
        logger.info(f"批次 {batch.batch_id} 完成, 耗时 {latency:.2f}s")
        return results
    
    async def process_loop(self, interval_ms: int = 50):
        """处理循环"""
        self._running = True
        
        while self._running:
            batches = await self.buffer.flush()
            
            if batches:
                # 并行执行多个批次
                tasks = [self._execute_batch(batch) for batch in batches]
                await asyncio.gather(*tasks, return_exceptions=True)
            
            await asyncio.sleep(interval_ms / 1000)
    
    def stop(self):
        """停止调度器"""
        self._running = False
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            "success_rate": (
                self.stats["success_count"] / 
                max(1, self.stats["success_count"] + self.stats["fail_count"])
            ),
            "avg_latency": (
                self.stats["total_latency"] / 
                max(1, self.stats["total_batches"])
            )
        }


# ==================== 真实API测试 ====================

async def test_with_real_api():
    """使用真实API测试批处理"""
    import requests
    
    # 使用火山引擎API
    API_URL = "https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions"
    API_KEY = "your-api-key-here"  # 需替换
    
    async def real_api_call(prompt: str, model: str, **kwargs) -> str:
        """真实API调用"""
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000)
        }
        
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        data = resp.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    # 测试
    scheduler = BatchScheduler(
        api_executor=real_api_call,
        window_ms=100,
        max_batch_size=5
    )
    
    # 提交测试请求
    test_prompts = [
        "你好，请介绍一下自己",
        "今天天气怎么样",
        "给我讲个笑话",
        "Python和JavaScript哪个好",
        "如何学习编程"
    ]
    
    for i, prompt in enumerate(test_prompts):
        await scheduler.submit(prompt, "ep-20250319101524-2jvc9", temperature=0.7)
    
    # 启动处理
    process_task = asyncio.create_task(scheduler.process_loop())
    
    # 等待处理完成
    await asyncio.sleep(5)
    scheduler.stop()
    await process_task
    
    # 输出统计
    stats = scheduler.get_stats()
    print("\n=== 批处理测试结果 ===")
    print(f"总请求数: {stats['total_requests']}")
    print(f"总批次: {stats['total_batches']}")
    print(f"平均批次大小: {stats['avg_batch_size']:.2f}")
    print(f"成功率: {stats['success_rate']*100:.1f}%")
    print(f"平均延迟: {stats['avg_latency']:.2f}s")


if __name__ == "__main__":
    asyncio.run(test_with_real_api())
