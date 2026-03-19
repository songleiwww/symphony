# -*- coding: utf-8 -*-
"""
序境系统 - 智能模型检测与组队系统
先检测模型状态，再智能组队的多模型合作系统
"""
import sqlite3
import requests
import time
import json
from typing import Dict, List, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ModelHealthDetector:
    """
    模型健康检测器
    检测模型可用性、响应时间、能力评分
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.test_results = {}

    def detect_single_model(self, model_info: Dict) -> Dict:
        """检测单个模型"""
        result = {
            "model_id": model_info.get("id"),
            "model_name": model_info.get("name"),
            "status": "unknown",
            "latency": 0,
            "score": 0,
            "error": None,
            "timestamp": time.time()
        }

        try:
            api_url = model_info.get("api_url")
            api_key = model_info.get("api_key")

            headers = {
                'Authorization': 'Bearer ' + api_key,
                'Content-Type': 'application/json'
            }

            # 简单测试
            data = {
                "model": model_info.get("name"),
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 10
            }

            start = time.time()
            resp = requests.post(api_url, headers=headers, json=data, timeout=10)
            latency = time.time() - start

            result["latency"] = round(latency, 2)

            if resp.status_code == 200:
                result["status"] = "online"
                # 根据延迟评分
                if latency < 2:
                    result["score"] = 100
                elif latency < 5:
                    result["score"] = 80
                else:
                    result["score"] = 60
            else:
                result["status"] = "error"
                result["error"] = f"HTTP {resp.status_code}"
                result["score"] = 0

        except requests.Timeout:
            result["status"] = "timeout"
            result["error"] = "Timeout"
            result["score"] = 0

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            result["score"] = 0

        return result

    def detect_all_models(self) -> List[Dict]:
        """检测所有模型"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''
            SELECT id, 模型名称, API地址, API密钥
            FROM 模型配置表
            LIMIT 30
        ''')

        models = []
        for row in c.fetchall():
            models.append({
                "id": row[0],
                "name": row[1],
                "api_url": row[2],
                "api_key": row[3]
            })

        conn.close()

        results = []
        for model in models:
            result = self.detect_single_model(model)
            results.append(result)
            # 更新数据库
            self.update_model_status(model["id"], result["status"])

        return results

    def update_model_status(self, model_id: str, status: str):
        """更新模型状态"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute(
                "UPDATE 模型配置表 SET 在线状态 = ? WHERE id = ?",
                (status, model_id)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Update failed: {e}")

    def get_online_models(self) -> List[Dict]:
        """获取在线模型列表"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''
            SELECT id, 模型名称, API地址, API密钥, 在线状态
            FROM 模型配置表
            WHERE 在线状态 = 'online'
            ORDER BY id
            LIMIT 20
        ''')

        models = []
        for row in c.fetchall():
            models.append({
                "id": row[0],
                "name": row[1],
                "api_url": row[2],
                "api_key": row[3],
                "status": row[4]
            })

        conn.close()
        return models


