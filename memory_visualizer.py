#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony Memory Visualizer - 交响记忆可视化
Visualize Symphony memory system
"""

from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import json
import sys


class MemoryVisualizer:
    """Visualize Symphony memory"""
    
    def __init__(self, memory_path: str = "symphony_memory.json"):
        self.memory_path = Path(memory_path)
        self.data = self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory data"""
        if self.memory_path.exists():
            try:
                return json.loads(self.memory_path.read_text(encoding='utf-8'))
            except Exception as e:
                print(f"Warning: Could not load memory: {e}")
        return {"memories": [], "preferences": {}}
    
    def render_ascii_dashboard(self):
        """Render ASCII dashboard"""
        print("\n" + "=" * 80)
        print("SYMPHONY MEMORY DASHBOARD - 交响记忆仪表盘")
        print("=" * 80)
        
        memories = self.data.get("memories", [])
        preferences = self.data.get("preferences", {})
        
        # Summary
        print("\nSummary - 摘要")
        print("-" * 80)
        print(f"  Total Memories: {len(memories)}")
        print(f"  Preferences: {len(preferences)}")
        
        if memories:
            # By type
            long_term = [m for m in memories if m.get("memory_type") == "long_term"]
            short_term = [m for m in memories if m.get("memory_type") == "short_term"]
            print(f"  Long-term: {len(long_term)}")
            print(f"  Short-term: {len(short_term)}")
            
            # By importance
            high_imp = [m for m in memories if m.get("importance", 0) >= 0.7]
            med_imp = [m for m in memories if 0.4 <= m.get("importance", 0) < 0.7]
            low_imp = [m for m in memories if m.get("importance", 0) < 0.4]
            print(f"  High Importance (>=0.7): {len(high_imp)}")
            print(f"  Medium Importance (0.4-0.7): {len(med_imp)}")
            print(f"  Low Importance (<0.4): {len(low_imp)}")
        
        # Preferences
        if preferences:
            print("\nPreferences - 偏好设置")
            print("-" * 80)
            for key, value in preferences.items():
                print(f"  {key}: {value}")
        
        # Recent memories
        if memories:
            print("\nRecent Memories - 最近记忆")
            print("-" * 80)
            # Sort by created_at (newest first)
            sorted_mem = sorted(memories, key=lambda x: x.get("created_at", ""), reverse=True)
            for i, mem in enumerate(sorted_mem[:5]):
                importance = mem.get("importance", 0)
                mem_type = mem.get("memory_type", "unknown")
                tags = ", ".join(mem.get("tags", []))
                content = mem.get("content", "")[:60]
                
                # Importance bar
                bar_length = int(importance * 20)
                bar = "#" * bar_length + "-" * (20 - bar_length)
                
                print(f"\n  [{i+1}] {mem_type.upper()} | Importance: [{bar}] {importance:.2f}")
                print(f"      Tags: {tags}")
                print(f"      Content: {content}...")
        
        # Tag cloud
        if memories:
            print("\nTag Cloud - 标签云")
            print("-" * 80)
            tag_counts: Dict[str, int] = {}
            for mem in memories:
                for tag in mem.get("tags", []):
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
            tag_line = ""
            for tag, count in sorted_tags:
                size = min(count * 2, 8)
                tag_line += f"{tag}({count}) "
                if len(tag_line) > 70:
                    print(f"  {tag_line}")
                    tag_line = ""
            if tag_line:
                print(f"  {tag_line}")
        
        # Timeline (simple)
        if memories:
            print("\nTimeline - 时间线")
            print("-" * 80)
            sorted_mem = sorted(memories, key=lambda x: x.get("created_at", ""))
            for mem in sorted_mem:
                created = mem.get("created_at", "")[:10]
                content = mem.get("content", "")[:40]
                print(f"  {created} | {content}...")
        
        print("\n" + "=" * 80)
    
    def render_text_report(self) -> str:
        """Render text report"""
        memories = self.data.get("memories", [])
        preferences = self.data.get("preferences", {})
        
        report = []
        report.append("=" * 60)
        report.append("SYMPHONY MEMORY REPORT - 交响记忆报告")
        report.append("=" * 60)
        
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Memories: {len(memories)}")
        report.append(f"Preferences: {len(preferences)}")
        
        if memories:
            report.append("\n--- MEMORIES ---")
            for i, mem in enumerate(memories, 1):
                report.append(f"\n[{i}] {mem.get('memory_type', 'unknown').upper()}")
                report.append(f"    Importance: {mem.get('importance', 0):.2f}")
                report.append(f"    Tags: {', '.join(mem.get('tags', []))}")
                report.append(f"    Created: {mem.get('created_at', '')}")
                report.append(f"    Content: {mem.get('content', '')}")
        
        if preferences:
            report.append("\n--- PREFERENCES ---")
            for key, value in preferences.items():
                report.append(f"  {key}: {value}")
        
        report.append("\n" + "=" * 60)
        return "\n".join(report)
    
    def export_html(self, output_path: str = "memory_report.html"):
        """Export as simple HTML"""
        memories = self.data.get("memories", [])
        preferences = self.data.get("preferences", {})
        
        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html><head><title>Symphony Memory Report</title>")
        html.append("<style>")
        html.append("body { font-family: Arial, sans-serif; margin: 20px; }")
        html.append("h1 { color: #333; }")
        html.append(".memory { border: 1px solid #ddd; padding: 10px; margin: 10px 0; }")
        html.append(".high { background: #ffeb3b; }")
        html.append(".medium { background: #fff3cd; }")
        html.append(".low { background: #d4edda; }")
        html.append("</style></head><body>")
        html.append("<h1>Symphony Memory Report - 交响记忆报告</h1>")
        
        html.append(f"<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        html.append(f"<p>Total Memories: {len(memories)}</p>")
        
        for mem in memories:
            imp = mem.get('importance', 0)
            cls = "high" if imp >= 0.7 else "medium" if imp >= 0.4 else "low"
            html.append(f'<div class="memory {cls}">')
            html.append(f"<h3>{mem.get('memory_type', 'unknown').upper()}</h3>")
            html.append(f"<p>Importance: {imp:.2f}</p>")
            html.append(f"<p>Tags: {', '.join(mem.get('tags', []))}</p>")
            html.append(f"<p>{mem.get('content', '')}</p>")
            html.append("</div>")
        
        html.append("</body></html>")
        
        Path(output_path).write_text("\n".join(html), encoding='utf-8')
        print(f"HTML exported to: {output_path}")


# Convenience function
def visualize_memory(memory_path: str = "symphony_memory.json", 
                    output_format: str = "ascii"):
    """Visualize memory"""
    viz = MemoryVisualizer(memory_path)
    
    if output_format == "ascii":
        viz.render_ascii_dashboard()
    elif output_format == "text":
        print(viz.render_text_report())
    elif output_format == "html":
        viz.export_html()
    else:
        print(f"Unknown format: {output_format}")


if __name__ == "__main__":
    format_arg = sys.argv[1] if len(sys.argv) > 1 else "ascii"
    visualize_memory(output_format=format_arg)
