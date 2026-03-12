#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
少府监自适应全能系统 - 完整版
功能: 主被动应答、主备动技能、汇报工作、自动述职
============================================================================
"""
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
import threading
import time

# API配置
API_KEY = "3b922877-3fbe-45d1-a298-53f2231c5224"
URL = "https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions"

# =============================================================================
# 数据结构
# =============================================================================

@dataclass
class PersonStatus:
    id: str
    name: str
    role: str
    model_id: str
    provider: str
    status: str = "空闲"  # 空闲/忙碌/离线
    active_calls: int = 0
    passive_calls: int = 0
    adaptive_calls: int = 0
    total_tokens: int = 0
    contribution: float = 0.0
    last_active: str = ""
    functions: List[Dict] = field(default_factory=list)

@dataclass
class Problem:
    id: str
    title: str
    description: str
    priority: str = "中"
    status: str = "待处理"  # 待处理/分析中/已指派/解决中/已解决/已关闭
    assigned_to: List[str] = field(default_factory=list)
    solution: str = ""
    created_at: str = ""
    resolved_at: str = ""
    closed: bool = False

@dataclass
class WorkReport:
    person_id: str
    person_name: str
    period: str  # 日报/周报/月报
    tasks: List[Dict]
    summary: str
    suggestions: str
    created_at: str

# =============================================================================
# 核心系统
# =============================================================================

class ShaofuJianSystem:
    """少府监自适应全能系统"""
    
    def __init__(self):
        self.data_dir = Path(r"C:\Users\Administrator\.openclaw\workspace\skills\symphony")
        self.roster_file = self.data_dir / "sf_team_roster.json"
        self.status_file = self.data_dir / "sf_person_status.json"
        self.problems_file = self.data_dir / "sf_problems_v3.json"
        self.reports_file = self.data_dir / "sf_work_reports.json"
        
        self.persons = {}
        self.problems = []
        self.reports = []
        self.lock = threading.Lock()
        
        # 加载数据
        self.load_all()
        
    def load_all(self):
        """加载所有数据"""
        # 加载花名册
        try:
            roster = json.loads(self.roster_file.read_text(encoding="utf-8"))
            for m in roster.get("team", []):
                funcs = self.assign_functions(m.get("role", ""))
                self.persons[m["id"]] = PersonStatus(
                    id=m["id"],
                    name=m["name"],
                    role=m["role"],
                    model_id=m.get("model_id", ""),
                    provider=m.get("服务商", ""),
                    functions=funcs,
                    last_active=datetime.now().isoformat()
                )
        except Exception as e:
            print(f"加载花名册失败: {e}")
        
        # 加载问题
        try:
            if self.problems_file.exists():
                data = json.loads(self.problems_file.read_text(encoding="utf-8"))
                self.problems = [Problem(**p) for p in data.get("problems", [])]
        except:
            pass
            
        # 加载报告
        try:
            if self.reports_file.exists():
                self.reports = json.loads(self.reports_file.read_text(encoding="utf-8"))
        except:
            pass
    
    def assign_functions(self, role: str) -> List[Dict]:
        """根据角色分配功能"""
        base = [
            {"id": "主动应答", "name": "主动应答", "active": True, "level": 5},
            {"id": "被动应答", "name": "被动应答", "active": True, "level": 5},
            {"id": "学习进化", "name": "学习进化", "active": True, "level": 5}
        ]
        
        if "枢密使" in role or "少府监" in role or "尚书" in role:
            base.extend([
                {"id": "问题分析", "name": "问题分析", "active": True, "level": 10},
                {"id": "任务调度", "name": "任务调度", "active": True, "level": 10},
                {"id": "汇报工作", "name": "汇报工作", "active": True, "level": 9},
                {"id": "主备动", "name": "主备动切换", "active": True, "level": 10},
                {"id": "工作统计", "name": "工作统计", "active": True, "level": 8}
            ])
        elif "博士" in role or "编修" in role:
            base.extend([
                {"id": "问题分析", "name": "问题分析", "active": True, "level": 8},
                {"id": "学习进化", "name": "学习进化", "active": True, "level": 10}
            ])
        
        return base
    
    def save_all(self):
        """保存所有数据"""
        with self.lock:
            # 保存状态
            status_data = {
                "version": "3.0",
                "updated": datetime.now().isoformat(),
                "persons": {k: asdict(v) for k, v in self.persons.items()}
            }
            self.status_file.write_text(json.dumps(status_data, ensure_ascii=False, indent=2), encoding="utf-8")
            
            # 保存问题
            problems_data = {
                "version": "3.0",
                "updated": datetime.now().isoformat(),
                "problems": [asdict(p) for p in self.problems]
            }
            self.problems_file.write_text(json.dumps(problems_data, ensure_ascii=False, indent=2), encoding="utf-8")
            
            # 保存报告
            self.reports_file.write_text(json.dumps(self.reports, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # =========================================================================
    # 主被动应答
    # =========================================================================
    
    def handle_active_call(self, person_id: str, task: str) -> Dict:
        """处理主动调用"""
        if person_id not in self.persons:
            return {"success": False, "error": "人员不存在"}
        
        person = self.persons[person_id]
        person.status = "忙碌"
        person.active_calls += 1
        person.last_active = datetime.now().isoformat()
        
        # 调用AI处理
        result = self.call_ai(person.model_id, task)
        
        person.total_tokens += result.get("tokens", 0)
        person.contribution = (
            person.active_calls * 2 +
            person.passive_calls * 1.5 +
            person.adaptive_calls * 1.8 +
            person.total_tokens / 1000
        )
        person.status = "空闲"
        
        self.save_all()
        
        return {
            "success": True,
            "person": person.name,
            "result": result.get("content", ""),
            "tokens": result.get("tokens", 0)
        }
    
    def handle_passive_call(self, person_id: str, event: str) -> Dict:
        """处理被动调用"""
        if person_id not in self.persons:
            return {"success": False, "error": "人员不存在"}
        
        person = self.persons[person_id]
        person.status = "忙碌"
        person.passive_calls += 1
        person.last_active = datetime.now().isoformat()
        
        # 被动响应
        result = self.call_ai(person.model_id, f"被动响应事件: {event}")
        
        person.total_tokens += result.get("tokens", 0)
        person.status = "空闲"
        
        self.save_all()
        
        return {
            "success": True,
            "person": person.name,
            "result": result.get("content", ""),
            "type": "被动应答"
        }
    
    def handle_adaptive_call(self, person_id: str, context: Dict) -> Dict:
        """处理自适应调用"""
        if person_id not in self.persons:
            return {"success": False, "error": "人员不存在"}
        
        person = self.persons[person_id]
        person.adaptive_calls += 1
        
        # 根据上下文自动判断调用类型
        call_type = context.get("type", "主动")
        
        if call_type == "主备动":
            # 主备动切换
            new_status = "离线" if person.status == "空闲" else "空闲"
            person.status = new_status
            result = f"主备动切换: {person.name} 状态变为 {new_status}"
        else:
            result = self.call_ai(person.model_id, context.get("task", ""))
        
        person.contribution += 1.8
        self.save_all()
        
        return {"success": True, "result": result}
    
    # =========================================================================
    # 问题分析与解决
    # =========================================================================
    
    def analyze_problem(self, description: str) -> Dict:
        """AI分析问题"""
        prompt = f"""作为少府监智囊阁博士，请分析以下问题：

