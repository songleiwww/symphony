#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统 - Agent+Skills 架构
Agent = 大脑(LLM调度) + Skills = 技能库
"""
import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Skill:
    """技能"""
    name: str
    category: str
    description: str
    keywords: List[str]
    enabled: bool = True

class SkillRegistry:
    """技能注册中心"""
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.categories: Dict[str, List[str]] = {}
    
    def register(self, skill: Skill):
        """注册技能"""
        self.skills[skill.name] = skill
        if skill.category not in self.categories:
            self.categories[skill.category] = []
        self.categories[skill.category].append(skill.name)
    
    def get_by_keyword(self, keyword: str) -> List[Skill]:
        """通过关键词获取技能"""
        results = []
        for skill in self.skills.values():
            if keyword.lower() in skill.name.lower():
                results.append(skill)
            elif any(keyword.lower() in k.lower() for k in skill.keywords):
                results.append(skill)
        return results
    
    def get_by_category(self, category: str) -> List[Skill]:
        """获取分类下所有技能"""
        names = self.categories.get(category, [])
        return [self.skills[n] for n in names]
    
    def list_categories(self) -> Dict[str, int]:
        """列出所有分类"""
        return {cat: len(names) for cat, names in self.categories.items()}

class AgentBrain:
    """Agent大脑 - 负责理解任务并调度技能"""
    
    def __init__(self, skill_registry: SkillRegistry):
        self.skill_registry = skill_registry
        self.task_history: List[Dict] = []
    
    def understand_task(self, user_input: str) -> Dict:
        """理解任务并规划"""
        # 简单关键词匹配
        keywords = user_input.lower()
        
        # 任务类型识别
        task_type = "general"
        if any(w in keywords for w in ["搜索", "找", "查"]):
            task_type = "search"
        elif any(w in keywords for w in ["写", "创建", "生成"]):
            task_type = "create"
        elif any(w in keywords for w in ["读", "看", "分析"]):
            task_type = "analyze"
        elif any(w in keywords for w in ["发送", "通知"]):
            task_type = "notify"
        
        # 技能匹配
        matched_skills = []
        for skill in self.skill_registry.skills.values():
            if not skill.enabled:
                continue
            if any(kw in keywords for kw in skill.keywords):
                matched_skills.append(skill.name)
        
        return {
            "task_type": task_type,
            "matched_skills": matched_skills,
            "timestamp": datetime.now().isoformat()
        }
    
    def dispatch(self, user_input: str) -> Dict:
        """调度技能"""
        plan = self.understand_task(user_input)
        
        # 记录任务
        self.task_history.append({
            "input": user_input,
            "plan": plan,
            "timestamp": plan["timestamp"]
        })
        
        return plan

# 初始化技能注册
def init_skill_registry() -> SkillRegistry:
    """初始化技能注册中心"""
    registry = SkillRegistry()
    
    # 基础技能
    skills = [
        # 搜索类
        Skill("web_search", "搜索", "网络搜索", ["搜索", "查找", "百度"]),
        Skill("multi_search", "搜索", "多引擎搜索", ["多引擎", "综合搜索"]),
        
        # 知识类
        Skill("memory", "记忆", "记忆系统", ["记住", "记忆", "存储"]),
        
        # 沟通类
        Skill("feishu_message", "沟通", "飞书消息", ["飞书", "发送消息"]),
        Skill("discord", "沟通", "Discord消息", ["Discord", "电报"]),
        Skill("slack", "沟通", "Slack消息", ["Slack", "工作消息"]),
        
        # 办公类
        Skill("calendar", "办公", "日历管理", ["日历", "日程", "会议"]),
        Skill("email", "办公", "邮件处理", ["邮件", "发邮件", "收件箱"]),
        Skill("notion", "办公", "Notion协作", ["Notion", "笔记", "文档"]),
        
        # 媒体类
        Skill("tts", "媒体", "语音合成", ["语音", "朗读", "说话"]),
        Skill("image_gen", "媒体", "图像生成", ["图片", "画", "图像"]),
        
        # 数据类
        Skill("sqlite", "数据", "SQLite数据库", ["数据库", "SQL", "查询"]),
        Skill("s3", "数据", "S3存储", ["存储", "文件", "S3"]),
        
        # 开发类
        Skill("github", "开发", "GitHub操作", ["GitHub", "代码", "仓库"]),
        Skill("jira", "开发", "Jira任务", ["Jira", "任务", "工单"]),
        
        # AI能力
        Skill("llm_call", "AI", "大模型调用", ["模型", "LLM", "调用"]),
        Skill("rag", "AI", "RAG知识检索", ["知识", "检索", "RAG"]),
    ]
    
    for skill in skills:
        registry.register(skill)
    
    return registry

# 测试
if __name__ == "__main__":
    # 初始化
    registry = init_skill_registry()
    agent = AgentBrain(registry)
    
    print("=== Agent+Skills 架构初始化 ===\n")
    
    # 显示分类
    print("📂 技能分类:")
    cats = registry.list_categories()
    for cat, count in cats.items():
        print(f"  {cat}: {count}个技能")
    
    print("\n📋 测试任务调度:")
    
    # 测试调度
    test_tasks = [
        "帮我搜索最新的AI新闻",
        "记住今天的重要事情",
        "发送飞书消息给同事",
        "调用大模型回答问题"
    ]
    
    for task in test_tasks:
        result = agent.dispatch(task)
        print(f"\n输入: {task}")
        print(f"类型: {result['task_type']}")
        print(f"技能: {result['matched_skills']}")
