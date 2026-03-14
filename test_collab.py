# -*- coding: utf-8 -*-
"""
并发模型协作测试 - 验证多模型并行调用能力
"""
import sys
import os
import time
import importlib.util

# 设置控制台编码
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 设置项目路径
project_dir = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony"
os.chdir(project_dir)
sys.path.insert(0, project_dir)

# 导入核心模块
print("=" * 70)
print("并发模型协作测试报告")
print("=" * 70)

# 1. 加载内核
print("\n[1] 加载内核...")
spec = importlib.util.spec_from_file_location("kernel_loader", "Kernel/kernel_loader.py")
kernel_loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kernel_loader)
kernel = kernel_loader.get_kernel()
print(f"    ✓ 官属角色: {len(kernel.roles)} 位")
print(f"    ✓ 模型配置: {len(kernel.models)} 个")

# 2. 加载模型管理器
print("\n[2] 加载模型管理器...")
spec2 = importlib.util.spec_from_file_location("model_call_manager", "core/model_call_manager.py")
model_mgr_mod = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(model_mgr_mod)
model_manager = model_mgr_mod.get_model_manager()
print(f"    ✓ 可用模型: {len(model_manager.model_configs)}")

# 3. 加载协作引擎
print("\n[3] 加载协作引擎...")
spec3 = importlib.util.spec_from_file_location("collaboration_engine", "core/collaboration_engine.py")
collab_mod = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(collab_mod)
collaboration = collab_mod.get_collaboration_engine()
print(f"    ✓ 协作引擎就绪")

# 4. 查看可用模型
print("\n[4] 可用模型列表:")
print("-" * 50)
providers = {}
for name, config in list(model_manager.model_configs.items())[:10]:
    provider = config.get("provider", "未知")
    if provider not in providers:
        providers[provider] = 0
    providers[provider] += 1
    print(f"    • {name} ({provider})")

print(f"\n    ... 共 {len(model_manager.model_configs)} 个模型")
print(f"    服务商统计: {providers}")

# 5. 并发调用测试
print("\n" + "=" * 70)
print("[5] 并发调用测试")
print("=" * 70)

test_prompts = [
    "你好，请用一句话介绍自己",
    "什么是人工智能？",
    "写一个最简单的Python函数",
]

# 使用 ThreadPoolExecutor 进行并发测试
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

results = []
errors = []
lock = threading.Lock()

def call_model(model_name, prompt):
    """调用单个模型"""
    try:
        start = time.time()
        # call_model(model_name, prompt) - 参数顺序修正
        success, result, info = model_manager.call_model(model_name, prompt)
        elapsed = time.time() - start
        with lock:
            if success:
                results.append({
                    "prompt": prompt[:30],
                    "model": model_name,
                    "result": result[:100] if result else "无响应",
                    "time": elapsed,
                    "success": True
                })
            else:
                errors.append({
                    "prompt": prompt[:30],
                    "model": model_name,
                    "error": str(result)[:50]
                })
        return success
    except Exception as e:
        with lock:
            errors.append({
                "prompt": prompt[:30],
                "model": model_name,
                "error": str(e)[:50]
            })
        return False

# 选择几个不同提供商的模型
test_models = []
for name in model_manager.model_configs:
    config = model_manager.model_configs[name]
    if len(test_models) < 3:  # 选3个模型
        test_models.append(name)

print(f"\n测试模型: {test_models}")
print(f"测试提示: {len(test_prompts)} 个")
print(f"总调用次数: {len(test_models) * len(test_prompts)}")
print("\n开始并发执行...")

start_time = time.time()

# 并发执行
with ThreadPoolExecutor(max_workers=6) as executor:
    futures = []
    for model in test_models:
        for prompt in test_prompts:
            futures.append(executor.submit(call_model, model, prompt))
    
    # 等待完成
    for future in as_completed(futures):
        try:
            future.result()
        except Exception as e:
            pass

total_time = time.time() - start_time

# 6. 结果统计
print("\n" + "=" * 70)
print("[6] 测试结果")
print("=" * 70)

print(f"\n总调用次数: {len(test_models) * len(test_prompts)}")
print(f"成功: {len(results)}")
print(f"失败: {len(errors)}")
print(f"总耗时: {total_time:.2f}秒")
print(f"平均响应: {total_time/len(results):.2f}秒/请求" if results else "N/A")

if results:
    print("\n成功案例:")
    for r in results[:5]:
        print(f"  ✓ {r['model']}: {r['prompt']}... ({r['time']:.2f}s)")
        print(f"    → {r['result']}")

if errors:
    print("\n失败案例:")
    for e in errors[:3]:
        print(f"  ✗ {e['model']}: {e['prompt']}...")
        print(f"    → {e['error']}")

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)
