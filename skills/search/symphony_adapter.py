"""
Tavily 搜索技能 序境核心适配器
零侵入原有技能实现，通过调用原shell脚本完成功能
支持序境核心调度、多模型优先级、QPS限制、跨平台适配
"""
import os
import json
import subprocess
from typing import Dict, Any, List
from pathlib import Path

# 导入序境核心适配器接口
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "symphony"))
from adapters.skill_interface import SymphonySkillAdapter

class SearchSkill(SymphonySkillAdapter):
    def __init__(self):
        super().__init__(skill_name="search", skill_version="1.1.0")
        self.script_path = self.skill_root / "scripts" / "search.sh"
        self.tavily_api_key = self.config.get("tavily_api_key", os.environ.get("TAVILY_API_KEY", ""))
    
    def get_capabilities(self) -> List[str]:
        return [
            "web_search",
            "news_search",
            "finance_search",
            "real_time_data",
            "multilingual_search"
        ]
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索查询词，最多400字符"
                },
                "search_depth": {
                    "type": "string",
                    "enum": ["ultra-fast", "fast", "basic", "advanced"],
                    "default": "basic",
                    "description": "搜索深度"
                },
                "topic": {
                    "type": "string",
                    "enum": ["general", "news", "finance"],
                    "default": "general",
                    "description": "搜索主题"
                },
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 20,
                    "default": 5,
                    "description": "返回结果数量"
                },
                "time_range": {
                    "type": "string",
                    "enum": ["day", "week", "month", "year"],
                    "description": "时间范围"
                },
                "include_answer": {
                    "type": ["boolean", "string"],
                    "description": "是否返回整合答案"
                }
            }
        }
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        # 验证参数
        if not self.validate_parameters(parameters):
            return {
                "success": False,
                "data": None,
                "message": "参数验证失败",
                "model_used": None,
                "cost": 0
            }
        
        # 检查API Key
        if not self.tavily_api_key:
            return {
                "success": False,
                "data": None,
                "message": "TAVILY_API_KEY未配置",
                "model_used": None,
                "cost": 0
            }
        
        # 检查QPS限制 (Tavily服务商)
        if not self._check_qps("tavily"):
            return {
                "success": False,
                "data": None,
                "message": "QPS限制触发，请稍后重试",
                "model_used": None,
                "cost": 0
            }
        
        try:
            # 构造输入JSON
            input_json = json.dumps(parameters, ensure_ascii=False)
            
            # 调用原脚本
            env = os.environ.copy()
            env["TAVILY_API_KEY"] = self.tavily_api_key
            
            # 跨平台适配：Windows下使用WSL/Git Bash运行sh脚本
            if os.name == "nt":
                cmd = ["bash", str(self.script_path), input_json]
            else:
                cmd = [str(self.script_path), input_json]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=env,
                timeout=30
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "data": None,
                    "message": f"脚本执行失败: {result.stderr}",
                    "model_used": None,
                    "cost": 0
                }
            
            # 解析返回结果
            search_result = json.loads(result.stdout)
            
            # 计算消耗（Tavily按请求计费）
            cost = 0.001 if parameters.get("search_depth") == "advanced" else 0.0005
            
            return {
                "success": True,
                "data": search_result,
                "message": "搜索成功",
                "model_used": "tavily_search_api",
                "cost": cost
            }
            
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"执行异常: {str(e)}",
                "model_used": None,
                "cost": 0
            }

# 序境核心自动注册入口
if __name__ == "__main__":
    skill = SearchSkill()
    if len(sys.argv) > 1 and sys.argv[1] == "manifest":
        print(json.dumps(skill.get_manifest(), ensure_ascii=False, indent=2))
    elif len(sys.argv) > 1:
        # 执行命令
        params = json.loads(sys.argv[1])
        result = skill.execute(params)
        print(json.dumps(result, ensure_ascii=False, indent=2))
