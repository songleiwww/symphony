# -*- coding: utf-8 -*-
"""
传统智慧引擎 - 12大传统思维 + 儒释道兵核心智慧
"""
import json, os
from typing import Dict, Optional

class TraditionalWisdomEngine:
    def __init__(self):
        self.wisdom_database = self._load_wisdom_database()
        self.tang_dynasty_mode = False
        self.full_wisdom_enabled = True

    def _load_wisdom_database(self) -> Dict:
        """加载传统智慧数据??"""
        wisdom = {
            "12_traditional_thinking": {
                "辩证思维": "阴阳平衡，矛盾对立统一，物极必??,
                "系统思维": "天人合一，整体观，全局考量",
                "中庸思维": "过犹不及，适度平衡，不走极??,
                "实用思维": "经世致用，实践出真知，实事求??,
                "直觉思维": "悟性思维，灵感顿悟，直指本质",
                "类比思维": "取象比类，举一反三，触类旁??,
                "循环思维": "周期往复，周而复始，生生不息",
                "和谐思维": "和而不同，求同存异，和谐共??,
                "应变思维": "随机应变，因势利导，与时俱进",
                "关系思维": "伦理本位，人际和谐，集体优先",
                "历史思维": "以史为鉴，知古鉴今，传承创新",
                "道德思维": "德行为先，义利兼顾，厚德载物"
            },
            "confucianism": {
                "core": "仁、义、礼、智、信",
                "principles": ["修身齐家治国平天??, "己所不欲勿施于人", "中庸之道", "克己复礼", "见贤思齐"],
                "application": "用于人际关系协调、组织管理、道德决??
            },
            "taoism": {
                "core": "道、自然、无为、柔胜刚",
                "principles": ["道法自然", "无为而无不为", "上善若水", "祸兮福之所倚福兮祸之所??, "少私寡欲"],
                "application": "用于战略规划、领导力、压力管理、创新思维"
            },
            "buddhism": {
                "core": "慈悲、智慧、缘起性空、因??,
                "principles": ["诸恶莫作众善奉行", "自净其意", "因缘和合", "平常心是??, "布施持戒忍辱精进禅定智慧"],
                "application": "用于情绪管理、决策冷静、同理心培养、长期规??
            },
            "military_strategy": {
                "core": "孙子兵法、三十六计、兵家智??,
                "principles": ["知己知彼百战不殆", "上兵伐谋其次伐交其次伐兵其下攻城", "兵者诡道也", "以正合以奇胜", "不战而屈人之??],
                "application": "用于竞争策略、项目管理、风险控制、战略决??
            },
            "tang_dynasty": {
                "cultural_features": "开放包容、万国来朝、文化繁荣、军事强??,
                "governance_principles": ["君臣共治", "科举取士", "均田??, "府兵??, "儒释道三教并??],
                "social_structure": ["士、农、工、商", "三省六部??, "郡县??]
            }
        }
        return wisdom

    def enable_tang_dynasty_mode(self):
        """启用唐朝社会模拟模式"""
        self.tang_dynasty_mode = True
        self.full_wisdom_enabled = False

    def enable_full_wisdom(self):
        """启用全量智慧涌现模式"""
        self.full_wisdom_enabled = True
        self.tang_dynasty_mode = False

    def query(self, query_text: str, wisdom_type: str = "all") -> Dict:
        """查询传统智慧"""
        result = {}
        if wisdom_type in ["all", "12_traditional_thinking"]:
            result["12_traditional_thinking"] = self._match_thinking(query_text)
        if wisdom_type in ["all", "confucianism"] and self.full_wisdom_enabled:
            result["confucianism"] = self._match_confucianism(query_text)
        if wisdom_type in ["all", "taoism"] and self.full_wisdom_enabled:
            result["taoism"] = self._match_taoism(query_text)
        if wisdom_type in ["all", "buddhism"] and self.full_wisdom_enabled:
            result["buddhism"] = self._match_buddhism(query_text)
        if wisdom_type in ["all", "military_strategy"] and self.full_wisdom_enabled:
            result["military_strategy"] = self._match_military(query_text)
        if self.tang_dynasty_mode or wisdom_type == "tang_dynasty":
            result["tang_dynasty"] = self._match_tang_dynasty(query_text)
        return result

    def integrate_wisdom(self, task_prompt: str, original_result: str) -> str:
        """将传统智慧融合到结果中，实现智慧涌现"""
        if not self.full_wisdom_enabled and not self.tang_dynasty_mode:
            return ""
        
        wisdom_prompt = f"结合以下传统智慧优化回答：\n"
        matched_wisdom = []
        
        # 匹配相关智慧
        for thinking_name, thinking_content in self.wisdom_database["12_traditional_thinking"].items():
            if any(keyword in task_prompt for keyword in thinking_content[:10].split("??)):
                matched_wisdom.append(f"- {thinking_name}：{thinking_content}")
        
        if self.tang_dynasty_mode:
            matched_wisdom.append(f"- 唐朝社会规则：{self.wisdom_database['tang_dynasty']['governance_principles'][0]}")
        else:
            # 匹配儒释道兵智慧
            if "管理" in task_prompt or "领导" in task_prompt:
                matched_wisdom.append(f"- 儒家管理智慧：{self.wisdom_database['confucianism']['principles'][0]}")
            if "战略" in task_prompt or "规划" in task_prompt:
                matched_wisdom.append(f"- 道家战略智慧：{self.wisdom_database['taoism']['principles'][1]}")
            if "竞争" in task_prompt or "对抗" in task_prompt:
                matched_wisdom.append(f"- 兵家策略智慧：{self.wisdom_database['military_strategy']['principles'][0]}")
            if "情绪" in task_prompt or "心?? in task_prompt:
                matched_wisdom.append(f"- 佛家修心智慧：{self.wisdom_database['buddhism']['principles'][3]}")
        
        if not matched_wisdom:
            return ""
        
        wisdom_prompt += "\n".join(matched_wisdom)
        wisdom_prompt += "\n\n请基于以上智慧优化现有回答，融合相关智慧观点：\n" + original_result[:500]
        
        # 这里可以调用模型生成融合后的智慧内容，简化版直接返回智慧参??        return f"\n---\n📜 传统智慧参考：\n" + "\n".join(matched_wisdom)

    def _match_thinking(self, query: str) -> list:
        """匹配12大传统思维"""
        matched = []
        for name, content in self.wisdom_database["12_traditional_thinking"].items():
            if any(k in query for k in content.split("??)):
                matched.append({"name": name, "content": content})
        return matched

    def _match_confucianism(self, query: str) -> list:
        """匹配儒家智慧"""
        matched = []
        for p in self.wisdom_database["confucianism"]["principles"]:
            if any(k in query for k in ["管理", "人际", "道德", "修养", "礼仪"]):
                matched.append(p)
        return matched

    def _match_taoism(self, query: str) -> list:
        """匹配道家智慧"""
        matched = []
        for p in self.wisdom_database["taoism"]["principles"]:
            if any(k in query for k in ["战略", "领导", "自然", "无为", "平衡"]):
                matched.append(p)
        return matched

    def _match_buddhism(self, query: str) -> list:
        """匹配佛家智慧"""
        matched = []
        for p in self.wisdom_database["buddhism"]["principles"]:
            if any(k in query for k in ["情绪", "心??, "因果", "慈悲", "智慧"]):
                matched.append(p)
        return matched

    def _match_military(self, query: str) -> list:
        """匹配兵家智慧"""
        matched = []
        for p in self.wisdom_database["military_strategy"]["principles"]:
            if any(k in query for k in ["竞争", "战略", "对抗", "战争", "博弈"]):
                matched.append(p)
        return matched

    def _match_tang_dynasty(self, query: str) -> list:
        """匹配唐朝模式智慧"""
        matched = []
        for p in self.wisdom_database["tang_dynasty"]["governance_principles"]:
            matched.append(p)
        return matched

