#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境智能互补组合引擎
利用各引擎模型特长，弥补自身缺陷
"""
import os
import sys
from typing import Dict, List, Optional
from datetime import datetime

KERNEL_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KERNEL_PATH)

from combo_skill import get_combo_engine
from data_takeover import get_takeover
from flow_executor import get_flow_executor


class ModelProfile:
    """模型能力画像"""
    
    # 模型特长定义
    PROFILES = {
        'ark-code-latest': {
            'name': 'Ark Code',
            'strengths': ['代码生成', '逻辑推理', '结构化输出'],
            'weaknesses': ['创意写作', '情感表达'],
            'best_for': ['code', 'analysis', 'logic']
        },
        'deepseek-v3.2': {
            'name': 'DeepSeek V3',
            'strengths': ['中文理解', '知识广博', '创意写作'],
            'weaknesses': ['代码调试', '长文本'],
            'best_for': ['creative', 'knowledge', 'discuss']
        },
        'doubao-seed-2.0-code': {
            'name': 'Doubao Code',
            'strengths': ['代码理解', '技术文档', '编程问答'],
            'weaknesses': ['创意文案', '诗歌'],
            'best_for': ['code', 'tech', 'document']
        },
        'doubao-seed-2.0-lite': {
            'name': 'Doubao Lite',
            'strengths': ['快速响应', '简洁回答', '日常对话'],
            'weaknesses': ['复杂推理', '专业内容'],
            'best_for': ['quick', 'simple', 'chat']
        }
    }
    
    @classmethod
    def get_profile(cls, model: str) -> Dict:
        return cls.PROFILES.get(model, {
            'name': model,
            'strengths': ['通用'],
            'weaknesses': [],
            'best_for': ['general']
        })


class ComplementaryCombiner:
    """智能互补组合器"""
    
    def __init__(self):
        self.combo_engine = get_combo_engine()
        self.takeover = get_takeover()
        self.flow = get_flow_executor()
        self.profile = ModelProfile()
        
        # 互补策略
        self.strategies = {
            'code_plus_creative': self._code_plus_creative,
            'fast_plus_deep': self._fast_plus_deep,
            'multi_perspective': self._multi_perspective
        }
    
    def _code_plus_creative(self, task: Dict) -> List[Dict]:
        """代码+创意互补: 弥补代码模型创意不足"""
        return [
            {'role_id': 'role-1', 'messages': task['messages'], 'strategy': 'code_main'},
            {'role_id': 'role-10', 'messages': task['messages'], 'strategy': 'creative_backup'}
        ]
    
    def _fast_plus_deep(self, task: Dict) -> List[Dict]:
        """快速+深度互补: 弥补快速模型深度不足"""
        return [
            {'role_id': 'role-1', 'messages': task['messages'], 'strategy': 'fast_first'},
            {'role_id': 'role-55', 'messages': task['messages'], 'strategy': 'deep_expand'}
        ]
    
    def _multi_perspective(self, task: Dict) -> List[Dict]:
        """多视角互补: 弥补单一视角局限"""
        return [
            {'role_id': 'role-1', 'messages': task['messages'], 'strategy': 'perspective_tech'},
            {'role_id': 'role-10', 'messages': task['messages'], 'strategy': 'perspective_creative'},
            {'role_id': 'role-55', 'messages': task['messages'], 'strategy': 'perspective_practical'}
        ]
    
    def analyze_task(self, task: Dict) -> str:
        """分析任务类型，选择互补策略"""
        content = str(task.get('messages', [])).lower()
        
        if any(w in content for w in ['代码', '编程', 'function', 'def ', 'class ']):
            return 'code_plus_creative'
        elif any(w in content for w in ['快速', '简单', '什么是']):
            return 'fast_plus_deep'
        else:
            return 'multi_perspective'
    
    def complementary_execute(self, user_openid: str, task: Dict) -> Dict:
        """执行互补组合"""
        print()
        print('=' * 60)
        print('序境智能互补组合引擎')
        print('=' * 60)
        
        # 数据接管
        self.takeover.takeover_user_data(user_openid, {
            'mode': 'complementary',
            'task_type': self.analyze_task(task),
            'timestamp': datetime.now().isoformat()
        }, {'source': 'complementary'})
        
        # 分析任务
        strategy_name = self.analyze_task(task)
        print('  策略: ' + strategy_name)
        
        # 获取互补任务
        strategy_func = self.strategies.get(strategy_name, self.strategies['multi_perspective'])
        tasks = strategy_func(task)
        
        print('  模型数: ' + str(len(tasks)))
        
        # 执行
        result = self.combo_engine.execute(tasks, mode='parallel')
        
        # 分析结果
        analysis = self._analyze_complementary(result, strategy_name)
        
        return {
            'status': 'ok',
            'strategy': strategy_name,
            'tasks': len(tasks),
            'tokens': result['total_tokens'],
            'analysis': analysis
        }
    
    def _analyze_complementary(self, result: Dict, strategy: str) -> Dict:
        """分析互补效果"""
        individual = result.get('individual_results', [])
        
        strengths_used = []
        weaknesses_covered = []
        
        for r in individual:
            model = r.get('model', '')
            profile = self.profile.get_profile(model)
            strengths_used.extend(profile.get('strengths', []))
        
        return {
            'strengths': list(set(strengths_used)),
            'covered_weaknesses': list(set(weaknesses_covered))
        }


# 全局实例
_complementary = None


def get_complementary() -> ComplementaryCombiner:
    global _complementary
    if _complementary is None:
        _complementary = ComplementaryCombiner()
    return _complementary
