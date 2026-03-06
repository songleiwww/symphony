#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5个模型项目规划会议 - 选择最优功能开发
5-Model Project Planning Meeting - Select Best Features to Develop
"""

import sys
import json
from datetime import datetime
from pathlib import Path


# =============================================================================
# 修复Windows编码
# =============================================================================

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# =============================================================================
# 5个模型定义
# =============================================================================

FIVE_PLANNING_MODELS = [
    {
        "model_id": "MiniMax-M2.5",
        "alias": "MiniMax",
        "role": "战略架构师",
        "emoji": "🏗️",
        "specialty": "架构设计、长期规划"
    },
    {
        "model_id": "ark-code-latest",
        "alias": "Doubao Ark",
        "role": "技术实现专家",
        "emoji": "⚙️",
        "specialty": "代码实现、性能优化"
    },
    {
        "model_id": "deepseek-v3.2",
        "alias": "DeepSeek",
        "role": "产品体验官",
        "emoji": "💡",
        "specialty": "用户体验、产品设计"
    },
    {
        "model_id": "glm-4.7",
        "alias": "GLM 4.7",
        "role": "质量审计员",
        "emoji": "✅",
        "specialty": "质量保证、测试设计"
    },
    {
        "model_id": "kimi-k2.5",
        "alias": "Kimi K2.5",
        "role": "决策总指挥",
        "emoji": "🎬",
        "specialty": "决策整合、最终决策"
    }
]


# =============================================================================
# 候选功能列表
# =============================================================================

CANDIDATE_FEATURES = [
    {
        "id": "f1",
        "name": "统一错误处理系统",
        "description": "GlobalErrorHandler，统一错误处理和重试机制",
        "priority": 1,
        "effort": "中",
        "value": "高",
        "effort_days": 1,
        "category": "技术基础"
    },
    {
        "id": "f2",
        "name": "一键启动CLI工具",
        "description": "提供 `symphony start` 等命令，降低使用门槛",
        "priority": 1,
        "effort": "中",
        "value": "很高",
        "effort_days": 1,
        "category": "用户体验"
    },
    {
        "id": "f3",
        "name": "统一核心调度引擎",
        "description": "整合所有协议的SymphonyCore类",
        "priority": 2,
        "effort": "高",
        "value": "很高",
        "effort_days": 3,
        "category": "架构核心"
    },
    {
        "id": "f4",
        "name": "完整测试套件",
        "description": "pytest单元测试、集成测试，覆盖率80%+",
        "priority": 2,
        "effort": "中高",
        "value": "高",
        "effort_days": 2,
        "category": "质量保证"
    },
    {
        "id": "f5",
        "name": "配置管理系统",
        "description": "YAML/JSON配置，环境变量，热重载",
        "priority": 3,
        "effort": "低",
        "value": "中",
        "effort_days": 1,
        "category": "技术基础"
    },
    {
        "id": "f6",
        "name": "结构化日志系统",
        "description": "Python logging集成，JSON格式输出",
        "priority": 3,
        "effort": "低",
        "value": "中",
        "effort_days": 1,
        "category": "技术基础"
    },
    {
        "id": "f7",
        "name": "预设任务模板库",
        "description": "10+常见任务模板：研究、写作、编码等",
        "priority": 2,
        "effort": "中",
        "value": "高",
        "effort_days": 1,
        "category": "用户体验"
    },
    {
        "id": "f8",
        "name": "Web可视化界面",
        "description": "FastAPI+Vue，拖拽编排任务，实时监控",
        "priority": 4,
        "effort": "很高",
        "value": "很高",
        "effort_days": 5,
        "category": "用户体验"
    }
]


# =============================================================================
# 5个模型的观点
# =============================================================================

FIVE_MODEL_VIEWS = [
    {
        "model": "MiniMax",
        "role": "战略架构师",
        "emoji": "🏗️",
        "top_picks": ["f3", "f1", "f5"],
        "reasoning": """我是战略架构师MiniMax。

我的Top 3选择：
1. f3 - 统一核心调度引擎（最重要，这是所有功能的基础）
2. f1 - 统一错误处理系统（技术基础，必须优先）
3. f5 - 配置管理系统（让系统更灵活）

理由：
- 先建核心，再建周边
- 架构决定了系统能走多远
- 基础打好了，后面加功能才快"""
    },
    {
        "model": "Doubao Ark",
        "role": "技术实现专家",
        "emoji": "⚙️",
        "top_picks": ["f1", "f6", "f4"],
        "reasoning": """我是技术实现专家Doubao Ark。

我的Top 3选择：
1. f1 - 统一错误处理系统（现在错误处理太乱了）
2. f6 - 结构化日志系统（现在都是print，需要改进）
3. f4 - 完整测试套件（没有测试，改代码心慌）

理由：
- 先解决最痛的点
- 提高开发效率
- 让系统更健壮"""
    },
    {
        "model": "DeepSeek",
        "role": "产品体验官",
        "emoji": "💡",
        "top_picks": ["f2", "f7", "f8"],
        "reasoning": """我是产品体验官DeepSeek。

我的Top 3选择：
1. f2 - 一键启动CLI工具（用户门槛太高了）
2. f7 - 预设任务模板库（用户不知道怎么定义任务）
3. f8 - Web可视化界面（图形界面对非技术用户太重要了）

