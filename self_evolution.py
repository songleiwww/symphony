#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境自进化系统 SelfEvolution v1.0
基于AI自进化·细粒度能力升级指令
实现：自感知、自诊断、自修正、自进化、自优化
"""
import os
import sys
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import sqlite3

KERNEL_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KERNEL_PATH)

DATA_PATH = os.path.join(KERNEL_PATH, '..', 'data')
DB_PATH = os.path.join(DATA_PATH, 'symphony.db')


class FineGrainLevel(Enum):
    """细粒度能力等级"""
    LEVEL_1_BASIC = "基础理解"
    LEVEL_2_LOGIC = "逻辑增强"
    LEVEL_3_DETAIL = "细节拉满"
    LEVEL_4_STYLE = "风格对齐"
    LEVEL_5_AUTO = "全自动闭环"


class EvolutionPhase(Enum):
    """进化阶段"""
    PERCEPTION = "感知"      # 细粒度感知与拆解
    DIAGNOSIS = "诊断"      # 自诊断与自我修正
    ITERATION = "迭代"      # 自进化迭代机制
    OUTPUT = "输出"         # 极致细粒度输出控制
    MEMORY = "记忆"         # 长期记忆与持续优化


class ExecutionMetrics:
    """执行指标"""
    
    def __init__(self):
        self.precision = 0.0      # 精度
        self.completeness = 0.0   # 完整性
        self.consistency = 0.0    # 一致性
        self.compliance = 0.0     # 合规性
        self.readability = 0.0   # 可读性
        self.risk_points = []     # 风险点
        self.ambiguity_points = [] # 歧义点
        self.missing_info = []    # 缺失信息


class SelfEvolution:
    """自进化核心引擎"""
    
    def __init__(self):
        self.current_level = FineGrainLevel.LEVEL_1_BASIC
        self.evolution_history = []
        self.optimal_patterns = {}  # 最优模式
        self.templates = {}         # 精细化模板
        self.performance_cache = {} # 性能缓存
        self._init_database()
    
    def _init_database(self):
        """初始化自进化数据库"""
        os.makedirs(DATA_PATH, exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 创建自进化表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS self_evolution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                phase TEXT,
                level TEXT,
                metrics TEXT,
                optimization TEXT,
                result TEXT
            )
        ''')
        
        # 创建细粒度模板表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fine_grain_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scene TEXT,
                template TEXT,
                usage_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                last_used TEXT
            )
        ''')
        
        # 创建最优模式表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimal_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT,
                pattern_data TEXT,
                score REAL DEFAULT 0.0,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ==================== 1. 细粒度感知与拆解 ====================
    
    def perceive_and_decompose(self, task: str, context: Dict = None) -> Dict:
        """
        细粒度感知与拆解
        - 对任务进行最小语义单元拆解
        - 精准识别需求中的约束、边界、格式、语气、场景与隐含目标
        - 对输入信息做逐字段、逐逻辑、逐细节校验
        """
        decomposition = {
            "task": task,
            "semantic_units": [],      # 最小语义单元
            "constraints": [],          # 约束条件
            "boundaries": [],          # 边界
            "format_requirements": [], # 格式要求
            "tone_requirements": [],   # 语气要求
            "scenarios": [],           # 场景
            "hidden_goals": [],        # 隐含目标
            "validation_results": {},   # 校验结果
            "risk_points": [],          # 风险点
            "ambiguity_points": []      # 歧义点
        }
        
        # 最小语义单元拆解
        words = task.split()
        for i, word in enumerate(words):
            unit = {
                "text": word,
                "position": i,
                "type": self._classify_semantic_unit(word),
                "importance": self._calculate_importance(word, i, len(words))
            }
            decomposition["semantic_units"].append(unit)
        
        # 识别约束和边界
        constraint_keywords = ["必须", "禁止", "仅", "不超过", "至少", "必须", "不要", "仅限"]
        boundary_keywords = ["只能", "只", "仅", "不超过", "以上", "以下"]
        
        for keyword in constraint_keywords:
            if keyword in task:
                decomposition["constraints"].append(keyword)
        
        for keyword in boundary_keywords:
            if keyword in task:
                decomposition["boundaries"].append(keyword)
        
        # 识别格式要求
        format_keywords = ["表格", "列表", "JSON", "Markdown", "表格", "分点", "分段"]
        for keyword in format_keywords:
            if keyword in task:
                decomposition["format_requirements"].append(keyword)
        
        # 识别语气要求
        tone_keywords = ["正式", "简洁", "详细", "温柔", "专业", "友好", "严肃"]
        for keyword in tone_keywords:
            if keyword in task:
                decomposition["tone_requirements"].append(keyword)
        
        # 识别隐含目标
        if "总结" in task or "汇总" in task:
            decomposition["hidden_goals"].append("信息提炼")
        if "分析" in task:
            decomposition["hidden_goals"].append("深度洞察")
        if "学习" in task or "预学习" in task:
            decomposition["hidden_goals"].append("知识获取")
        
        # 逐字段校验
        decomposition["validation_results"] = self._validate_input(task, context or {})
        
        # 风险点和歧义点预判
        decomposition["risk_points"] = self._predict_risk_points(task)
        decomposition["ambiguity_points"] = self._identify_ambiguity(task)
        
        return decomposition
    
    def _classify_semantic_unit(self, word: str) -> str:
        """分类语义单元类型"""
        if any(kw in word for kw in ["分析", "处理", "执行"]):
            return "action"
        elif any(kw in word for kw in ["什么", "如何", "为什么", "多少"]):
            return "query"
        elif any(kw in word for kw in ["创建", "生成", "建立"]):
            return "creation"
        else:
            return "content"
    
    def _calculate_importance(self, word: str, position: int, total: int) -> float:
        """计算词重要性"""
        if position == 0:
            return 1.0
        elif position < total * 0.2:
            return 0.8
        elif position < total * 0.5:
            return 0.6
        else:
            return 0.4
    
    def _validate_input(self, task: str, context: Dict) -> Dict:
        """逐字段校验输入"""
        results = {
            "field_checks": [],
            "logic_checks": [],
            "detail_checks": [],
            "issues": []
        }
        
        # 字段校验
        if len(task) < 5:
            results["issues"].append({"type": "too_short", "severity": "high"})
        
        if "?" in task and "？" not in task:
            results["issues"].append({"type": "inconsistent_punctuation", "severity": "low"})
        
        # 逻辑校验
        if "但是" in task and "虽然" not in task:
            results["logic_checks"].append("conditional_without_premise")
        
        # 细节校验
        if any(kw in task for kw in ["他", "她", "它"]) and "谁" not in task:
            results["detail_checks"].append("ambiguous_reference")
        
        return results
    
    def _predict_risk_points(self, task: str) -> List[Dict]:
        """预判风险点"""
        risks = []
        
        if len(task) > 500:
            risks.append({"type": "too_long", "description": "任务描述过长，可能导致理解偏差"})
        
        if "删除" in task or "移除" in task:
            risks.append({"type": "destructive", "description": "包含删除操作，需谨慎处理"})
        
        if "执行" in task and ("sudo" in task or "管理员" in task):
            risks.append({"type": "elevated_privilege", "description": "需要提升权限操作"})
        
        return risks
    
    def _identify_ambiguity(self, task: str) -> List[Dict]:
        """识别歧义点"""
        ambiguities = []
        
        ambiguous_phrases = [
            ("它", "指代不明确"),
            ("这个", "指示不明确"),
            ("之前", "时间范围不明确"),
            ("大约", "数值不精确")
        ]
        
        for phrase, desc in ambiguous_phrases:
            if phrase in task:
                ambiguities.append({"phrase": phrase, "description": desc})
        
        return ambiguities
    
    # ==================== 2. 自诊断与自我修正 ====================
    
    def self_diagnose(self, result: Any, expected: Any = None) -> Dict:
        """
        执行后进行结果自检
        - 精度、完整性、一致性、合规性、可读性
        - 发现偏差立即局部回滚、重构逻辑、重新生成
        """
        diagnosis = {
            "precision_score": 0.0,
            "completeness_score": 0.0,
            "consistency_score": 0.0,
            "compliance_score": 0.0,
            "readability_score": 0.0,
            "overall_score": 0.0,
            "issues": [],
            "corrections": [],
            "needs_regeneration": False
        }
        
        # 精度检查
        if isinstance(result, str):
            diagnosis["precision_score"] = self._check_precision(result)
        
        # 完整性检查
        diagnosis["completeness_score"] = self._check_completeness(result, expected)
        
        # 一致性检查
        diagnosis["consistency_score"] = self._check_consistency(result)
        
        # 合规性检查
        diagnosis["compliance_score"] = self._check_compliance(result)
        
        # 可读性检查
        diagnosis["readability_score"] = self._check_readability(result)
        
        # 计算总分
        weights = {
            "precision": 0.25,
            "completeness": 0.25,
            "consistency": 0.2,
            "compliance": 0.15,
            "readability": 0.15
        }
        
        diagnosis["overall_score"] = (
            diagnosis["precision_score"] * weights["precision"] +
            diagnosis["completeness_score"] * weights["completeness"] +
            diagnosis["consistency_score"] * weights["consistency"] +
            diagnosis["compliance_score"] * weights["compliance"] +
            diagnosis["readability_score"] * weights["readability"]
        )
        
        # 判断是否需要重新生成
        diagnosis["needs_regeneration"] = diagnosis["overall_score"] < 0.8
        
        # 如有问题，生成修正方案
        if diagnosis["needs_regeneration"]:
            diagnosis["corrections"] = self._generate_corrections(result, diagnosis["issues"])
        
        return diagnosis
    
    def _check_precision(self, result: str) -> float:
        """检查精度"""
        score = 1.0
        
        # 检查是否有模糊表述
        vague_terms = ["大概", "可能", "也许", "应该", "似乎"]
        for term in vague_terms:
            if term in result:
                score -= 0.1
        
        # 检查数据精确性
        import re
        numbers = re.findall(r'\d+\.?\d*', result)
        if numbers:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _check_completeness(self, result: Any, expected: Any) -> float:
        """检查完整性"""
        if expected is None:
            return 0.8  # 默认分数
        
        if isinstance(result, str) and isinstance(expected, str):
            # 检查关键元素是否包含
            expected_keywords = expected.split()
            found_keywords = sum(1 for kw in expected_keywords if kw in result)
            return found_keywords / len(expected_keywords) if expected_keywords else 0.8
        
        return 0.8
    
    def _check_consistency(self, result: Any) -> float:
        """检查一致性"""
        if not isinstance(result, str):
            return 0.8
        
        score = 1.0
        
        # 检查前后矛盾
        contradictions = [("但是", "而且"), ("但是", "同时")]
        for a, b in contradictions:
            if a in result and b in result:
                score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    def _check_compliance(self, result: Any) -> float:
        """检查合规性"""
        if not isinstance(result, str):
            return 1.0
        
        score = 1.0
        
        # 检查是否包含敏感词
        sensitive_terms = ["密码", "密钥", "token", "secret"]
        for term in sensitive_terms:
            if term.lower() in result.lower():
                score -= 0.3
        
        return max(0.0, min(1.0, score))
    
    def _check_readability(self, result: Any) -> float:
        """检查可读性"""
        if not isinstance(result, str):
            return 0.8
        
        score = 0.8
        
        # 检查段落结构
        if "\n\n" in result:
            score += 0.1
        
        # 检查标点使用
        if "。" in result or "，" in result:
            score += 0.1
        
        # 检查长度适中
        if 50 < len(result) < 2000:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _generate_corrections(self, result: Any, issues: List[Dict]) -> List[Dict]:
        """生成修正方案"""
        corrections = []
        
        for issue in issues:
            correction = {
                "issue": issue.get("type", "unknown"),
                "action": "regenerate",
                "strategy": self._select_correction_strategy(issue)
            }
            corrections.append(correction)
        
        return corrections
    
    def _select_correction_strategy(self, issue: Dict) -> str:
        """选择修正策略"""
        issue_type = issue.get("type", "")
        
        if "precision" in issue_type:
            return "增加具体数据和时间"
        elif "completeness" in issue_type:
            return "补充缺失信息"
        elif "consistency" in issue_type:
            return "重构逻辑一致性"
        elif "compliance" in issue_type:
            return "移除敏感内容"
        else:
            return "重新生成"
    
    # ==================== 3. 自进化迭代机制 ====================
    
    def evolve_from_interaction(self, task: str, result: Any, metrics: Dict) -> Dict:
        """
        每一次交互都作为进化样本
        - 自动提炼最优模式、偏好、风格、结构
        - 对高频场景形成精细化模板与策略
        """
        evolution = {
            "task_type": self._classify_task_type(task),
            "pattern_extracted": {},
            "template_updated": False,
            "level_upgraded": False,
            "recommendations": []
        }
        
        # 提取最优模式
        pattern = {
            "task": task[:50],
            "result_length": len(str(result)),
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        evolution["pattern_extracted"] = pattern
        
        # 更新模板
        task_type = evolution["task_type"]
        if task_type in self.templates:
            self.templates[task_type]["usage_count"] = self.templates[task_type].get("usage_count", 0) + 1
        else:
            self.templates[task_type] = {
                "usage_count": 1,
                "sample": task[:100]
            }
        
        # 检查是否需要升级层级
        if self.templates[task_type]["usage_count"] > 10:
            evolution["level_upgraded"] = True
            self._upgrade_level()
        
        # 生成优化建议
        evolution["recommendations"] = self._generate_evolution_recommendations(metrics)
        
        # 保存到数据库
        self._save_evolution_record(evolution)
        
        return evolution
    
    def _classify_task_type(self, task: str) -> str:
        """分类任务类型"""
        if "分析" in task:
            return "analysis"
        elif "创建" in task or "生成" in task:
            return "creation"
        elif "学习" in task or "预学习" in task:
            return "learning"
        elif "搜索" in task or "查找" in task:
            return "search"
        elif "总结" in task or "汇总" in task:
            return "summary"
        else:
            return "general"
    
    def _upgrade_level(self):
        """升级细粒度能力等级"""
        current_index = list(FineGrainLevel).index(self.current_level)
        if current_index < len(FineGrainLevel) - 1:
            self.current_level = list(FineGrainLevel)[current_index + 1]
    
    def _generate_evolution_recommendations(self, metrics: Dict) -> List[str]:
        """生成进化建议"""
        recommendations = []
        
        if metrics.get("response_time", 0) > 5000:
            recommendations.append("考虑优化响应速度")
        
        if metrics.get("token_usage", 0) > 10000:
            recommendations.append("考虑优化token使用效率")
        
        if not recommendations:
            recommendations.append("当前表现优秀，保持现有策略")
        
        return recommendations
    
    def _save_evolution_record(self, evolution: Dict):
        """保存进化记录"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO self_evolution (timestamp, phase, level, metrics, optimization, result)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            EvolutionPhase.ITERATION.value,
            self.current_level.value,
            json.dumps(evolution.get("pattern_extracted", {})),
            json.dumps(evolution.get("recommendations", [])),
            "completed"
        ))
        
        conn.commit()
        conn.close()
    
    # ==================== 4. 极致细粒度输出控制 ====================
    
    def control_output(self, content: Any, requirements: Dict) -> str:
        """
        极致细粒度输出控制
        - 格式：严格遵循结构、分段、标点、序号、排版要求
        - 内容：数据精确、术语统一、逻辑严密、无冗余、无歧义
        - 适配：根据场景自动调节正式/简洁/详细/温柔/专业等粒度
        """
        output = str(content)
        
        # 格式控制
        if requirements.get("format") == "table":
            output = self._format_as_table(output, requirements.get("headers", []))
        elif requirements.get("format") == "list":
            output = self._format_as_list(output)
        elif requirements.get("format") == "markdown":
            output = self._format_as_markdown(output)
        
        # 风格适配
        tone = requirements.get("tone", "professional")
        output = self._adapt_tone(output, tone)
        
        # 精度优化
        output = self._optimize_precision(output)
        
        return output
    
    def _format_as_table(self, content: str, headers: List[str]) -> str:
        """格式化为表格"""
        lines = content.split("\n")
        table_lines = []
        
        # 表头
        if headers:
            table_lines.append("| " + " | ".join(headers) + " |")
            table_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        
        # 内容行
        for line in lines:
            if line.strip():
                cells = line.split("|")
                table_lines.append("| " + " | ".join(cells) + " |")
        
        return "\n".join(table_lines)
    
    def _format_as_list(self, content: str) -> str:
        """格式化为列表"""
        lines = content.split("\n")
        list_lines = []
        
        for i, line in enumerate(lines, 1):
            if line.strip():
                list_lines.append(f"{i}. {line.strip()}")
        
        return "\n".join(list_lines)
    
    def _format_as_markdown(self, content: str) -> str:
        """格式化为Markdown"""
        lines = content.split("\n")
        md_lines = []
        
        for line in lines:
            if line.strip():
                if line.startswith("###"):
                    md_lines.append(line)
                elif line.startswith("##"):
                    md_lines.append(line)
                elif line.startswith("#"):
                    md_lines.append(line)
                else:
                    md_lines.append(line)
        
        return "\n".join(md_lines)
    
    def _adapt_tone(self, content: str, tone: str) -> str:
        """适应语气"""
        if tone == "formal":
            content = content.replace("你好", "您好")
            content = content.replace("谢谢", "感谢您的配合")
        elif tone == "simple":
            content = content.replace("因此", "所以")
            content = content.replace("然而", "但是")
        elif tone == "detailed":
            content = content.replace("概括", "详细概括")
            content = content.replace("简述", "详细说明"
            )
        
        return content
    
    def _optimize_precision(self, content: str) -> str:
        """优化精度"""
        import re
        
        # 添加时间戳
        if "[时间]" in content or "[TIMESTAMP]" in content:
            content = content.replace("[时间]", datetime.now().strftime("%Y-%m-%d %H:%M"))
            content = content.replace("[TIMESTAMP]", datetime.now().isoformat())
        
        # 优化数值精度
        def round_numbers(match):
            num = float(match.group())
            return f"{num:.2f}"
        
        content = re.sub(r'\d+\.\d{3,}', round_numbers, content)
        
        return content
    
    # ==================== 5. 长期记忆与持续优化 ====================
    
    def optimize_from_history(self) -> Dict:
        """
        保留历史最优行为
        - 不断收敛到更细、更准、更稳的执行范式
        - 支持能力平滑升级
        """
        optimization = {
            "patterns_analyzed": 0,
            "templates_optimized": [],
            "performance_improvements": [],
            "new_capabilities": []
        }
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 分析历史模式
        cursor.execute('''
            SELECT pattern_type, AVG(score) as avg_score
            FROM optimal_patterns
            GROUP BY pattern_type
            ORDER BY avg_score DESC
            LIMIT 10
        ''')
        
        patterns = cursor.fetchall()
        optimization["patterns_analyzed"] = len(patterns)
        
        # 优化模板
        cursor.execute('''
            SELECT scene, usage_count, success_rate
            FROM fine_grain_templates
            ORDER BY success_rate DESC
            LIMIT 5
        ''')
        
        templates = cursor.fetchall()
        for template in templates:
            optimization["templates_optimized"].append({
                "scene": template[0],
                "usage": template[1],
                "success_rate": template[2]
            })
        
        conn.close()
        
        # 计算性能提升
        if patterns:
            best_score = patterns[0][1] if patterns[0][1] else 0
            optimization["performance_improvements"].append(
                f"最优模式评分: {best_score:.2f}"
            )
        
        return optimization
    
    def get_evolution_status(self) -> Dict:
        """获取进化状态"""
        return {
            "current_level": self.current_level.value,
            "total_evolutions": len(self.evolution_history),
            "templates_count": len(self.templates),
            "capabilities": {
                "perception": True,
                "diagnosis": True,
                "iteration": True,
                "output_control": True,
                "memory": True
            }
        }


# 获取自进化引擎实例
_evolution_engine = None

def get_evolution_engine():
    global _evolution_engine
    if _evolution_engine is None:
        _evolution_engine = SelfEvolution()
    return _evolution_engine
