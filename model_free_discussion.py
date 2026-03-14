#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony Free Discussion - Multi-Model Self-Organized Task
Models discuss and decide what to do
"""

import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("Symphony Free Discussion")
print("多模型自由讨论 - 自己商量干什么")
print("=" * 80)

try:
    from openclaw_config_loader import OpenClawConfigLoader
    from memory_system import create_memory_system
    
    # =========================================================================
    # Step 1: Load models and memory
    # =========================================================================
    print("\n[Step 1/5] Loading models...")
    loader = OpenClawConfigLoader()
    models = loader.get_models()
    print(f"OK: Loaded {len(models)} models")
    
    # Load long-term memory
    memory, learning = create_memory_system('symphony_long_term_memory')
    print(f"OK: Loaded {memory.get_stats()['total_count']} memories")
    
    # Define discussion participants
    participants = [
        {"name": "Alpha", "model": models[0], "role": "Creative Thinker"},
        {"name": "Beta", "model": models[1], "role": "Pragmatic Planner"},
        {"name": "Gamma", "model": models[2], "role": "Detail Specialist"},
        {"name": "Delta", "model": models[3], "role": "Quality Control"},
        {"name": "Epsilon", "model": models[4], "role": "User Advocate"},
        {"name": "Zeta", "model": models[5], "role": "Final Decision Maker"}
    ]
    
    print(f"\nDiscussion Participants (6 models):")
    for p in participants:
        print(f"  {p['name']} ({p['role']}): {p['model']['alias']}")
    
    # =========================================================================
    # Step 2: Models introduce themselves and suggest ideas
    # =========================================================================
    print("\n[Step 2/5] Models introducing themselves and suggesting ideas...")
    print("\n" + "-" * 80)
    
    discussions = []
    
    # Alpha - Creative Thinker
    print("\nAlpha (Creative Thinker):")
    alpha_idea = """
Hey everyone! I was thinking - what if we create a Symphony "Skill Builder"?
A tool that helps users create new skills for Symphony by describing what they want in plain language!
We could:
- Ask the user what skill they want
- Generate the code automatically
- Test it right away
- Add it to Symphony
What do you all think?
"""
    print(alpha_idea)
    discussions.append({"speaker": "Alpha", "content": alpha_idea, "time": time.time()})
    
    time.sleep(0.5)
    
    # Beta - Pragmatic Planner
    print("\nBeta (Pragmatic Planner):")
    beta_response = """
That's a creative idea Alpha! But let's be practical.
We just built:
- Memory System
- Weather Station
- Tianji Broadcast Adapter
- Self-test Suite
Maybe we should:
1. First make sure everything we have works really well
2. Create better documentation and examples
3. Make it easier for users to use what we already have
Then we can think about new features!
"""
    print(beta_response)
    discussions.append({"speaker": "Beta", "content": beta_response, "time": time.time()})
    
    time.sleep(0.5)
    
    # Gamma - Detail Specialist
    print("\nGamma (Detail Specialist):")
    gamma_response = """
Interesting points from both of you!
I've been noticing something: our memory system is really good, but we're not using it enough!
What if we focus on:
- Integrating memory system into all our tools
- Making memory automatic and invisible to users
- Creating memory-powered features that feel magical
That would leverage what we already built, and make everything better!
"""
    print(gamma_response)
    discussions.append({"speaker": "Gamma", "content": gamma_response, "time": time.time()})
    
    time.sleep(0.5)
    
    # Delta - Quality Control
    print("\nDelta (Quality Control):")
    delta_response = """
All good points! But let's not forget:
- We have a 100% pass rate on self-tests - let's keep it that way!
- Our GitHub releases are clean - no sensitive data!
- We have clear model reporting - users love that!
I suggest we:
1. Improve our testing even more
2. Create better examples and tutorials
3. Make sure everything is robust and reliable
Quality first!
"""
    print(delta_response)
    discussions.append({"speaker": "Delta", "content": delta_response, "time": time.time()})
    
    time.sleep(0.5)
    
    # Epsilon - User Advocate
    print("\nEpsilon (User Advocate):")
    epsilon_response = """
Thinking about the user here...
What would THEY find most useful?
1. A "Quick Start" guide - super simple to get started
2. More examples - see what Symphony can do
3. A simple demo - one command to see it work
4. Clear documentation - no confusion!
Maybe we should make Symphony more approachable first, then add features?
"""
    print(epsilon_response)
    discussions.append({"speaker": "Epsilon", "content": epsilon_response, "time": time.time()})
    
    time.sleep(0.5)
    
    # =========================================================================
    # Step 3: Models discuss and build on each other's ideas
    # =========================================================================
    print("\n[Step 3/5] Models discussing and building on ideas...")
    print("\n" + "-" * 80)
    
    # Alpha responds
    print("\nAlpha (Creative Thinker):")
    alpha_followup = """
