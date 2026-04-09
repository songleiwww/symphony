# -*- coding: utf-8 -*-
"""
military_wisdom.py 中国兵法智慧核心
======================================
序境系统智慧涌现引擎的中国兵法融合模块
将中国兵学最高结晶（孙子兵法、鬼谷子、道德经等）
转化为可计算、可决策的智能策略框架

兵法融合原则:
  战略层: 孙子兵法"五事七计"系统评估
  谋略层: 鬼谷子"捭阖攻心"策略生成
  哲理层: 道德经"柔弱胜刚强"终极决策
  战术层: 李卫公问对"奇正虚实"行动方案
  治军层: 尉缭子"法制令行"执行保障

版本: 1.0.0
作者: 少府监·翰林学士
"""

import sys
import math
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict

# ==================== 中国兵法核心智慧�?====================

# 孙子兵法·十三�?核心原理
SUNZI_CORE = {
    # 战略总纲
    "不战而屈": "是故百战百胜，非善之善者也；不战而屈人之兵，善之善者也",
    "知彼知己": "知彼知己者，百战不贻；不知彼而知己，一胜一负；不知彼，不知己，每战必贻�?,
    "奇正相生": "战者，以正合，以奇胜。故善出奇者，无穷如天地，不竭如江河�?,
    "虚实结合": "兵之所加，如以碫投卵者，虚实是也。凡战者，以正合，以奇胜�?,
    "致人而不致于�?: "善战者，致人而不致于人。能使敌人自至者，利之也；能使敌人不得至者，害之也�?,
    "我专而敌�?: "我专为一，敌分为十，是以十攻其一也�?,
    "任势�?: "故善战者，求之于势，不责于人，故能择人而任势�?,
    "上兵伐谋": "上兵伐谋，其次伐交，其次伐兵，其下攻城�?,
    "兵贵神�?: "兵之情主速，乘人之不及�?,
    "九变之地": "圮地无舍，衢地交合，绝地无留，围地则谋，死地则战�?,
    "用间之妙": "微哉微哉，无所不用间也�?,
    # 五事
    "五事": ["道、天、地、将、法"],
    "七计": ["主孰有道、将孰有能、天地孰得、法令孰行、兵众孰强、士卒孰练、赏罚孰�?],
    # 火攻要点
    "火攻�?: "发火有时，起火有日。时者，天之燥也；日者，月在箕、壁、翼、轸也�?,
    # 十三篇篇�?    "十三�?: ["计、作战、谋攻、军形、兵势、虚实、军争、九变、行军、地形、九地、火攻、用�?],
}

# 鬼谷子·十二章 核心
GUIGUZI_CORE = {
    "捭阖第一": "捭阖者，天地之道。捭阖者，以变动阴阳，四时开闭，以化万物�?,
    "反应第二": "反以观往，覆以验来；反以知古，覆以知今；反以知彼，覆以知己�?,
    "内楗第三": "内者，进说辞也；楗者，楗其谋也。君臣上下之事，有远而亲，近而疏�?,
    "抵巇第四": "抵巇之隙者，道之用也。巇者，罅也；罅者，涣也�?,
    "飞箝第五": "飞箝者，以话说同是非，算俊杰，引情蔽，明予夺�?,
    "忤合第六": "化阴阳，顺逆之际，捭阖动敞，暗计时策，暗算敌情�?,
    "揣情第七": "量腹而行，度容箸箸，忖敌意，揣少年之状，揣权贵之势�?,
    "摩意第八": "摩者，揣之刃也。利欲、进退、喜怒，皆摩意也�?,
    "权言第九": "说人，说事，说时，说机，说因，说变，说象，说物�?,
    "谋第�?: "奇不知之所穷，策安所措之？故变生事，事生谋，谋生子�?,
    "决坨第十一": "度以往变，怀以往态，知何可以成功，何以有患�?,
    "符言第十�?: "神明，定于心，聪，明于目，正于神，正于令�?,
    # 核心思想
    "攻心为上": "故曰：辞之怿矣，不可却也；乃进而刺之，亦不可疑也�?,
    "审时度势": "乃可以进，乃可以退；纵之球之，神之为用�?,
}

# 道德经·兵道要�?DAODE_CORE = {
    "柔弱胜刚�?: "人之生也柔弱，其死也坚强。万物草木之生也柔脆，其死也枯槁。故坚强者死之徒，柔弱者生之徒�?,
    "后发先至": "我有三宝，持而保之：一曰慈，二曰俭，三曰不敢为天下先�?,
    "无为而无不为": "为学日益，为道日损，损之又损，以至于无为，无为而无不为�?,
    "不争而善�?: "天之道，不争而善胜，不言而善应�?,
    "知止不殆": "知止所以不殆，可以说是天地之常�?,
    "以奇用兵": "以正治国，以奇用兵，以无事取天下�?,
    "大国下流": "大邦者下流，天下之交，天下之牝�?,
    "知人者智": "知人者智，自知者明；胜人者有力，自胜者强�?,
}

