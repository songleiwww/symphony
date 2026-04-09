# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# 序境系统蜂蚁计算节点-3 运行脚本
# 已严格遵守所有调度规?import sys
import os
import time
import logging
from datetime import datetime

# 加载序境内核
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
from Kernel import evolution_kernel

# 核心配置（严格遵循调度规则）
NODE_ID = "bee_ant_node_3"
ALLOWED_PROVIDERS = ["doubao", "glm", "qianwen"]  # 规则1：字?智谱/阿里三家并行，禁止单依赖
MAX_QPS_PER_PROVIDER = 2  # 规则2：同服务商QPS?
SNAPSHOT_INTERVAL = 1800  # 规则3：每30分钟=1800秒同步进度快?
# 初始化日志（全操作可追溯?log_path = os.path.join(os.path.dirname(__file__), f"logs/node_{NODE_ID}_operation.log")
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filemode="a"
)
logger = logging.getLogger(__name__)
logger.info(f"=== 蜂蚁计算节点 {NODE_ID} 启动 ===")

# 初始化进化内?kernel = evolution_kernel.EvolutionKernel()
logger.info("?进化内核初始化完?)

# 规则1：配置服务商限制，禁止单服务商依?kernel.model_federation.allowed_providers = ALLOWED_PROVIDERS
kernel.model_federation.min_available_providers = 2  # 至少2家服务商同时在线
kernel.model_federation.enable_failover = True
logger.info(f"?规则1生效：允许服务商 {ALLOWED_PROVIDERS}，强制至?家可用，禁止单依?)

# 规则2：配置QPS限制与调度策?kernel.scheduler.max_concurrent_per_provider = MAX_QPS_PER_PROVIDER
kernel.scheduler.queue_mode = "FIFO"
kernel.scheduler.prioritize_core_tasks = True
logger.info(f"?规则2生效：单服务商QPS上限{MAX_QPS_PER_PROVIDER}，超阈值FIFO排队，核心P0任务优先")

# 规则3：配置进度快照与可追?snapshot_dir = os.path.join(os.path.dirname(__file__), f"progress/{NODE_ID}")
os.makedirs(snapshot_dir, exist_ok=True)
kernel.snapshot_interval = SNAPSHOT_INTERVAL
kernel.snapshot_output_dir = snapshot_dir
kernel.enable_operation_tracing = True
logger.info(f"?规则3生效：每{SNAPSHOT_INTERVAL/60}分钟同步进度快照，所有操作写入日志可追溯")

# 加入全局集群
kernel.join_global_cluster(node_id=NODE_ID, node_type="worker", priority="P0")
logger.info(f"?节点 {NODE_ID} 已成功加入全局蜂蚁集群调度")

print(f"\n🎉 蜂蚁计算节点 {NODE_ID} 已成功上线！")
print(f"\n=== 已生效调度规?===")
print(f"1. 多服务商调度：仅使用字节(doubao)、智?glm)、阿?qianwen)三家模型，强制至?家同时可用，禁止单服务商依赖")
print(f"2. QPS限制：同服务商调用QPS?，超出阈值自动进入FIFO队列，P0核心任务优先处理")
print(f"3. 可追溯性：所有操作自动写入日?{log_path}，每30分钟同步进度快照到集群，全流程可审计")
print(f"\n节点已就绪，等待接收P0功能开发并行任?..")
logger.info("节点启动完成，进入运行状?)

# 保持节点运行
last_snapshot = time.time()
while True:
    # 手动快照实现（解决内置快照bug?    if time.time() - last_snapshot >= SNAPSHOT_INTERVAL:
        snapshot_file = os.path.join(snapshot_dir, f"snapshot_{int(time.time())}.json")
        kernel.export_snapshot(snapshot_file)
        logger.info(f"📸 进度快照已生成：{snapshot_file}")
        last_snapshot = time.time()
    
    # 处理任务队列
    kernel.process_pending_tasks()
    time.sleep(10)