class SmartTeamBuilder:
    """
    智能组队器
    根据任务类型和能力检测结果，智能组建模型团队
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.detector = ModelHealthDetector(db_path)

    def analyze_task_type(self, task: Dict) -> Dict:
        """分析任务类型"""
        prompt = task.get("prompt", "").lower()

        task_analysis = {
            "type": "general",
            "sub_types": [],
            "requirements": []
        }

        # 代码任务
        if any(k in prompt for k in ["code", "编程", "代码", "function", "def ", "class "]):
            task_analysis["type"] = "code"
            task_analysis["requirements"].append("coding")

        # 推理任务
        if any(k in prompt for k in ["reason", "思考", "分析", "reasoning", "逻辑"]):
            task_analysis["type"] = "reasoning"
            task_analysis["requirements"].append("reasoning")

        # 知识任务
        if any(k in prompt for k in ["what", "什么是", "介绍", "知识", "explain"]):
            task_analysis["type"] = "knowledge"
            task_analysis["requirements"].append("knowledge")

        # 创意任务
        if any(k in prompt for k in ["create", "创作", "写", "故事", "创意"]):
            task_analysis["type"] = "creative"
            task_analysis["requirements"].append("creative")

        # 数学任务
        if any(k in prompt for k in ["math", "计算", "数学", "+", "-", "*", "/"]):
            task_analysis["type"] = "math"
            task_analysis["requirements"].append("math")

        return task_analysis

    def build_team(self, task: Dict, team_size: int = 3) -> Dict:
        """智能组建团队"""
        # 1. 先检测模型
        print("Step 1: 检测模型状态...")
        online_models = self.detector.get_online_models()

        if not online_models:
            # 如果没有缓存，检测所有模型
            print("  检测所有模型...")
            results = self.detector.detect_all_models()
            online_models = [r for r in results if r["status"] == "online"]

        print(f"  在线模型数: {len(online_models)}")

        # 2. 分析任务
        task_analysis = self.analyze_task_type(task)
        print(f"Step 2: 任务分析 - 类型: {task_analysis['type']}")

        # 3. 选择模型团队
        team = []
        selected_names = set()

        # 优先选择不同类型的模型
        for model in online_models:
            if len(team) >= team_size:
                break

            model_name = model.get("name", "").lower()

            # 根据任务类型选择
            if task_analysis["type"] == "code":
                if "code" in model_name or "coder" in model_name:
                    if model["name"] not in selected_names:
                        team.append(model)
                        selected_names.add(model["name"])
            elif task_analysis["type"] == "reasoning":
                if "reason" in model_name or "r1" in model_name or "think" in model_name:
                    if model["name"] not in selected_names:
                        team.append(model)
                        selected_names.add(model["name"])
            elif task_analysis["type"] == "knowledge":
                if "glm" in model_name or "claude" in model_name or "gpt" in model_name:
                    if model["name"] not in selected_names:
                        team.append(model)
                        selected_names.add(model["name"])

        # 如果不够，补充其他模型
        if len(team) < team_size:
            for model in online_models:
                if len(team) >= team_size:
                    break
                if model["name"] not in selected_names:
                    team.append(model)
                    selected_names.add(model["name"])

        print(f"Step 3: 组队完成 - 成员: {[m['name'] for m in team]}")

        return {
            "task_analysis": task_analysis,
            "team_size": len(team),
            "team": team,
            "detection_time": time.time()
        }

    def execute_team_task(self, task: Dict, team: List[Dict]) -> Dict:
        """执行团队任务"""
        results = []

        for model in team:
            print(f"  调用模型: {model['name']}")

            try:
                headers = {
                    'Authorization': 'Bearer ' + model.get("api_key", ""),
                    'Content-Type': 'application/json'
                }

                data = {
                    "model": model.get("name"),
                    "messages": [{"role": "user", "content": task.get("prompt", "")}],
                    "max_tokens": task.get("max_tokens", 500)
                }

                start = time.time()
                resp = requests.post(
                    model.get("api_url"),
                    headers=headers,
                    json=data,
                    timeout=30
                )
                latency = time.time() - start

                if resp.status_code == 200:
                    result = resp.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

                    results.append({
                        "model_name": model["name"],
                        "status": "success",
                        "latency": round(latency, 2),
                        "content": content[:200]
                    })
                else:
                    results.append({
                        "model_name": model["name"],
                        "status": "error",
                        "error": f"HTTP {resp.status_code}"
                    })

            except Exception as e:
                results.append({
                    "model_name": model["name"],
                    "status": "error",
                    "error": str(e)
                })

        # 投票融合
        success_results = [r for r in results if r["status"] == "success"]
        if success_results:
            # 简单选择第一个成功的
            final_result = success_results[0]["content"]
            method = "first_success"
        else:
            final_result = "All models failed"
            method = "all_failed"

        return {
            "individual_results": results,
            "final_result": final_result,
            "fusion_method": method,
            "success_count": len(success_results),
            "total_count": len(team)
        }


class DetectThenTeamSystem:
    """
    检测后组队系统
    整合检测和组队的一体化系统
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
        self.db_path = db_path
        self.detector = ModelHealthDetector(db_path)
        self.builder = SmartTeamBuilder(db_path)

    def detect_models(self) -> List[Dict]:
        """检测所有模型"""
        return self.detector.detect_all_models()

    def build_and_execute(self, task: Dict, team_size: int = 3) -> Dict:
        """检测后组队并执行"""
        # 1. 检测模型
        detection = {
            "timestamp": time.time(),
            "action": "detect_and_team"
        }

        # 2. 智能组队
        team_info = self.builder.build_team(task, team_size)

        # 3. 执行任务
        execution = self.builder.execute_team_task(task, team_info["team"])

        return {
            "detection": detection,
            "team": team_info,
            "execution": execution
        }

    def get_system_status(self) -> Dict:
        """获取系统状态"""
        online = self.detector.get_online_models()
        return {
            "total_online": len(online),
            "models": [m["name"] for m in online[:10]]
        }


# 全局系统
_global_detect_team_system = None

def get_detect_then_team_system(db_path: str = None) -> DetectThenTeamSystem:
    """获取检测后组队系统"""
    global _global_detect_team_system

    if _global_detect_team_system is None:
        _global_detect_team_system = DetectThenTeamSystem(db_path)

    return _global_detect_team_system


# 测试
if __name__ == '__main__':
    db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

    print('=== Detect-Then-Team System Test ===\n')

    system = get_detect_then_team_system(db_path)

    # 查看状态
    status = system.get_system_status()
    print('System Status:')
    print(f'  Online Models: {status["total_online"]}')
    print(f'  Sample: {status["models"]}')

    # 测试组队
    print('\n=== Test Build Team ===')
    task = {
        "prompt": "你好，请介绍一下序境系统",
        "max_tokens": 100
    }

    result = system.build_and_execute(task, team_size=2)

    print('\nTeam:')
    for m in result['team']['team']:
        print(f'  - {m["name"]}')

    print('\nExecution:')
    print(f'  Success: {result["execution"]["success_count"]}/{result["execution"]["total_count"]}')
    print(f'  Method: {result["execution"]["fusion_method"]}')
