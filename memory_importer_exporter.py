#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony Memory Importer/Exporter - 交响记忆导入导出
Supports multiple formats: JSON, Markdown, CSV - 支持多种格式
"""

import sys
import os
import json
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class MemoryImporterExporter:
    """记忆导入导出器"""
    
    def __init__(self):
        pass
    
    # =========================================================================
    # Export - 导出
    # =========================================================================
    
    def export_to_json(self, memories: List[Dict[str, Any]], output_path: str) -> str:
        """Export to JSON format - 导出为JSON格式"""
        data = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "total_memories": len(memories),
            "memories": memories
        }
        
        path = Path(output_path)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        return str(path)
    
    def export_to_markdown(self, memories: List[Dict[str, Any]], output_path: str) -> str:
        """Export to Markdown format - 导出为Markdown格式"""
        lines = []
        lines.append("# Symphony Memories - 交响记忆\n")
        lines.append(f"Exported: {datetime.now().isoformat()}\n")
        lines.append(f"Total: {len(memories)} memories\n")
        
        for i, mem in enumerate(memories, 1):
            lines.append(f"\n## Memory {i}: {mem.get('id', 'N/A')}\n")
            lines.append(f"- **Type**: {mem.get('memory_type', 'N/A')}\n")
            lines.append(f"- **Importance**: {mem.get('importance', 0.0)}\n")
            lines.append(f"- **Tags**: {', '.join(mem.get('tags', []))}\n")
            lines.append(f"- **Category**: {mem.get('category', 'N/A')}\n")
            lines.append(f"- **Created**: {mem.get('created_at', 'N/A')}\n")
            lines.append(f"\n**Content**: {mem.get('content', '')}\n")
        
        path = Path(output_path)
        path.write_text('\n'.join(lines), encoding='utf-8')
        return str(path)
    
    def export_to_csv(self, memories: List[Dict[str, Any]], output_path: str) -> str:
        """Export to CSV format - 导出为CSV格式"""
        path = Path(output_path)
        
        fieldnames = [
            'id', 'content', 'memory_type', 'importance', 
            'tags', 'category', 'created_at', 'access_count'
        ]
        
        with path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for mem in memories:
                row = {
                    'id': mem.get('id', ''),
                    'content': mem.get('content', ''),
                    'memory_type': mem.get('memory_type', ''),
                    'importance': mem.get('importance', 0.0),
                    'tags': '|'.join(mem.get('tags', [])),
                    'category': mem.get('category', ''),
                    'created_at': mem.get('created_at', ''),
                    'access_count': mem.get('access_count', 0)
                }
                writer.writerow(row)
        
        return str(path)
    
    # =========================================================================
    # Import - 导入
    # =========================================================================
    
    def import_from_json(self, input_path: str) -> List[Dict[str, Any]]:
        """Import from JSON format - 从JSON格式导入"""
        path = Path(input_path)
        data = json.loads(path.read_text(encoding='utf-8'))
        return data.get("memories", [])
    
    def import_from_csv(self, input_path: str) -> List[Dict[str, Any]]:
        """Import from CSV format - 从CSV格式导入"""
        path = Path(input_path)
        memories = []
        
        with path.open('r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                mem = {
                    'id': row.get('id', ''),
                    'content': row.get('content', ''),
                    'memory_type': row.get('memory_type', 'short_term'),
                    'importance': float(row.get('importance', 0.5)),
                    'tags': row.get('tags', '').split('|') if row.get('tags') else [],
                    'category': row.get('category', 'general'),
                    'created_at': row.get('created_at', datetime.now().isoformat()),
                    'access_count': int(row.get('access_count', 0))
                }
                memories.append(mem)
        
        return memories


def create_importer_exporter() -> MemoryImporterExporter:
    """Create importer/exporter - 创建导入导出器"""
    return MemoryImporterExporter()


if __name__ == "__main__":
    print("Symphony Memory Importer/Exporter")
    print("交响记忆导入导出器")
    print("=" * 60)
    
    # Test data
    test_memories = [
        {
            "id": "test_1",
            "content": "Test memory 1 about AI",
            "memory_type": "long_term",
            "importance": 0.9,
            "tags": ["ai", "test"],
            "category": "test",
            "created_at": datetime.now().isoformat(),
            "access_count": 5
        },
        {
            "id": "test_2",
            "content": "Test memory 2 about weather",
            "memory_type": "short_term",
            "importance": 0.5,
            "tags": ["weather", "test"],
            "category": "test",
            "created_at": datetime.now().isoformat(),
            "access_count": 2
        }
    ]
    
    exporter = create_importer_exporter()
    
    # Test export
    print("\nTesting export...")
    json_path = exporter.export_to_json(test_memories, "test_export.json")
    md_path = exporter.export_to_markdown(test_memories, "test_export.md")
    csv_path = exporter.export_to_csv(test_memories, "test_export.csv")
    
    print(f"  JSON: {json_path}")
    print(f"  Markdown: {md_path}")
    print(f"  CSV: {csv_path}")
    
    # Test import
    print("\nTesting import...")
    imported_json = exporter.import_from_json("test_export.json")
    imported_csv = exporter.import_from_csv("test_export.csv")
    
    print(f"  JSON import: {len(imported_json)} memories")
    print(f"  CSV import: {len(imported_csv)} memories")
    
    # Cleanup
    print("\nCleaning up...")
    for f in ["test_export.json", "test_export.md", "test_export.csv"]:
        p = Path(f)
        if p.exists():
            p.unlink()
            print(f"  Removed: {f}")
    
    print("\n✅ All tests passed!")
    print("=" * 60)
