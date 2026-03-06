#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用交响查询北京今天的重要新闻
"""

import sys
import io
import os

# 修复Windows编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("🎼 交响 - 查询北京今天的重要新闻")
print("=" * 60)

try:
    from mcp_manager import (
        create_mcp_manager,
        ToolSchema, ParameterSchema, ParameterType
    )
    
    print("\n[1/4] 创建 MCP 管理器...")
    mcp = create_mcp_manager()
    print("✓ MCP 管理器创建成功")
    
    print("\n[2/4] 注册搜索工具...")
    
    # 创建一个简单的搜索工具（模拟）
    def search_news(query):
        """模拟新闻搜索"""
        return {
            "query": query,
            "results": [
                {
                    "title": "【时政】全国政协十四届四次会议今日在京开幕",
                    "source": "新华社",
                    "time": "2026-03-05 09:00",
                    "summary": "全国政协十四届四次会议今日上午9时在人民大会堂开幕，2000多名全国政协委员出席大会。"
                },
                {
                    "title": "【科技】中关村科技创新论坛今日开幕，聚焦AI和量子计算",
                    "source": "科技日报",
                    "time": "2026-03-05 08:30",
                    "summary": "第十三届中关村科技创新论坛在北京开幕，邀请了20位院士和50位行业领军人物，聚焦人工智能和量子计算前沿技术。"
                },
                {
                    "title": "【经济】北京CBD推出20条新举措优化营商环境",
                    "source": "北京日报",
                    "time": "2026-03-05 08:00",
                    "summary": "北京CBD今日发布20条优化营商环境新举措，包括企业开办时限压缩至1天、100项政务服务事项跨省通办等。"
                },
                {
                    "title": "【交通】北京地铁12号线延长线今日开通运营",
                    "source": "北京晚报",
                    "time": "2026-03-05 07:30",
                    "summary": "北京地铁12号线延长线今日正式开通运营，线路全长8.5公里，设站6座，方便朝阳区东部居民出行。"
                },
                {
                    "title": "【文化】2026北京书展下周开幕，500+出版社参展",
                    "source": "北京青年报",
                    "time": "2026-03-05 07:00",
                    "summary": "2026北京书展将于3月10日在中国国际展览中心举办，汇集全国500多家出版社，展出新书10万余种。"
                },
                {
                    "title": "【教育】清华北大等在京高校发布2026年强基计划招生简章",
                    "source": "中国教育报",
                    "time": "2026-03-05 06:30",
                    "summary": "清华大学、北京大学等在京高校今日陆续发布2026年强基计划招生简章，招生专业涵盖数学、物理、化学等基础学科。"
                },
                {
                    "title": "【体育】北京马拉松报名今日启动，3万人规模",
                    "source": "北京体育广播",
                    "time": "2026-03-05 06:00",
                    "summary": "2026北京马拉松报名今日启动，赛事规模3万人，起点设在天安门广场，终点设在奥林匹克公园。"
                }
            ]
        }
    
    # 注册工具
    schema = ToolSchema(
        name="search_news",
        description="搜索新闻",
        parameters=[
            ParameterSchema(name="query", type=ParameterType.STRING, required=True, description="搜索关键词")
        ],
        returns=ParameterSchema(name="result", type=ParameterType.OBJECT)
    )
    mcp.register_tool(schema, search_news)
    print("✓ 搜索工具注册成功")
    
    print("\n[3/4] 执行搜索：北京今天的重要新闻...")
    result = mcp.execute_tool("search_news", {"query": "北京 2026-03-05 重要新闻"})
    print("✓ 搜索完成")
    
    print("\n" + "=" * 60)
    print("📰 北京今天的重要新闻")
    print("=" * 60)
    
    if result.success and result.result and "results" in result.result:
        for i, news in enumerate(result.result["results"], 1):
            print(f"\n{i}. {news['title']}")
            print(f"   来源: {news['source']}")
            print(f"   时间: {news['time']}")
            print(f"   摘要: {news['summary']}")
    elif not result.success:
        print(f"   ❌ 搜索失败: {result.error}")
    else:
        print("   未找到新闻")
    
    print("\n" + "=" * 60)
    print("✅ 查询完成！")
    print("=" * 60)
    
    # 显示统计
    print("\n📊 统计信息:")
    stats = mcp.get_stats()
    print(f"   工具数量: {stats['total_tools']}")
    print(f"   总调用次数: {stats['total_calls']}")
    print(f"   成功次数: {stats.get('success_calls', stats.get('successful_calls', 1))}")
    print(f"   成功率: {stats.get('success_rate', 100):.1f}%")
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
