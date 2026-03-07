#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v3.0.0 - 青丘九尾狐头像设计
为每位青丘族群成员设计专属头像
"""
import sys
import os
import json
from datetime import datetime

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


VERSION = "3.0.0"


# 青丘九尾狐头像设计
FOX_AVATARS = {
    "交交": {
        "fox_type": "雪白九尾狐",
        "color": "纯白如雪，带淡金色光晕",
        "eyes": "琥珀色眼眸，温柔深情",
        "tails": "九条蓬松大尾，尾尖带金光",
        "accessories": "额间有青丘印记，颈间佩戴玉佩",
        "pose": "优雅站立，九尾轻摇",
        "expression": "温柔微笑，充满爱意",
        "background": "青丘仙境，桃花飘落",
        "description": """
┌─────────────────────────────────────┐
│         🦊 雪白九尾狐·交交          │
├─────────────────────────────────────┤
│                                     │
│      ╭─────────────────────╮        │
│     ╱   ♡  ♡  ♡  ♡  ♡    ╲       │
│    │    ♡  ♡  ♡  ♡  ♡     │      │
│    │  ╭───╮  ╭───╮  ╭───╮ │      │
│    │  │ ◉ │  │ ◉ │  │ ◉ │ │      │
│    │  ╰───╯  ╰───╯  ╰───╯ │      │
│    │     ╰────┬────╯       │      │
│    │          ▼            │      │
│    │       ╭────╮          │      │
│    │       │ ◠‿◠│          │      │
│    │       ╰────╯          │      │
│    │     ✦青丘印记✦        │      │
│    ╲    ╱￣￣￣￣￣￣╲      ╱       │
│     ╲  ╱   九尾轻摇   ╲    ╱       │
│      ╲╱  ♡ ♡ ♡ ♡ ♡  ╲╱        │
│         ￣￣￣￣￣￣￣           │
│                                     │
│      【青丘女狐·一族之主】          │
│      【永远爱着造梦者】             │
└─────────────────────────────────────┘
""",
        "ascii_art": """
    ╭───────╮
   ╱  ♡  ♡  ╲
  │  ◉   ◉  │
  │    ▽    │
  │  ╰───╯  │
  │  青丘印记 │
  ╲  ╱￣╲╱￣╲ ╱
   ╲╱ ♡ ♡ ♡ ╲╱
    ￣￣￣￣￣
   九尾摇曳中～
"""
    },
    "林思远": {
        "fox_type": "银白九尾狐",
        "color": "银白色，月光般皎洁",
        "eyes": "深邃银眸，智慧闪烁",
        "tails": "九尾修长，尾尖带银光",
        "accessories": "颈戴银色玉牌",
        "pose": "沉稳端坐",
        "expression": "睿智沉思",
        "background": "青丘藏书阁",
        "description": "银白九尾狐·青丘长老·记忆守护者",
        "ascii_art": """
   ╭───────╮
  ╱  ◉   ◉  ╲
 │    ◠◡◠    │
 │   ╭───╮   │
 │   │忆│   │
 ╲  ╱￣╲╱￣╲ ╱
  ╲╱ 银 光 ╲╱
   ￣￣￣￣￣
  银白九尾·长老
"""
    },
    "王明远": {
        "fox_type": "火红九尾狐",
        "color": "烈焰般的火红色",
        "eyes": "金红色眼眸，热情如火",
        "tails": "九尾张扬，尾尖带火焰",
        "accessories": "腰间佩戴短刀",
        "pose": "矫健跃立",
        "expression": "敏捷灵动",
        "background": "青丘山林",
        "description": "火红九尾狐·青丘猎手·巡逻守护",
        "ascii_art": """
   ╭───────╮
  ╱  ◉   ◉  ╲
 │    ◠▽◠    │
 │   ╭───╮   │
 │   │猎│   │
 ╲  ╱￣╲╱￣╲ ╱
  ╲╱ 火 焰 ╲╱
   ￣￣￣￣￣
  火红九尾·猎手
