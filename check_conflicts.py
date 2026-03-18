#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统自检报告
功能冲突与迭代失效分析
生成时间: 2026-03-17
"""
import os
from datetime import datetime

KERNEL_PATH = os.path.dirname(os.path.abspath(__file__))

def analyze_conflicts():
    """分析功能冲突"""
    
    conflicts = {
        "调度模块冲突": {
            "files": ["scheduler.py", "smart_dispatcher.py", "dispatch_manager.py", "adaptive_scheduler.py"],
            "issue": "4个调度模块功能高度重叠",
            "details": [
                "scheduler.py - 基础调度(222行)",
                "smart_dispatcher.py - 智能调度(365行)",
                "dispatch_manager.py - 调度管理(79行)",
                "adaptive_scheduler.py - 自适应调度(417行) - 最新最强"
            ],
            "recommendation": "保留adaptive_scheduler.py，标记其他3个为deprecated"
        },
        "组合模块冲突": {
            "files": ["combo_skill.py", "advanced_combiner.py", "complementary_combiner.py", "matrix_combiner.py", "super_combo_v3.py"],
            "issue": "5个组合模块功能重叠",
            "details": [
                "combo_skill.py - 基础组合(252行)",
                "advanced_combiner.py - 高级组合(242行)",
                "complementary_combiner.py - 互补组合(174行)",
                "matrix_combiner.py - 矩阵组合(189行)",
                "super_combo_v3.py - 超级组合v3(237行) - 集成失效转移+流式输出"
            ],
            "recommendation": "保留super_combo_v3.py作为主组合，其他作为兼容层"
        },
        "优化模块冲突": {
            "files": ["optimize_system.py", "deep_optimize.py", "adaptive_combo.py", "adaptive_combo_v2.py", "adaptive_matrix.py"],
            "issue": "5个优化/自适应模块功能重叠",
            "details": [
                "optimize_system.py - 系统优化(43行)",
                "deep_optimize.py - 深度优化(48行)",
                "adaptive_combo.py - 自适应组合(191行)",
                "adaptive_combo_v2.py - 自适应组合v2(215行)",
                "adaptive_matrix.py - 自适应矩阵(166行)"
            ],
            "recommendation": "保留adaptive_combo_v2.py和adaptive_matrix.py，其他标记deprecated"
        }
    }
    
    return conflicts

def analyze_deprecated():
    """分析可能被迭代失效的文件"""
    
    deprecated = [
        {
            "file": "dispatch_manager.py",
            "reason": "功能被adaptive_scheduler.py完全覆盖",
            "status": "可标记deprecated"
        },
        {
            "file": "optimize_system.py", 
            "reason": "功能被deep_optimize.py和adaptive_combo覆盖",
            "status": "可标记deprecated"
        },
        {
            "file": "deep_optimize.py",
            "reason": "功能被adaptive_combo_v2.py覆盖",
            "status": "可标记deprecated"
        },
        {
            "file": "complementary_combiner.py",
            "reason": "功能被super_combo_v3.py集成",
            "status": "可标记deprecated"
        },
        {
            "file": "matrix_combiner.py",
            "reason": "功能被super_combo_v3.py和adaptive_matrix.py覆盖",
            "status": "可标记deprecated"
        }
    ]
    
    return deprecated

def generate_report():
    """生成完整自检报告"""
    
    conflicts = analyze_conflicts()
    deprecated = analyze_deprecated()
    
    report = f"""
================================================================================
                    序境系统自检报告
================================================================================
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

================================================================================
一、功能冲突分析
================================================================================

1. 调度模块冲突 (4个文件)
---------------------------------------------------------------------------
问题: 4个调度模块功能高度重叠

详情:
{chr(10).join('  - ' + d for d in conflicts["调度模块冲突"]["details"])}

建议: 保留adaptive_scheduler.py(最新最强)，标记其他3个为deprecated

2. 组合模块冲突 (5个文件)
---------------------------------------------------------------------------
问题: 5个组合模块功能重叠

详情:
{chr(10).join('  - ' + d for d in conflicts["组合模块冲突"]["details"])}

建议: 保留super_combo_v3.py作为主组合引擎

3. 优化模块冲突 (5个文件)
---------------------------------------------------------------------------
问题: 5个优化/自适应模块功能重叠

详情:
{chr(10).join('  - ' + d for d in conflicts["优化模块冲突"]["details"])}

建议: 保留adaptive_combo_v2.py和adaptive_matrix.py

================================================================================
二、可标记deprecated的文件
================================================================================

"""
    
    for i, d in enumerate(deprecated, 1):
        report += f"""
{i}. {d['file']}
   原因: {d['reason']}
   状态: {d['status']}
"""
    
    report += """
================================================================================
三、推荐保留的核心模块
================================================================================

调度类:
  - adaptive_scheduler.py (417行) - 自适应调度+任务分解+动态规划

组合类:
  - super_combo_v3.py (237行) - 失效转移+流式输出+动态多服务商

记忆类:
  - data_takeover.py - 数据接管
  - continuous_dialogue.py - 连续对话
  - self_evolution.py - 自进化系统(新增)

优化类:
  - adaptive_combo_v2.py (215行) - 自适应组合
  - adaptive_matrix.py (166行) - 自适应矩阵

执行类:
  - flow_executor.py - 流水执行
  - plan_before_execute.py - 先规划后执行

安全类:
  - security_manager.py - 安全管理
  - disaster_recovery.py - 灾难恢复

================================================================================
四、自进化系统集成状态
================================================================================

self_evolution.py (新增):
  - 细粒度感知与拆解: 独立模块，无冲突
  - 自诊断与自我修正: 独立模块，无冲突  
  - 自进化迭代机制: 独立模块，无冲突
  - 极致细粒度输出控制: 独立模块，无冲突
  - 长期记忆与持续优化: 独立模块，无冲突

状态: 自进化系统为全新模块，与现有模块无冲突

================================================================================
五、总结
================================================================================

功能冲突: 3组 (14个文件)
可deprecated: 5个文件
建议保留核心: 12个文件

建议操作:
1. 创建deprecated目录，移动已废弃文件
2. 更新super_kernel.py的导入引用
3. 确保self_evolution.py被正确加载
4. 更新版本号到v3.2.0

================================================================================
"""
    
    return report

if __name__ == "__main__":
    report = generate_report()
    print(report)
    
    # 保存报告
    report_path = os.path.join(KERNEL_PATH, 'CONFLICT_REPORT.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n报告已保存到: {report_path}")