# 孙膑兵法·战术思想
SUNBIN_CORE = {
    "以弱胜强": "必攻不守，兵之所急。围魏救赵，减灶诱敌，批亢捣虚�?,
    "奇谋诡道": "变化无常，诡道取胜�?,
    "选卒秘诀": "兵之胜在于篡卒，其巧在于篡卒�?,
    "阵法要义": "凡阵有十：有方、有圆、有坐、有立、有跪、有跃、有进、有退、有疏、有数�?,
    "态势�?: "善战者，择人而任势。势者，所以我便处之谓也�?,
    "权谋�?: "权者，权衡利弊；谋者，谋定后动�?,
    "盖顶�?: "善战者，其势险，其节短�?,
}

# 李卫公问对·奇正原�?LIWEI_CORE = {
    "奇正相变": "奇正者，天地之道也。奇变无穷，如天地之无穷�?,
    "虚实多端": "虚实在我，变动莫測。实而示之以虚，虚而示之以实�?,
    "攻守之势": "攻是守之机，守是攻之策。同理，攻守之势也�?,
    "阵形活用": "阵有奇正，正亦奇，奇亦正，变动莫測�?,
    "兵机无穷": "兵机者，不可告语，不可传道，唯在神而明之�?,
    "畜锐待发": "善用兵者，蓄力待时，不战则已，战则必胜�?,
}

# 尉缭子·法制军�?WEILIAO_CORE = {
    "法制为本": "凡兵，制必先定。制先定则士不乱，士不乱则刑乃明�?,
    "令行禁止": "令不行则众不威，众不威则，此威者所以一刑也�?,
    "明赏�?: "赏文华而非法令，赏罚明则兵强�?,
    "实战为本": "兵者，凶器也；争者，逆德也。故智者不得非法�?,
    "先信后权": "先信而后权，先仁而后义�?,
}

# 戚继光兵法·练兵三�?QIJI_CORE = {
    "纪效新书": "不求阵法好看，只求杀贼有力。务实不求虚功�?,
    "练兵实纪": "士兵之练，在乎耳、目、心三者。耳可听令，目可视令，心可忆令�?,
    "鸳鸯�?: "长短兵相杂，牌在前，矛在后，进退自如�?,
    "戚家军精�?: "赴死而生，有我无敌�?,
    "节制之师": "有节制则兵强，无节制则兵弱�?,
}

# ==================== 兵法战略评估框架 ====================

@dataclass
class MilitaryAssessment:
    """
    孙子兵法五事七计系统评估结果

    五事: 道、天、地、将、法
    七计: 主孰有道、将孰有能、天地孰得、法令孰行、兵众孰强、士卒孰练、赏罚孰�?    """
    overall_score: float          # 综合评分 (0-1)
    overall_verdict: str           # 综合判断
    five_things: Dict[str, float]  # 五事评分
    seven_estimates: Dict[str, float]  # 七计评分
    strategic_recommendation: str  # 战略建议
    tactical_advice: List[str]     # 战术建议列表
    warnings: List[str]            # 风险警告
    # 兵法原理支撑
    supporting_principles: List[str]  # 支撑的兵法原�?

