import json
import os
from typing import List, Dict, Any
from pathlib import Path


class Storage:
    """数据存储类，处理JSON文件的读写"""

    DEFAULT_DATA_FILE = ".todo.json"

    def __init__(self, file_path: str = None):
        if file_path is None:
            # 使用用户主目录下的默认文件
            home_dir = Path.home()
            file_path = str(home_dir / self.DEFAULT_DATA_FILE)
        self.file_path = file_path
        self.ensure_file_exists()

    def ensure_file_exists(self) -> None:
        """确保数据文件存在，如果不存在则创建"""
        if not os.path.exists(self.file_path):
            # 创建空的数据文件
            initial_data = {
                "version": "1.0",
                "next_id": 1,
                "tasks": []
            }
            self._write_json(initial_data)

    def _read_json(self) -> Dict[str, Any]:
        """读取JSON文件"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # 如果文件损坏，返回默认数据
            return {
                "version": "1.0",
                "next_id": 1,
                "tasks": []
            }
        except Exception as e:
            raise IOError(f"读取文件失败: {e}")

    def _write_json(self, data: Dict[str, Any]) -> None:
        """写入JSON文件"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise IOError(f"写入文件失败: {e}")

    def load(self) -> Dict[str, Any]:
        """加载所有数据"""
        return self._read_json()

    def save(self, data: Dict[str, Any]) -> None:
        """保存所有数据"""
        self._write_json(data)

    def load_tasks(self) -> List[Dict[str, Any]]:
        """加载任务列表"""
        data = self.load()
        return data.get("tasks", [])

    def save_tasks(self, tasks: List[Dict[str, Any]], next_id: int) -> None:
        """保存任务列表"""
        data = self.load()
        data["tasks"] = tasks
        data["next_id"] = next_id
        self.save(data)

    def get_next_id(self) -> int:
        """获取下一个任务ID"""
        data = self.load()
        return data.get("next_id", 1)

    def backup(self, backup_path: str = None) -> str:
        """创建数据备份"""
        if backup_path is None:
            backup_path = f"{self.file_path}.backup"

        import shutil
        shutil.copy2(self.file_path, backup_path)
        return backup_path
