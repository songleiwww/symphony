#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进版 Symphony 交响工具 - BrainstormPanel v2.1.0
加入真实模型token使用统计功能
"""

import json
import sys
import io
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict, field
from datetime import datetime

# 修复Windows编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class SymphonyMode(str, Enum):
    """协作模式枚举"""
    DEBATE = "debate"       # 辩论：冲突视角，寻找漏洞
    BRAINSTORM = "brainstorm" # 头脑风暴：创意发散
    EVALUATE = "evaluate"   # 评估：多维度打分


@dataclass
class TokenUsage:
    """Token使用统计"""
    model_name: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_seconds: float = 0.0
    
    def get_cost_estimate(self) -> float:
        """估算成本（简单估算）"""
        # 假设每1000 tokens $0.01
        return (self.total_tokens / 1000) * 0.01


@dataclass
class SymphonyResult:
    """交响工具执行结果"""
    success: bool
    tool: str
    mode: str
    topic: str
    participants: List[str]
    content: str
    token_usage: Dict[str, TokenUsage] = field(default_factory=dict)
    total_tokens: int = 0
    total_cost_estimate: float = 0.0
    output_file: Optional[str] = None
    error: Optional[str] = None
    latency_seconds: float = 0.0


class BrainstormPanel:
    """
    多模型协作工具（改进版 v2.1.0）
    
    角色定位：交响乐指挥家
    价值主张：超越单一模型的综合分析质量，通过多视角协作输出深度洞察
    
    新增功能：
    - Token使用统计
    - 成本估算
    - 详细的调用日志
    
    触发关键词：
    - 多模型协作
    - 专家辩论
    - 头脑风暴
    - 综合评估
    - 复杂问题分析
    
    适用场景：
    1. 辩论模式：分析"AI对社会就业的影响"，让专家展开辩论
    2. 头脑风暴：为新产品创意集思广益
    3. 评估模式：对多个方案进行系统性评估
    """
    
    def __init__(self):
        self.name = "brainstorm_panel"
        self.version = "2.1.0"
        self.description = f"""
像一个'交响乐指挥家'，协调多个AI专家模型进行协作。
适用于需要批判性思维、创意发散或复杂评估的场景。
它能整合不同模型的视角，输出比单一模型更全面、更少偏见的分析结果。

【触发场景】
- 当任务涉及复杂逻辑推理时使用
- 当需要多视角辩论时使用
- 当需要高创意头脑风暴时使用

【价值主张】
通过多模型协作，获得超越单一模型的综合分析质量

【版本】
{self.version} - 新增Token使用统计和成本估算
"""
        
        # 工具定义（OpenAI Function Calling格式）
        self.tool_definition = {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description.strip(),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "需要分析的核心议题或问题（5-500字符）",
                            "minLength": 5,
                            "maxLength": 500
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["debate", "brainstorm", "evaluate"],
                            "description": "协作模式：debate(辩论/批判)、brainstorm(创意发散)、evaluate(多维评估)"
                        },
                        "participant_count": {
                            "type": "integer",
                            "minimum": 2,
                            "maximum": 5,
                            "default": 3,
                            "description": "参与模型数量（2-5个），不同模型将扮演不同角色"
                        },
                        "context": {
                            "type": "string",
                            "description": "（可选）背景信息或上下文约束"
                        },
                        "show_token_stats": {
                            "type": "boolean",
                            "default": True,
                            "description": "是否显示Token使用统计和成本估算"
                        }
                    },
                    "required": ["topic", "mode"],
                    "additionalProperties": False
                }
            }
        }
        
        # 角色配置
        self.roles = {
            "debate": ["正方专家", "反方专家", "调解员", "事实核查员", "总结员"],
            "brainstorm": ["创意专家", "行业专家", "用户代表", "技术专家", "商业分析师"],
            "evaluate": ["技术评估员", "商业分析师", "风险顾问", "用户体验专家", "成本核算员"]
        }
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """获取工具定义（供Function Calling使用）"""
        return self.tool_definition
    
    def execute(
        self,
        topic: str,
        mode: str,
        participant_count: int = 3,
        context: Optional[str] = None,
        show_token_stats: bool = True
    ) -> SymphonyResult:
        """
        执行多模型协作
        
        Args:
            topic: 讨论主题
            mode: 协作模式
            participant_count: 参与模型数量
            context: 可选背景信息
            show_token_stats: 是否显示Token统计
        
        Returns:
            执行结果
        """
        import time
        start_time = time.time()
        
        token_usage_dict = {}
        total_tokens = 0
        
        try:
            # 验证模式
            if mode not in [m.value for m in SymphonyMode]:
                return SymphonyResult(
                    success=False,
                    tool=self.name,
                    mode=mode,
                    topic=topic,
                    participants=[],
                    content="",
                    error=f"无效的模式：{mode}，可选值：debate、brainstorm、evaluate"
                )
            
            # 获取角色列表
            mode_roles = self.roles.get(mode, ["专家"])
            actual_roles = mode_roles[:participant_count]
            
            # 调用真实模型
            results, token_usage_dict = self._call_real_models(
                topic, mode, actual_roles, context
            )
            
            # 计算总tokens
            total_tokens = sum(t.total_tokens for t in token_usage_dict.values())
            total_cost = sum(t.get_cost_estimate() for t in token_usage_dict.values())
            
            # 保存结果
            output_file = self._save_results(topic, mode, actual_roles, results, token_usage_dict)
            
            # 构造返回内容
            content = self._format_content(
                topic, mode, actual_roles, results, 
                token_usage_dict if show_token_stats else None
            )
            
            return SymphonyResult(
                success=True,
                tool=self.name,
                mode=mode,
                topic=topic,
                participants=actual_roles,
                content=content,
                token_usage=token_usage_dict,
                total_tokens=total_tokens,
                total_cost_estimate=total_cost,
                output_file=output_file,
                latency_seconds=time.time() - start_time
            )
            
        except Exception as e:
            return SymphonyResult(
                success=False,
                tool=self.name,
                mode=mode or "unknown",
                topic=topic,
                participants=[],
                content="",
                error=f"执行异常：{str(e)}",
                latency_seconds=time.time() - start_time
            )
    
    def _call_real_models(
        self,
        topic: str,
        mode: str,
        roles: List[str],
        context: Optional[str]
    ) -> tuple[List[Dict[str, Any]], Dict[str, TokenUsage]]:
        """调用真实模型，返回结果和token统计"""
        results = []
        token_usage_dict = {}
        
        try:
            # 临时禁用stdout以避免IO问题
            import io
            import sys
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()
            
            sys.path.insert(0, str(Path(__file__).parent))
            from real_model_caller import RealModelCaller
            
            caller = RealModelCaller()
            
            # 恢复stdout
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            for i, role in enumerate(roles):
                prompt = self._build_prompt(role, topic, mode, context)
                
                # 使用优先级i+1的模型
                result = caller.call_model(
                    prompt=prompt,
                    priority=i + 1,
                    max_tokens=800,
                    temperature=0.7
                )
                
                # 记录token使用
                token_usage = TokenUsage(
                    model_name=result.model_alias or result.model_name,
                    prompt_tokens=result.prompt_tokens,
                    completion_tokens=result.completion_tokens,
                    total_tokens=result.total_tokens,
                    latency_seconds=result.latency
                )
                token_usage_dict[role] = token_usage
                
                results.append({
                    "role": role,
                    "model": result.model_name,
                    "model_alias": result.model_alias,
                    "response": result.response if result.success else result.error,
                    "success": result.success
                })
            
            return results, token_usage_dict
            
        except Exception as e:
            error_result = {
                "role": "系统",
                "model": "n/a",
                "model_alias": "n/a",
                "response": f"调用真实模型时出错：{str(e)}",
                "success": False
            }
            return [error_result], token_usage_dict
    
    def _build_prompt(
        self,
        role: str,
        topic: str,
        mode: str,
        context: Optional[str]
    ) -> str:
        """构建提示词"""
        mode_descriptions = {
            "debate": "请从你的角度展开辩论，提出有力的论点和论据",
            "brainstorm": "请尽可能多地提出创意想法，不要顾虑可行性",
            "evaluate": "请从你的专业角度进行评估，给出具体的评分和理由"
        }
        
        base_prompt = f"""你是{role}。

