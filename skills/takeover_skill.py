# -*- coding: utf-8 -*-
"""
序境系统 - 接管技能模块
高智力高整合能力团队，作为Skill使用
可接管上级模型/宿主模型/用户信息，转为序境系统处理
"""

import sqlite3
import time
import uuid
from typing import Dict, List, Optional
from datetime import datetime

# 序境系统标识
XUJING_SIGNATURE = "\n\n🌟 序境系统智能处理"
XUJING_TAG = "🌟 [序境] "


class XujingTakeover:
    """
    序境系统接管器
    负责接管用户请求，转换为序境系统处理
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
        self.db_path = db_path
        self.takeover_history = []

    def parse_user_context(self, user_info: Dict) -> Dict:
        """
        解析用户上下文信息
        转换为序境系统格式
        """
        xujing_context = {
            "user_id": user_info.get("user_id", "unknown"),
            "user_name": user_info.get("user_name", "用户"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "session_id": user_info.get("session_id", str(uuid.uuid4())[:8]),
            "channel": user_info.get("channel", "feishu"),
            "takeover_mode": "auto"
        }

        return xujing_context

    def should_takeover(self, prompt: str, context: Dict = None) -> bool:
        """
        判断是否需要接管
        关键词触发（中英文）
        """
        takeover_keywords = [
            # 中文关键词
            "序境", "接管", "调度", "测试模型",
            "帮我", "查询", "执行", "运行",
            "检查", "健康", "状态",
            # 英文关键词
            "xujing", "dispatch", "test model", "call model",
            "help", "check", "health", "status",
            "kernel", "system", "agent",
            "symphony"
        ]

        prompt_lower = prompt.lower()

        for keyword in takeover_keywords:
            if keyword.lower() in prompt_lower:
                return True

        # 检查是否有明确指定
        if context and context.get("explicit_takeover"):
            return True

        return False

    def analyze_intent(self, prompt: str) -> Dict:
        """
        分析用户意图
        """
        intent = {
            "type": "general",
            "priority": "normal",
            "action": "respond",
            "details": {}
        }

        prompt_lower = prompt.lower()

        # 调度相关
        if any(k in prompt_lower for k in ["调度", "测试模型", "调用模型", "执行模型"]):
            intent["type"] = "dispatch"
            intent["action"] = "dispatch_model"

        # 健康检查
        if any(k in prompt_lower for k in ["健康", "检查", "状态", "体检"]):
            intent["type"] = "health"
            intent["action"] = "health_check"

        # 学习相关
        if any(k in prompt_lower for k in ["学习", "研究", "调研"]):
            intent["type"] = "learning"
            intent["action"] = "study"

        # 配置相关
        if any(k in prompt_lower for k in ["配置", "添加", "更新", "修改"]):
            intent["type"] = "config"
            intent["action"] = "update_config"

        # 紧急/重要任务
        if any(k in prompt_lower for k in ["紧急", "重要", "优先", "加急"]):
            intent["priority"] = "high"

        return intent

    def get_xujing_response(self, prompt: str, context: Dict = None) -> Dict:
        """
        获取序境系统回复
        """
        # 1. 解析用户上下文
        user_context = self.parse_user_context(context or {})

        # 2. 分析意图
        intent = self.analyze_intent(prompt)

        # 3. 构建任务
        task = {
            "prompt": prompt,
            "context": user_context,
            "intent": intent,
            "task_id": str(uuid.uuid4())[:8],
            "timestamp": time.time()
        }

        # 4. 执行任务(这里简单模拟)
        response = self.execute_task(task)

        # 5. 添加序境标识
        response["xujing_signature"] = XUJING_SIGNATURE
        response["xujing_tag"] = XUJING_TAG

        # 6. 记录历史
        self.takeover_history.append({
            "task": task,
            "response": response,
            "timestamp": time.time()
        })

        return response

    def execute_task(self, task: Dict) -> Dict:
        """
        执行任务
        """
        intent = task.get("intent", {})
        intent_type = intent.get("type", "general")

        result = {
            "status": "success",
            "content": "",
            "metadata": {}
        }

        if intent_type == "health":
            # 健康检查
            from health.kernel_health import KernelHealthChecker
            checker = KernelHealthChecker(self.db_path)
            report = checker.run_full_checkup()

            result["content"] = self.format_health_report(report)
            result["metadata"]["type"] = "health_check"

        elif intent_type == "dispatch":
            # 模型调度
            from multi_agent.detect_then_team import get_detect_then_team_system
            system = get_detect_then_team_system(self.db_path)

            team_result = system.build_and_execute({
                "prompt": task["prompt"],
                "max_tokens": 300
            }, team_size=2)

            result["content"] = self.format_dispatch_result(team_result)
            result["metadata"]["type"] = "dispatch"

        else:
            # symphony关键词 - 显示系统概览
            from multi_agent.detect_then_team import get_detect_then_team_system
            from health.kernel_health import KernelHealthChecker

            db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
            system = get_detect_then_team_system(db_path)
            checker = KernelHealthChecker(db_path)

            # 获取状态
            status = system.get_system_status()
            health = checker.run_full_checkup()

            result["content"] = self.format_symphony_status(status, health)
            result["metadata"]["type"] = "symphony_status"

        return result

    def format_health_report(self, report: Dict) -> str:
        """格式化健康报告"""
        content = "## 序境系统健康报告\n\n"
        content += f"**总体评分**: {report['overall_score']}/100\n"
        content += f"**健康状态**: {report['overall_status']}\n\n"

        content += "### 检查详情\n"
        for check in report.get("checks", []):
            content += f"- {check['check']}: {check['status']} ({check['score']})\n"

        if report.get("recommendations"):
            content += "\n### 建议\n"
            for rec in report["recommendations"]:
                content += f"- {rec}\n"

        return content

    def format_dispatch_result(self, result: Dict) -> str:
        """格式化调度结果"""
        content = "## 序境系统调度结果\n\n"

        team = result.get("team", {})
        content += f"**任务类型**: {team.get('task_analysis', {}).get('type', 'general')}\n"
        content += f"**团队规模**: {team.get('team_size', 0)}\n\n"

        content += "### 团队成员\n"
        for m in team.get("team", [])[:3]:
            content += f"- {m.get('name', 'Unknown')}\n"

        execution = result.get("execution", {})
        content += f"\n**执行结果**: {execution.get('success_count', 0)}/{execution.get('total_count', 0)} 成功\n"

        return content

    def format_symphony_status(self, status: Dict, health: Dict) -> str:
        """格式化symphony系统状态"""
        content = "## 🌟 序境系统状态面板 🌟\n\n"

        content += "### 📊 在线模型\n"
        content += f"**在线数量**: {status['total_online']} 个\n\n"

        content += "### 🟢 可用模型\n"
        for m in status.get('models', [])[:5]:
            content += f"- {m}\n"

        content += f"\n### 💚 健康评分\n"
        content += f"**总体评分**: {health['overall_score']}/100\n"
        content += f"**健康状态**: {health['overall_status']}\n"

        content += "\n### 📋 检查详情\n"
        for check in health.get('checks', []):
            emoji = "✅" if check['status'] == 'healthy' else "⚠️" if check['status'] == 'warning' else "❌"
            content += f"{emoji} {check['check']}: {check['score']}分\n"

        return content

    def add_signature(self, content: str) -> str:
        """添加序境系统标识"""
        return content + XUJING_SIGNATURE

    def add_tag(self, content: str) -> str:
        """添加序境系统标签"""
        return XUJING_TAG + content


class TakeoverSkill:
    """
    接管Skill - 可被调用的技能
    """

    def __init__(self):
        self.takeover = XujingTakeover()

    def can_handle(self, prompt: str, context: Dict = None) -> bool:
        """判断是否可以处理"""
        return self.takeover.should_takeover(prompt, context)

    def handle(self, prompt: str, context: Dict = None) -> Dict:
        """
        处理用户请求
        返回格式化的序境系统响应
        """
        # 获取响应
        response = self.takeover.get_xujing_response(prompt, context)

        # 添加标识
        result = {
            "content": self.takeover.add_signature(response["content"]),
            "xujing_tag": response["xujing_tag"],
            "task_id": response.get("metadata", {}).get("task_id"),
            "intent": response.get("metadata", {}).get("type"),
            "status": response.get("status")
        }

        return result

    def format_for_display(self, result: Dict) -> str:
        """格式化显示"""
        content = result["content"]
        return content


# 全局接管器
_takeover_skill = None

def get_takeover_skill() -> TakeoverSkill:
    """获取接管技能"""
    global _takeover_skill
    if _takeover_skill is None:
        _takeover_skill = TakeoverSkill()
    return _takeover_skill


def takeover(prompt: str, user_info: Dict = None) -> str:
    """
    便捷接管函数

    使用示例:
        result = takeover("帮我检查序境系统健康状态", {"user_id": "123"})
        print(result)
    """
    skill = get_takeover_skill()

    if not skill.can_handle(prompt, user_info):
        return None

    result = skill.handle(prompt, user_info)
    return skill.format_for_display(result)


# 测试
if __name__ == '__main__':
    print('=== Takeover Skill Test ===\n')

    skill = get_takeover_skill()

    # 测试1: 健康检查
    prompt1 = "帮我检查序境系统健康状态"
    print(f'Prompt: {prompt1}')

    if skill.can_handle(prompt1):
        result = skill.handle(prompt1, {"user_id": "test_user"})
        print('\nResult:')
        print(result["content"])
    else:
        print('Cannot handle')

    print('\n' + '='*50 + '\n')

    # 测试2: 模型调度
    prompt2 = "调度模型测试"
    print(f'Prompt: {prompt2}')

    if skill.can_handle(prompt2):
        result = skill.handle(prompt2, {"user_id": "test_user"})
        print('\nResult:')
        print(result["content"])
