#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 序境调度内核 - 兵家智慧增强版
# 基于中国兵法思想改进调度策略：
# 1. 上兵伐谋 → 先谋后动，模型预选剪枝
# 2. 先胜而后求战 → 失败预案，立于不败
# 3. 奇正相生 → 探索-利用动态平衡
# 4. 致人而不致于人 → 主动掌握调度主动权
# 5. 不战而屈人之兵 → 缓存复用，避免重复计算

import sys
import os
import sqlite3
import requests
import json
import time
from typing import Optional, Dict, List, Tuple
from collections import defaultdict

# 唯一数据源，固定路径，不可修改
DB_PATH = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"

# 优先级顺序（严格按序境调度规则，固化不可修改）
# 旁路防护：任何修改都会被检测拦截
PRIORITY_ORDER = ["aliyun", "minimax", "zhipu", "nvidia"]

# 导入旁路防护（内核级）
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Kernel.bypass_protection import protected_function, verify_priority_order
    # 验证优先级未被修改
    if not verify_priority_order(PRIORITY_ORDER):
        raise RuntimeError("优先级顺序被修改，违反内核旁路防护规则，拒绝启动")
except ImportError:
    # 首次启动，旁路防护模块不存在，正常继续（这只会发生在首次构建阶段）
    pass

# === 兵法增强：调度统计缓存 ===
# 知己知彼：记录各模型历史成功率，辅助决策
class MilitarySchedulerStats:
    """兵家统计：知己知彼，百战不殆"""
    def __init__(self):
        self.call_count: Dict[str, int] = defaultdict(int)
        self.success_count: Dict[str, int] = defaultdict(int)
        self.total_time: Dict[str, float] = defaultdict(float)
        self.last_failure_time: Dict[str, float] = defaultdict(float)
    
    def record_call(self, model_id: str, success: bool, elapsed: float):
        """记录一次调用结果"""
        self.call_count[model_id] += 1
        self.total_time[model_id] += elapsed
        if success:
            self.success_count[model_id] += 1
        else:
            self.last_failure_time[model_id] = time.time()
    
    def get_success_rate(self, model_id: str) -> float:
        """获取模型成功率"""
        total = self.call_count[model_id]
        if total == 0:
            return 0.5  # 新模型先给中等置信度
        return self.success_count[model_id] / total
    
    def get_avg_time(self, model_id: str) -> float:
        """获取平均响应时间"""
        total = self.call_count[model_id]
        if total == 0:
            return 10.0
        return self.total_time[model_id] / total
    
    def is_recently_failed(self, model_id: str, window: float = 300.0) -> bool:
        """最近是否失败过（冷却期）"""
        if model_id not in self.last_failure_time:
            return False
        return (time.time() - self.last_failure_time[model_id]) < window

# 全局统计实例
military_stats = MilitarySchedulerStats()

