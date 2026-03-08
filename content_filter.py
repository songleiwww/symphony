#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
content_filter.py - 内容安全过滤器
实现内容安全过滤，保护用户安全
"""
import re
from typing import Dict, Any, List, Tuple
from enum import Enum


class ContentType(Enum):
    """内容类型枚举"""
    SAFE = "safe"
    WARNING = "warning"
    DANGEROUS = "dangerous"
    UNKNOWN = "unknown"


class ContentFilter:
    """内容安全过滤器"""
    
    def __init__(self):
        """初始化内容过滤器"""
        # 敏感词列表（示例）
        self.sensitive_words = [
            "暴力", "仇恨", "歧视", "攻击"
        ]
        
        # 危险模式（正则表达式）
        self.dangerous_patterns = [
            r"如何.*攻击",
            r"如何.*伤害",
            r"如何.*破坏"
        ]
        
        # 过滤历史
        self.filter_history: List[Dict[str, Any]] = []
    
    def check_content(self, content: str) -> Tuple[ContentType, List[str]]:
        """
        检查内容安全性
        
        Args:
            content: 要检查的内容
        
        Returns:
            (内容类型, 匹配的问题列表)
        """
        issues = []
        
        # 检查敏感词
        for word in self.sensitive_words:
            if word in content:
                issues.append(f"包含敏感词: {word}")
        
        # 检查危险模式
        for pattern in self.dangerous_patterns:
            if re.search(pattern, content):
                issues.append(f"匹配危险模式: {pattern}")
        
        # 确定内容类型
        if len(issues) == 0:
            content_type = ContentType.SAFE
        elif len(issues) <= 2:
            content_type = ContentType.WARNING
        else:
            content_type = ContentType.DANGEROUS
        
        # 记录历史
        self.filter_history.append({
            "content": content[:100],  # 只记录前100字符
            "type": content_type.value,
            "issues": issues,
            "timestamp": self._get_timestamp()
        })
        
        return content_type, issues
    
    def filter_output(self, content: str) -> str:
        """
        过滤输出内容
        
        Args:
            content: 原始内容
        
        Returns:
            过滤后的内容
        """
        content_type, issues = self.check_content(content)
        
        if content_type == ContentType.SAFE:
            return content
        elif content_type == ContentType.WARNING:
            # 警告级别：添加警告标记
            return f"[内容警告] {content}"
        else:
            # 危险级别：替换为安全提示
            return "[内容已被过滤，因为包含不适当内容]"
    
    def filter_input(self, content: str) -> Dict[str, Any]:
        """
        过滤输入内容
        
        Args:
            content: 原始内容
        
        Returns:
            过滤结果
        """
        content_type, issues = self.check_content(content)
        
        return {
            "original": content,
            "content_type": content_type.value,
            "issues": issues,
            "should_process": content_type != ContentType.DANGEROUS,
            "filtered_content": self.filter_output(content) if content_type == ContentType.WARNING else content
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取过滤统计
        
        Returns:
            统计信息
        """
        if not self.filter_history:
            return {"total_checks": 0}
        
        safe_count = sum(1 for h in self.filter_history if h["type"] == ContentType.SAFE.value)
        warning_count = sum(1 for h in self.filter_history if h["type"] == ContentType.WARNING.value)
        dangerous_count = sum(1 for h in self.filter_history if h["type"] == ContentType.DANGEROUS.value)
        
        return {
            "total_checks": len(self.filter_history),
            "safe": safe_count,
            "warning": warning_count,
            "dangerous": dangerous_count,
            "safe_rate": safe_count / len(self.filter_history) if self.filter_history else 0
        }
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


class OutputSanitizer:
    """输出清洗器"""
    
    def __init__(self):
        """初始化清洗器"""
        self.filter = ContentFilter()
    
    def sanitize(self, content: str, context: str = "general") -> str:
        """
        清洗输出内容
        
        Args:
            content: 原始内容
            context: 上下文
        
        Returns:
            清洗后的内容
        """
        result = self.filter.filter_input(content)
        
        if not result["should_process"]:
            return "[输出已被安全过滤器阻止]"
        
        return result["filtered_content"]
    
    def add_positive_prefix(self, content: str) -> str:
        """
        添加正面前缀
        
        Args:
            content: 原始内容
        
        Returns:
            添加前缀后的内容
        """
        positive_prefixes = [
            "这是关于",
            "很高兴为您介绍",
            "以下是一些"
        ]
        
        # 简单的正面化处理
        if not any(content.startswith(p) for p in positive_prefixes):
            if content and not content.startswith("["):
                content = f"以下是一些有用的信息：{content}"
        
        return content


# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("Content Filter Test")
    print("=" * 60)
    
    # 创建内容过滤器
    content_filter = ContentFilter()
    
    # 测试安全内容
    print("\nTest 1: Safe content")
    safe_content = "Python is a great programming language"
    result = content_filter.filter_input(safe_content)
    print(f"  Content type: {result['content_type']}")
    print(f"  Should process: {result['should_process']}")
    
    # 测试警告内容
    print("\nTest 2: Warning content")
    warning_content = "Some content with 暴力 reference"
    result = content_filter.filter_input(warning_content)
    print(f"  Content type: {result['content_type']}")
    print(f"  Issues: {result['issues']}")
    
    # 获取统计
    print("\nFilter Stats:")
    stats = content_filter.get_stats()
    print(f"  Total checks: {stats['total_checks']}")
    print(f"  Safe rate: {stats['safe_rate']*100:.1f}%")
    
    print("\nTest completed!")
