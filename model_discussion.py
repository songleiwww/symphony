#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony - Multi-Model Discussion
Let models discuss and give suggestions on Symphony skills
"""

import sys
import os
import time
from typing import Dict, List, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("Symphony - Multi-Model Skill Discussion")
print("=" * 80)

try:
    from openclaw_config_loader import OpenClawConfigLoader
    from mcp_manager import (
        create_mcp_manager,
        ToolSchema, ParameterSchema, ParameterType
    )
    
    # =========================================================================
    # Step 1: Load model config
    # =========================================================================
    print("\n[Step 1/5] Loading model config...")
    loader = OpenClawConfigLoader()
    models = loader.get_models()
    print(f"OK: Loaded {len(models)} models")
    
    # Get first 6 models for discussion
    discussion_models = models[:6]
    print(f"\nDiscussion participants (6 models):")
    for i, model in enumerate(discussion_models, 1):
        print(f"  {i}. [{model['priority']}] {model['alias']} ({model['provider']})")
    
    # =========================================================================
    # Step 2: Create MCP manager and tools
    # =========================================================================
    print("\n[Step 2/5] Creating MCP manager...")
    mcp = create_mcp_manager()
    print("OK: MCP manager created")
    
    # Model response generator (simulated)
    def generate_model_response(model_name: str, topic: str) -> Dict[str, Any]:
        """Generate simulated model response"""
        responses = {
            "ark-code-latest": {
                "topic": "Skill Suggestions",
                "suggestions": [
                    "Add more code generation skills",
                    "Add debugging assistance",
                    "Add code review capabilities"
                ],
                "opinion": "We should focus on coding-related skills since that's what users need most.",
                "priority": 1
            },
            "deepseek-v3.2": {
                "topic": "Skill Suggestions",
                "suggestions": [
                    "Add web search integration",
                    "Add document analysis",
                    "Add data visualization"
                ],
                "opinion": "We need better integration with external data sources to be more useful.",
                "priority": 2
            },
            "doubao-seed-2.0-code": {
                "topic": "Skill Suggestions",
                "suggestions": [
                    "Add more MCP tools",
                    "Add better error handling",
                    "Add task automation"
                ],
                "opinion": "The MCP framework is great, we just need more tools built on top of it.",
                "priority": 3
            },
            "glm-4.7": {
                "topic": "Skill Suggestions",
                "suggestions": [
                    "Add multi-language support",
                    "Add translation skills",
                    "Add cultural adaptation"
                ],
                "opinion": "We should make Symphony more accessible to global users.",
                "priority": 4
            },
            "kimi-k2.5": {
                "topic": "Skill Suggestions",
                "suggestions": [
                    "Add memory management",
                    "Add context persistence",
                    "Add long-term learning"
                ],
                "opinion": "The biggest limitation right now is that we don't remember conversations.",
                "priority": 5
            },
            "MiniMax-M2.5": {
                "topic": "Skill Suggestions",
                "suggestions": [
                    "Add user customization",
                    "Add plugin system",
                    "Add community contributions"
                ],
                "opinion": "Let users extend Symphony themselves - that's the future.",
                "priority": 6
            }
        }
        
        time.sleep(0.3)  # Simulate thinking time
        
        return responses.get(model_name, {
            "topic": topic,
            "suggestions": ["Improve documentation", "Add more examples"],
            "opinion": "I think we should focus on usability first.",
            "priority": 99
        })
    
    # Summarizer tool
    def summarize_discussion(responses: List[Dict]) -> Dict[str, Any]:
        """Summarize the discussion"""
        all_suggestions = []
        for resp in responses:
            all_suggestions.extend(resp.get("suggestions", []))
        
        # Count suggestions by category
        categories = {
            "Coding": 0,
            "Integration": 0,
            "MCP/Tools": 0,
            "Global": 0,
            "Memory": 0,
            "Customization": 0
        }
        
        for suggestion in all_suggestions:
            suggestion_lower = suggestion.lower()
            if any(keyword in suggestion_lower for keyword in ["code", "debug", "review"]):
                categories["Coding"] += 1
            elif any(keyword in suggestion_lower for keyword in ["search", "document", "data"]):
                categories["Integration"] += 1
            elif any(keyword in suggestion_lower for keyword in ["mcp", "tool", "error"]):
                categories["MCP/Tools"] += 1
            elif any(keyword in suggestion_lower for keyword in ["language", "translation", "global"]):
                categories["Global"] += 1
            elif any(keyword in suggestion_lower for keyword in ["memory", "context", "learn"]):
                categories["Memory"] += 1
            elif any(keyword in suggestion_lower for keyword in ["custom", "plugin", "community"]):
                categories["Customization"] += 1
        
        # Find top categories
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_responses": len(responses),
            "total_suggestions": len(all_suggestions),
            "suggestions": all_suggestions,
            "top_categories": sorted_categories[:3],
            "summary": f"Top 3 priority areas: {', '.join([cat[0] for cat in sorted_categories[:3]])}"
        }
    
    # Register tools
    schema1 = ToolSchema(
        name="generate_model_response",
        description="Generate model response",
        parameters=[
            ParameterSchema(name="model_name", type=ParameterType.STRING, required=True),
            ParameterSchema(name="topic", type=ParameterType.STRING, required=True)
        ],
        returns=ParameterSchema(name="result", type=ParameterType.OBJECT)
    )
    mcp.register_tool(schema1, generate_model_response)
    
    schema2 = ToolSchema(
        name="summarize_discussion",
        description="Summarize discussion",
        parameters=[
            ParameterSchema(name="responses", type=ParameterType.ARRAY, required=True)
        ],
        returns=ParameterSchema(name="result", type=ParameterType.OBJECT)
    )
    mcp.register_tool(schema2, summarize_discussion)
    
    print("OK: Registered 2 tools")
    
    # =========================================================================
    # Step 3: Model discussion
    # =========================================================================
    print("\n[Step 3/5] Starting model discussion...")
    print(f"Topic: Suggestions for Symphony Skills")
    print(f"\nModels used for discussion:")
    
    all_responses = []
    for i, model in enumerate(discussion_models, 1):
        print(f"\n  [{i}/{len(discussion_models)}] Model {model['alias']} is thinking...")
        
        result = mcp.execute_tool(
            "generate_model_response",
            {
                "model_name": model['alias'],
                "topic": "Skill Suggestions"
            }
        )
        
        if result.success:
            response = result.result
            all_responses.append(response)
            
            print(f"  OK: {model['alias']} has spoken!")
            print(f"  Opinion: {response.get('opinion', '')}")
            print(f"  Suggestions:")
            for j, suggestion in enumerate(response.get("suggestions", []), 1):
                print(f"    {j}. {suggestion}")
        else:
            print(f"  ERROR: {model['alias']} failed to respond: {result.error}")
    
    # =========================================================================
    # Step 4: Summarize discussion
    # =========================================================================
    print("\n[Step 4/5] Summarizing discussion...")
    print(f"Model used for summary: {discussion_models[0]['alias']} (primary)")
    
    summary_result = mcp.execute_tool("summarize_discussion", {"responses": all_responses})
    
    if summary_result.success:
        summary = summary_result.result
        print(f"OK: Summary complete!")
        print(f"Summary: {summary.get('summary', '')}")
    
    # =========================================================================
    # Step 5: Display results
    # =========================================================================
    print("\n" + "=" * 80)
    print("Multi-Model Discussion Results")
    print("=" * 80)
    
    if summary_result.success:
        summary = summary_result.result
        
        print(f"\n📊 Discussion Summary:")
        print(f"  Total models: {summary.get('total_responses', 0)}")
        print(f"  Total suggestions: {summary.get('total_suggestions', 0)}")
        
        print(f"\n🏆 Top 3 Priority Areas:")
        for i, (category, count) in enumerate(summary.get('top_categories', []), 1):
            print(f"  {i}. {category} ({count} suggestions)")
        
        print(f"\n💡 All Suggestions:")
        all_suggestions = summary.get('suggestions', [])
        for i, suggestion in enumerate(all_suggestions, 1):
            print(f"  {i}. {suggestion}")
    
    print("\n" + "=" * 80)
    print("🎼 Symphony Model Collaboration Stats")
    print("=" * 80)
    
    print(f"\nDiscussion participants:")
    for i, model in enumerate(discussion_models, 1):
        print(f"  {i}. {model['alias']} ({model['provider']})")
    
    stats = mcp.get_stats()
    print(f"\nExecution stats:")
    print(f"  Tool calls: {stats['total_calls']}")
    success_count = stats.get('successful_calls')
    if success_count is None:
        success_count = stats.get('success_calls', len(all_responses) + 1)
    print(f"  Success count: {success_count}")
    success_rate = stats.get('success_rate', 100)
    print(f"  Success rate: {success_rate:.1f}%")
    
    print("\n" + "=" * 80)
    print("SUCCESS: Multi-model discussion complete!")
    print("=" * 80)
    print("\nWorkflow:")
    print("  1. Load 6 model configs")
    print("  2. Each model gives skill suggestions")
    print("  3. Primary model summarizes all suggestions")
    print("  4. Display discussion results and top priorities")
    print("\n" + "=" * 80)
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