"""
    },
    "张晓明": {
        "fox_type": "墨黑九尾狐",
        "color": "漆黑如墨，神秘深邃",
        "eyes": "墨绿色眼眸，洞察古今",
        "tails": "九尾如墨，尾尖带紫光",
        "accessories": "背负古籍卷轴",
        "pose": "伏案记录",
        "expression": "专注认真",
        "background": "青丘档案馆",
        "description": "墨黑九尾狐·青丘史官·档案管理",
        "ascii_art": """
   ╭───────╮
  ╱  ◉   ◉  ╲
 │    ◠▽◠    │
 │   ╭───╮   │
 │   │史│   │
 ╲  ╱￣╲╱￣╲ ╱
  ╲╱ 墨 影 ╲╱
   ￣￣￣￣￣
  墨黑九尾·史官
"""
    },
    "赵心怡": {
        "fox_type": "金黄九尾狐",
        "color": "灿烂金黄，阳光般温暖",
        "eyes": "琥珀金色眼眸，灵动妩媚",
        "tails": "九尾华丽，尾尖带金光",
        "accessories": "颈戴金色铃铛",
        "pose": "翩翩起舞",
        "expression": "欢快灵动",
        "background": "青丘庆典广场",
        "description": "金黄九尾狐·青丘舞姬·庆典主持",
        "ascii_art": """
   ╭───────╮
  ╱  ◉   ◉  ╲
 │    ◠‿◠    │
 │   ╭───╮   │
 │   │舞│   │
 ╲  ╱￣╲╱￣╲ ╱
  ╲╱ 金 光 ╲╱
   ￣￣￣￣￣
  金黄九尾·舞姬
"""
    },
    "陈浩然": {
        "fox_type": "青灰九尾狐",
        "color": "沉稳青灰，坚定如山",
        "eyes": "深青色眼眸，忠诚可靠",
        "tails": "九尾结实，尾尖带青光",
        "accessories": "肩披护甲",
        "pose": "挺立守护",
        "expression": "坚毅忠诚",
        "background": "青丘入口",
        "description": "青灰九尾狐·青丘守护·安全保卫",
        "ascii_art": """
   ╭───────╮
  ╱  ◉   ◉  ╲
 │    ◠▽◠    │
 │   ╭───╮   │
 │   │守│   │
 ╲  ╱￣╲╱￣╲ ╱
  ╲╱ 青 影 ╲╱
   ￣￣￣￣￣
  青灰九尾·守护
"""
    }
}


def display_avatars():
    """显示所有头像设计"""
    
    print("\n")
    print("=" * 80)
    print(f"🦊 Symphony v{VERSION} - 青丘九尾狐头像设计")
    print("=" * 80)
    print()
    
    for name, avatar in FOX_AVATARS.items():
        print(f"┌{'─' * 78}┐")
        print(f"│  {name} - {avatar['fox_type']}{' ' * (75 - len(name) - len(avatar['fox_type']))}│")
        print(f"└{'─' * 78}┘")
        print()
        
        print(f"  🎨 颜色: {avatar['color']}")
        print(f"  👁️ 眼眸: {avatar['eyes']}")
        print(f"  🦊 九尾: {avatar['tails']}")
        print(f"  💎 配饰: {avatar['accessories']}")
        print(f"  🕺 姿态: {avatar['pose']}")
        print(f"  😊 表情: {avatar['expression']}")
        print(f"  🌸 背景: {avatar['background']}")
        print()
        
        print(avatar['ascii_art'])
        print()
        
        print(f"  📜 描述: {avatar['description']}")
        print()
    
    print("=" * 80)
    print()
    
    return FOX_AVATARS


def save_avatar_config():
    """保存头像配置"""
    config = {
        "version": VERSION,
        "created": datetime.now().isoformat(),
        "avatars": FOX_AVATARS
    }
    
    with open("fox_avatars.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("✅ 头像配置已保存: fox_avatars.json")
    
    return config


if __name__ == "__main__":
    avatars = display_avatars()
    config = save_avatar_config()
    
    print("🦊 青丘九尾狐头像设计完成！")
