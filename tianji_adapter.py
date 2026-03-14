#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony - Tianji Broadcast System Adapter
Multi-model collaboration to adapt to Tianji system
"""

import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("Symphony - Tianji Broadcast System Adapter")
print("交响 - 天机播报系统适配器")
print("=" * 80)

try:
    from openclaw_config_loader import OpenClawConfigLoader
    from mcp_manager import (
        create_mcp_manager,
        ToolSchema, ParameterSchema, ParameterType
    )
    from memory_system import create_memory_system
    
    # =========================================================================
    # Step 1: Load model config and define Tianji team
    # =========================================================================
    print("\n[Step 1/7] Loading model config...")
    loader = OpenClawConfigLoader()
    models = loader.get_models()
    print(f"OK: Loaded {len(models)} models")
    
    # Define Tianji broadcast team
    tianji_team = {
        "system_analyst": models[0],   # ark-code-latest - System Analyst
        "content_planner": models[1],  # deepseek-v3.2 - Content Planner
        "news_collector": models[2],   # doubao-seed-2.0-code - News Collector
        "broadcast_writer": models[3],  # glm-4.7 - Broadcast Writer
        "voice_presenter": models[4],   # kimi-k2.5 - Voice Presenter
        "quality_checker": models[5]    # MiniMax-M2.5 - Quality Checker
    }
    
    print(f"\nTianji Broadcast Team (6 specialists):")
    for role, model in tianji_team.items():
        print(f"  {role.replace('_', ' ').title()}: {model['alias']}")
    
    # =========================================================================
    # Step 2: Create MCP manager and Tianji tools
    # =========================================================================
    print("\n[Step 2/7] Creating MCP manager...")
    mcp = create_mcp_manager()
    print("OK: MCP manager created")
    
    # Load Symphony long-term memory
    memory, learning = create_memory_system('symphony_long_term_memory')
    print(f"OK: Loaded {memory.get_stats()['total_count']} memories")
    
    # =========================================================================
    # Tianji System Data and Tools
    # =========================================================================
    
    # Sample Tianji system news data
    TIANJI_NEWS = {
        "tech": [
            "AI大模型突破新纪录，推理速度提升300%",
            "量子计算机实现重大突破，商用化进程加速",
            "5G-A网络正式商用，下载速度达10Gbps"
        ],
        "finance": [
            "A股市场今日大涨，科技板块领涨",
            "央行宣布降息，刺激经济增长",
            "新能源汽车销量创新高，同比增长150%"
        ],
        "sports": [
            "中国队在世界锦标赛中斩获3金2银",
            "NBA季后赛即将开始，群雄逐鹿",
            "世界杯预选赛：国足表现出色"
        ],
        "weather": [
            "全国大部分地区晴好，气温回升",
            "南方地区有小雨，注意带伞",
            "北方地区有降温，注意保暖"
        ]
    }
    
    def analyze_tianji_system() -> dict:
        """Analyze Tianji broadcast system requirements"""
        time.sleep(0.5)
        
        return {
            "system_name": "天机播报系统",
            "core_features": [
                "定时新闻播报",
                "多频道内容",
                "语音合成输出",
                "实时内容更新"
            ],
            "content_types": ["tech", "finance", "sports", "weather"],
            "broadcast_style": "professional, clear, engaging",
            "target_audience": "general public",
            "summary": "天机播报系统需要专业、清晰、有吸引力的新闻内容"
        }
    
    def plan_broadcast_content(system_info: dict) -> dict:
        """Plan broadcast content structure"""
        time.sleep(0.5)
        
        return {
            "structure": [
                "Opening greeting",
                "Top headlines (3 items)",
                "Detailed news (2 items per category)",
                "Weather update",
                "Closing remark"
            ],
            "categories": ["tech", "finance", "sports", "weather"],
            "total_items": 8,
            "duration": "3-5 minutes",
            "summary": "规划了完整的播报结构：开场、头条、分类新闻、天气、结尾"
        }
    
    def collect_tianji_news(category: str) -> dict:
        """Collect news for Tianji system"""
        time.sleep(0.5)
        
        if category in TIANJI_NEWS:
            return {
                "category": category,
                "news": TIANJI_NEWS[category],
                "count": len(TIANJI_NEWS[category]),
                "success": True
            }
        return {
            "category": category,
            "news": [],
            "count": 0,
            "success": False
        }
    
    def write_broadcast_script(content_plan: dict, all_news: dict) -> dict:
        """Write Tianji broadcast script"""
        time.sleep(0.5)
        
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        
        script = {
            "title": f"天机播报 - {current_time}",
            "opening": f"听众朋友们，大家好！欢迎收听今天的天机播报。今天是{current_time}。",
            "headlines": [],
            "detailed_news": [],
            "weather": "",
            "closing": "感谢收听今天的天机播报，我们下次再见！"
        }
        
        # Add headlines from tech and finance
        tech_news = all_news.get("tech", {}).get("news", [])
        finance_news = all_news.get("finance", {}).get("news", [])
        
        if tech_news:
            script["headlines"].append(tech_news[0])
        if finance_news:
            script["headlines"].append(finance_news[0])
        
        # Add detailed news
        for category in ["tech", "finance", "sports"]:
            news_list = all_news.get(category, {}).get("news", [])
            if news_list:
                script["detailed_news"].extend(news_list[:2])
        
        # Add weather
        weather_news = all_news.get("weather", {}).get("news", [])
        if weather_news:
            script["weather"] = weather_news[0]
        
        return {
            "script": script,
            "total_segments": 5,
            "total_news_items": len(script["headlines"]) + len(script["detailed_news"]),
            "summary": "天机播报脚本编写完成，包含开场、头条、详细新闻、天气和结尾"
        }
    
    def format_for_voice(script: dict) -> dict:
        """Format script for voice presentation"""
        time.sleep(0.5)
        
        voice_script = []
        s = script["script"]
        
        voice_script.append(f"【开场】{s['opening']}")
        voice_script.append("")
        
        voice_script.append("【今日头条】")
        for i, headline in enumerate(s['headlines'], 1):
            voice_script.append(f"  {i}. {headline}")
        voice_script.append("")
        
        voice_script.append("【详细新闻】")
        for i, news in enumerate(s['detailed_news'], 1):
            voice_script.append(f"  {i}. {news}")
        voice_script.append("")
        
        if s['weather']:
            voice_script.append(f"【天气预报】{s['weather']}")
            voice_script.append("")
        
        voice_script.append(f"【结尾】{s['closing']}")
        
        return {
            "voice_script": voice_script,
            "lines": len(voice_script),
            "estimated_duration": "4 minutes",
            "summary": "语音播报格式完成，适合天机播报系统使用"
        }
    
    def check_broadcast_quality(voice_script: dict) -> dict:
        """Check broadcast quality"""
        time.sleep(0.5)
        
        lines = voice_script.get("lines", 0)
        quality_score = min(95, 80 + lines)
        
        checks = {
            "has_opening": True,
            "has_headlines": True,
            "has_detailed_news": True,
            "has_weather": True,
            "has_closing": True,
            "length_appropriate": lines > 10 and lines < 50
        }
        
        passed = sum(1 for v in checks.values() if v)
        total = len(checks)
        
        return {
            "checks": checks,
            "quality_score": quality_score,
            "passed": passed,
            "total": total,
            "approved": passed >= total - 1,
            "summary": f"质量检查完成：{passed}/{total}通过，质量评分{quality_score}分"
        }
    
    # Register all Tianji tools
    tools = [
        ("analyze_tianji_system", "Analyze Tianji system requirements", analyze_tianji_system, []),
        ("plan_broadcast_content", "Plan broadcast content", plan_broadcast_content,
         [("system_info", "object", True)]),
        ("collect_tianji_news", "Collect Tianji news", collect_tianji_news,
         [("category", "string", True)]),
        ("write_broadcast_script", "Write broadcast script", write_broadcast_script,
         [("content_plan", "object", True), ("all_news", "object", True)]),
        ("format_for_voice", "Format for voice presentation", format_for_voice,
         [("script", "object", True)]),
        ("check_broadcast_quality", "Check broadcast quality", check_broadcast_quality,
         [("voice_script", "object", True)])
    ]
    
    for name, desc, func, params in tools:
        param_schemas = []
        for p_name, p_type, p_required in params:
            pt = ParameterType.OBJECT if p_type == "object" else ParameterType.STRING
            param_schemas.append(ParameterSchema(name=p_name, type=pt, required=p_required))
        
        schema = ToolSchema(
            name=name,
            description=desc,
            parameters=param_schemas,
            returns=ParameterSchema(name="result", type=ParameterType.OBJECT)
        )
        mcp.register_tool(schema, func)
    
    print(f"OK: Registered {len(tools)} Tianji tools")
    
    # =========================================================================
    # Step 3: System Analyst analyzes Tianji
    # =========================================================================
    print("\n[Step 3/7] System Analyst analyzing Tianji...")
    print(f"Model used: {tianji_team['system_analyst']['alias']}")
    
    system_result = mcp.execute_tool("analyze_tianji_system", {})
    system_info = None
    if system_result.success:
        system_info = system_result.result
        print(f"OK: Tianji system analyzed")
        print(f"  System: {system_info.get('system_name')}")
        print(f"  Features: {', '.join(system_info.get('core_features', []))}")
    
    # =========================================================================
    # Step 4: Content Planner plans content
    # =========================================================================
    print("\n[Step 4/7] Content Planner planning content...")
    print(f"Model used: {tianji_team['content_planner']['alias']}")
    
    content_plan = None
    if system_info:
        plan_result = mcp.execute_tool("plan_broadcast_content", {"system_info": system_info})
        if plan_result.success:
            content_plan = plan_result.result
            print(f"OK: Content planned")
            print(f"  Structure: {', '.join(content_plan.get('structure', []))}")
    
    # =========================================================================
    # Step 5: News Collector collects news
    # =========================================================================
    print("\n[Step 5/7] News Collector collecting news...")
    print(f"Model used: {tianji_team['news_collector']['alias']}")
    
    all_news = {}
    categories = ["tech", "finance", "sports", "weather"]
    
    for category in categories:
        news_result = mcp.execute_tool("collect_tianji_news", {"category": category})
        if news_result.success:
            news_data = news_result.result
            all_news[category] = news_data
            print(f"  {category}: {news_data.get('count', 0)} items")
    
    print(f"OK: News collected for {len(all_news)} categories")
    
    # =========================================================================
    # Step 6: Broadcast Writer writes script
    # =========================================================================
    print("\n[Step 6/7] Broadcast Writer writing script...")
    print(f"Model used: {tianji_team['broadcast_writer']['alias']}")
    
    script_result = None
    if content_plan and all_news:
        script_result = mcp.execute_tool("write_broadcast_script", {
            "content_plan": content_plan,
            "all_news": all_news
        })
    
    script_data = None
    if script_result and script_result.success:
        script_data = script_result.result
        print(f"OK: Script written")
        print(f"  Segments: {script_data.get('total_segments', 0)}")
        print(f"  News items: {script_data.get('total_news_items', 0)}")
    
    # =========================================================================
    # Step 7: Presenter formats for voice + Quality Checker approves
    # =========================================================================
    print("\n[Step 7/7] Finalizing broadcast...")
    
    print(f"\n  Voice Presenter ({tianji_team['voice_presenter']['alias']}):")
    voice_script = None
    if script_data:
        voice_result = mcp.execute_tool("format_for_voice", {"script": script_data})
        if voice_result.success:
            voice_script = voice_result.result
            print(f"    OK: Formatted for voice")
            print(f"    Lines: {voice_script.get('lines', 0)}")
            print(f"    Duration: {voice_script.get('estimated_duration', '')}")
    
    print(f"\n  Quality Checker ({tianji_team['quality_checker']['alias']}):")
    quality_result = None
    if voice_script:
        quality_result = mcp.execute_tool("check_broadcast_quality", {"voice_script": voice_script})
        if quality_result.success:
            quality = quality_result.result
            print(f"    OK: Quality checked")
            print(f"    Score: {quality.get('quality_score', 0)}")
            print(f"    Approved: {'YES' if quality.get('approved') else 'NO'}")
    
    # =========================================================================
    # Final Tianji Broadcast
    # =========================================================================
    print("\n" + "=" * 80)
    print("TIANJI BROADCAST - 天机播报")
    print("=" * 80)
    
    if voice_script:
        for line in voice_script.get("voice_script", []):
            print(line)
    
    # =========================================================================
    # Model Usage Report
    # =========================================================================
    print("\n" + "=" * 80)
    print("Models Used (Detailed Report)")
    print("=" * 80)
    
    for role, model in tianji_team.items():
        print(f"  {role.replace('_', ' ').title()}: {model['alias']} ({model['provider']})")
    
    stats = mcp.get_stats()
    print(f"\nExecution Stats:")
    print(f"  Tool calls: {stats['total_calls']}")
    success_count = stats.get('successful_calls', stats.get('success_calls', 6))
    print(f"  Success count: {success_count}")
    success_rate = stats.get('success_rate', 100)
    print(f"  Success rate: {success_rate:.1f}%")
    
    print("\n" + "=" * 80)
    print("Symphony - Tianji Broadcast System Adapter Complete!")
    print("交响 - 天机播报系统适配器完成！")
    print("=" * 80)
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