问题描述: {description}

请给出:
1. 问题分类
2. 优先级(高/中/低)
3. 建议解决方案
4. 预计处理时间

简洁回答:"""
        
        result = self.call_ai("ark-code-latest", prompt)
        return {"analysis": result.get("content", ""), "tokens": result.get("tokens", 0)}
    
    def create_problem(self, title: str, description: str) -> Problem:
        """创建问题"""
        problem = Problem(
            id=f"P{len(self.problems)+1:04d}",
            title=title,
            description=description,
            created_at=datetime.now().isoformat()
        )
        
        # AI分析
        analysis = self.analyze_problem(description)
        problem.solution = analysis.get("analysis", "")
        problem.status = "分析中"
        
        # 自动指派
        best = self.find_best_person("问题分析")
        if best:
            problem.assigned_to = [best.id]
            problem.status = "已指派"
            best.status = "忙碌"
        
        self.problems.append(problem)
        self.save_all()
        
        return problem
    
    def assign_problem(self, problem_id: str, person_ids: List[str]):
        """指派问题"""
        for p in self.problems:
            if p.id == problem_id:
                p.status = "解决中"
                p.assigned_to = person_ids
                for pid in person_ids:
                    if pid in self.persons:
                        self.persons[pid].status = "忙碌"
                break
        self.save_all()
    
    def resolve_problem(self, problem_id: str, solution: str, closed: bool = True):
        """解决问题"""
        for p in self.problems:
            if p.id == problem_id:
                p.status = "已关闭" if closed else "已解决"
                p.solution = solution
                p.resolved_at = datetime.now().isoformat()
                p.closed = closed
                
                # 释放人员
                for pid in p.assigned_to:
                    if pid in self.persons:
                        self.persons[pid].status = "空闲"
                break
        self.save_all()
    
    def find_best_person(self, func_id: str) -> Optional[PersonStatus]:
        """找到最适合的人员"""
        best = None
        candidates = []  # for random selection
        
        for p in self.persons.values():
            if p.status == "离线":
                continue
            for f in p.functions:
                if f["id"] == func_id and f["active"]:
                    score = f["level"] * (1.0 if p.status == "空闲" else 0.3)
                    if score > best_score:
                        best_score = score
                        best = p
        return best
    
    # =========================================================================
    # 汇报工作与自动述职
    # =========================================================================
    
    def generate_report(self, person_id: str, period: str = "日报") -> WorkReport:
        """生成工作报告"""
        if person_id not in self.persons:
            return None
        
        person = self.persons[person_id]
        
        # 统计工作
        tasks = []
        if person.active_calls > 0:
            tasks.append({"type": "主动调用", "count": person.active_calls})
        if person.passive_calls > 0:
            tasks.append({"type": "被动调用", "count": person.passive_calls})
        if person.adaptive_calls > 0:
            tasks.append({"type": "自适应调用", "count": person.adaptive_calls})
        
        # AI生成总结
        prompt = f"""作为{person.name}，请生成{period}工作总结：
