#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony Skill Wrapper - 交响技能封装器
使AI模型能够通过Function Calling准确调用交响技能，
确保调用的是真实模型而不是模拟
"""

import json
import sys
import io
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# 修复Windows编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加symphony技能到路径
sys.path.insert(0, str(Path(__file__).parent))


class SymphonyMode(Enum):
    """交响技能运行模式"""
    DISCUSSION = "discussion"      # 多模型讨论
    BRAINSTORM = "brainstorm"      # 头脑风暴
    DEV_TEAM = "dev_team"          # 开发团队
    CRITIQUE = "critique"          # 评论/反馈


@dataclass
class SymphonyRequest:
    """交响技能调用请求"""
    topic: str                      # 讨论主题
    mode: str = "discussion"        # 运行模式
    num_models: int = 5             # 参与模型数量
    max_tokens_per_model: int = 800  # 每个模型最大token数
    require_real_api: bool = True   # 强制要求真实API调用（禁止模拟）
    output_format: str = "json"     # 输出格式：json/markdown
    save_to_file: bool = True       # 是否保存到文件


@dataclass
class SymphonyResponse:
    """交响技能调用响应"""
    success: bool
    topic: str
    mode: str
    num_models: int
    results: List[Dict[str, Any]]
    execution_mode: str = "real_api"  # 执行模式：real_api/simulated
    output_file: Optional[str] = None
    error: Optional[str] = None
    latency_seconds: float = 0.0


class SymphonySkillWrapper:
    """交响技能封装器 - 供Function Calling使用"""
    
    def __init__(self):
        self.name = "symphony_orchestrator"
        self.description = """
        交响多模型协作系统：调用多个真实AI模型进行讨论、头脑风暴或开发协作。
        【重要】此工具会调用真实的模型API，不是模拟！
        
        功能：
        - discussion: 多模型圆桌讨论
        - brainstorm: 多模型头脑风暴
        - dev_team: 多模型开发团队协作
        - critique: 多模型评论/反馈
        
        参数说明：
        - topic: 讨论主题（必填）
        - mode: 运行模式（默认discussion）
        - num_models: 参与模型数量（3-10，默认5）
        - require_real_api: 是否强制真实API调用（默认true，禁止模拟）
        """
        
        # 工具定义（OpenAI Function Calling格式）
        self.tool_definition = {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "讨论主题，要具体明确"
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["discussion", "brainstorm", "dev_team", "critique"],
                            "description": "运行模式：discussion（讨论）、brainstorm（头脑风暴）、dev_team（开发团队）、critique（评论）",
                            "default": "discussion"
                        },
                        "num_models": {
                            "type": "integer",
                            "minimum": 3,
                            "maximum": 10,
                            "description": "参与模型数量，3-10个",
                            "default": 5
                        },
                        "require_real_api": {
                            "type": "boolean",
                            "description": "是否强制真实API调用（true=禁止模拟，必须调用真实模型）",
                            "default": True
                        }
                    },
                    "required": ["topic"],
                    "additionalProperties": False
                }
            }
        }
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """获取工具定义（供Function Calling使用）"""
        return self.tool_definition
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行交响技能
        
        Args:
            arguments: Function Calling参数字典
            
        Returns:
            执行结果字典
        """
        import time
        start_time = time.time()
        
        try:
            # 解析参数
            request = SymphonyRequest(
                topic=arguments.get("topic", ""),
                mode=arguments.get("mode", "discussion"),
                num_models=arguments.get("num_models", 5),
                require_real_api=arguments.get("require_real_api", True)
            )
            
            # 验证参数
            if not request.topic.strip():
                return {
                    "success": False,
                    "error": "topic不能为空"
                }
            
            # 【关键】检查是否允许模拟
            if not request.require_real_api:
                print("⚠️  警告：require_real_api=False，允许模拟模式")
            else:
                print("✅ require_real_api=True，强制真实API调用模式")
            
            # 执行交响技能
            result = self._run_symphony(request)
            
            result["latency_seconds"] = time.time() - start_time
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"执行异常：{str(e)}",
                "latency_seconds": time.time() - start_time
            }
    
    def _run_symphony(self, request: SymphonyRequest) -> Dict[str, Any]:
        """运行真实的交响技能"""
        # 导入真实模型调用器
        try:
            from real_model_caller import RealModelCaller
        except ImportError:
            return {
                "success": False,
                "error": "无法导入RealModelCaller，请检查symphony技能安装",
                "execution_mode": "error"
            }
        
        # 根据模式选择专家配置
        panelists = self._get_panelists_by_mode(request.mode, request.num_models)
        
        # 初始化调用器
        caller = RealModelCaller()
        
        # 调用真实模型
        results = []
        for panelist in panelists:
            print(f"\n🎤 {panelist['name']} 正在思考...")
            
            # 构建提示词
            prompt = self._build_prompt(panelist, request.topic, request.mode)
            
            # 调用真实模型（这里简化处理，实际应使用caller）
            # 注意：为了演示，这里我们调用真实的API
            result = self._call_real_model(panelist, prompt)
            
            results.append({
                "panelist": panelist['name'],
                "model": panelist['model'],
                "provider": panelist['provider'],
                "role": panelist['role'],
                "response": result.get('response', ''),
                "success": result.get('success', False)
            })
        
        # 保存结果
        output_file = None
        if request.save_to_file:
            output_file = self._save_results(request, results)
        
        return {
            "success": True,
            "topic": request.topic,
            "mode": request.mode,
            "num_models": len(results),
            "results": results,
            "execution_mode": "real_api",  # 【关键】标记为真实API
            "output_file": output_file
        }
    
    def _get_panelists_by_mode(self, mode: str, num_models: int) -> List[Dict[str, Any]]:
        """根据模式获取专家配置"""
        base_panelists = [
            {
                "name": "战略分析师",
                "provider": "cherry-doubao",
                "model": "deepseek-v3.2",
                "role": "全局视角、长期规划"
            },
            {
                "name": "创意专家",
                "provider": "cherry-doubao",
                "model": "kimi-k2.5",
                "role": "创新思维、突破常规"
            },
            {
                "name": "技术专家",
                "provider": "cherry-doubao",
                "model": "glm-4.7",
                "role": "技术实现、可行性分析"
            },
            {
                "name": "风险评估师",
                "provider": "cherry-minimax",
                "model": "MiniMax-M2.5",
                "role": "风险识别、应急预案"
            },
            {
                "name": "用户体验专家",
                "provider": "cherry-doubao",
                "model": "deepseek-v3.2",
                "role": "用户需求、体验优化"
            }
        ]
        
        # 根据模式调整
        if mode == "dev_team":
            return [
                {"name": "产品经理", "provider": "cherry-doubao", "model": "kimi-k2.5", "role": "需求分析"},
                {"name": "架构师", "provider": "cherry-doubao", "model": "deepseek-v3.2", "role": "系统设计"},
                {"name": "开发工程师", "provider": "cherry-doubao", "model": "glm-4.7", "role": "代码实现"},
                {"name": "测试工程师", "provider": "cherry-doubao", "model": "kimi-k2.5", "role": "质量保证"},
                {"name": "运维工程师", "provider": "cherry-minimax", "model": "MiniMax-M2.5", "role": "部署运维"}
            ][:num_models]
        
        return base_panelists[:num_models]
    
    def _build_prompt(self, panelist: Dict[str, Any], topic: str, mode: str) -> str:
        """构建提示词"""
        if mode == "discussion":
            return f"""你是{panelist['name']}。{panelist['role']}

讨论主题：{topic}

请从你的专业角度发表看法，150-300字，用中文回复。"""
        elif mode == "brainstorm":
            return f"""你是{panelist['name']}。{panelist['role']}

头脑风暴主题：{topic}

请尽可能多地提出创意想法，200-400字，用中文回复。"""
        elif mode == "dev_team":
            return f"""你是{panelist['name']}。{panelist['role']}

开发任务：{topic}

请从你的专业角度给出具体方案，200-400字，用中文回复。"""
        else:
            return f"""你是{panelist['name']}。{panelist['role']}

评论主题：{topic}

请给出你的评论和建议，150-300字，用中文回复。"""
    
    def _call_real_model(self, panelist: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """调用真实模型"""
        import requests
        
        # 加载配置
        config_path = Path(r"C:\Users\Administrator\.openclaw\openclaw.cherry.json")
        config = json.loads(config_path.read_text(encoding='utf-8'))
        
        provider_config = config["models"]["providers"][panelist["provider"]]
        api_key = provider_config["apiKey"]
        base_url = provider_config["baseUrl"]
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": panelist["model"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 800
        }
        
        url = f"{base_url}/chat/completions"
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=90)
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result['choices'][0]['message']['content']
                }
            else:
                return {
                    "success": False,
                    "response": f"HTTP {response.status_code}: {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "response": f"调用异常：{str(e)}"
            }
    
    def _save_results(self, request: SymphonyRequest, results: List[Dict[str, Any]]) -> str:
        """保存结果到文件"""
        from datetime import datetime
        
        output = {
            "topic": request.topic,
            "mode": request.mode,
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
        
        outfile = Path(__file__).parent / "outputs" / f"symphony_wrapper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        outfile.parent.mkdir(exist_ok=True)
        outfile.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
        
        return str(outfile)


def main():
    """测试"""
    print("=" * 80)
    print("Symphony Skill Wrapper - 交响技能封装器测试")
    print("=" * 80)
    
    wrapper = SymphonySkillWrapper()
    
    # 显示工具定义
    print("\n📋 工具定义:")
    print(json.dumps(wrapper.get_tool_definition(), indent=2, ensure_ascii=False))
    
    # 测试执行
    print("\n🧪 测试执行...")
    result = wrapper.execute({
        "topic": "人工智能如何改变未来的工作方式？",
        "mode": "discussion",
        "num_models": 3,
        "require_real_api": True
    })
    
    print("\n📊 执行结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
