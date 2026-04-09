# -*- coding: utf-8 -*-
"""
Symphony Detect-Then-Team System
Model health detection + Smart team building for higher success rate
"""
import sqlite3
import requests
import time
import os
from typing import Dict, List, Optional

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

class ModelHealthDetector:
    """Model health detector - tests model availability and response time"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.test_results = {}
    
    def detect_model(self, provider_code: str, model_id: str, api_key: str, base_url: str) -> Dict:
        """Detect single model health"""
        result = {
            "model_id": model_id,
            "provider": provider_code,
            "status": "unknown",
            "latency_ms": 0,
            "score": 0,
            "error": None
        }
        
        try:
            url = f"{base_url.replace('/api/v1', '/compatible-mode/v1')}/chat/completions"
            payload = {
                "model": model_id,
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 5
            }
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            
            start = time.time()
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            latency = (time.time() - start) * 1000
            
            result["latency_ms"] = round(latency, 1)
            
            if resp.status_code == 200:
                result["status"] = "online"
                if latency < 1000:
                    result["score"] = 100
                elif latency < 3000:
                    result["score"] = 80
                else:
                    result["score"] = 60
            else:
                result["status"] = "error"
                result["error"] = f"HTTP {resp.status_code}"
                result["score"] = 0
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)[:50]
            result["score"] = 0
        
        return result
    
    def detect_provider_models(self, provider_code: str, api_key: str, base_url: str, limit: int = 10) -> List[Dict]:
        """Detect all models for a provider"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT model_id, model_name, model_type
            FROM model_config 
            WHERE provider = ? AND is_enabled = 1
            LIMIT ?
        """, (provider_code, limit))
        
        results = []
        for row in cursor.fetchall():
            model_id, model_name, model_type = row
            detection = self.detect_model(provider_code, model_id, api_key, base_url)
            detection["model_name"] = model_name
            detection["model_type"] = model_type
            results.append(detection)
        
        conn.close()
        return results
    
    def get_online_models(self) -> List[Dict]:
        """Get cached online models from previous detection"""
        results = []
        for provider_code in ["aliyun", "minimax", "zhipu", "nvidia"]:
            detection = self.detect_provider_models(provider_code, "", "", limit=3)
            results.extend([d for d in detection if d["status"] == "online"])
        return results


class SmartTeamBuilder:
    """Smart team builder - selects best models based on task type"""
    
    def __init__(self, detector: ModelHealthDetector):
        self.detector = detector
    
    def analyze_task(self, task: str) -> Dict:
        """Analyze task type"""
        task_lower = task.lower()
        
        analysis = {"type": "general", "requirements": []}
        
        if any(k in task_lower for k in ["code", "编程", "function", "def ", "class "]):
            analysis["type"] = "code"
            analysis["requirements"].append("coding")
        elif any(k in task_lower for k in ["reason", "分析", "逻辑", "reasoning"]):
            analysis["type"] = "reasoning"
            analysis["requirements"].append("reasoning")
        elif any(k in task_lower for k in ["what", "什么是", "介绍", "知识"]):
            analysis["type"] = "knowledge"
            analysis["requirements"].append("knowledge")
        elif any(k in task_lower for k in ["create", "创作", "故事", "creative"]):
            analysis["type"] = "creative"
            analysis["requirements"].append("creative")
        elif any(k in task_lower for k in ["math", "计算", "数学"]):
            analysis["type"] = "math"
            analysis["requirements"].append("math")
        
        return analysis
    
    def select_team(self, online_models: List[Dict], task_type: str, team_size: int = 3) -> List[Dict]:
        """Select best team based on task type"""
        team = []
        selected_ids = set()
        
        # Priority selection by task type
        for model in sorted(online_models, key=lambda x: -x["score"]):
            if len(team) >= team_size:
                break
            if model["model_id"] in selected_ids:
                continue
            
            # Task-specific selection
            model_name = model.get("model_name", "").lower()
            model_type = model.get("model_type", "")
            
            if task_type == "code" and ("code" in model_name or model_type == "code"):
                team.append(model)
                selected_ids.add(model["model_id"])
            elif task_type == "reasoning" and ("r1" in model_name or "reason" in model_name):
                team.append(model)
                selected_ids.add(model["model_id"])
            elif task_type == "knowledge":
                team.append(model)
                selected_ids.add(model["model_id"])
        
        # Fill with best available if needed
        if len(team) < team_size:
            for model in sorted(online_models, key=lambda x: -x["score"]):
                if len(team) >= team_size:
                    break
                if model["model_id"] not in selected_ids:
                    team.append(model)
                    selected_ids.add(model["model_id"])
        
        return team


class DetectThenTeamSystem:
    """Integrated system: detect models first, then build smart team"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.detector = ModelHealthDetector(db_path)
        self.builder = SmartTeamBuilder(self.detector)
        self.provider_config = self._load_providers()
    
    def _load_providers(self) -> Dict:
        """Load provider configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT provider_code, base_url, api_key FROM provider_registry WHERE is_enabled = 1")
        providers = {}
        for row in cursor.fetchall():
            providers[row[0]] = {"base_url": row[1].rstrip("/"), "api_key": row[2]}
        conn.close()
        return providers
    
    def detect_all_models(self) -> Dict:
        """Detect all enabled models"""
        all_results = {"providers": {}, "summary": {"total": 0, "online": 0, "offline": 0}}
        
        for provider_code, config in self.provider_config.items():
            results = self.detector.detect_provider_models(
                provider_code, 
                config["api_key"], 
                config["base_url"],
                limit=5
            )
            online = [r for r in results if r["status"] == "online"]
            all_results["providers"][provider_code] = {
                "tested": len(results),
                "online": len(online),
                "models": results
            }
            all_results["summary"]["total"] += len(results)
            all_results["summary"]["online"] += len(online)
            all_results["summary"]["offline"] += len(results) - len(online)
        
        return all_results
    
    def build_team(self, task: str, team_size: int = 3) -> Dict:
        """Build smart team for task"""
        # Step 1: Detect all models
        detection = self.detect_all_models()
        
        # Collect online models
        online_models = []
        for p_data in detection["providers"].values():
            online_models.extend(p_data["models"])
        online_models = [m for m in online_models if m["status"] == "online"]
        
        # Step 2: Analyze task
        task_analysis = self.builder.analyze_task(task)
        
        # Step 3: Select team
        team = self.builder.select_team(online_models, task_analysis["type"], team_size)
        
        return {
            "task": task,
            "task_type": task_analysis["type"],
            "online_count": len(online_models),
            "team_size": len(team),
            "team": team,
            "detection": detection
        }
    
    def execute(self, task: str, team_size: int = 3) -> Dict:
        """Detect -> Team -> Execute"""
        # Build team
        team_info = self.build_team(task, team_size)
        
        # Execute with team
        results = []
        for model in team_info["team"]:
            provider = model["provider"]
            config = self.provider_config.get(provider, {})
            if not config:
                continue
            
            try:
                url = f"{config['base_url'].replace('/api/v1', '/compatible-mode/v1')}/chat/completions"
                payload = {
                    "model": model["model_id"],
                    "messages": [{"role": "user", "content": task}],
                    "max_tokens": 500
                }
                headers = {"Authorization": f"Bearer {config['api_key']}", "Content-Type": "application/json"}
                
                start = time.time()
                resp = requests.post(url, headers=headers, json=payload, timeout=30)
                latency = (time.time() - start) * 1000
                
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"]
                    results.append({
                        "model": model["model_id"],
                        "status": "success",
                        "latency_ms": round(latency, 1),
                        "content": content[:200]
                    })
                else:
                    results.append({"model": model["model_id"], "status": "error", "error": f"HTTP {resp.status_code}"})
            except Exception as e:
                results.append({"model": model["model_id"], "status": "error", "error": str(e)[:50]})
        
        # Fusion: pick first success
        success_results = [r for r in results if r["status"] == "success"]
        final = success_results[0]["content"] if success_results else "All models failed"
        
        return {
            "team_info": team_info,
            "results": results,
            "final_result": final,
            "success_count": len(success_results)
        }


def get_system() -> DetectThenTeamSystem:
    """Get global Detect-Then-Team system instance"""
    global _system
    if '_system' not in globals():
        _system = DetectThenTeamSystem()
    return _system


if __name__ == '__main__':
    print("=" * 60)
    print(" Detect-Then-Team System Test ")
    print("=" * 60)
    
    system = DetectThenTeamSystem()
    
    # Detection test
    print("\n[1] Model Detection...")
    detection = system.detect_all_models()
    print(f"    Total tested: {detection['summary']['total']}")
    print(f"    Online: {detection['summary']['online']}")
    print(f"    Offline: {detection['summary']['offline']}")
    
    # Team building test
    print("\n[2] Team Building...")
    task = "What is 1+1? Reply with one number."
    team_info = system.build_team(task, team_size=2)
    print(f"    Task: {task}")
    print(f"    Task type: {team_info['task_type']}")
    print(f"    Online models: {team_info['online_count']}")
    print(f"    Team size: {team_info['team_size']}")
    for m in team_info["team"]:
        print(f"      - {m['model_id']} ({m['score']}pts)")
    
    # Execution test
    print("\n[3] Team Execution...")
    result = system.execute(task, team_size=2)
    print(f"    Success: {result['success_count']}/{len(result['results'])}")
    print(f"    Result: {result['final_result'][:50]}...")
    
    print("\n" + "=" * 60)
    print(" Detect-Then-Team System Ready ")
    print("=" * 60)
