#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony Model Reporter - Standardized Model Reporting
交响模型报告器 - 标准化模型报告
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class ModelUsage:
    """Single model usage record"""
    role: str
    model_name: str
    provider: str
    status: str = "success"


class SymphonyModelReporter:
    """Standardized model reporting for Symphony"""
    
    def __init__(self):
        self.usages: List[ModelUsage] = []
        self.start_time = None
        self.end_time = None
        self.tool_calls = 0
        self.successful_calls = 0
    
    def record_usage(self, role: str, model_name: str, provider: str, status: str = "success"):
        """Record a model usage"""
        usage = ModelUsage(
            role=role,
            model_name=model_name,
            provider=provider,
            status=status
        )
        self.usages.append(usage)
    
    def record_tool_call(self, success: bool = True):
        """Record a tool call"""
        self.tool_calls += 1
        if success:
            self.successful_calls += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary report"""
        success_rate = (self.successful_calls / self.tool_calls * 100) if self.tool_calls > 0 else 100
        
        return {
            "models_used": len(self.usages),
            "tool_calls": self.tool_calls,
            "successful_calls": self.successful_calls,
            "success_rate": success_rate,
            "usages": self.usages
        }
    
    def print_report(self):
        """Print formatted report"""
        print("\n" + "=" * 60)
        print("Models Used (Detailed Report)")
        print("=" * 60)
        
        for usage in self.usages:
            print(f"  {usage.role}: {usage.model_name} ({usage.provider})")
        
        summary = self.get_summary()
        print(f"\nExecution Stats:")
        print(f"  Tool calls: {summary['tool_calls']}")
        print(f"  Success count: {summary['successful_calls']}")
        print(f"  Success rate: {summary['success_rate']:.1f}%")
        
        print("\n" + "=" * 60)


# Convenience function to create a reporter
def create_reporter() -> SymphonyModelReporter:
    """Create a new model reporter"""
    return SymphonyModelReporter()


if __name__ == "__main__":
    # Example usage
    reporter = create_reporter()
    
    reporter.record_usage("Product Manager", "ark-code-latest", "cherry-doubao")
    reporter.record_usage("UX Designer", "deepseek-v3.2", "cherry-doubao")
    reporter.record_tool_call(success=True)
    reporter.record_tool_call(success=True)
    
    reporter.print_report()
