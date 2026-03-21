# -*- coding: utf-8 -*-
"""
序境系统 - 定时学习任务配置
无需用户确认，自动执行
"""

# 定时任务配置
TASKS = [
    {
        "name": "自动学习AI知识",
        "script": "auto_learn.py",
        "interval_hours": 2,  # 每2小时学习一次
        "enabled": True,
        "description": "抓取AI资讯+模型研究，无需用户确认"
    },
    {
        "name": "健康检测",
        "script": "health_check.py", 
        "interval_hours": 4,  # 每4小时检测一次
        "enabled": True,
        "description": "检测模型在线状态"
    },
    {
        "name": "记忆整理",
        "script": "memory_loader.py",
        "interval_hours": 1,  # 每小时整理记忆
        "enabled": True,
        "description": "整理当天记忆到长期记忆"
    }
]

# Windows定时任务示例
WINDOWS_CRON = """
# 每2小时自动学习（Windows计划任务）
schtasks /create /tn "序境自动学习" /tr "python C:\\Users\\Administrator\\.openclaw\\workspace\\skills\\symphony\\auto_learn.py" /sc hourly /mo 2

# 每4小时健康检测
schtasks /create /tn "序境健康检测" /tr "python C:\\Users\\Administrator\\.openclaw\\workspace\\skills\\symphony\\health_check.py" /sc hourly /mo 4
"""

# Linux/Mac定时任务示例
LINUX_CRON = """
# 每2小时自动学习
0 */2 * * * python /Users/Administrator/.openclaw/workspace/skills/symphony/auto_learn.py

# 每4小时健康检测
0 */4 * * * python /Users/Administrator/.openclaw/workspace/skills/symphony/health_check.py
"""

def setup_cron():
    """设置定时任务"""
    import os
    import subprocess
    
    task_name = "XujingAutoLearn"
    script_path = os.path.abspath("auto_learn.py")
    
    # Windows计划任务
    cmd = f'schtasks /create /tn "{task_name}" /tr "python {script_path}" /sc hourly /mo 2 /f'
    
    print("="*50)
    print("【定时任务配置】")
    print("="*50)
    print(f"任务: {task_name}")
    print(f"脚本: {script_path}")
    print(f"频率: 每2小时")
    print("\nWindows命令:")
    print(cmd)
    print("\n如需立即生效，请手动执行:")
    print(f"python {script_path}")
    
    return cmd

if __name__ == "__main__":
    setup_cron()