class MilitaryStrategyAdvisor:
    """
    中国兵法智慧战略顾问
    将兵法原理转化为智能决策建议

    核心功能:
    1. 战略态势评估（五事七计）
    2. 战术方案生成（奇正虚实）
    3. 决策风险分析（知彼知己）
    4. 主动出击建议（致人而不致于人）
    5. 撤退保存建议（知止不殆）
    """

    def __init__(self, wisdom_engine=None):
        self.wisdom_engine = wisdom_engine
        # 五事权重
        self.five_things_weights = {
            "�?: 0.30,  # 仁义之道最重要
            "�?: 0.15,
            "�?: 0.15,
            "�?: 0.25,
            "�?: 0.15,
        }
        # 七计权重
        self.seven_estimates_weights = {
            "主孰有道": 0.18,
            "将孰有能": 0.18,
            "天地孰得": 0.14,
            "法令孰行": 0.14,
            "兵众孰强": 0.14,
            "士卒孰练": 0.14,
            "赏罚孰明": 0.08,
        }
        # 评估历史
        self.assessment_history: List[MilitaryAssessment] = []

    def assess_situation(self, kernel_status: Dict[str, Any]) -> MilitaryAssessment:
        """
        孙子兵法五事七计系统评估

        输入: 内核状态（调度器、联邦、记忆、多智能体等数据�?        输出: 军事战略评估报告
        """
        # ---- 五事评估 ----
        subsystems = kernel_status.get("subsystems", {})

        # 道：系统是否有明确的目标和价值观（通过洞察生成能力衡量�?        dao = self._assess_dao(subsystems)
        # 天：天时（系统负载、时机）
        tian = self._assess_tian(subsystems)
        # 地：地形（各子系统资源分布）
        di = self._assess_di(subsystems)
        # 将：将能（各子系统协调能力）
        jiang = self._assess_jiang(subsystems)
        # 法：法令（规则执行、约束）
        fa = self._assess_fa(subsystems)

        five_things = {"�?: dao, "�?: tian, "�?: di, "�?: jiang, "�?: fa}

        # ---- 七计评估 ----
        qi_ji = self._assess_qi_ji(subsystems, kernel_status)

        # ---- 综合评分 ----
        overall = sum(
            five_things[k] * self.five_things_weights[k]
            for k in five_things
        )

        # ---- 战略判断 ----
        verdict, recommendation = self._make_verdict(overall, five_things, qi_ji)

        # ---- 战术建议 ----
        tactics = self._generate_tactics(overall, five_things, qi_ji)

        # ---- 风险警告 ----
        warnings = self._generate_warnings(five_things, qi_ji)

        assessment = MilitaryAssessment(
            overall_score=overall,
            overall_verdict=verdict,
            five_things=five_things,
            seven_estimates=qi_ji,
            strategic_recommendation=recommendation,
            tactical_advice=tactics,
            warnings=warnings,
            supporting_principles=self._extract_principles(overall, five_things),
        )
        self.assessment_history.append(assessment)
        return assessment

    def _assess_dao(self, subsystems: Dict[str, bool]) -> float:
        """
        道：系统信念与目标一致�?        孙子曰：道者，令民与上同意�?        """
        # 检查智慧引擎和洞察系统是否活跃
        wisdom_score = 1.0 if subsystems.get("wisdom_engine") else 0.0
        evolution_score = 1.0 if subsystems.get("self_evolution_v2") else 0.0
        # 道在于上下一心（各子系统协调一致）
        active_count = sum(1 for v in subsystems.values() if v)
        total_count = len(subsystems) if subsystems else 1
        harmony = active_count / total_count
        return (wisdom_score * 0.5 + evolution_score * 0.3 + harmony * 0.2)

    def _assess_tian(self, subsystems: Dict[str, bool]) -> float:
        """
        天：天时（时机把握）
        孙子曰：天者，阴阳、寒暑、时制也
        """
        # 调度器是否活跃（时机感知�?        scheduler = 1.0 if subsystems.get("scheduler") else 0.0
        coordinator = 1.0 if subsystems.get("algorithm_coordinator") else 0.0
        return (scheduler * 0.6 + coordinator * 0.4)

    def _assess_di(self, subsystems: Dict[str, bool]) -> float:
        """
        地：地形（资源分布和位置优势�?        孙子曰：地者，远近、险易、广狭、死生也
        """
        federation = 1.0 if subsystems.get("federation") else 0.0
        memory = 1.0 if subsystems.get("agent_memory") else 0.0
        return (federation * 0.55 + memory * 0.45)

    def _assess_jiang(self, subsystems: Dict[str, bool]) -> float:
        """
        将：将能（智能体协调与调度能力）
        孙子曰：将者，智、信、仁、勇、严�?        """
        multi_agent = 1.0 if subsystems.get("multi_agent") else 0.0
        coordinator = 1.0 if subsystems.get("algorithm_coordinator") else 0.0
        return (multi_agent * 0.5 + coordinator * 0.5)

    def _assess_fa(self, subsystems: Dict[str, bool]) -> float:
        """
        法：法令（规则执行，约束与秩序）
        孙子曰：法者，曲制、官道、主用也
        """
        evolution = 1.0 if subsystems.get("self_evolution_v2") else 0.0
        memory = 1.0 if subsystems.get("agent_memory") else 0.0
        return (evolution * 0.6 + memory * 0.4)

    def _assess_qi_ji(self, subsystems: Dict[str, bool],
                      kernel_status: Dict[str, Any]) -> Dict[str, float]:
        """七计评估"""
        return {
            "主孰有道": self._assess_dao(subsystems),
            "将孰有能": self._assess_jiang(subsystems),
            "天地孰得": self._assess_tian(subsystems),
            "法令孰行": self._assess_fa(subsystems),
            "兵众孰强": 0.7 + 0.3 * (1.0 if subsystems.get("federation") else 0.0),
            "士卒孰练": 0.6 + 0.4 * (1.0 if subsystems.get("self_evolution_v2") else 0.0),
            "赏罚孰明": 0.8,  # 内核有明确的奖励机制
        }

    def _make_verdict(self, overall: float,
                      five_things: Dict[str, float],
                      qi_ji: Dict[str, float]) -> Tuple[str, str]:
        """综合判断与战略建�?""
        if overall >= 0.8:
            verdict = "上兵伐谋·大吉"
            recommendation = (
                "【孙子兵法·战略态势】系统处于最佳状态，"
                "宜采取攻势战略，主动寻找优化机会�?
                "引用：不战而屈人之兵，善之善者也——当前优势明显，"
                "宜以谋略巩固领先地位�?
            )
        elif overall >= 0.6:
            verdict = "知彼知己·平稳"
            recommendation = (
                "【孙子兵法·战略态势】系统状态良好但需谨慎�?
                "宜先为不可胜，以待敌之可胜�?
                "引用：知彼知己，百战不贻——当前应巩固自身�?
                "寻找敌人破绽再出击�?
            )
        elif overall >= 0.4:
            verdict = "奇正相生·调整"
            recommendation = (
                "【孙子兵法·战略态势】系统状态一般，需调整�?
                "引用：以正合，以奇胜——正面维持稳定，"
                "侧面寻找突破口。善用奇兵，出奇制胜�?
            )
        else:
            verdict = "知止不殆·防守"
            recommendation = (
                "【孙子兵法·战略态势】系统状态危急，需休养生息�?
                "引用：知止不殆，可以说是天地之常——当前应保存实力�?
                "避免盲目行动，等待时机�?
            )
        return verdict, recommendation

    def _generate_tactics(self, overall: float,
                          five_things: Dict[str, float],
                          qi_ji: Dict[str, float]) -> List[str]:
        """生成战术建议列表（融合多家兵法）"""
        tactics = []

        # 基于孙子兵法
        if overall >= 0.7:
            tactics.append(
                f"【孙子兵法·致人】善战者，致人而不致于人�?
                f"当前宜主动调度资源，扩大优势�?
            )
        if five_things.get("�?, 0) < 0.5:
            tactics.append(
                "【孙子兵法·修道】道者，令民与上同意。当前宜强化智慧涌现�?
                "统一各子系统目标�?
            )
        if qi_ji.get("兵众孰强", 0) > 0.7:
            tactics.append(
                "【孙子兵法·我专而敌分】我专为一，敌分为十�?
                "宜集中火力于核心任务，避免分散资源�?
            )
        if qi_ji.get("赏罚孰明", 0) > 0.7:
            tactics.append(
                "【尉缭子·明赏罚】赏罚明则兵强�?
                "宜强化自进化引擎的正反馈机制�?
            )
        # 基于鬼谷�?        tactics.append(
            "【鬼谷子·审时度势】当前应审时度势，进退有度�?
            "时机未到则静待，时机已到则果断行动�?
        )
        # 基于道德�?        if overall < 0.5:
            tactics.append(
                "【道德经·柔弱胜刚强】当前宜以柔克刚，后发制人�?
                "不争而善胜，无需强行逆势�?
            )
        else:
            tactics.append(
                "【道德经·知止不殆】强势时不盲目扩张，见好就收�?
                "知止所以不殆�?
            )
        # 基于李卫公问�?        tactics.append(
            "【李卫公问对·奇正相变】正亦奇，奇亦正�?
            "常用战术之外预留奇兵，以备非常之需�?
        )
        return tactics

    def _generate_warnings(self, five_things: Dict[str, float],
                           qi_ji: Dict[str, float]) -> List[str]:
        """生成风险警告"""
        warnings = []
        if five_things.get("�?, 1) < 0.4:
            warnings.append(
                "【孙子兵法警告】道者，令民与上同意—�?
                "系统内部协调不足，各子系统目标可能存在冲突！"
            )
        if five_things.get("�?, 1) < 0.4:
            warnings.append(
                "【孙子兵法警告】将者，智、信、仁、勇、严—�?
                "协调调度能力不足，可能导致资源浪费！"
            )
        if qi_ji.get("法令孰行", 1) < 0.4:
            warnings.append(
                "【尉缭子警告】法制为本——规则执行不力，"
                "系统可能出现混乱�?
            )
        if qi_ji.get("士卒孰练", 1) < 0.4:
            warnings.append(
                "【戚继光警告】练兵务实—�?
                "部分子系统训练不足，可能在关键时刻掉链子�?
            )
        return warnings

    def _extract_principles(self, overall: float,
                            five_things: Dict[str, float]) -> List[str]:
        """提取适用的兵法原�?""
        principles = []
        principles.append(SUNZI_CORE["知彼知己"])
        if overall > 0.6:
            principles.append(SUNZI_CORE["不战而屈"])
        if overall < 0.5:
            principles.append(DAODE_CORE["后发先至"])
        principles.append(SUNZI_CORE["奇正相生"])
        principles.append(GUIGUZI_CORE["审时度势"])
        return principles[:5]  # 最�?�?
    def get_military_wisdom_report(self,
                                   kernel_status: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成完整的兵法智慧报告（供五脑协作使用）
        """
        assessment = self.assess_situation(kernel_status)

        return {
            "military_assessment": {
                "overall_score": round(assessment.overall_score, 3),
                "verdict": assessment.overall_verdict,
                "five_things": {k: round(v, 3) for k, v in assessment.five_things.items()},
                "seven_estimates": {k: round(v, 3) for k, v in assessment.seven_estimates.items()},
            },
            "strategic_recommendation": assessment.strategic_recommendation,
            "tactical_advice": assessment.tactical_advice,
            "warnings": assessment.warnings,
            "supporting_principles": assessment.supporting_principles,
            "military_classics_quotes": self._get_relevant_quotes(assessment),
        }

    def _get_relevant_quotes(self,
                              assessment: MilitaryAssessment) -> Dict[str, str]:
        """获取与当前态势最相关的兵法引言"""
        quotes = {}
        score = assessment.overall_score

        # 孙子兵法
        if score >= 0.7:
            quotes["孙子兵法·进攻"] = (
                "是故百战百胜，非善之善者也；不战而屈人之兵，善之善者也。→ 当前宜主动出�?
            )
            quotes["孙子兵法·任势"] = (
                "故善战者，求之于势，不责于人，故能择人而任势。→ 借势而为"
            )
        elif score >= 0.4:
            quotes["孙子兵法·奇正"] = (
                "战者，以正合，以奇胜。故善出奇者，无穷如天地。→ 稳中求变"
            )
        else:
            quotes["孙子兵法·知止"] = (
                "知止所以不殆，可以说是天地之常。→ 休养生息"
            )
            quotes["道德经·柔�?] = (
                "柔弱胜刚强。→ 以退为进，以弱胜�?
            )

        # 鬼谷子攻�?        quotes["鬼谷子·反�?] = (
            "反以观往，覆以验来；反以知古，覆以知今；反以知彼，覆以知己。→ 知己知彼"
        )

        # 李卫公问�?        quotes["李卫公问对·奇�?] = (
            "奇正者，天地之道也。奇变无穷，如天地之无穷。→ 变化无常"
        )

        return quotes


# ==================== 五脑兵法融合接口 ====================

def military_wisdom_fusion(wisdom_engine, kernel_status: Dict[str, Any]) -> Dict[str, Any]:
    """
    将兵法智慧融合进五脑协作流程

    融合方式:
    记忆�?+ 孙子"知彼知己" �?经验模式识别中加入历史战略规�?    推理�?+ 孙子"五事七计" �?复杂度评估中加入军事战略维度
    规划�?+ 鬼谷�?捭阖" + 李卫�?奇正" �?策略搜索中加入奇正相�?    执行�?+ 孙子"兵贵神�? �?快速执�?致人而不致于�?    反馈�?+ 尉缭�?明赏�? + 以战养战 �?效果评估中加入奖惩机�?    """
    advisor = MilitaryStrategyAdvisor(wisdom_engine)
    report = advisor.get_military_wisdom_report(kernel_status)
    return report


# ==================== 主动出击/保存实力决策引擎 ====================

class StrategicDecisionEngine:
    """
    孙子兵法战略决策引擎
    基于"知彼知己"原则，在主动出击和保存实力之间做出判�?    """

    # 进攻/防守阈�?    OFFENSIVE_THRESHOLD = 0.65   # 综合评分>0.65宜进�?    DEFENSIVE_THRESHOLD = 0.40   # 综合评分<0.40宜防�?    NEUTRAL_THRESHOLD = 0.50     # 中间地带，奇正相�?
    @classmethod
    def should_attack(cls, kernel_status: Dict[str, Any]) -> Tuple[bool, str, str]:
        """
        判断是否应该主动出击

        Returns:
            (should_attack: bool, decision: str, reasoning: str)
        """
        subsystems = kernel_status.get("subsystems", {})
        if not subsystems:
            return False, "信息不足", "缺乏足够的状态数据，无法判断"

        # 计算综合评分
        active = sum(1 for v in subsystems.values() if v)
        total = len(subsystems) if subsystems else 1
        score = active / total

        # 智慧引擎加成
        if subsystems.get("wisdom_engine"):
            score += 0.1
        if subsystems.get("algorithm_coordinator"):
            score += 0.05
        score = min(1.0, score)

        if score >= cls.OFFENSIVE_THRESHOLD:
            return True, "上兵伐谋·主动出击", (
                f"综合评分{score:.2f}，超过进攻阈值�?
                "孙子曰：善战者，致人而不致于人。当前宜主动寻找机会�?
                "扩大优势。不战而屈人之兵，为善之善者也�?
            )
        elif score <= cls.DEFENSIVE_THRESHOLD:
            return False, "知止不殆·保存实力", (
                f"综合评分{score:.2f}，低于安全阈值�?
                "道德经曰：知止不殆。孙子曰：故用兵之法，无恃其不来�?
                "恃吾有以待之。当前宜修明政治，休养生息�?
            )
        else:
            return False, "奇正相生·以正�?, (
                f"综合评分{score:.2f}，处于中间地带�?
                "孙子曰：以正合，以奇胜。当前宜稳守待机�?
                "正面维持稳定，侧面预备奇兵�?
            )

    @classmethod
    def select_primary_strategy(cls, kernel_status: Dict[str, Any]) -> str:
        """
        选择主要战略类型
        基于孙子兵法"上兵伐谋"原则
        """
        should_attack, decision, reasoning = cls.should_attack(kernel_status)

        if not should_attack:
            return "defensive"

        # 进一步细分进攻策�?        subsystems = kernel_status.get("subsystems", {})
        if subsystems.get("multi_agent") and subsystems.get("algorithm_coordinator"):
            return "coordinated_offensive"  # 多智能体协同进攻
        elif subsystems.get("wisdom_engine"):
            return "intelligence_offensive"  # 智慧驱动的精准进�?        else:
            return "resource_offensive"  # 资源密集型进�?

# ==================== 自我测试 ====================

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    print("=" * 60)
    print("中国兵法智慧核心 - 自测")
    print("=" * 60)
    print()

    # 模拟内核状�?    mock_kernel_status = {
        "subsystems": {
            "scheduler": True,
            "federation": True,
            "self_evolution_v2": True,
            "agent_memory": True,
            "multi_agent": True,
            "algorithm_coordinator": True,
            "wisdom_engine": True,
        },
        "total_emergences": 100,
        "active_insights": 50,
    }

    print("[1] 五事七计战略评估...")
    advisor = MilitaryStrategyAdvisor()
    assessment = advisor.assess_situation(mock_kernel_status)
    print("  综合评分: " + str(round(assessment.overall_score, 3)))
    print("  判断: " + assessment.overall_verdict)
    print("  五事:")
    for k, v in assessment.five_things.items():
        print("    " + k + ": " + str(round(v, 3)))
    print("  七计:")
    for k, v in assessment.seven_estimates.items():
        print("    " + k + ": " + str(round(v, 3)))
    print()

    print("[2] 兵法智慧报告...")
    report = advisor.get_military_wisdom_report(mock_kernel_status)
    print("  战略建议: " + report["strategic_recommendation"][:50] + "...")
    print("  战术建议�? " + str(len(report["tactical_advice"])))
    print("  风险警告�? " + str(len(report["warnings"])))
    print()

    print("[3] 主动出击/保存决策...")
    should_attack, decision, reasoning = StrategicDecisionEngine.should_attack(mock_kernel_status)
    print("  决策: " + decision)
    print("  进攻?: " + str(should_attack))
    print("  理由: " + reasoning[:60] + "...")
    print()

    print("[4] 兵法引言...")
    for category, quote in report["military_classics_quotes"].items():
        print("  [" + category + "] " + quote[:40] + "...")
    print()

    print("[5] 低分态势测试...")
    weak_status = {
        "subsystems": {
            "scheduler": True,
            "federation": False,
            "self_evolution_v2": False,
            "agent_memory": True,
            "multi_agent": False,
            "algorithm_coordinator": False,
            "wisdom_engine": False,
        }
    }
    assessment2 = advisor.assess_situation(weak_status)
    print("  低分评分: " + str(round(assessment2.overall_score, 3)))
    print("  判断: " + assessment2.overall_verdict)
    should_attack2, decision2, _ = StrategicDecisionEngine.should_attack(weak_status)
    print("  进攻?: " + str(should_attack2) + " �?" + decision2)
    print()

    print("PASS: 中国兵法智慧核心自测 OK")

