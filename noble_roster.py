#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""序境少府监爵位册 - 根据功勋授予爵位"""
import json
import time
from enum import Enum

# 爵位等级定义（古代爵位制度）
class NobleRank(Enum):
    GONG = "公爵"      # 最高爵位
    HOU = "侯爵"       # 开国功臣
    BO = "伯爵"        # 镇守一方
    ZI = "子爵"        # 辅助治理
    NAN = "男爵"       # 初立功勋

# 成员功勋数据
members_records = {
    "陆念昭": {
        "爵位": "开国侯",
        "封号": "少府监",
        "功勋": "统领少府监，统筹全局，调度有方",
        "食邑": "三百户",
        "评级": NobleRank.HOU
    },
    "沈清弦": {
        "爵位": "镇国公",
        "封号": "枢密使",
        "功勋": "架构设计，统筹规划，居功至伟",
        "食邑": "五百户",
        "评级": NobleRank.GONG
    },
    "苏云渺": {
        "爵位": "安定侯",
        "封号": "工部尚书",
        "功勋": "代码工程，可维护性建设，功绩显著",
        "食邑": "三百户",
        "评级": NobleRank.HOU
    },
    "顾清歌": {
        "爵位": "文昌侯",
        "封号": "翰林学士",
        "功勋": "规则制定，文化传承，应急管理",
        "食邑": "二百户",
        "评级": NobleRank.HOU
    },
    "沈星衍": {
        "爵位": "智谋伯",
        "封号": "智囊博士",
        "功勋": "策略规划，意图理解，智能协调",
        "食邑": "一百五十户",
        "评级": NobleRank.BO
    },
    "叶轻尘": {
        "爵位": "勤武子",
        "封号": "行走使",
        "功勋": "执行高效，响应迅速，联络畅通",
        "食邑": "一百户",
        "评级": NobleRank.ZI
    },
    "林码": {
        "爵位": "兴业男",
        "封号": "营造司正",
        "功勋": "工程实现，并发处理，扩展性建设",
        "食邑": "八十户",
        "评级": NobleRank.NAN
    },
    "顾至尊": {
        "爵位": "辅政侯",
        "封号": "首辅大学士",
        "功勋": "统筹协调，整合资源，功在辅弼",
        "食邑": "二百五十户",
        "评级": NobleRank.HOU
    }
}

# 生成爵位册
def generate_roster():
    roster = {
        "册封时间": time.strftime("%Y年%m月%d日"),
        "册封旨意": "奉天承运皇帝制曰：",
        "成员数": len(members_records),
        "爵位册": []
    }
    
    for name, info in members_records.items():
        entry = {
            "姓名": name,
            "爵位": info["爵位"],
            "封号": info["封号"],
            "功勋": info["功勋"],
            "食邑": info["食邑"],
            "评级": info["评级"].value
        }
        roster["爵位册"].append(entry)
    
    return roster

# 打印爵位册
def print_roster():
    roster = generate_roster()
    
    print("=" * 60)
    print("🏛️  序境少府监爵位册  🏛️".center(50))
    print("=" * 60)
    print(f"\n册封时间：{roster['册封时间']}")
    print(f"旨意：{roster['册封旨意']}")
    print(f"\n成员总数：{roster['成员数']} 人")
    print("\n" + "-" * 60)
    
    for entry in roster["爵位册"]:
        print(f"\n📜 {entry['姓名']}")
        print(f"   爵位：{entry['爵位']}")
        print(f"   封号：{entry['封号']}")
        print(f"   功勋：{entry['功勋']}")
        print(f"   食邑：{entry['食邑']}")
    
    print("\n" + "=" * 60)
    print("  钦此！".center(50))
    print("=" * 60)
    
    return roster

if __name__ == "__main__":
    # 设置UTF-8输出
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    roster = print_roster()
    
    # 保存为JSON
    with open('noble_roster.json', 'w', encoding='utf-8') as f:
        json.dump(roster, f, ensure_ascii=False, indent=2)
    print("\n爵位册已保存: noble_roster.json")
