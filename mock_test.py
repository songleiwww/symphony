# -*- coding: utf-8 -*-
"""
模拟并发模型测试 - 展示并发能力
"""
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

print("=" * 70)
print("模拟并发模型协作测试 - 展示并发能力")
print("=" * 70)

# 模拟模型响应
def mock_model_call(model_name, prompt, delay=1.5):
    """模拟模型调用 - 固定延迟"""
    time.sleep(delay)
    return f"[{model_name}] 处理: {prompt[:20]}..."

# 测试配置
models = ["GLM-4.7", "Qwen2.5-14B", "GPT-4", "Claude-3"]
prompts = [
    "分析这段代码的性能问题",
    "优化这个算法的时间复杂度",
    "解释什么是设计模式"
]

print(f"\n测试场景: {len(models)}个模型 x {len(prompts)}个提示 = {len(models)*len(prompts)}次调用")
print(f"模型: {models}")
print(f"提示: {prompts}")

# Test 1: 串行执行
print("\n" + "=" * 70)
print("[Test 1] 串行执行 ( Sequential )")
print("=" * 70)
start = time.time()
results_sequential = []
for model in models:
    for prompt in prompts:
        result = mock_model_call(model, prompt)
        results_sequential.append(result)
seq_time = time.time() - start
print(f"串行耗时: {seq_time:.2f}秒")

# Test 2: 并行执行
print("\n" + "=" * 70)
print("[Test 2] 并行执行 ( Parallel )")
print("=" * 70)

results_parallel = []
lock = threading.Lock()

def parallel_call(model, prompt):
    result = mock_model_call(model, prompt)
    with lock:
        results_parallel.append(result)

start = time.time()
with ThreadPoolExecutor(max_workers=6) as executor:
    futures = []
    for model in models:
        for prompt in prompts:
            futures.append(executor.submit(parallel_call, model, prompt))
    for f in as_completed(futures):
        f.result()
par_time = time.time() - start
print(f"并行耗时: {par_time:.2f}秒")

# Test 3: 分组并行
print("\n" + "=" * 70)
print("[Test 3] 分组并行 ( Batch Parallel )")
print("=" * 70)

def batch_call(batch):
    """批量调用 - 每组一起返回"""
    return [mock_model_call(m, p) for m, p in batch]

# 创建批次
batches = []
for i in range(0, len(models)*len(prompts), 4):
    batch = []
    for j in range(i, min(i+4, len(models)*len(prompts))):
        model_idx = j % len(models)
        prompt_idx = j // len(models)
        if prompt_idx < len(prompts):
            batch.append((models[model_idx], prompts[prompt_idx]))
    if batch:
        batches.append(batch)

start = time.time()
results_batch = []
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(batch_call, batch) for batch in batches]
    for f in as_completed(futures):
        results_batch.extend(f.result())
batch_time = time.time() - start
print(f"批次耗时: {batch_time:.2f}秒")

# 总结
print("\n" + "=" * 70)
print("性能对比")
print("=" * 70)
total_calls = len(models) * len(prompts)
print(f"总调用次数: {total_calls}")
print(f"串行: {seq_time:.2f}秒 ({total_calls/seq_time:.1f} 调用/秒)")
print(f"并行: {par_time:.2f}秒 ({total_calls/par_time:.1f} 调用/秒)")
print(f"批次: {batch_time:.2f}秒 ({total_calls/batch_time:.1f} 调用/秒)")
print(f"\n加速比:")
print(f"  并行 vs 串行: {seq_time/par_time:.1f}x 加速")
print(f"  批次 vs 串行: {seq_time/batch_time:.1f}x 加速")

print("\n" + "=" * 70)
print("测试完成 - 并发框架工作正常!")
print("=" * 70)