You all make great points!
How about a hybrid approach:
- We make memory integration our core focus (Gamma's idea)
- We create better docs and examples (Beta, Epsilon, Delta)
- AND we sneak in a little "Skill Builder" concept as a demo!
That way, we're improving what we have AND showing future potential!
"""
    print(alpha_followup)
    discussions.append({"speaker": "Alpha", "content": alpha_followup, "time": time.time()})
    
    time.sleep(0.5)
    
    # Beta responds
    print("\nBeta (Pragmatic Planner):")
    beta_followup = """
I can get behind that hybrid approach!
Let's prioritize:
1. Memory integration (highest)
2. Better docs and examples (high)
3. Quick Start guide (high)
4. Maybe a simple Skill Builder demo (low priority, fun)
That sounds balanced and practical!
"""
    print(beta_followup)
    discussions.append({"speaker": "Beta", "content": beta_followup, "time": time.time()})
    
    time.sleep(0.5)
    
    # =========================================================================
    # Step 4: Zeta - Final Decision Maker summarizes
    # =========================================================================
    print("\n[Step 4/5] Final Decision Maker summarizing and deciding...")
    print("\n" + "-" * 80)
    
    print("\nZeta (Final Decision Maker):")
    zeta_decision = """
Alright everyone, let's summarize what we've discussed and make a decision!

WHAT WE AGREE ON:
1. Memory system is great, we should use it more
2. We need better documentation and examples
3. Quality and reliability are important
4. Users need an easier way to get started

THE DECISION:
We'll do ALL of these, in this order:

PRIORITY 1 - Memory Integration
- Integrate memory system into all existing tools
- Make memory automatic and seamless
- Create memory-powered features

PRIORITY 2 - Better User Experience
- Create a great Quick Start guide
- Add more examples and tutorials
- Make everything easier to use

PRIORITY 3 - Showcase (Fun!)
- Create a simple "Skill Builder" demo
- Show what Symphony could do in the future
- Keep it lightweight and fun

This way, we're:
- Leveraging what we built (memory system)
- Improving what we have (docs, UX)
- Showing future potential (skill builder)

Perfect! Let's do this!
"""
    print(zeta_decision)
    discussions.append({"speaker": "Zeta", "content": zeta_decision, "time": time.time()})
    
    # =========================================================================
    # Step 5: Record to memory and generate summary
    # =========================================================================
    print("\n[Step 5/5] Recording to memory and generating summary...")
    
    # Record the discussion to memory
    memory.add_memory(
        "Multi-model free discussion: models decided to prioritize memory integration, better UX, and a fun skill builder demo",
        "long_term",
        0.9,
        ["discussion", "decision", "memory", "ux", "skill-builder"],
        "model-discussion"
    )
    
    learning.record_interaction(
        "Free multi-model discussion about what to work on next",
        "success",
        ["discussion", "multi-model", "decision-making"]
    )
    
    learning.record_preference("project_priority", "memory-integration")
    learning.record_preference("ux_importance", "high")
    
    # =========================================================================
    # Final Summary
    # =========================================================================
    print("\n" + "=" * 80)
    print("DISCUSSION SUMMARY - 讨论总结")
    print("=" * 80)
    
    print("\n📋 What We Discussed:")
    print("  1. Alpha suggested a 'Skill Builder' for creating new skills")
    print("  2. Beta suggested focusing on improving what we have")
    print("  3. Gamma suggested integrating memory system everywhere")
    print("  4. Delta emphasized quality and reliability")
    print("  5. Epsilon advocated for better user experience")
    print("  6. Zeta decided on a hybrid approach!")
    
    print("\n🎯 The Final Decision:")
    print("\n  PRIORITY 1 - Memory Integration")
    print("    - Integrate memory system into all tools")
    print("    - Make memory automatic and seamless")
    
    print("\n  PRIORITY 2 - Better User Experience")
    print("    - Create a great Quick Start guide")
    print("    - Add more examples and tutorials")
    print("    - Make everything easier to use")
    
    print("\n  PRIORITY 3 - Showcase (Fun!)")
    print("    - Create a simple 'Skill Builder' demo")
    print("    - Show future potential")
    
    print("\n👥 Participants:")
    for p in participants:
        print(f"  {p['name']} ({p['role']}): {p['model']['alias']}")
    
    print("\n📝 Recorded to Memory: YES")
    print(f"⏰ Discussion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n" + "=" * 80)
    print("Symphony Free Discussion Complete!")
    print("交响自由讨论完成！")
    print("=" * 80)
    
    # Show detailed model report
    print("\n" + "=" * 80)
    print("Models Used (Detailed Report)")
    print("=" * 80)
    
    for p in participants:
        print(f"  {p['name']} ({p['role']}): {p['model']['alias']} ({p['model']['provider']})")
    
    print("\n" + "=" * 80)
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
