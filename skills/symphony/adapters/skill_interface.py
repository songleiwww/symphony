# -*- coding: utf-8 -*-
"""
序境核心技能适配器接口
为第三方技能提供标准化接入基类
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, List


class SymphonySkillAdapter:
    """技能适配器基类 - 提供通用能力接口"""

    def __init__(self, skill_name: str, skill_version: str):
        self.skill_name = skill_name
        self.skill_version = skill_version
        self.skill_root = Path(__file__).parent.parent
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载技能配置（从 skill_config.json 或环境变量）"""
        config_path = self.skill_root / "skill_config.json"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """验证参数是否符合 schema"""
        schema = self.get_parameters_schema()
        required = schema.get("required", [])
        for field in required:
            if field not in parameters:
                return False
        return True

    def get_manifest(self) -> Dict[str, Any]:
        """返回技能清单"""
        return {
            "name": self.skill_name,
            "version": self.skill_version,
            "capabilities": self.get_capabilities(),
            "parameters": self.get_parameters_schema(),
        }

    def get_capabilities(self) -> List[str]:
        return ["execute"]

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def _check_qps(self, provider: str) -> bool:
        """QPS 检查（目前为占位实现）"""
        return True