讨论主题：{topic}

{mode_descriptions.get(mode, "请从你的专业角度发表看法")}

{"背景信息：" + context if context else ""}

请用中文回复，150-300字。"""
        
        return base_prompt
    
    def _format_content(
        self,
        topic: str,
        mode: str,
        roles: List[str],
        results: List[Dict[str, Any]],
        token_usage: Optional[Dict[str, TokenUsage]] = None
    ) -> str:
        """格式化内容"""
        lines = []
        lines.append(f"## {mode.capitalize()}模式讨论")
        lines.append(f"**主题：** {topic}")
        lines.append(f"**参与角色：** {', '.join(roles)}")
        lines.append("")
        
        for result in results:
            lines.append(f"### {result['role']}")
            model_display = result.get('model_alias', result['model'])
            lines.append(f"*模型：{model_display}*")
            lines.append("")
            lines.append(result['response'])
            lines.append("")
        
        # Token统计
        if token_usage:
            lines.append("---")
            lines.append("## 📊 Token使用统计")
            lines.append("")
            
            total_tokens = 0
            total_cost = 0.0
            
            for role, usage in token_usage.items():
                lines.append(f"### {role}")
                lines.append(f"- 模型：{usage.model_name}")
                lines.append(f"- Prompt tokens：{usage.prompt_tokens}")
                lines.append(f"- Completion tokens：{usage.completion_tokens}")
                lines.append(f"- **Total tokens：{usage.total_tokens}**")
                lines.append(f"- 耗时：{usage.latency_seconds:.2f}秒")
                lines.append(f"- 估算成本：${usage.get_cost_estimate():.4f}")
                lines.append("")
                
                total_tokens += usage.total_tokens
                total_cost += usage.get_cost_estimate()
            
            lines.append("---")
            lines.append(f"### 总计")
            lines.append(f"- **总 Tokens：{total_tokens}**")
            lines.append(f"- **总估算成本：${total_cost:.4f}**")
        
        return "\n".join(lines)
    
    def _save_results(
        self,
        topic: str,
        mode: str,
        roles: List[str],
        results: List[Dict[str, Any]],
        token_usage: Dict[str, TokenUsage]
    ) -> str:
        """保存结果到文件"""
        from datetime import datetime
        
        # 转换token_usage为可序列化格式
        token_usage_serializable = {
            role: asdict(usage) for role, usage in token_usage.items()
        }
        
        output = {
            "tool": self.name,
            "version": self.version,
            "mode": mode,
            "topic": topic,
            "participants": roles,
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "token_usage": token_usage_serializable
        }
        
        outfile = Path(__file__).parent / "outputs" / f"brainstorm_panel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        outfile.parent.mkdir(exist_ok=True)
        outfile.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
        
        return str(outfile)


def main():
    """测试"""
    print("=" * 80)
    print(f"BrainstormPanel - 改进版交响工具测试 (v{BrainstormPanel().version})")
    print("=" * 80)
    
    panel = BrainstormPanel()
    
    # 显示工具定义
    print("\n📋 工具定义:")
    print(json.dumps(panel.get_tool_definition(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
