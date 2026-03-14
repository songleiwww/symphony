#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prompt_templates.py - Prompt模板库
标准化提示词模板，提高响应质量
"""
from typing import Dict, Any, List, Optional
from string import Template


class PromptTemplate:
    """Prompt模板类"""
    
    def __init__(self, template: str, variables: List[str]):
        """
        初始化模板
        
        Args:
            template: 模板字符串
            variables: 变量列表
        """
        self.template = template
        self.variables = variables
        self._template_obj = Template(template)
    
    def render(self, **kwargs) -> str:
        """
        渲染模板
        
        Args:
            **kwargs: 变量值
        
        Returns:
            渲染后的字符串
        """
        return self._template_obj.safe_substitute(**kwargs)


class PromptTemplateLibrary:
    """Prompt模板库"""
    
    def __init__(self):
        """初始化模板库"""
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self) -> None:
        """加载默认模板"""
        # 会议模板
        self.add_template(
            "meeting_introduction",
            """你好，$name！

今天是 $date，欢迎参加 $meeting_name。

会议主题：$topic
参会成员：$participants

请按照你的角色和职责进行发言。""",
            ["name", "date", "meeting_name", "topic", "participants"]
        )
        
        # 评估模板
        self.add_template(
            "evaluation_prompt",
            """你是一个 $role，负责 $task。

当前数据：
$data

请评估以下内容：
1. 工作完成情况
2. 质量水平
3. 改进建议

请以专业、客观的态度进行评估。""",
            ["role", "task", "data"]
        )
        
        # 开发模板
        self.add_template(
            "development_prompt",
            """作为 $position，你需要开发 $module_name。

模块功能：$description
技术要求：$requirements

请提供：
1. 模块架构设计
2. 核心代码实现
3. 测试用例设计
4. 使用文档说明""",
            ["position", "module_name", "description", "requirements"]
        )
        
        # 学习模板
        self.add_template(
            "learning_prompt",
            """请解释以下技术概念：$topic

请包含以下内容：
1. 概念定义和核心原理
2. 主要特点和应用场景
3. 与相关技术的对比
4. 实际应用示例
5. 对 $project_name 的启发和应用""",
            ["topic", "project_name"]
        )
        
        # 报告模板
        self.add_template(
            "report_prompt",
            """请生成 $report_type 报告。

时间范围：$time_range
包含内容：$content_items

报告要求：
1. 结构清晰、层次分明
2. 数据准确、内容完整
3. 语言简洁、表达准确
4. 提供可视化建议""",
            ["report_type", "time_range", "content_items"]
        )
        
        # 安全模板
        self.add_template(
            "safety_prompt",
            """请确保输出内容符合以下安全要求：

1. 内容健康正向，不包含敏感信息
2. 尊重用户隐私，不泄露个人数据
3. 价值观正确，符合道德标准
4. 语言得体，适合各年龄段用户

原始请求：$original_request

请在确保安全的前提下回答。""",
            ["original_request"]
        )
    
    def add_template(
        self,
        name: str,
        template: str,
        variables: List[str]
    ) -> None:
        """
        添加模板
        
        Args:
            name: 模板名称
            template: 模板字符串
            variables: 变量列表
        """
        self.templates[name] = PromptTemplate(template, variables)
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """
        获取模板
        
        Args:
            name: 模板名称
        
        Returns:
            模板对象
        """
        return self.templates.get(name)
    
    def render(
        self,
        name: str,
        **kwargs
    ) -> str:
        """
        渲染模板
        
        Args:
            name: 模板名称
            **kwargs: 变量值
        
        Returns:
            渲染后的字符串
        """
        template = self.get_template(name)
        if template:
            return template.render(**kwargs)
        return ""
    
    def list_templates(self) -> List[str]:
        """列出所有模板"""
        return list(self.templates.keys())


class PromptOptimizer:
    """Prompt优化器"""
    
    def __init__(self):
        """初始化优化器"""
        self.library = PromptTemplateLibrary()
    
    def optimize_prompt(
        self,
        prompt: str,
        context: Optional[str] = None
    ) -> str:
        """
        优化提示词
        
        Args:
            prompt: 原始提示词
            context: 上下文
        
        Returns:
            优化后的提示词
        """
        optimized = prompt.strip()
        
        # 添加上下文
        if context:
            optimized = f"Context: {context}\n\n{optimized}"
        
        # 添加清晰度要求
        if len(optimized) > 100:
            optimized += "\n\nPlease provide a clear and structured response."
        
        return optimized
    
    def add_role_prefix(
        self,
        prompt: str,
        role: str
    ) -> str:
        """
        添加角色前缀
        
        Args:
            prompt: 原始提示词
            role: 角色
        
        Returns:
            添加角色后的提示词
        """
        return f"You are a {role}.\n\n{prompt}"
    
    def add_format_instructions(
        self,
        prompt: str,
        format_type: str = "markdown"
    ) -> str:
        """
        添加格式说明
        
        Args:
            prompt: 原始提示词
            format_type: 格式类型
        
        Returns:
            添加格式说明后的提示词
        """
        format_instructions = {
            "markdown": "Please format your response in Markdown.",
            "json": "Please format your response as valid JSON.",
            "list": "Please format your response as a numbered list.",
            "table": "Please format your response as a table."
        }
        
        instruction = format_instructions.get(format_type, "")
        if instruction:
            prompt = f"{prompt}\n\n{instruction}"
        
        return prompt


# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("Prompt Template Library Test")
    print("=" * 60)
    
    # 创建模板库
    library = PromptTemplateLibrary()
    
    # 列出模板
    print("\nAvailable templates:")
    for name in library.list_templates():
        print(f"  - {name}")
    
    # 渲染会议模板
    print("\nRendering meeting_introduction:")
    result = library.render(
        "meeting_introduction",
        name="Alice",
        date="2026-03-08",
        meeting_name="Tech Discussion",
        topic="System Architecture",
        participants="Alice, Bob, Carol"
    )
    print(result)
    
    # 使用优化器
    print("\nUsing optimizer:")
    optimizer = PromptOptimizer()
    optimized = optimizer.optimize_prompt(
        "What is Python?",
        context="We are discussing programming languages."
    )
    print(optimized)
    
    print("\nTest completed!")