- 角色: {person.role}
- 模型: {person.model_id}
- 主动调用: {person.active_calls}次
- 被动调用: {person.passive_calls}次
- 自适应调用: {person.adaptive_calls}次
- 总Token: {person.total_tokens}
- 贡献度: {person.contribution:.1f}

请用50字以内总结工作内容，并提出改进建议。"""
        
        result = self.call_ai(person.model_id, prompt)
        
        report = WorkReport(
            person_id=person_id,
            person_name=person.name,
            period=period,
            tasks=tasks,
            summary=result.get("content", "无"),
            suggestions="继续优化",
            created_at=datetime.now().isoformat()
        )
        
        self.reports.append(asdict(report))
        self.save_all()
        
        return report
    
    def auto_report_all(self, period: str = "日报") -> List[WorkReport]:
        """自动生成所有人工作报告"""
        reports = []
        for pid in self.persons.keys():
            # 只报告有工作的人员
            person = self.persons[pid]
            if person.active_calls + person.passive_calls + person.adaptive_calls > 0:
                report = self.generate_report(pid, period)
                if report:
                    reports.append(report)
        return reports
    
    # =========================================================================
    # AI调用
    # =========================================================================
    
    def call_ai(self, model_id: str, prompt: str) -> Dict:
        """调用AI模型"""
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        try:
            resp = requests.post(URL, headers=headers, json={
                "model": model_id,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500
            }, timeout=30)
            
            if resp.status_code == 200:
                result = resp.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                tokens = result.get("usage", {}).get("total_tokens", 0)
                return {"success": True, "content": content, "tokens": tokens}
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "API调用失败"}
    
    # =========================================================================
    # 统计与查询
    # =========================================================================
    
    def get_statistics(self) -> Dict:
        """获取统计"""
        total = len(self.persons)
        active = sum(p.active_calls for p in self.persons.values())
        passive = sum(p.passive_calls for p in self.persons.values())
        adaptive = sum(p.adaptive_calls for p in self.persons.values())
        
        ranking = sorted(self.persons.values(), key=lambda x: -x.contribution)[:10]
        
        open_probs = sum(1 for p in self.problems if p.status in ["待处理", "分析中", "已指派", "解决中"])
        closed_probs = sum(1 for p in self.problems if p.closed)
        
        return {
            "total_persons": total,
            "active_calls": active,
            "passive_calls": passive,
            "adaptive_calls": adaptive,
            "total_tokens": sum(p.total_tokens for p in self.persons.values()),
            "open_problems": open_probs,
            "closed_problems": closed_probs,
            "top_10": [{"name": p.name, "contribution": f"{p.contribution:.1f}", "calls": p.active_calls + p.passive_calls + p.adaptive_calls} for p in ranking]
        }

# =============================================================================
# 触发器
# =============================================================================

def trigger_example():
    """触发示例"""
    system = ShaofuJianSystem()
    
    print("="*60)
    print("少府监自适应全能系统 - 演示")
    print("="*60)
    
    # 1. 主动调用
    print("\n【1. 主动调用】")
    result = system.handle_active_call("sf-001", "请分析当前AI发展趋势")
    print(f"结果: {result['result'][:100]}...")
    
    # 2. 被动调用
    print("\n【2. 被动调用】")
    result = system.handle_passive_call("sf-001", "收到新消息提醒")
    print(f"响应: {result['result'][:100]}...")
    
    # 3. 自适应调用
    print("\n【3. 主备动切换】")
    result = system.handle_adaptive_call("sf-001", {"type": "主备动", "task": ""})
    print(f"结果: {result['result']}")
    
    # 4. 创建问题
    print("\n【4. 问题分析解决】")
    prob = system.create_problem("API配置不同步", "修改配置后未同步")
    print(f"问题: {prob.id} - {prob.title}")
    print(f"分析: {prob.solution[:100]}...")
    
    # 5. 解决问题
    system.resolve_problem(prob.id, "建立统一配置中心", closed=True)
    print("问题已闭环!")
    
    # 6. 汇报工作
    print("\n【5. 工作汇报】")
    report = system.generate_report("sf-001", "日报")
    print(f"汇报人: {report.person_name}")
    print(f"总结: {report.summary}")
    
    # 7. 统计
    print("\n【6. 统计信息】")
    stats = system.get_statistics()
    print(f"总人员: {stats['total_persons']}")
    print(f"总调用: {stats['active_calls'] + stats['passive_calls'] + stats['adaptive_calls']}")
    print(f"问题: {stats['open_problems']}待解决, {stats['closed_problems']}已闭环")
    print("\n贡献度 Top 5:")
    for t in stats['top_10'][:5]:
        print(f"  {t['name']}: {t['contribution']}分")
    
    print("\n" + "="*60)
    print("使用方法:")
    print("="*60)
    print("""
# 触发方式

## 1. 主动调用
result = system.handle_active_call("sf-001", "任务描述")

## 2. 被动调用  
result = system.handle_passive_call("sf-001", "事件描述")

## 3. 主备动切换
result = system.handle_adaptive_call("sf-001", {"type": "主备动"})

## 4. 创建问题
prob = system.create_problem("标题", "描述")

## 5. 解决问题
system.resolve_problem("P0001", "解决方案", closed=True)

## 6. 工作汇报
report = system.generate_report("sf-001", "日报")

## 7. 自动述职（所有人）
reports = system.auto_report_all("日报")

## 8. 获取统计
stats = system.get_statistics()
""")
    print("="*60)

if __name__ == "__main__":
    trigger_example()
