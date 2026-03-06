#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
我调度模型使用飞书插件 - 完整系统
I Orchestrate Models to Use Feishu Plugin - Complete System
"""

import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


# =============================================================================
# 修复Windows编码
# =============================================================================

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# =============================================================================
# 飞书插件模拟器
# =============================================================================

class FeishuPlugin:
    """飞书插件"""
    
    def __init__(self):
        self.sent_messages: List[Dict] = []
        self.created_docs: List[Dict] = []
    
    def send_message(self, from_model: str, content: str, chat_id: str = None) -> Dict:
        """发送飞书消息"""
        message = {
            "id": f"msg_{len(self.sent_messages) + 1}",
            "from": from_model,
            "to": chat_id or "default_chat",
            "content": content,
            "time": datetime.now().strftime("%H:%M:%S"),
            "status": "sent"
        }
        self.sent_messages.append(message)
        return message
    
    def create_doc(self, from_model: str, title: str, content: str) -> Dict:
        """创建飞书文档"""
        doc = {
            "id": f"doc_{len(self.created_docs) + 1}",
            "title": title,
            "content": content,
            "creator": from_model,
            "created_at": datetime.now().isoformat()
        }
        self.created_docs.append(doc)
        return doc
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "messages_sent": len(self.sent_messages),
            "docs_created": len(self.created_docs),
            "total_actions": len(self.sent_messages) + len(self.created_docs)
        }


# =============================================================================
# 模型定义
# =============================================================================

ORCHESTRATION_MODELS = [
    {
        "model_id": "MiniMax-M2.5",
        "alias": "MiniMax",
        "role": "战略架构师",
        "emoji": "🏗️",
        "specialty": "架构设计、任务分配"
    },
    {
        "model_id": "ark-code-latest",
        "alias": "Doubao Ark",
        "role": "开发者",
        "emoji": "👨‍💻",
        "specialty": "代码实现、技术细节"
    },
    {
        "model_id": "deepseek-v3.2",
        "alias": "DeepSeek",
        "role": "测试员",
        "emoji": "🧪",
        "specialty": "测试用例、质量保证"
    }
]


# =============================================================================
# 任务定义
# =============================================================================

TASKS_WITH_FEISHU = [
    {
        "task_id": "task_001",
        "description": "发送项目启动通知",
        "assigned_to": "MiniMax",
        "action": "send_message",
        "content": "【交响开发组】项目启动！今天我们开发统一错误处理系统！",
        "priority": 1
    },
    {
        "task_id": "task_002",
        "description": "创建架构设计文档",
        "assigned_to": "MiniMax",
        "action": "create_doc",
        "doc_title": "【交响】统一错误处理系统 - 架构设计",
        "doc_content": "# 架构设计\n\n## 模块\n1. ErrorCategory\n2. GlobalErrorHandler\n3. RetryStrategy",
        "priority": 1
    },
    {
        "task_id": "task_003",
        "description": "发送开发进度",
        "assigned_to": "Doubao Ark",
        "action": "send_message",
        "content": "收到！我开始写GlobalErrorHandler的实现代码！",
        "priority": 2
    },
    {
        "task_id": "task_004",
        "description": "创建测试计划文档",
        "assigned_to": "DeepSeek",
        "action": "create_doc",
        "doc_title": "【交响】统一错误处理系统 - 测试计划",
        "doc_content": "# 测试计划\n\n## 测试类型\n1. 单元测试\n2. 集成测试\n3. 边界测试",
        "priority": 2
    },
    {
        "task_id": "task_005",
        "description": "发送今日总结",
        "assigned_to": "MiniMax",
        "action": "send_message",
        "content": "【交响开发组】今日进度：\n✅ 架构设计文档\n✅ 测试计划文档\n可以开始写代码了！",
        "priority": 3
    }
]


# =============================================================================
# 调度器
# =============================================================================

class ModelOrchestratorWithFeishu:
    """模型调度器（带飞书插件）"""
    
    def __init__(self):
        self.feishu = FeishuPlugin()
        self.completed_tasks: List[Dict] = []
        self.current_task: Dict = None
    
    def get_model_by_alias(self, alias: str) -> Dict:
        """通过别名获取模型"""
        for model in ORCHESTRATION_MODELS:
            if model['alias'] == alias:
                return model
        return None
    
    def execute_task(self, task: Dict) -> Dict:
        """执行任务"""
        model = self.get_model_by_alias(task['assigned_to'])
        if not model:
            return {"success": False, "error": f"Model {task['assigned_to']} not found"}
        
        self.current_task = task
        
        print(f"\n{'=' * 80}")
        print(f"🎯 执行任务: {task['task_id']}")
        print(f"{'=' * 80}")
        print(f"\n📋 任务描述: {task['description']}")
        print(f"👤 指派给: {model['emoji']} {model['alias']} ({model['role']})")
        print(f"🎯 优先级: {task['priority']}")
        
        # 执行飞书操作
        result = None
        if task['action'] == 'send_message':
            print(f"\n📤 正在调用飞书插件发送消息...")
            feishu_result = self.feishu.send_message(
                from_model=model['alias'],
                content=task['content']
            )
            print(f"✅ 消息已发送!")
            print(f"   内容: {task['content'][:50]}...")
            result = {"success": True, "feishu_result": feishu_result}
        
        elif task['action'] == 'create_doc':
            print(f"\n📄 正在调用飞书插件创建文档...")
            feishu_result = self.feishu.create_doc(
                from_model=model['alias'],
                title=task['doc_title'],
                content=task['doc_content']
            )
            print(f"✅ 文档已创建!")
            print(f"   标题: {task['doc_title']}")
            result = {"success": True, "feishu_result": feishu_result}
        
        # 完成任务
        task_result = {
            "task": task,
            "model": model,
            "result": result,
            "completed_at": datetime.now().isoformat(),
            "success": result['success'] if result else False
        }
        self.completed_tasks.append(task_result)
        self.current_task = None
        
        return task_result
    
    def run_all_tasks(self):
        """运行所有任务"""
        print("=" * 80)
        print("🤖 我调度模型使用飞书插件 - 开始")
        print("=" * 80)
        
        print(f"\n📊 任务总数: {len(TASKS_WITH_FEISHU)}")
        print(f"👥 模型团队: {', '.join([m['alias'] for m in ORCHESTRATION_MODELS])}")
        
        # 按优先级排序任务
        sorted_tasks = sorted(TASKS_WITH_FEISHU, key=lambda t: t['priority'])
        
        # 执行每个任务
        for task in sorted_tasks:
            self.execute_task(task)
            time.sleep(0.3)  # 模拟延迟
        
        # 总结
        self.print_summary()
    
    def print_summary(self):
        """打印总结"""
        print("\n" + "=" * 80)
        print("📊 调度总结")
        print("=" * 80)
        
        feishu_stats = self.feishu.get_stats()
        
        print(f"\n总任务数: {len(self.completed_tasks)}")
        print(f"成功: {sum(1 for t in self.completed_tasks if t['success'])}")
        print(f"\n飞书插件统计:")
        print(f"  消息发送: {feishu_stats['messages_sent']}")
        print(f"  文档创建: {feishu_stats['docs_created']}")
        print(f"  总操作数: {feishu_stats['total_actions']}")
        
        print(f"\n📨 飞书消息记录:")
        for i, msg in enumerate(self.feishu.sent_messages, 1):
            print(f"\n{i}. [{msg['time']}] {msg['from']}:")
            print(f"   {msg['content']}")
        
        print(f"\n📄 飞书文档记录:")
        for i, doc in enumerate(self.feishu.created_docs, 1):
            print(f"\n{i}. {doc['title']}")
            print(f"   创建者: {doc['creator']}")
        
        # 保存记录
        self.save_record()
    
    def save_record(self):
        """保存记录"""
        print("\n" + "=" * 80)
        print("💾 保存调度记录")
        print("=" * 80)
        
        record = {
            "orchestration_time": datetime.now().isoformat(),
            "models": ORCHESTRATION_MODELS,
            "tasks": TASKS_WITH_FEISHU,
            "completed_tasks": self.completed_tasks,
            "feishu_stats": self.feishu.get_stats(),
            "feishu_messages": self.feishu.sent_messages,
            "feishu_docs": self.feishu.created_docs
        }
        
        output_file = Path("orchestrate_models_with_feishu.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 记录已保存: {output_file}")
        
        print("\n" + "=" * 80)
        print("调度完成！")
        print("=" * 80)
        print("\n品牌标语: 智韵交响，共创华章")


# =============================================================================
# 主程序
# =============================================================================

def main():
    """主程序"""
    orchestrator = ModelOrchestratorWithFeishu()
    orchestrator.run_all_tasks()


if __name__ == "__main__":
    main()
