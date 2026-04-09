"""
多模态图像分析技能 序境核心适配器
使用免费多模态模型实现图像识别、OCR、视觉问答等功能
遵循多模型调度优先级，优先使用免费模型
"""
import os
import json
import base64
from typing import Dict, Any, List
from pathlib import Path
from openai import OpenAI

# 导入序境核心适配器接口
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "symphony"))
from adapters.skill_interface import SymphonySkillAdapter

class ImageAnalysisSkill(SymphonySkillAdapter):
    def __init__(self):
        super().__init__(skill_name="image_analysis", skill_version="1.0.0")
        # 优先使用免费多模态模型
        self.client = OpenAI(
            api_key="7165f8ffad664d06bac6f9be04b48e26.ovDm4h1vaajj8N3w",
            base_url="https://open.bigmodel.cn/api/paas/v4/"
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "image_description",
            "ocr",
            "visual_qa",
            "image_classification",
            "qrcode_recognition",
            "table_recognition"
        ]
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["image_path", "action"],
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "本地图片路径或URL"
                },
                "action": {
                    "type": "string",
                    "enum": ["describe", "ocr", "qa", "classify", "qrcode", "table"],
                    "description": "执行操作类型"
                },
                "question": {
                    "type": "string",
                    "description": "视觉问答问题（action=qa时必填）"
                }
            }
        }
    
    def _encode_image(self, image_path: str) -> str:
        """编码图片为base64"""
        if image_path.startswith("http"):
            return image_path
        with open(image_path, "rb") as f:
            return f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode('utf-8')}"
    
    def _get_prompt(self, action: str, question: str = None) -> str:
        """根据动作类型获取提示词"""
        prompts = {
            "describe": "详细描述这张图片的内容，包括场景、物体、人物、文字等所有可见信息。",
            "ocr": "识别图片中所有的文字内容，按原文格式输出，不要遗漏任何文字。",
            "classify": "对这张图片进行分类，返回最准确的分类标签和置信度。",
            "qrcode": "识别图片中的二维码或条形码，返回其内容。",
            "table": "识别图片中的表格内容，返回Markdown格式的表格。"
        }
        if action == "qa":
            return question or "请回答关于这张图片的问题。"
        return prompts.get(action, "描述这张图片。")
    
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
        
        if parameters["action"] == "qa" and "question" not in parameters:
            return {
                "success": False,
                "data": None,
                "message": "视觉问答需要提供question参数",
                "model_used": None,
                "cost": 0
            }
        
        # 检查QPS限制
        if not self._check_qps("zhipu"):
            return {
                "success": False,
                "data": None,
                "message": "QPS限制触发，请稍后重试",
                "model_used": None,
                "cost": 0
            }
        
        try:
            # 编码图片
            image_url = self._encode_image(parameters["image_path"])
            prompt = self._get_prompt(parameters["action"], parameters.get("question"))
            
            # 选择最优模型
            model_used = self._select_best_model(required_capabilities=["multimodal", "vision"])
            
            # 调用模型
            response = self.client.chat.completions.create(
                model=model_used,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                max_tokens=4096,
                stream=False
            )
            
            result = response.choices[0].message.content
            
            return {
                "success": True,
                "data": result,
                "message": "图像分析成功",
                "model_used": model_used,
                "cost": 0  # 使用免费模型，无消耗
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
    skill = ImageAnalysisSkill()
    if len(sys.argv) > 1 and sys.argv[1] == "manifest":
        print(json.dumps(skill.get_manifest(), ensure_ascii=False, indent=2))
    elif len(sys.argv) > 1:
        params = json.loads(sys.argv[1])
        result = skill.execute(params)
        print(json.dumps(result, ensure_ascii=False, indent=2))
