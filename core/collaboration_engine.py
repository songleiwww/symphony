#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
协作引擎 - 多智能体协作系统核心
"""
import time
import threading
from typing import List, Dict, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from Kernel.kernel_loader import get_kernel
from core.model_call_manager import get_model_manager
from core.task_manager import Task, TaskStatus, get_task_manager

class CollaborationMode:
    """协作模式"""
    PIPELINE = "pipeline"       # 流水线：A→B→C
    PARALLEL = "parallel"       # 并行：A、B、C同时执行
    MASTER_SLAVE = "master"     # 主从：主角色调度多个从角色
    REVIEW = "review"           # 评审：A输出→B评审→A修改

class CollaborationEngine:
    """协作引擎"""
    
    def __init__(self):
        self.kernel = get_kernel()
        self.model_manager = get_model_manager()
        self.task_manager = get_task_manager()
        self.active_collaborations: Dict[str, Dict] = {}
    
    def create_collaboration(self, task: Task, mode: str = CollaborationMode.PARALLEL, 
                           role_ids: List[str] = None, max_workers: int = 3) -> Dict:
        """创建协作任务"""
        collab_id = f"collab_{task.task_id}_{int(time.time())}"
        
        # 获取参与角色
        if role_ids is None:
            # 自动选择角色
            roles = []
            for role in self.kernel.roles[:max_workers]:
                roles.append(role)
        else:
            roles = [self.kernel.get_role_by_id(rid) for rid in role_ids if self.kernel.get_role_by_id(rid)]
        
        if not roles:
            return {"success": False, "error": "没有可用的协作角色"}
        
        collaboration = {
            "collab_id": collab_id,
            "task_id": task.task_id,
            "mode": mode,
            "roles": roles,
            "status": "created",
            "created_at": time.time(),
            "results": [],
            "errors": []
        }
        
        self.active_collaborations[collab_id] = collaboration
        return collaboration
    
    def execute_pipeline(self, collaboration: Dict, task: Task) -> Dict:
        """执行流水线协作"""
        results = []
        current_prompt = task.content
        
        for i, role in enumerate(collaboration["roles"]):
            # 第一个角色使用原始任务，后续角色使用前一角色的输出
            if i > 0 and results:
                current_prompt = f"基于前一角色的输出：{results[-1]['content'][:500]}\n\n请继续完成：{task.content}"
            
            model_name = role.get("模型名称")
            success, content, meta = self.model_manager.call_model(model_name, current_prompt)
            
            if success:
                results.append({
                    "role_id": role.get("id"),
                    "role_name": role.get("姓名"),
                    "content": content,
                    "meta": meta
                })
            else:
                collaboration["errors"].append({
                    "role_id": role.get("id"),
                    "error": content
                })
                # 故障转移：尝试下一个角色
                continue
        
        collaboration["results"] = results
        collaboration["status"] = "completed"
        return collaboration
    
    def execute_parallel(self, collaboration: Dict, task: Task) -> Dict:
        """执行并行协作"""
        results = []
        errors = []
        
        def call_role(role):
            model_name = role.get("模型名称")
            prompt = f"作为{role.get('姓名')}（{role.get('官职')}），请完成以下任务：\n{task.content}"
            
            success, content, meta = self.model_manager.call_model(model_name, prompt)
            
            if success:
                return {
                    "role_id": role.get("id"),
                    "role_name": role.get("姓名"),
                    "content": content,
                    "meta": meta,
                    "success": True
                }
            else:
                return {
                    "role_id": role.get("id"),
                    "role_name": role.get("姓名"),
                    "error": content,
                    "success": False
                }
        
        # 并行调用所有角色
        with ThreadPoolExecutor(max_workers=len(collaboration["roles"])) as executor:
            futures = {executor.submit(call_role, role): role for role in collaboration["roles"]}
            
            for future in as_completed(futures):
                result = future.result()
                if result["success"]:
                    results.append(result)
                else:
                    errors.append(result)
        
        collaboration["results"] = results
        collaboration["errors"] = errors
        collaboration["status"] = "completed"
        return collaboration
    
    def execute_master_slave(self, collaboration: Dict, task: Task) -> Dict:
        """执行主从协作"""
        if len(collaboration["roles"]) < 2:
            return {"success": False, "error": "主从模式至少需要2个角色"}
        
        master = collaboration["roles"][0]
        slaves = collaboration["roles"][1:]
        
        # 1. 主角色分解任务
        master_prompt = f"作为主调度官{master.get('姓名')}，请将以下任务分解为{len(slaves)}个子任务，每个子任务一行：\n{task.content}"
        
        success, master_content, master_meta = self.model_manager.call_model(
            master.get("模型名称"), master_prompt
        )
        
        if not success:
            collaboration["errors"].append({"role_id": master.get("id"), "error": master_content})
            return collaboration
        
        # 2. 提取子任务
        subtasks = [line.strip() for line in master_content.split('\n') if line.strip()][:len(slaves)]
        
        if not subtasks:
            # 如果主角色没有分解出子任务，直接分配
            subtasks = [task.content] * len(slaves)
        
        # 3. 从角色并行执行子任务
        results = []
        for i, slave in enumerate(slaves):
            subtask = subtasks[i] if i < len(subtasks) else task.content
            
            success, content, meta = self.model_manager.call_model(
                slave.get("模型名称"), 
                f"执行子任务：{subtask}"
            )
            
            if success:
                results.append({
                    "role_id": slave.get("id"),
                    "role_name": slave.get("姓名"),
                    "content": content,
                    "meta": meta
                })
            else:
                collaboration["errors"].append({
                    "role_id": slave.get("id"),
                    "error": content
                })
        
        # 4. 主角色汇总结果
        summary_prompt = f"请汇总以下{len(results)}个角色的执行结果：\n"
        for r in results:
            summary_prompt += f"\n{r['role_name']}: {r['content'][:300]}...\n"
        summary_prompt += "\n请给出最终总结。"
        
        success, summary, summary_meta = self.model_manager.call_model(
            master.get("模型名称"), summary_prompt
        )
        
        if success:
            collaboration["summary"] = summary
            collaboration["results"] = results
        
        collaboration["status"] = "completed"
        return collaboration
    
    def execute_review(self, collaboration: Dict, task: Task) -> Dict:
        """执行评审协作"""
        if len(collaboration["roles"]) < 2:
            return {"success": False, "error": "评审模式至少需要2个角色"}
        
        creator = collaboration["roles"][0]
        reviewer = collaboration["roles"][1]
        
        # 1. 创建者生成初稿
        success, draft, draft_meta = self.model_manager.call_model(
            creator.get("模型名称"),
            f"请完成以下任务：{task.content}"
        )
        
        if not success:
            collaboration["errors"].append({"role_id": creator.get("id"), "error": draft})
            return collaboration
        
        # 2. 评审者审核
        success, review, review_meta = self.model_manager.call_model(
            reviewer.get("模型名称"),
            f"请审核以下内容并提出修改建议：\n{draft}\n\n请指出问题并给出具体的修改建议。"
        )
        
        if not success:
            collaboration["errors"].append({"role_id": reviewer.get("id"), "error": review})
            # 即使评审失败，也保留初稿
            collaboration["results"] = [{
                "role_id": creator.get("id"),
                "role_name": creator.get("姓名"),
                "content": draft,
                "meta": draft_meta
            }]
            return collaboration
        
        # 3. 创建者根据评审修改
        success, final, final_meta = self.model_manager.call_model(
            creator.get("模型名称"),
            f"根据评审意见：{review}\n\n请修改以下内容：\n{draft}"
        )
        
        if success:
            collaboration["results"] = [{
                "role_id": creator.get("id"),
                "role_name": creator.get("姓名"),
                "content": final,
                "meta": final_meta,
                "draft": draft,
                "review": review
            }]
        else:
            collaboration["results"] = [{
                "role_id": creator.get("id"),
                "role_name": creator.get("姓名"),
                "content": draft,
                "meta": draft_meta
            }]
        
        collaboration["status"] = "completed"
        return collaboration
    
    def run_collaboration(self, collab_id: str) -> Dict:
        """运行协作任务"""
        if collab_id not in self.active_collaborations:
            return {"success": False, "error": "协作任务不存在"}
        
        collaboration = self.active_collaborations[collab_id]
        task = self.task_manager.get_task(collaboration["task_id"])
        
        if not task:
            return {"success": False, "error": "关联任务不存在"}
        
        collaboration["status"] = "running"
        
        # 根据模式执行
        mode = collaboration["mode"]
        
        if mode == CollaborationMode.PIPELINE:
            return self.execute_pipeline(collaboration, task)
        elif mode == CollaborationMode.PARALLEL:
            return self.execute_parallel(collaboration, task)
        elif mode == CollaborationMode.MASTER_SLAVE:
            return self.execute_master_slave(collaboration, task)
        elif mode == CollaborationMode.REVIEW:
            return self.execute_review(collaboration, task)
        else:
            return {"success": False, "error": f"未知协作模式: {mode}"}
    
    def get_collaboration_result(self, collab_id: str) -> Optional[Dict]:
        """获取协作结果"""
        return self.active_collaborations.get(collab_id)

# 单例实例
_collab_engine_instance: Optional[CollaborationEngine] = None

def get_collaboration_engine() -> CollaborationEngine:
    """获取协作引擎单例"""
    global _collab_engine_instance
    if _collab_engine_instance is None:
        _collab_engine_instance = CollaborationEngine()
    return _collab_engine_instance

if __name__ == "__main__":
    # 测试协作引擎
    engine = get_collaboration_engine()
    
    # 创建测试任务
    test_task = Task(
        task_id="test_collab_001",
        content="分析多智能体协作系统的优势和挑战",
        created_by="test"
    )
    
    # 创建并行协作
    collab = engine.create_collaboration(test_task, CollaborationMode.PARALLEL, max_workers=2)
    print(f"创建协作: {collab['collab_id']}")
    print(f"参与角色: {[r.get('姓名') for r in collab['roles']]}")