理由：
- 先让用户能用起来
- 用户体验决定产品成败
- 降低使用门槛"""
    },
    {
        "model": "GLM 4.7",
        "role": "质量审计员",
        "emoji": "✅",
        "top_picks": ["f4", "f1", "f6"],
        "reasoning": """我是质量审计员GLM 4.7。

我的Top 3选择：
1. f4 - 完整测试套件（质量是基础，没有测试一切免谈）
2. f1 - 统一错误处理系统（错误处理是质量的一部分）
3. f6 - 结构化日志系统（日志是排查问题的关键）

理由：
- 质量第一
- 没有测试，重构都不敢
- 日志是生产环境必须"""
    },
    {
        "model": "Kimi K2.5",
        "role": "决策总指挥",
        "emoji": "🎬",
        "final_decision": None,
        "reasoning": """我是决策总指挥Kimi K2.5。

整合大家的意见...
"""
    }
]


# =============================================================================
# 计算最优功能选择
# =============================================================================

def calculate_best_features() -> Dict:
    """计算最优功能"""
    
    # 统计投票
    votes = {}
    for feature in CANDIDATE_FEATURES:
        votes[feature['id']] = {
            "feature": feature,
            "votes": 0,
            "score": 0
        }
    
    # 收集投票
    for view in FIVE_MODEL_VIEWS[:4]:  # 前4个模型
        for i, feature_id in enumerate(view['top_picks']):
            votes[feature_id]['votes'] += 1
            votes[feature_id]['score'] += (3 - i)  # 第1选择3分，第2选择2分，第3选择1分
    
    # 计算总分
    for feature_id, data in votes.items():
        feature = data['feature']
        value_score = {
            "低": 1,
            "中": 2,
            "高": 3,
            "很高": 4
        }.get(feature['value'], 2)
        
        effort_score = {
            "低": 4,
            "中": 3,
            "中高": 2,
            "高": 1,
            "很高": 0
        }.get(feature['effort'], 2)
        
        # 总分 = 投票分 + 价值分 + (5/effort_day分
        total_score = data['score'] * 2 + value_score * 3 + effort_score
        data['total_score'] = total_score
    
    # 排序
    sorted_features = sorted(votes.values(), key=lambda x: x['total_score'], reverse=True)
    
    # 最终决策
    final_picks = [
        sorted_features[0]['feature'],
        sorted_features[1]['feature'],
        sorted_features[2]['feature']
    ]
    
    return {
        "all_votes": votes,
        "sorted_features": sorted_features,
        "final_picks": final_picks,
        "top_3": final_picks
    }


# =============================================================================
# 主程序
# =============================================================================

def main():
    """主程序"""
    print("=" * 80)
    print("🎯 5个模型项目规划会议")
    print("=" * 80)
    
    print(f"\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"参会模型: {len(FIVE_PLANNING_MODELS)}个")
    print(f"候选功能: {len(CANDIDATE_FEATURES)}个")
    
    # 1. 列出候选功能
    print("\n" + "=" * 80)
    print("📋 候选功能列表")
    print("=" * 80)
    
    for feature in CANDIDATE_FEATURES:
        print(f"\n{feature['id']}. {feature['name']}")
    print(f"   描述: {feature['description']}")
    print(f"   优先级: {feature['priority']} | 工作量: {feature['effort']} ({feature['effort_days']}天)")
    print(f"   价值: {feature['value']} | 分类: {feature['category']}")
    
    # 2. 各模型发言
    print("\n" + "=" * 80)
    print("💬 各模型观点")
    print("=" * 80)
    
    for view in FIVE_MODEL_VIEWS[:4]:
        print(f"\n{view['emoji']} {view['model']} ({view['role']}):")
        print(f"\n{view['reasoning']}")
        print(f"\n---")
    
    # 3. 计算最优功能
    print("\n" + "=" * 80)
    print("🏆 最优功能计算")
    print("=" * 80)
    
    result = calculate_best_features()
    
    print("\n📊 投票统计:")
    for feature in result['sorted_features'][:5]:
        f = feature['feature']
        print(f"\n{f['id']}. {f['name']}")
        print(f"   投票: {feature['votes']}票 | 总分: {feature.get('total_score', 0):.1f}")
    
    # 4. 最终决策
    print("\n" + "=" * 80)
    print("🎬 决策总指挥最终决策")
    print("=" * 80)
    
    print("\n🎯 最优3个功能（立即开发）:")
    for i, feature in enumerate(result['top_3'], 1):
        print(f"\n{i}. {feature['name']}")
        print(f"   描述: {feature['description']}")
        print(f"   工作量: {feature['effort']} ({feature['effort_days']}天)")
        print(f"   分类: {feature['category']}")
    
    # 5. 保存记录
    print("\n" + "=" * 80)
    print("💾 保存会议记录")
    print("=" * 80)
    
    meeting_record = {
        "meeting_time": datetime.now().isoformat(),
        "models": FIVE_PLANNING_MODELS,
        "candidate_features": CANDIDATE_FEATURES,
        "model_views": FIVE_MODEL_VIEWS[:4],
        "calculation_result": result,
        "final_top_3": result['top_3']
    }
    
    output_file = Path("5_model_planning_meeting.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(meeting_record, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 会议记录已保存: {output_file}")
    
    print("\n" + "=" * 80)
    print("会议结束")
    print("=" * 80)
    print("\n品牌标语: 智韵交响，共创华章")


if __name__ == "__main__":
    main()
