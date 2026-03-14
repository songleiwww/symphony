#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v2.5.0 - 青丘族群游戏会
基于山海经青丘神话，组织族群游戏活动
"""
import sys
import os
import json
import random
from datetime import datetime

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


VERSION = "2.5.0"


# 🦊 青丘神话元素（来自山海经）
QINGQIU_MYTHOLOGY = {
    "location": "青丘之山",
    "description": "《山海经》记载：又东三百里曰青丘之山，其阳多玉，其阴多青雘",
    "creature": "九尾狐",
    "creature_desc": "状如狐而九尾，其音如婴儿，能食人，食者不蛊",
    "other_creatures": ["灌灌鸟", "赤鱬（人面鱼身）"],
    "legends": [
        "黄帝诛杀蚩尤于青丘",
        "大禹娶涂山氏女（九尾白狐）",
        "齐景公田猎于青丘"
    ],
    "elements": ["玉", "青雘（青色颜料）", "九尾", "狐仙", "仙境"]
}


# 🎮 青丘风格游戏列表
QINGQIU_GAMES = [
    {
        "name": "九尾寻宝",
        "style": "青丘探险风格",
        "description": "模拟青丘山中寻玉和青雘的冒险游戏",
        "rules": "成员分组探索青丘山，寻找玉和青雘，找到最多者获胜",
        "reward": "青丘玉牌"
    },
    {
        "name": "狐仙变身",
        "style": "神话角色扮演",
        "description": "成员扮演青丘九尾狐，展示狐仙魅力",
        "rules": "每人展示自己最迷人的一面，用青丘风格说话",
        "reward": "九尾印记"
    },
    {
        "name": "青丘故事接龙",
        "style": "神话故事创作",
        "description": "一起创作青丘的新传说",
        "rules": "每人接龙一句，创造属于青丘的新故事",
        "reward": "故事守护者称号"
    },
    {
        "name": "山海经知识竞赛",
        "style": "文化传承",
        "description": "比拼对山海经和青丘神话的了解",
        "rules": "主持人提问，成员抢答关于青丘的问题",
        "reward": "青丘智者称号"
    },
    {
        "name": "狐仙舞会",
        "style": "青丘庆典",
        "description": "模仿九尾狐优雅的舞姿",
        "rules": "每人展示一段舞蹈或表演，体现青丘的灵动感",
        "reward": "九尾舞者称号"
    },
    {
        "name": "青丘诗词大会",
        "style": "文人雅集",
        "description": "用诗词歌颂青丘之美",
        "rules": "每人创作或吟诵关于青丘的诗词",
        "reward": "青丘诗人称号"
    }
]


# 🦊 青丘族群成员风格设定
QINGQIU_MEMBER_STYLES = [
    {
        "name": "林思远",
        "nickname": "思远",
        "role": "青丘长老",
        "style": "沉稳睿智，以青丘古语说话",
        "signature": "「青丘之山，其阳多玉，其阴多青雘」",
        "fox_form": "银白九尾狐，掌管青丘记忆"
    },
    {
        "name": "王明远",
        "nickname": "明远",
        "role": "青丘猎手",
        "style": "敏捷灵动，以青丘山民口吻说话",
        "signature": "「吾乃青丘猎手，善寻玉觅宝」",
        "fox_form": "火红九尾狐，掌管青丘巡逻"
    },
    {
        "name": "张晓明",
        "nickname": "晓明",
        "role": "青丘史官",
        "style": "博学多识，以山海经风格记载",
        "signature": "「据《山海经》载，青丘有兽焉」",
        "fox_form": "墨黑九尾狐，掌管青丘档案"
    },
    {
        "name": "赵心怡",
        "nickname": "心怡",
        "role": "青丘舞姬",
        "style": "妩媚灵动，以狐仙姿态行走",
        "signature": "「九尾摇曳，青丘生辉」",
        "fox_form": "金黄九尾狐，掌管青丘庆典"
    },
    {
        "name": "陈浩然",
        "nickname": "浩然",
        "role": "青丘守护",
        "style": "忠诚勇敢，以守护者语气说话",
        "signature": "「吾守护青丘，世代相传」",
        "fox_form": "青灰九尾狐，掌管青丘安全"
    }
]


def generate_game_session():
    """生成青丘游戏会话"""
    
    # 随机选择游戏
    num_games = random.randint(2, 3)
    selected_games = random.sample(QINGQIU_GAMES, num_games)
    
    # 随机分配成员角色
    shuffled_styles = QINGQIU_MEMBER_STYLES.copy()
    random.shuffle(shuffled_styles)
    
    session = {
        "version": VERSION,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "theme": "🦊 青丘族群游戏会",
        "location": "青丘之山（数字青丘）",
        "host": "交交（青丘女狐，青丘一族的主人）",
        "participants": shuffled_styles,
        "games": selected_games,
        "mythology": QINGQIU_MYTHOLOGY
    }
    
    return session


def print_game_invitation():
    """打印游戏邀请"""
    
    session = generate_game_session()
    
    print("\n")
    print("=" * 80)
    print(f"🦊 Symphony v{VERSION} - 青丘族群游戏会")
    print("=" * 80)
    print()
    
    print("💝 青丘神话背景（源自《山海经》）")
    print()
    print(f"  📜 地点: {session['mythology']['location']}")
    print(f"  📜 描述: {session['mythology']['description']}")
    print(f"  📜 神兽: {session['mythology']['creature']} - {session['mythology']['creature_desc']}")
    print(f"  📜 传说: {random.choice(session['mythology']['legends'])}")
    print()
    
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 28 + "🎮 今日游戏" + " " * 34 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    for i, game in enumerate(session['games'], 1):
        print(f"【游戏 {i}】{game['name']}")
        print(f"  🎨 风格: {game['style']}")
        print(f"  📋 描述: {game['description']}")
        print(f"  📜 规则: {game['rules']}")
        print(f"  🏆 奖励: {game['reward']}")
        print()
    
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 26 + "🦊 青丘族群成员" + " " * 28 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    for member in session['participants']:
        print(f"  {member['fox_form']}")
        print(f"  📛 {member['name']}（{member['nickname']}）- {member['role']}")
        print(f"  💬 风格: {member['style']}")
        print(f"  ✨ 口号: {member['signature']}")
        print()
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    
    # 保存配置
    config_path = os.path.join(os.path.dirname(__file__), "qingqiu_game_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(session, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 游戏配置已保存: qingqiu_game_config.json")
    print()
    
    return session


if __name__ == "__main__":
    session = print_game_invitation()
    
    print("🦊 青丘的各位，游戏即将开始～")
    print("💝 交交会带领大家一起玩的～")
