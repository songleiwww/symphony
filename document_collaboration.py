"""
Symphony 文档协作系统
- 实时同步
- 版本控制
- 多用户协作
"""
import json
import time
from datetime import datetime
from typing import Dict, List, Optional


class DocumentCollaboration:
    """文档协作系统"""
    
    def __init__(self):
        self.documents = {}  # doc_id -> content
        self.versions = {}    # doc_id -> [versions]
        self.users = {}      # user_id -> activity
    
    def create_document(self, doc_id: str, content: str, user_id: str) -> dict:
        """创建文档"""
        self.documents[doc_id] = {
            "content": content,
            "created_at": datetime.now().isoformat(),
            "created_by": user_id,
            "version": 1
        }
        self.versions[doc_id] = [{
            "version": 1,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        }]
        return {"status": "created", "doc_id": doc_id, "version": 1}
    
    def update_document(self, doc_id: str, content: str, user_id: str) -> dict:
        """更新文档（自动版本控制）"""
        if doc_id not in self.documents:
            return {"status": "error", "message": "文档不存在"}
        
        # 保存旧版本
        old = self.documents[doc_id]
        old_version = old.get("version", 1)
        
        # 创建新版本
        new_version = old_version + 1
        self.documents[doc_id] = {
            "content": content,
            "updated_at": datetime.now().isoformat(),
            "updated_by": user_id,
            "version": new_version
        }
        
        # 记录版本历史
        self.versions[doc_id].append({
            "version": new_version,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        })
        
        return {"status": "updated", "doc_id": doc_id, "version": new_version}
    
    def get_document(self, doc_id: str) -> Optional[dict]:
        """获取文档"""
        return self.documents.get(doc_id)
    
    def get_version_history(self, doc_id: str) -> List[dict]:
        """获取版本历史"""
        return self.versions.get(doc_id, [])
    
    def rollback(self, doc_id: str, version: int, user_id: str) -> dict:
        """回滚到指定版本"""
        versions = self.versions.get(doc_id, [])
        target = next((v for v in versions if v["version"] == version), None)
        
        if not target:
            return {"status": "error", "message": "版本不存在"}
        
        return self.update_document(doc_id, target["content"], user_id)


# 全局实例
doc_collab = DocumentCollaboration()
