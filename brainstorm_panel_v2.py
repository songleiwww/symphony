#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整版 BrainstormPanel v2.2.0 - 真实模型调用 + 工作总结汇报
"""

import json
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class TokenStats:
    """Token使用统计"""
    model_name: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_seconds: float = 0.0
    
    def get_cost_estimate(self, price_per_1k: float = 0.01) -> float:
        """估算成本"""
        return (self.total_tokens / 1000) * price_per_1k


@dataclass
class SymphonyReport:
    """工作总结汇报"""
    topic: str
    mode: str
    participants: List[Dict[str, str]]
    discussion_summary: str
    key_points: List[str]
    conclusions: List[str]
    token_stats: Dict[str, TokenStats]
    total_tokens: int
    total_cost: float
    execution_time: float


class BrainstormPanel:
    """
    多模型协作工具 v2.2.0
    
    功能：
    - 调用真实模型进行讨论
    - Token使用统计
    - 成本估算
    - 完整的工作总结汇报
    """
    
    def __init__(self):
        self.name = "brainstorm_panel"
        self.version = "2.2.0"
        
        # 加载配置
        config_path = Path(r"C:\Users\Administrator\.openclaw\openclaw.cherry.json")
        self.config = json.loads(config_path.read_text(encoding='utf-8'))
        
        # 角色配置
        self.roles_config = {
            "debate": [
                {"name": "正方专家", "provider": "cherry-doubao", "model": "deepseek-v3.2"},
                {"name": "反方专家", "provider": "cherry-doubao", "model": "kimi-k2.5"},
                {"name": "调解员", "provider": "cherry-doubao", "model": "glm-4.7"},
            ],
            "brainstorm": [
                {"name": "创意专家", "provider": "cherry-doubao", "model": "deepseek-v3.2"},
                {"name": "行业专家", "provider": "cherry-doubao", "model": "kimi-k2.5"},
                {"name": "用户代表", "provider": "cherry-doubao", "model": "glm-4.7"},
            ],
            "evaluate": [
                {"name": "技术评估员", "provider": "cherry-doubao", "model": "deepseek-v3.2"},
                {"name": "商业分析师", "provider": "cherry-doubao", "model": "kimi-k2.5"},
                {"name": "风险顾问", "provider": "cherry-doubao", "model": "glm-4.7"},
            ]
        }
    
    def execute(
        self,
        topic: str,
        mode: str = "brainstorm",
        participant_count: int = 3
    ) -> SymphonyReport:
        """执行多模型协作并生成汇报"""
        import time
        start_time = time.time()
        
        # 获取角色配置
        roles = self.roles_config.get(mode, self.roles_config["brainstorm"])[:participant_count]
        
        # 调用真实模型
        results, token_stats = self._call_models(topic, mode, roles)
        
        # 生成汇报
        report = self._generate_report(
            topic, mode, results, token_stats, 
            time.time() - start_time
        )
        
        return report
    
    def _call_models(
        self,
        topic: str,
        mode: str,
        roles: List[Dict]
    ) -> tuple[List[Dict], Dict[str, TokenStats]]:
        """调用真实模型"""
        results = []
        token_stats = {}
        
        mode_prompts = {
            "debate": "请从你的角度展开辩论，提出有力的论点和论据",
            "brainstorm": "请尽可能多地提出创意想法，不要顾虑可行性",
            "evaluate": "请从你的专业角度进行评估，给出具体的评分和理由"
        }
        
        for role_cfg in roles:
            prompt = f"""你是{role_cfg['name']}。

讨论主题：{topic}

{mode_prompts.get(mode, '请从你的专业角度发表看法')}

