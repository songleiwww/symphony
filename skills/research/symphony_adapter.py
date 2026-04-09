"""
AI 研究综述技能 序境核心适配器
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

class ResearchSkill(SymphonySkillAdapter):
    def __init__(self):
        super().__init__(skill_name="research", skill_version="1.1.0")
        self.script_path = self.skill_root / "scripts" / "research.sh"
        self.tavily_api_key = self.config.get("tavily_api_key", os.environ.get("TAVILY_API_KEY", ""))
    
    def get_capabilities(self) -> List[str]:
        return [
            "ai_research",
            "literature_review",
            "topic_synthesis",
            "citation_generation",
            "structured_research"
        ]
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {
                    "type": "string",
                    "description": "研究主题查询词"
                },
                "search_depth": {
                    "type": "string",
                    "enum": ["basic", "advanced"],
                    "default": "basic",
                    "description": "研究深度"
                },
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 20,
                    "default": 10,
                    "description": "引用来源数量"
                },
                "time_range": {
                    "type": "string",
                    "enum": ["day", "week", "month", "year", "all"],
                    "description": "文献时间范围"
                },
                "include_citations": {
                    "type": "boolean",
                    "default": True,
                    "description": "是否包含引用格式"
                },
                "output_format": {
                    "type": "string",
                    "enum": ["markdown", "json", "text"],
                    "default": "markdown",
                    "description": "输出格式"
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
        
        # 检查QPS限制
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
            
            # 跨平台适配
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
                timeout=120  # 研究任务需要更长时间
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
            research_result = json.loads(result.stdout) if parameters.get("output_format") == "json" else result.stdout
            
            # 选择最优模型生成综述内容
            model_used = self._select_best_model(required_capabilities=["text-generation"])
            cost = 0.005 if parameters.get("search_depth") == "advanced" else 0.002
            
            return {
                "success": True,
                "data": research_result,
                "message": "研究综述生成成功",
                "model_used": model_used,
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
    skill = ResearchSkill()
    if len(sys.argv) > 1 and sys.argv[1] == "manifest":
        print(json.dumps(skill.get_manifest(), ensure_ascii=False, indent=2))
    elif len(sys.argv) > 1:
        params = json.loads(sys.argv[1])
        result = skill.execute(params)
        print(json.dumps(result, ensure_ascii=False, indent=2))
