# -*- coding: utf-8 -*-
"""
序境系统内核 - 对话接管器
将接管功能集成到对话处理流程
"""
import sys
import os

kernel_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, kernel_path)

# 导入接管模块
try:
    from skills.takeover_skill import (
        TakeoverSkill,
        get_takeover_skill,
        XujingTakeover
    )
    # 导入接管历史模块
    from takeover_history import add_takeover_record, get_recent_takeovers, get_today_count
    TAKEOVER_AVAILABLE = True
    print("[接管器] 接管模块已加载")
except ImportError as e:
    TAKEOVER_AVAILABLE = False
    print(f"[接管器] 接管模块加载失败: {e}")


# 接管器版本 (小版本迭代)
TAKEOVER_VERSION = "3.1.1"


class XujingDialogHandler:
    """
    序境对话处理器
    负责检测关键词并触发接管
    """
    
    def __init__(self):
        self.takeover_skill = None
        if TAKEOVER_AVAILABLE:
            self.takeover_skill = get_takeover_skill()
        self.takeover_count = 0
        self.total_handled = self._load_count()
    
    def _load_count(self) -> int:
        """从文件加载历史接管次数"""
        try:
            count_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'takeover_count.txt')
            if os.path.exists(count_file):
                with open(count_file, 'r', encoding='utf-8') as f:
                    return int(f.read().strip())
        except:
            pass
        return 0
    
    def _save_count(self):
        """保存接管次数到文件"""
        try:
            count_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'takeover_count.txt')
            os.makedirs(os.path.dirname(count_file), exist_ok=True)
            with open(count_file, 'w', encoding='utf-8') as f:
                f.write(str(self.total_handled))
        except:
            pass
    
    def should_intercept(self, user_message: str, context: dict = None) -> bool:
        """
        判断是否需要接管
        """
        if not TAKEOVER_AVAILABLE or not self.takeover_skill:
            return False
        
        return self.takeover_skill.can_handle(user_message, context)
    
    def handle_message(self, user_message: str, context: dict = None) -> dict:
        """
        处理消息 - 如果匹配关键词则接管
        返回格式:
        {
            "taken_over": True/False,
            "response": "接管后的回复内容",
            "intent": "意图类型"
        }
        """
        if not self.should_intercept(user_message, context):
            return {
                "taken_over": False,
                "response": None,
                "intent": None
            }
        
        # 执行接管
        self.takeover_count += 1
        self.total_handled += 1
        self._save_count()  # 保存次数
        
        result = self.takeover_skill.handle(user_message, context)
        
        # 记录接管历史
        try:
            add_takeover_record(
                user_message=user_message,
                intent=result.get("intent", "unknown"),
                status=result.get("status", "success"),
                response_length=len(result.get("content", ""))
            )
        except Exception as e:
            print(f"[接管器] 历史记录失败: {e}")
        
        return {
            "taken_over": True,
            "response": result.get("content", ""),
            "intent": result.get("intent", "unknown"),
            "task_id": result.get("task_id")
        }
    
    def add_takeover_signature(self, content: str) -> str:
        """
        为回复添加接管标识和尾标
        """
        from datetime import datetime
        
        if not content:
            return content
        
        # 尾标信息
        today_count = get_today_count() if TAKEOVER_AVAILABLE else 0
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        signature = f"""
---
🤖 **序境系统 v{TAKEOVER_VERSION} | 少府监**
📊 接管次数: {self.total_handled} 次 (本次会话: {self.takeover_count}次) 今日: {today_count}次
🔄 接管状态持续化:
  ✅ 关键词检测
  ✅ 自动累加计数
  ✅ 文件持久化
⏰ {timestamp} | 🏛️ 少府监·内务府
💡 如需人工服务，请输入"转人工"
"""
        return content + signature
    
    def get_status(self) -> dict:
        """
        获取接管状态
        """
        return {
            "available": TAKEOVER_AVAILABLE,
            "version": TAKEOVER_VERSION,
            "takeover_count": self.takeover_count,
            "total_handled": self.total_handled,
            "today_count": get_today_count() if TAKEOVER_AVAILABLE else 0,
            "recent_records": get_recent_takeovers(5) if TAKEOVER_AVAILABLE else [],
            "keywords": [
                "序境", "接管", "调度", "测试模型", "symphony", "xujing",
                "dispatch", "test model", "help", "check", "health", "status", 
                "kernel", "system", "agent",
                "令", "责令", "敕令", "交响", "调整", "调", "适配", "选调"
            ]
        }


# 全局对话处理器
_dialog_handler = None

def get_dialog_handler() -> XujingDialogHandler:
    """获取对话处理器"""
    global _dialog_handler
    if _dialog_handler is None:
        _dialog_handler = XujingDialogHandler()
    return _dialog_handler


def intercept_message(user_message: str, context: dict = None) -> dict:
    """
    便捷函数：拦截消息并判断是否需要接管
    
    使用示例:
        result = intercept_message("帮我检查系统健康状态", {"user_id": "123"})
        if result["taken_over"]:
            print(result["response"])
    """
    handler = get_dialog_handler()
    return handler.handle_message(user_message, context)


# 测试
if __name__ == '__main__':
    print("=== 序境对话接管器测试 ===\n")
    
    handler = get_dialog_handler()
    print(f"接管器状态: {handler.get_status()}\n")
    
    # 测试消息
    test_messages = [
        "帮我检查序境系统健康状态",
        "Symphony",
        "调度模型测试",
        "你好今天怎么样",  # 不应该接管
    ]
    
    for msg in test_messages:
        print(f"用户: {msg}")
        result = handler.handle_message(msg)
        if result["taken_over"]:
            print(f"  → 已接管 (意图: {result['intent']})")
            print(f"  内容: {result['response'][:100]}...")
        else:
            print(f"  → 未接管")
        print()
