#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
顺序调度 - 给两个模型安排工作
Sequential Scheduling - Assign Work to Two Models
"""

import sys
from datetime import datetime


# =============================================================================
# 修复Windows编码
# =============================================================================

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# =============================================================================
# 两个模型配置
# =============================================================================

TWO_MODELS = [
    {
        "model_id": "cherry-minimax/MiniMax-M2.5",
        "alias": "MiniMax-M2.5",
        "provider": "cherry-minimax",
        "role": "第一阶段：需求分析",
        "emoji": "🔍"
    },
    {
        "model_id": "cherry-doubao/ark-code-latest",
        "alias": "Doubao-Ark",
        "provider": "cherry-doubao",
        "role": "第二阶段：代码实现",
        "emoji": "💻"
    }
]


# =============================================================================
# 工作任务
# =============================================================================

WORK_TASKS = [
    {
        "phase": 1,
        "model": "MiniMax-M2.5",
        "role": "需求分析师",
        "title": "需求分析",
        "description": "分析任务队列系统的需求",
        "tasks": [
            "收集用户需求",
            "分析系统用例",
            "设计数据结构",
            "确定接口规范"
        ],
        "output": """
## 需求分析报告

### 1. 用户需求
- 异步任务处理
- 优先级支持
- 任务状态跟踪
- 重试机制

### 2. 系统用例
- 提交任务
- 查询状态
- 取消任务
- 重试失败任务

### 3. 数据结构
- Task: 任务单元
- TaskQueue: 队列管理
- Worker: 工作线程

### 4. 接口规范
- submit(task) -> task_id
- get_status(task_id) -> status
- cancel(task_id) -> bool
        """
    },
    {
        "phase": 2,
        "model": "Doubao-Ark",
        "role": "开发者",
        "title": "代码实现",
        "description": "基于需求分析实现代码",
        "tasks": [
            "实现Task类",
            "实现TaskQueue类",
            "实现Worker池",
            "添加单元测试"
        ],
        "output": """
## 代码实现

### Task类
```python
class Task:
    def __init__(self, name, func, priority=1):
        self.name = name
        self.func = func
        self.priority = priority
        self.status = "pending"
```

### TaskQueue类
```python
class TaskQueue:
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.tasks = {}
    
    async def submit(self, task):
        task_id = generate_id()
        self.tasks[task_id] = task
        return task_id
```

### Worker池
```python
class WorkerPool:
    def __init__(self, size):
        self.workers = [Worker() for _ in range(size)]
```
        """
    }
]


# =============================================================================
# 顺序调度执行
# =============================================================================

def sequential_scheduling():
    """顺序调度执行"""
    
    print("=" * 80)
    print("🎯 顺序调度 - 给两个模型安排工作")
    print("=" * 80)
    
    print(f"\n📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👥 模型数: {len(TWO_MODELS)}")
    print(f"📋 任务阶段: {len(WORK_TASKS)}")
    
    # 显示模型
    print("\n" + "=" * 80)
    print("📋 参与模型")
    print("=" * 80)
    
    for model in TWO_MODELS:
        print(f"\n{model['emoji']} {model['alias']}")
        print(f"   提供商: {model['provider']}")
        print(f"   角色: {model['role']}")
    
    # 依次执行工作
    print("\n" + "=" * 80)
    print("🔄 顺序执行工作")
    print("=" * 80)
    
    results = []
    
    for task in WORK_TASKS:
        print(f"\n{'='*60}")
        print(f"📍 第{task['phase']}阶段: {task['title']}")
        print(f"{'='*60}")
        
        print(f"\n🤖 执行模型: {task['model']}")
        print(f"📝 角色: {task['role']}")
        print(f"\n📄 任务描述: {task['description']}")
        
        print(f"\n📋 子任务:")
        for i, t in enumerate(task['tasks'], 1):
            print(f"   {i}. {t}")
        
        print(f"\n📤 输出内容:")
        print(task['output'][:300] + "...")
        
        # 模拟完成
        result = {
            "phase": task['phase'],
            "model": task['model'],
            "role": task['role'],
            "title": task['title'],
            "tasks": task['tasks'],
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        results.append(result)
        
        print(f"\n✅ {task['model']} 完成第{task['phase']}阶段！")
        
        # 模拟交接
        if task['phase'] < len(WORK_TASKS):
            print(f"\n🔄 交接给下一个模型: {WORK_TASKS[task['phase']]['model']}")
    
    # 总结
    print("\n" + "=" * 80)
    print("🏆 顺序调度完成")
    print("=" * 80)
    
    print(f"\n📊 执行统计:")
    print(f"   总阶段数: {len(results)}")
    print(f"   全部完成: {sum(1 for r in results if r['status'] == 'completed')}")
    
    print(f"\n📋 完成的工作:")
    for r in results:
        print(f"\n   第{r['phase']}阶段: {r['title']}")
        print(f"   执行模型: {r['model']}")
        print(f"   子任务数: {len(r['tasks'])}")
    
    print("\n" + "=" * 80)
    print("✅ 两个模型顺序协作完成！")
    print("=" * 80)
    
    print("""
💡 工作流程：
   1. MiniMax-M2.5 做需求分析
   2. Doubao-Ark 基于需求实现代码
   3. 形成完整的开发闭环

⚠️ 注意：这里是模拟演示
    """)


# =============================================================================
# 主程序
# =============================================================================

def main():
    sequential_scheduling()


if __name__ == "__main__":
    main()
