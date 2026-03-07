"""
Symphony Enhanced Error Handler - 增强错误处理
"""
import traceback
import logging
from datetime import datetime
from typing import Dict, Any, Optional


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self):
        self.error_log = []
        self.error_counts = {}
        self.error_handlers = {
            "429": self.handle_rate_limit,
            "400": self.handle_bad_request,
            "401": self.handle_auth_error,
            "403": self.handle_forbidden,
            "500": self.handle_server_error,
            "timeout": self.handle_timeout,
            "connection": self.handle_connection_error
        }
    
    def handle_error(self, error: Exception, context: Dict = None) -> Dict:
        """处理错误"""
        error_type = type(error).__name__
        error_msg = str(error)
        
        # 记录错误
        error_info = {
            "type": error_type,
            "message": error_msg,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
            "traceback": traceback.format_exc()
        }
        
        self.error_log.append(error_info)
        
        # 统计计数
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
        
        # 获取处理建议
        suggestion = self.get_suggestion(error_type, error_msg)
        
        return {
            "error": error_info,
            "suggestion": suggestion,
            "recoverable": self.is_recoverable(error_type)
        }
    
    def handle_rate_limit(self, error: Exception) -> str:
        return "触发限流，建议等待30秒后重试或切换备用模型"
    
    def handle_bad_request(self, error: Exception) -> str:
        return "请求参数错误，检查请求格式和参数"
    
    def handle_auth_error(self, error: Exception) -> str:
        return "认证失败，检查API Key是否有效"
    
    def handle_forbidden(self, error: Exception) -> str:
        return "权限不足，检查API权限配置"
    
    def handle_server_error(self, error: Exception) -> str:
        return "服务器错误，建议稍后重试"
    
    def handle_timeout(self, error: Exception) -> str:
        return "请求超时，增加超时时间或检查网络"
    
    def handle_connection_error(self, error: Exception) -> str:
        return "连接错误，检查网络连接"
    
    def get_suggestion(self, error_type: str, error_msg: str) -> str:
        """获取处理建议"""
        msg_lower = error_msg.lower()
        
        if "429" in msg_lower or "rate" in msg_lower:
            return self.handle_rate_limit(Exception())
        if "timeout" in msg_lower:
            return self.handle_timeout(Exception())
        if "connection" in msg_lower:
            return self.handle_connection_error(Exception())
        
        return "请检查错误信息并重试"
    
    def is_recoverable(self, error_type: str) -> bool:
        """判断是否可恢复"""
        recoverable = ["timeout", "connection", "429", "500", "502", "503"]
        return any(r in error_type.lower() for r in recoverable)
    
    def get_error_summary(self) -> Dict:
        """获取错误摘要"""
        return {
            "total_errors": len(self.error_log),
            "error_counts": self.error_counts,
            "recent_errors": self.error_log[-5:]
        }


# 全局实例
error_handler = ErrorHandler()
