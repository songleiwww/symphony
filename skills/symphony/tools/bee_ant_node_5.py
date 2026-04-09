# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# 序境系统蜂蚁计算节点-5 初始化脚?# 遵守调度规则：多服务商并行、QPS限制、进度同步、可追溯

import sys
import os
import time
import logging
from datetime import datetime

# 加载序境内核路径
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
from Kernel import evolution_kernel

# 节点配置
NODE_ID = "bee_ant_node_5"
NODE_TYPE = "computing"
PRIORITY_LEVEL = "P0"
ALLOWED_PROVIDERS = ["doubao", "glm", "qianwen"]  # 字节/智谱/阿里三家
MAX_QPS_PER_PROVIDER = 2
SNAPSHOT_INTERVAL_MINUTES = 30

def init_node():
    print(f"[{datetime.now()}] 初始化蜂蚁计算节?{NODE_ID}...")
    
    # 配置全局日志追溯（所有操作自动写入日志文件）
    log_path = os.path.join(os.path.dirname(__file__), f"logs/node_{NODE_ID}_trace.log")
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='a',
        force=True
    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(console_handler)
    
    # 1. 初始化进化内?    kernel = evolution_kernel.EvolutionKernel()
    # 设置节点属?    kernel.node_id = NODE_ID
    kernel.node_type = NODE_TYPE
    kernel.priority = PRIORITY_LEVEL
    
    # 2. 通过多智能体协调器配置所有调度规?    coordinator = kernel.multi_agent_coordinator
    # 配置服务商限制：仅允许字?智谱/阿里三家，禁止单服务商依?    coordinator.config.allowed_providers = ALLOWED_PROVIDERS
    coordinator.config.min_providers_per_task = 2  # 至少2家服务商同时可用，禁止单依赖
    coordinator.config.provider_failover_enabled = True
    
    # 3. 配置QPS限制与调度规?    coordinator.config.max_qps_per_provider = MAX_QPS_PER_PROVIDER
    coordinator.config.queue_strategy = "FIFO"
    coordinator.config.core_task_first = True
    coordinator.config.node_priority = PRIORITY_LEVEL
    
    # 4. 配置进度快照和可追溯?    snapshot_path = os.path.join(os.path.dirname(__file__), "progress", f"node_{NODE_ID}")
    os.makedirs(snapshot_path, exist_ok=True)
    coordinator.config.snapshot_interval_seconds = SNAPSHOT_INTERVAL_MINUTES * 60
    coordinator.config.snapshot_save_dir = snapshot_path
    coordinator.config.trace_all_operations = True
    coordinator.config.trace_log_path = os.path.join(os.path.dirname(__file__), f"logs/node_{NODE_ID}_trace.log")
    
    logging.info(f"?所有调度规则配置完?)
    
    # 5. 注册节点到全局集群调度
    coordinator.register_compute_node(
        node_id=NODE_ID,
        node_type=NODE_TYPE,
        priority=PRIORITY_LEVEL,
        capabilities=["p0_development", "parallel_execution"]
    )
    logging.info(f"?节点 {NODE_ID} 已成功加入全局蜂蚁集群调度")
    
    print(f"\n🎉 蜂蚁计算节点 {NODE_ID} 启动完成?)
    print(f"=== 已生效调度规?===")
    print(f"1. 多服务商调度：仅使用字节(doubao)/智谱(glm)/阿里(qianwen)三家模型，强制至?家同时可用，禁止单服务商依赖")
    print(f"2. QPS限制：单服务商调用QPS?，超出阈值自动进入FIFO队列，P0核心任务优先处理")
    print(f"3. 可追溯性：所有操作自动写入日志文?{log_path}，每{SNAPSHOT_INTERVAL_MINUTES}分钟同步进度快照到集群，全流程可审计")
    print(f"\n节点已就绪，等待接收P0功能开发并行任?..")
    
    # 启动节点工作循环
    while True:
        # 保持节点运行，接收调度任?        time.sleep(60)
        logging.debug(f"节点 {NODE_ID} 运行正常，等待任?..")

if __name__ == "__main__":
    # 创建必要目录
    os.makedirs(os.path.join(os.path.dirname(__file__), "logs"), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), "progress", f"node_{NODE_ID}"), exist_ok=True)
    
    init_node()