请用中文回复，200-400字。"""
            
            result, stats = self._call_single_model(
                role_cfg['provider'],
                role_cfg['model'],
                prompt
            )
            
            results.append({
                "role": role_cfg['name'],
                "model": role_cfg['model'],
                "response": result
            })
            token_stats[role_cfg['name']] = stats
        
        return results, token_stats
    
    def _call_single_model(
        self,
        provider: str,
        model: str,
        prompt: str
    ) -> tuple[str, TokenStats]:
        """调用单个模型"""
        import time
        start_time = time.time()
        
        provider_config = self.config["models"]["providers"][provider]
        api_key = provider_config["apiKey"]
        base_url = provider_config["baseUrl"]
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 800
        }
        
        url = f"{base_url}/chat/completions"
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=90)
            
            if response.status_code == 200:
                result_data = response.json()
                content = result_data["choices"][0]["message"]["content"]
                usage = result_data.get("usage", {})
                
                stats = TokenStats(
                    model_name=model,
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                    latency_seconds=time.time() - start_time
                )
                
                return content, stats
            else:
                return f"HTTP {response.status_code}: {response.text}", TokenStats(model_name=model)
                
        except Exception as e:
            return f"调用异常: {str(e)}", TokenStats(model_name=model)
    
    def _generate_report(
        self,
        topic: str,
        mode: str,
        results: List[Dict],
        token_stats: Dict[str, TokenStats],
        execution_time: float
    ) -> SymphonyReport:
        """生成工作总结汇报"""
        
        # 提取讨论摘要
        discussion_parts = [r["response"] for r in results if not r["response"].startswith("HTTP") and not r["response"].startswith("调用")]
        discussion_summary = "\n\n".join(discussion_parts[:3])
        
        # 提取关键点（简单处理）
        key_points = []
        for r in results:
            response = r["response"]
            # 取每条回复的前50字作为关键点
            if len(response) > 50:
                key_points.append(response[:100] + "...")
        
        # 提取结论
        conclusions = [
            f"参与角色：{len(results)}个",
            f"总Token消耗：{sum(s.total_tokens for s in token_stats.values())}",
            f"总成本估算：${sum(s.get_cost_estimate() for s in token_stats.values()):.4f}",
            f"执行时间：{execution_time:.2f}秒"
        ]
        
        return SymphonyReport(
            topic=topic,
            mode=mode,
            participants=results,
            discussion_summary=discussion_summary,
            key_points=key_points,
            conclusions=conclusions,
            token_stats=token_stats,
            total_tokens=sum(s.total_tokens for s in token_stats.values()),
            total_cost=sum(s.get_cost_estimate() for s in token_stats.values()),
            execution_time=execution_time
        )
    
    def save_report(self, report: SymphonyReport, output_path: str = None) -> str:
        """保存汇报到文件"""
        if not output_path:
            output_path = str(Path(__file__).parent / "outputs" / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        output_data = {
            "tool": self.name,
            "version": self.version,
            "topic": report.topic,
            "mode": report.mode,
            "timestamp": datetime.now().isoformat(),
            "participants": report.participants,
            "discussion_summary": report.discussion_summary,
            "key_points": report.key_points,
            "conclusions": report.conclusions,
            "token_stats": {k: asdict(v) for k, v in report.token_stats.items()},
            "total_tokens": report.total_tokens,
            "total_cost": report.total_cost,
            "execution_time": report.execution_time
        }
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding='utf-8')
        
        return output_path


def main():
    """测试"""
    log_file = Path(__file__).parent / "outputs" / "full_test_log.txt"
    log_file.parent.mkdir(exist_ok=True)
    log_file.write_text("", encoding='utf-8')
    
    def log(msg):
        with open(log_file, "a", encoding='utf-8') as f:
            f.write(msg + "\n")
    
    log("=" * 70)
    log("BrainstormPanel v2.2.0 - 完整测试")
    log("=" * 70)
    
    panel = BrainstormPanel()
    log(f"版本: {panel.version}")
    
    # 执行
    topic = "人工智能如何改变未来的工作方式？"
    log(f"\n主题: {topic}")
    log("开始执行...")
    
    report = panel.execute(topic=topic, mode="brainstorm", participant_count=3)
    
    # 显示结果
    log("\n" + "=" * 70)
    log("工作总结汇报")
    log("=" * 70)
    
    log(f"\n【主题】{report.topic}")
    log(f"【模式】{report.mode}")
    
    log("\n【参与角色】")
    for p in report.participants:
        log(f"  - {p['role']} ({p['model']})")
    
    log("\n【讨论内容】")
    log(report.discussion_summary[:500] + "...")
    
    log("\n【关键观点】")
    for i, point in enumerate(report.key_points, 1):
        log(f"  {i}. {point}")
    
    log("\n【统计摘要】")
    for c in report.conclusions:
        log(f"  - {c}")
    
    log("\n【Token详细统计】")
    for role, stats in report.token_stats.items():
        log(f"  {role}:")
        log(f"    模型: {stats.model_name}")
        log(f"    Prompt: {stats.prompt_tokens}")
        log(f"    Completion: {stats.completion_tokens}")
        log(f"    Total: {stats.total_tokens}")
        log(f"    成本: ${stats.get_cost_estimate():.4f}")
    
    # 保存汇报
    output_file = panel.save_report(report)
    log(f"\n汇报已保存到: {output_file}")
    
    log("\n测试完成!")
    

if __name__ == "__main__":
    main()
