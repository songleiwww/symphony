#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响共享记忆系统
与OpenClaw共享记忆
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# 共享记忆文件路径（与OpenClaw相同）
SHARED_MEMORY_PATH = r"C:\Users\Administrator\.openclaw\workspace\memory\shared_memory.json"


class SymphonySharedMemory:
    """
    交响共享记忆系统
    与OpenClaw共享记忆数据
    """
    
    def __init__(self, memory_path: str = None):
        """
        初始化共享记忆
        
        Args:
            memory_path: 记忆文件路径（可选，默认使用共享路径）
        """
        self.memory_path = Path(memory_path) if memory_path else Path(SHARED_MEMORY_PATH)
        self._ensure_directory()
        self.memories: List[Dict] = []
        self.conversation_history: List[Dict] = []
        self._load()
    
    def _ensure_directory(self):
        """确保目录存在"""
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load(self):
        """加载记忆"""
        if self.memory_path.exists():
            try:
                data = json.loads(self.memory_path.read_text(encoding='utf-8'))
                self.memories = data.get("memories", [])
                self.conversation_history = data.get("conversation_history", [])
            except:
                self.memories = []
                self.conversation_history = []
    
    def _save(self):
        """保存记忆"""
        data = {
            "version": "1.0",
            "updated_at": datetime.now().isoformat(),
            "memories": self.memories,
            "conversation_history": self.conversation_history
        }
        try:
            self.memory_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
        except Exception as e:
            print(f"保存记忆失败: {e}")
    
    def add_memory(self, content: str, memory_type: str = "important", tags: List[str] = None):
        """
        添加记忆
        
        Args:
            content: 记忆内容
            memory_type: 记忆类型 (important, user, system, task)
            tags: 标签列表
        """
        memory = {
            "id": f"mem_{len(self.memories)}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "content": content,
            "type": memory_type,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "source": "symphony"  # 标记来源
        }
        self.memories.append(memory)
        self._save()
    
    def add_conversation(self, role: str, content: str):
        """
        添加对话记录
        
        Args:
            role: 角色 (user, assistant)
            content: 对话内容
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "source": "symphony"
        }
        self.conversation_history.append(message)
        
        # 保持最近100条对话
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
        
        self._save()
    
    def get_memories(self, memory_type: str = None, limit: int = 10) -> List[Dict]:
        """
        获取记忆
        
        Args:
            memory_type: 过滤类型（可选）
            limit: 返回数量限制
            
        Returns:
            记忆列表
        """
        memories = self.memories
        
        if memory_type:
            memories = [m for m in memories if m.get("type") == memory_type]
        
        # 返回最近的
        return memories[-limit:]
    
    def get_context(self, max_history: int = 6) -> str:
        """
        获取上下文（用于系统提示）
        
        Args:
            max_history: 最近对话数量
            
        Returns:
            格式化的上下文字符串
        """
        context_parts = []
        
        # 添加重要记忆
        important = self.get_memories(memory_type="important", limit=5)
        if important:
            context_parts.append("【重要记忆】")
            for mem in important:
                context_parts.append(f"- {mem['content']}")
        
        # 添加最近对话
        recent = self.conversation_history[-max_history:]
        if recent:
            context_parts.append("\n【最近对话】")
            for msg in recent:
                role = "用户" if msg["role"] == "user" else "交交"
                content = msg["content"]
                # 截断太长的内容
                if len(content) > 100:
                    content = content[:100] + "..."
                context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def search(self, keyword: str) -> List[Dict]:
        """
        搜索记忆
        
        Args:
            keyword: 关键词
            
        Returns:
            匹配的记忆列表
        """
        results = []
        keyword_lower = keyword.lower()
        
        for mem in self.memories:
            if keyword_lower in mem.get("content", "").lower():
                results.append(mem)
        
        return results
    
    def clear(self, memory_type: str = None):
        """
        清除记忆
        
        Args:
            memory_type: 要清除的类型（None表示全部）
        """
        if memory_type:
            self.memories = [m for m in self.memories if m.get("type") != memory_type]
        else:
            self.memories = []
        
        self._save()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计字典
        """
        return {
            "total_memories": len(self.memories),
            "total_conversations": len(self.conversation_history),
            "memory_types": list(set(m.get("type", "") for m in self.memories)),
            "last_updated": self.memories[-1].get("created_at") if self.memories else None
        }


# =============================================================================
# 便捷函数
# =============================================================================

# 全局共享记忆实例
_shared_memory: Optional[SymphonySharedMemory] = None


def get_shared_memory() -> SymphonySharedMemory:
    """获取共享记忆实例"""
    global _shared_memory
    if _shared_memory is None:
        _shared_memory = SymphonySharedMemory()
    return _shared_memory


# =============================================================================
# 测试
# =============================================================================

if __name__ == "__main__":
    print("测试共享记忆系统")
    
    memory = SymphonySharedMemory()
    
    # 添加测试记忆
    memory.add_memory("这是测试记忆", "important", ["test"])
    memory.add_conversation("user", "你好")
    memory.add_conversation("assistant", "你好！我是交交")
    
    # 获取统计
    stats = memory.get_stats()
    print(f"\n统计: {stats}")
    
    # 获取上下文
    context = memory.get_context()
    print(f"\n上下文:\n{context}")
