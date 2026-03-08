#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试模块 - 核心功能测试"""
import pytest
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestConfig:
    """测试配置模块"""
    
    def test_model_chain_exists(self):
        """测试模型链配置存在"""
        from config import MODEL_CHAIN
        assert MODEL_CHAIN is not None
        assert len(MODEL_CHAIN) > 0
    
    def test_model_count(self):
        """测试模型数量"""
        from config import MODEL_STATS
        assert MODEL_STATS["total_models"] >= 17
    
    def test_persona_config(self):
        """测试人设配置"""
        from config import SYMPHONY_CONFIG
        assert "persona" in SYMPHONY_CONFIG
        assert SYMPHONY_CONFIG["persona"]["name"] == "交交"
        assert SYMPHONY_CONFIG["persona"]["nickname"] == "娇娇"


class TestRetryManager:
    """测试重试管理器"""
    
    def test_import(self):
        """测试模块导入"""
        from retry_manager import RetryManager
        manager = RetryManager()
        assert manager is not None
    
    def test_default_config(self):
        """测试默认配置"""
        from retry_manager import RetryManager
        manager = RetryManager()
        assert manager.max_retries > 0
        assert manager.base_delay > 0


class TestTimeoutOptimizer:
    """测试超时优化器"""
    
    def test_import(self):
        """测试模块导入"""
        from timeout_optimizer import TimeoutOptimizer
        optimizer = TimeoutOptimizer()
        assert optimizer is not None
    
    def test_initial_timeout(self):
        """测试初始超时值"""
        from timeout_optimizer import TimeoutOptimizer
        optimizer = TimeoutOptimizer()
        assert optimizer.initial_timeout > 0


class TestHealthChecker:
    """测试健康检查器"""
    
    def test_import(self):
        """测试模块导入"""
        from health_checker import HealthChecker
        checker = HealthChecker()
        assert checker is not None
    
    def test_health_status(self):
        """测试健康状态"""
        from health_checker import HealthChecker
        checker = HealthChecker()
        status = checker.get_health_status()
        assert "status" in status


class TestContentFilter:
    """测试内容过滤器"""
    
    def test_import(self):
        """测试模块导入"""
        from content_filter import ContentFilter
        filter_obj = ContentFilter()
        assert filter_obj is not None
    
    def test_safe_content(self):
        """测试安全内容"""
        from content_filter import ContentFilter, ContentType
        filter_obj = ContentFilter()
        result = filter_obj.check("Hello, world!")
        assert result == ContentType.SAFE


class TestMemorySystem:
    """测试记忆系统"""
    
    def test_import(self):
        """测试模块导入"""
        from memory_layers import MemorySystem
        memory = MemorySystem()
        assert memory is not None
    
    def test_short_term_memory(self):
        """测试短期记忆"""
        from memory_layers import MemorySystem
        memory = MemorySystem()
        memory.add_conversation("test message", "user")
        recent = memory.short_term.get_recent(1)
        assert len(recent) > 0


class TestRAGRetriever:
    """测试RAG检索器"""
    
    def test_import(self):
        """测试模块导入"""
        from rag_retriever import RAGRetriever
        rag = RAGRetriever()
        assert rag is not None
    
    def test_add_document(self):
        """测试添加文档"""
        from rag_retriever import RAGRetriever
        rag = RAGRetriever()
        doc_id = rag.add_document("test content")
        assert doc_id is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
