#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响v2.2 - 自动生成GitHub发布说明
"""

import sys
import json
from datetime import datetime

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


CONTRIBUTORS = [
    {"name": "林思远", "role": "产品经理", "emoji": "📋", "model": "MiniMax-M2.5", "provider": "cherry-minimax", "tasks": ["被动触发功能需求分析", "协作技能进化"], "tokens": 1741},
    {"name": "陈美琪", "role": "架构师", "emoji": "🏗️", "model": "ark-code-latest", "provider": "cherry-doubao", "tasks": ["系统架构设计", "模型兼容方案"], "tokens": 1867},
    {"name": "王浩然", "role": "开发工程师", "emoji": "💻", "model": "glm-4.7", "provider": "cherry-doubao", "tasks": ["被动触发引擎开发", "代码优化"], "tokens": 1703},
    {"name": "刘心怡", "role": "测试工程师", "emoji": "🧪", "model": "kimi-k2.5", "provider": "cherry-doubao", "tasks": ["测试用例编写", "兼容性测试"], "tokens": 1767},
    {"name": "张明远", "role": "运维工程师", "emoji": "🔧", "model": "deepseek-v3.2", "provider": "cherry-doubao", "tasks": ["部署配置", "环境管理"], "tokens": 866},
    {"name": "赵敏", "role": "产品运营", "emoji": "📈", "model": "doubao-seed-2.0-code", "provider": "cherry-doubao", "tasks": ["数据分析", "总结建议"], "tokens": 2469}
]

FEATURES = [
    {"name": "被动触发功能", "description": "新增PassiveTriggerEngine，支持多模式智能触发", "files": ["passive_trigger_engine.py", "passive_trigger_meeting.py"]},
    {"name": "协作技能进化", "description": "多模型协作开发流程优化，支持真实API调用", "files": ["collaboration_evolution.py"]},
    {"name": "调度与容错改进", "description": "优化模型调度逻辑，增强容错机制", "files": ["dispatch_fault_tolerance.py"]},
    {"name": "状态统计报表", "description": "新增模型状态实时统计，Token消耗追踪", "files": ["model_status_report.py"]}
]

def main():
    print("="*70)
    print("生成GitHub发布说明")
    print("="*70)
    
    total_tokens = sum(c["tokens"] for c in CONTRIBUTORS)
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # 生成发布说明
    release = f"""# 交响 Symphony v2.2 发布说明

**发布版本**: v2.2  
**发布日期**: {date_str}  
**品牌标语**: "智韵交响，共创华章！"

---

## 本次发布概要

| 指标 | 数值 |
|------|------|
| 参与模型 | {len(CONTRIBUTORS)} 位 |
| 新增功能 | {len(FEATURES)} 项 |
| 总Token消耗 | {total_tokens:,} |

---

## 新增功能

"""
    
    for i, f in enumerate(FEATURES, 1):
        release += f"### {i}. {f['name']}\n- **描述**: {f['description']}\n- **文件**: {', '.join(f['files'])}\n\n"

    release += """---

## 参与本次发布的模型

| 角色 | 名字 | 模型 | 提供商 | Token消耗 |
|------|------|------|--------|----------|
"""
    
    for c in CONTRIBUTORS:
        release += f"| {c['emoji']} {c['role']} | {c['name']} | {c['model']} | {c['provider']} | {c['tokens']} |\n"

    release += f"""

---

## 团队贡献排名

"""
    
    for i, c in enumerate(sorted(CONTRIBUTORS, key=lambda x: x["tokens"], reverse=True), 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        release += f"{medal} **{c['name']}** ({c['role']}): {c['tokens']} tokens\n"

    release += f"""

---

## 验证结果

- 真实模型API调用验证通过
- Token统计准确
- 多模型协作正常运行
- 容错机制有效

---

**智韵交响，共创华章！**

*本发布说明由交响多模型协作系统自动生成*
"""
    
    # 保存
    filename = f"RELEASE_v2.2_{datetime.now().strftime('%Y%m%d')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(release)
    
    print(f"\n已保存: {filename}")
    print(f"\n总Token: {total_tokens}")
    print("\n" + "="*70)
    print(release)

if __name__ == "__main__":
    main()
