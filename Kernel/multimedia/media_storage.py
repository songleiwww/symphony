# -*- coding: utf-8 -*-
"""
多媒体处理模块 - 媒体存储管理器

功能：
- 媒体文件上传
- 本地存储管理
- 文件类型检测
"""
import os
import uuid
import time
import hashlib
from typing import Optional, Dict, Any
from pathlib import Path
import sqlite3


class MediaStorage:
    """媒体存储管理器"""
    
    def __init__(self, storage_root: str = None):
        if storage_root is None:
            storage_root = "C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/media"
        self.storage_root = storage_root
        self._ensure_storage_dir()
        self.db_path = os.path.join(self.storage_root, "media.db")
        self._init_db()
    
    def _ensure_storage_dir(self):
        """确保存储目录存在"""
        os.makedirs(self.storage_root, exist_ok=True)
        os.makedirs(os.path.join(self.storage_root, "images"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_root, "videos"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_root, "audio"), exist_ok=True)
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS media_files (
                file_id TEXT PRIMARY KEY,
                filename TEXT,
                file_type TEXT,
                file_size INTEGER,
                md5 TEXT,
                storage_path TEXT,
                created_at REAL,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def save_file(self, file_data: bytes, filename: str, file_type: str = None) -> Dict[str, Any]:
        """保存媒体文件"""
        # 生成文件ID
        file_id = str(uuid.uuid4())
        
        # 检测文件类型
        if file_type is None:
            ext = os.path.splitext(filename)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                file_type = 'image'
            elif ext in ['.mp4', '.avi', '.mov', '.mkv']:
                file_type = 'video'
            elif ext in ['.mp3', '.wav', '.ogg', '.m4a']:
                file_type = 'audio'
            else:
                file_type = 'unknown'
        
        # 计算MD5
        md5 = hashlib.md5(file_data).hexdigest()
        
        # 生成存储路径
        subdir = file_type + 's'
        storage_path = os.path.join(self.storage_root, subdir, f"{file_id}_{filename}")
        
        # 保存文件
        with open(storage_path, 'wb') as f:
            f.write(file_data)
        
        # 记录到数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO media_files (file_id, filename, file_type, file_size, md5, storage_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (file_id, filename, file_type, len(file_data), md5, storage_path, time.time()))
        conn.commit()
        conn.close()
        
        return {
            "file_id": file_id,
            "filename": filename,
            "file_type": file_type,
            "file_size": len(file_data),
            "md5": md5,
            "storage_path": storage_path
        }
    
    def get_file(self, file_id: str) -> Optional[bytes]:
        """获取媒体文件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT storage_path FROM media_files WHERE file_id = ?", (file_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            path = row[0]
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    return f.read()
        return None
    
    def delete_file(self, file_id: str) -> bool:
        """删除媒体文件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT storage_path FROM media_files WHERE file_id = ?", (file_id,))
        row = cursor.fetchone()
        
        if row:
            path = row[0]
            if os.path.exists(path):
                os.remove(path)
            cursor.execute("DELETE FROM media_files WHERE file_id = ?", (file_id,))
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False
    
    def list_files(self, file_type: str = None, limit: int = 100) -> list:
        """列出媒体文件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if file_type:
            cursor.execute("""
                SELECT file_id, filename, file_type, file_size, created_at 
                FROM media_files 
                WHERE file_type = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (file_type, limit))
        else:
            cursor.execute("""
                SELECT file_id, filename, file_type, file_size, created_at 
                FROM media_files 
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "file_id": r[0],
                "filename": r[1],
                "file_type": r[2],
                "file_size": r[3],
                "created_at": r[4]
            }
            for r in rows
        ]


class MediaUploader:
    """媒体上传处理器"""
    
    def __init__(self, storage: MediaStorage = None):
        self.storage = storage or MediaStorage()
    
    def upload(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """处理文件上传"""
        result = self.storage.save_file(file_data, filename)
        return {
            "success": True,
            "file_id": result["file_id"],
            "filename": result["filename"],
            "file_type": result["file_type"],
            "size": result["file_size"]
        }
    
    def upload_base64(self, base64_data: str, filename: str = None) -> Dict[str, Any]:
        """处理Base64编码的文件上传"""
        import base64
        
        # 解码
        file_data = base64.b64decode(base64_data)
        
        # 生成文件名
        if filename is None:
            filename = f"upload_{int(time.time())}.dat"
        
        return self.upload(file_data, filename)
    
    def upload_url(self, url: str, filename: str = None) -> Dict[str, Any]:
        """从URL下载并保存文件"""
        import urllib.request
        
        # 下载
        with urllib.request.urlopen(url) as response:
            file_data = response.read()
        
        # 生成文件名
        if filename is None:
            filename = os.path.basename(url) or f"download_{int(time.time())}"
        
        return self.upload(file_data, filename)


if __name__ == "__main__":
    # 测试
    storage = MediaStorage()
    print("MediaStorage: OK")
    
    uploader = MediaUploader(storage)
    print("MediaUploader: OK")
    
    # 测试保存
    test_data = b"test image data"
    result = uploader.upload(test_data, "test.jpg")
    print("Upload:", result)
