#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修改后验证工具 - 防线2
任何修改完成后必须执行，验证不通过必须回滚
"""
import os
import sys
import importlib

# 配置
SYMPHONY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SYMPHONY_ROOT)

def check_imports():
    """检查所有核心模块导入是否正常"""
    errors = []
    modules_to_check = [
        "Kernel.intelligent_strategy_scheduler",
        "Kernel.model_federation",
        "Kernel.swarm_hybrid_algorithms",
        "main"
    ]
    for module_name in modules_to_check:
        try:
            importlib.import_module(module_name)
        except Exception as e:
            errors.append(f"模块 {module_name} 导入失败: {str(e)}")
    return errors

def check_scheduler_function():
    """检查调度功能是否正常"""
    errors = []
    try:
        from Kernel.intelligent_strategy_scheduler import IntelligentStrategyScheduler, TaskInfo, TaskComplexity
        scheduler = IntelligentStrategyScheduler()
        task = TaskInfo.create(
            id='test_post_check',
            prompt='验证修改后功能',
            task_type='query',
            complexity=TaskComplexity.MEDIUM
        )
        result = scheduler.schedule(task)
        if len(result.selected_models) != 2:
            errors.append(f"调度功能异常：返回{len(result.selected_models)}个模型，预期2个")
    except Exception as e:
        errors.append(f"调度功能失败: {str(e)}")
    return errors

def check_db_integrity():
    """检查数据库完整性"""
    errors = []
    try:
        import sqlite3
        db_path = os.path.join(SYMPHONY_ROOT, 'data', 'symphony.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='model_config'")
        if not cursor.fetchone():
            errors.append("数据库缺失model_config表")
        else:
            cursor.execute("SELECT COUNT(*) FROM model_config WHERE status='online'")
            count = cursor.fetchone()[0]
            if count < 100:
                errors.append(f"激活模型数量过少：{count}个，预期至少100个")
        conn.close()
    except Exception as e:
        errors.append(f"数据库检查失败: {str(e)}")
    return errors

def check_skill_interfaces():
    """检查Skill标准接口是否正常"""
    errors = []
    try:
        import main
        # 测试execute接口
        result = main.execute("测试")
        if result.get('status') != 'success':
            errors.append(f"execute接口异常: {result.get('message')}")
        # 测试refresh接口
        refresh_result = main.refresh()
        if refresh_result.get('status') != 'success':
            errors.append(f"refresh接口异常: {refresh_result.get('message')}")
    except Exception as e:
        errors.append(f"Skill接口检查失败: {str(e)}")
    return errors

def main():
    print("🔍 开始修改后验证（防线2）...")
    all_errors = []
    
    # 检查导入
    import_errors = check_imports()
    all_errors.extend(import_errors)
    
    # 检查调度功能
    sch_errors = check_scheduler_function()
    all_errors.extend(sch_errors)
    
    # 检查数据库
    db_errors = check_db_integrity()
    all_errors.extend(db_errors)
    
    # 检查Skill接口
    skill_errors = check_skill_interfaces()
    all_errors.extend(skill_errors)
    
    if all_errors:
        print("❌ 验证不通过，请回滚修改：")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("✅ 验证通过，修改有效")
        sys.exit(0)

if __name__ == "__main__":
    main()
