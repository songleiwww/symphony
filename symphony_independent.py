#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响独立运行系统 - 配置流程 + 使用说明 + 导图
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from subagent_manager import SubAgentManager

# 独立运行任务
TASKS = [
    {"expert": "林架构", "provider": "cherry-doubao", 
     "prompt": "设计交响独立运行架构 - 主程序入口、配置文件结构、环境变量设置。输出完整代码。"},
    {"expert": "张配置", "provider": "cherry-doubao", 
     "prompt": "设计配置管理流程 - API Key配置、模型选择、多Provider设置。输出配置模板。"},
    {"expert": "王文档", "provider": "cherry-doubao", 
     "prompt": "编写快速开始指南 - 5步启动、依赖安装、运行示例。输出Markdown格式文档。"},
    {"expert": "陈导图", "provider": "cherry-doubao", 
     "prompt": "绘制系统架构图 - 用Mermaid格式展示核心模块、数据流、调用关系。"},
    {"expert": "赵运维", "provider": "cherry-doubao", 
     "prompt": "设计一键启动脚本 - run_symphony.bat，包含环境检查、依赖安装、启动命令。"},
    {"expert": "吴测试", "provider": "cherry-doubao", 
     "prompt": "编写自测脚本 - test_symphony.py，验证所有模块可用性。"},
]

def main():
    print("=" * 70)
    print("🎼 交响独立运行系统 - 配置 + 文档 + 导图")
    print("=" * 70)
    
    manager = SubAgentManager()
    results = manager.execute_parallel(TASKS)
    
    print("\n📊 结果")
    success = sum(1 for r in results if r["result"].get("success"))
    tokens = sum(r["result"].get("total_tokens", 0) for r in results)
    
    for r in results:
        status = "✅" if r["result"].get("success") else "❌"
        print(f"{status} {r['expert']} - {r['model']}")
    
    print(f"\n📈 成功: {success}/{len(TASKS)} | Token: {tokens}")
    
    return success, tokens

if __name__ == "__main__":
    main()
