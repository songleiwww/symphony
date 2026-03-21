"""
# 序境系统 - 健康监控模块
# 负责模型在线状态统计和健康检查
"""

import sqlite3
import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict

@dataclass
class HealthStats:
    provider: str
    total: int
    online: int
    offline: int
    
    @property
    def health_ratio(self) -> float:
        if self.total == 0:
            return 0.0
        return self.online / self.total

class HealthMonitor:
    """健康监控模块 - 统计各服务商模型在线状态"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_all_model_stats(self) -> Tuple[Dict[str, HealthStats], Dict[str, Any]]:
        """获取所有服务商模型统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 模型名称, 服务商, 在线状态 FROM "模型配置表"')
        results = cursor.fetchall()
        
        stats: Dict[str, HealthStats] = {}
        all_models: List[Dict[str, str]] = []
        
        for model_name, provider, online in results:
            if provider not in stats:
                stats[provider] = HealthStats(
                    provider=provider,
                    total=0,
                    online=0,
                    offline=0
                )
            stats[provider].total += 1
            is_online = online == "online" or online == "是"
            if is_online:
                stats[provider].online += 1
            else:
                stats[provider].offline += 1
            
            all_models.append({
                "provider": provider,
                "model_name": model_name,
                "online_status": online,
                "is_online": str(is_online)
            })
        
        conn.close()
        
        # 汇总统计
        total_all = sum(s.total for s in stats.values())
        online_all = sum(s.online for s in stats.values())
        offline_all = sum(s.offline for s in stats.values())
        
        summary = {
            "total_models": total_all,
            "total_online": online_all,
            "total_offline": offline_all,
            "overall_health_ratio": online_all / total_all if total_all > 0 else 0
        }
        
        return stats, summary
    
    def get_health_report(self) -> Dict[str, Any]:
        """生成完整健康报告"""
        stats, summary = self.get_all_model_stats()
        
        report = {
            "summary": summary,
            "providers": {},
            "timestamp": None
        }
        
        for provider, stat in stats.items():
            report["providers"][provider] = {
                "total": stat.total,
                "online": stat.online,
                "offline": stat.offline,
                "health_ratio": round(stat.health_ratio, 2)
            }
        
        return report
    
    def print_health_report(self) -> None:
        """打印健康报告到控制台"""
        stats, summary = self.get_all_model_stats()
        
        print("=" * 60)
        print("序境系统 - 模型健康监控报告")
        print("=" * 60)
        print(f"{'服务商':<15} {'总计':>6} {'在线':>6} {'离线':>6} {'健康率':>8}")
        print("-" * 60)
        
        sorted_providers = sorted(stats.values(), key=lambda x: -x.total)
        for stat in sorted_providers:
            ratio = f"{stat.health_ratio:.0%}"
            print(f"{stat.provider:<15} {stat.total:>6} {stat.online:>6} {stat.offline:>6} {ratio:>8}")
        
        print("-" * 60)
        ratio = f"{summary['overall_health_ratio']:.0%}"
        print(f"{'**总计**':<15} {summary['total_models']:>6} {summary['total_online']:>6} {summary['total_offline']:>6} {ratio:>8}")
        print("=" * 60)
    
    def save_health_report(self, output_path: str) -> None:
        """保存健康报告到JSON文件"""
        report = self.get_health_report()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

    def check_provider_health(self, provider: str) -> Dict[str, Any]:
        """检查特定服务商健康状况"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 模型名称, 在线状态 FROM "模型配置表" WHERE 服务商 = ?', (provider,))
        results = cursor.fetchall()
        
        total = len(results)
        online = sum(1 for _, stat in results if stat == "online" or stat == "是")
        offline = total - online
        
        conn.close()
        
        return {
            "provider": provider,
            "total": total,
            "online": online,
            "offline": offline,
            "health_ratio": online / total if total > 0 else 0,
            "models": [{"name": name, "online": (stat == "online" or stat == "是")} for name, stat in results]
        }

if __name__ == "__main__":
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
    monitor = HealthMonitor(db_path)
    monitor.print_health_report()
