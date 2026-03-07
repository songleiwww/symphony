"""
Symphony Memory Coordinator - 记忆协调器
实现Symphony与OpenClaw的记忆同步
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional

class MemoryCoordinator:
    """记忆协调器"""
    
    def __init__(self, workspace: str):
        self.workspace = workspace
        self.openclaw_memory = os.path.join(workspace, "MEMORY.md")
        self.symphony_memory = os.path.join(workspace, "memory")
        self.sync_status = "idle"
        self.last_sync = None
    
    def read_openclaw_memory(self) -> str:
        """读取OpenClaw主记忆"""
        try:
            if os.path.exists(self.openclaw_memory):
                with open(self.openclaw_memory, "r", encoding="utf-8") as f:
                    return f.read()
        except Exception as e:
            return f"Error: {e}"
        return ""
    
    def read_symphony_memory(self) -> List[Dict]:
        """读取Symphony记忆"""
        memories = []
        try:
            if os.path.exists(self.symphony_memory):
                for filename in os.listdir(self.symphony_memory):
                    if filename.endswith(".md"):
                        filepath = os.path.join(self.symphony_memory, filename)
                        with open(filepath, "r", encoding="utf-8") as f:
                            memories.append({
                                "file": filename,
                                "content": f.read()
                            })
        except Exception as e:
            print(f"Error: {e}")
        return memories
    
    def sync_to_openclaw(self, symphony_data: Dict) -> bool:
        """同步Symphony数据到OpenClaw"""
        try:
            # 读取现有MEMORY.md
            content = self.read_openclaw_memory()
            
            # 添加Symphony同步区块
            sync_block = f"""

## Symphony同步 - {datetime.now().strftime("%Y-%m-%d %H:%M")}
{symphony_data.get("summary", "")}
"""
            
            # 写入
            with open(self.openclaw_memory, "a", encoding="utf-8") as f:
                f.write(sync_block)
            
            self.last_sync = datetime.now()
            self.sync_status = "synced"
            return True
        except Exception as e:
            self.sync_status = f"error: {e}"
            return False
    
    def sync_from_openclaw(self) -> str:
        """从OpenClaw同步到Symphony"""
        content = self.read_openclaw_memory()
        # 可以提取关键信息传递给Symphony
        return content
    
    def get_coordination_status(self) -> Dict:
        """获取协调状态"""
        return {
            "status": self.sync_status,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "openclaw_memory_exists": os.path.exists(self.openclaw_memory),
            "symphony_memory_exists": os.path.exists(self.symphony_memory)
        }


def create_coordinator(workspace: str) -> MemoryCoordinator:
    """创建协调器实例"""
    return MemoryCoordinator(workspace)


# 使用示例
if __name__ == "__main__":
    workspace = r"C:\Users\Administrator\.openclaw\workspace"
    coordinator = create_coordinator(workspace)
    
    print("记忆协调器初始化完成")
    print("状态:", coordinator.get_coordination_status())