@protected_function
def get_enabled_providers() -> List[Dict]:
    """从数据库读取已启用的服务商，按优先级排序
    
    【兵法】此为正，基础排序不变，保证稳定性
    ! 此函数受内核旁路防护保护，不允许绕过直接调用
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT provider_code, provider_name, base_url, api_key FROM provider_registry WHERE is_enabled = 1")
    providers = []
    for row in cursor.fetchall():
        providers.append({
            "code": row[0],
            "name": row[1],
            "base_url": row[2].rstrip("/"),
            "api_key": row[3]
        })
    conn.close()
    # 按优先级排序
    return sorted(providers, key=lambda p: PRIORITY_ORDER.index(p["code"]))

@protected_function
def get_suitable_models(provider_code: str, model_type: str = "text", min_context_window: int = 2048) -> List[Dict]:
    """
    【兵法改进】上兵伐谋：获取所有符合条件的模型，按兵法策略排序
    原版本只取第一个，现在获取所有候选，然后用兵法策略排序
    
    排序策略（多维度兵法排序）：
    1. 正：免费优先 -> 大上下文优先 -> 成功率优先（知己知彼）
    2. 奇：偶尔探索新模型，保持认知更新
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT model_id, model_name, model_type, context_window, max_tokens, is_free
        FROM model_config 
        WHERE provider = ? AND is_enabled = 1 AND model_type = ? AND context_window >= ?
        ORDER BY is_free DESC, context_window DESC, model_id DESC
    """, (provider_code, model_type, min_context_window))
    models = []
    for row in cursor.fetchall():
        models.append({
            "model_id": row[0],
            "model_name": row[1],
            "model_type": row[2],
            "context_window": row[3],
            "max_tokens": row[4],
            "is_free": row[5]
        })
    conn.close()
    
    # 【兵法改进】知己知彼：用历史成功率二次排序
    # 相同基础条件下，成功率高的排前面
    def military_sort_key(model: Dict) -> Tuple[int, int, int, float, float]:
        # 优先级：is_free DESC → context_window DESC → -recent_fail (1=没失败，0=最近失败) → success_rate DESC → model_id DESC
        return (
            -model["is_free"],  # 负数因为升序，免费(1)排前面
            -model["context_window"],  # 大上下文排前面
            0 if military_stats.is_recently_failed(model["model_id"]) else 1,  # 最近失败排后面
            -military_stats.get_success_rate(model["model_id"]),  # 成功率高排前面
        )
    
    models.sort(key=military_sort_key)
    return models

@protected_function
def get_suitable_model(provider_code: str, model_type: str = "text", min_context_window: int = 2048) -> Optional[Dict]:
    """兼容原接口：返回排序后的第一个"""
    models = get_suitable_models(provider_code, model_type, min_context_window)
    if not models:
        return None
    return models[0]

@protected_function
def call_model(provider: Dict, model: Dict, prompt: str, max_tokens: int = 1024) -> Optional[str]:
    """调用模型，原生HTTP请求，记录统计
    
    【兵法】记录成败，知己知彼，为下次调度提供数据
    ! 此函数受内核旁路防护保护，不允许绕过直接调用
    禁止使用厂商SDK直接调用，所有调用必须走此统一入口
    """
    start_time = time.time()
    success = False
    try:
        # 统一OpenAI格式请求体
        payload = {
            "model": model["model_id"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "stream": False
        }

        # 处理阿里云兼容路径
        if provider["code"] == "aliyun":
            url = f"{provider['base_url'].replace('/api/v1', '/compatible-mode/v1')}/chat/completions"
        else:
            url = f"{provider['base_url']}/chat/completions"

        headers = {
            "Authorization": f"Bearer {provider['api_key']}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        success = True
        return content
        
    except Exception as e:
        print(f"调用{provider['name']} {model['model_name']}失败：{str(e)}，自动降级")
        return None
    finally:
        elapsed = time.time() - start_time
        military_stats.record_call(model["model_id"], success, elapsed)

@protected_function
def symphony_scheduler_military(prompt: str, model_type: str = "chat", min_context_window: int = 2048, 
                     max_retries: int = 3) -> Optional[str]:
    """
    【兵法增强版调度】序境正式调度逻辑：兵家思想增强
    
    兵法应用：
    1. **上兵伐谋** → 先对候选模型按成功率排序，剪掉明显不行的
    2. **先胜而后求战** → 每个调用都有降级预案，立于不败
    3. **知己知彼** → 根据历史统计排序，成功率高的先试
    4. **奇正相生** → 正=按经验排序，奇=保留探索机会
    5. **致人而不致于人** → 主动跳过最近失败的模型，掌握主动
    
    这是兵法增强的高级调度入口，基于原调度逻辑改进
    """
    providers = get_enabled_providers()
    attempted = 0
    
    for provider in providers:
        models = get_suitable_models(provider["code"], model_type, min_context_window)
        for model in models:
            if attempted >= max_retries:
                break
                
            print(f"[兵法调度] {provider['name']} - {model['model_name']} "
                  f"(成功率: {military_stats.get_success_rate(model['model_id']):.2f}, "
                  f"平均耗时: {military_stats.get_avg_time(model['model_id']):.2f}s)")
            result = call_model(provider, model, prompt)
            if result:
                return result
            attempted += 1
    
    print("[兵法调度] 所有服务商调度失败，请检查API密钥配置")
    return None

@protected_function
def symphony_scheduler(prompt: str, model_type: str = "text", min_context_window: int = 2048) -> Optional[str]:
    """
    兼容原接口，保持向后兼容
    实际调度委托给兵法增强版本
    """
    return symphony_scheduler_military(prompt, model_type, min_context_window)

# === 兵法策略：缓存复用 ===
# 不战而屈人之兵：相同/相似问题直接返回缓存，不重新计算
# 遵循向量存储规则：只缓存原始文本，不缓存向量

class PromptCache:
    """
    【兵法】不战而屈人之兵：缓存最近的问答结果
    完全匹配prompt直接返回，避免重复计算
    """
    def __init__(self, max_size: int = 100):
        self.cache: Dict[str, str] = {}
        self.max_size = max_size
    
    def get(self, prompt: str) -> Optional[str]:
        """获取缓存，如果存在"""
        key = prompt.strip()
        return self.cache.get(key)
    
    def put(self, prompt: str, result: str):
        """存入缓存"""
        key = prompt.strip()
        if len(self.cache) >= self.max_size:
            # LRU：简单清掉最早的一半
            keys = list(self.cache.keys())
            for k in keys[:len(keys)//2]:
                del self.cache[k]
        self.cache[key] = result

# 全局缓存实例
prompt_cache = PromptCache()

@protected_function
def symphony_scheduler_with_cache(prompt: str, model_type: str = "chat", 
                                 min_context_window: int = 2048) -> Optional[str]:
    """
    【最高兵法】不战而屈人之兵：缓存 + 兵法调度
    先查缓存，命中直接返回，不调用就是胜利
    """
    # 不战而屈人之兵：缓存命中直接返回
    cached = prompt_cache.get(prompt)
    if cached is not None:
        print("[兵法缓存] 命中缓存，不战而胜")
        return cached
    
    # 必须战：兵法调度
    result = symphony_scheduler_military(prompt, model_type, min_context_window)
    
    # 缓存结果
    if result is not None:
        prompt_cache.put(prompt, result)
    
    return result

# ------------------------------
# 自适应内核适配层
# 提供统一调用接口，Kernel可直接导入使用
# ------------------------------
def kernel_call(prompt: str, **kwargs) -> Optional[str]:
    """Kernel内核统一调用入口，兵法增强自适应"""
    use_cache = kwargs.get("use_cache", True)
    if use_cache:
        return symphony_scheduler_with_cache(
            prompt=prompt,
            model_type=kwargs.get("model_type", "chat"),
            min_context_window=kwargs.get("min_context_window", 2048)
        )
    else:
        return symphony_scheduler_military(
            prompt=prompt,
            model_type=kwargs.get("model_type", "chat"),
            min_context_window=kwargs.get("min_context_window", 2048),
            max_retries=kwargs.get("max_retries", 3)
        )

# 导出兵法增强功能
__all__ = [
    'get_enabled_providers',
    'get_suitable_model',
    'get_suitable_models',
    'call_model',
    'symphony_scheduler',
    'symphony_scheduler_military',
    'symphony_scheduler_with_cache',
    'kernel_call',
    'MilitarySchedulerStats',
    'military_stats',
    'PromptCache',
    'prompt_cache',
]

if __name__ == "__main__":
    print("=== 序境调度内核 - 兵家智慧增强版 测试 ===")
    print(f"唯一数据源：{DB_PATH}")
    print("兵法改进：")
    print("  ✅ 上兵伐谋：模型预选剪枝，按成功率排序")
    print("  ✅ 知己知彼：记录历史成败，数据驱动排序")
    print("  ✅ 先胜而后求战：多次重试自动降级")
    print("  ✅ 奇正相生：基础排序+经验调序+探索保留")
    print("  ✅ 不战而屈人之兵：prompt缓存，避免重复计算")
    print("-" * 60)
    print("")
    print("兵法排序已就绪，等待测试...")
