#!/usr/bin/env python3
# 序境技能适配层 V2 - 所有技能AI调用统一经由symphony_scheduler调度
import sys
import sqlite3
import requests
import json
import os
from typing import Optional, Dict, List

DB_PATH = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"
PRIORITY_ORDER = ["aliyun", "minimax", "zhipu", "nvidia"]

def get_enabled_providers() -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT provider_code, provider_name, base_url, api_key FROM provider_registry WHERE is_enabled = 1")
    providers = []
    for row in cursor.fetchall():
        providers.append({"code": row[0], "name": row[1], "base_url": row[2].rstrip("/"), "api_key": row[3]})
    conn.close()
    return sorted(providers, key=lambda p: PRIORITY_ORDER.index(p["code"]))

def get_suitable_model(provider_code: str, min_context_window: int = 2048) -> Optional[Dict]:
    """获取合适模型：优先chat类型，fallback到text类型"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 优先chat类型模型（阿里云等主使用chat类型）
    cursor.execute("""
        SELECT model_id, model_name, model_type, context_window, max_tokens, is_free
        FROM model_config 
        WHERE provider = ? AND is_enabled = 1 AND model_type = 'chat' AND context_window >= ?
        ORDER BY context_window DESC, is_free DESC LIMIT 1
    """, (provider_code, min_context_window))
    row = cursor.fetchone()
    if row:
        conn.close()
        return {"model_id": row[0], "model_name": row[1], "model_type": row[2], "context_window": row[3], "max_tokens": row[4], "is_free": row[5]}
    # Fallback: text类型模型
    cursor.execute("""
        SELECT model_id, model_name, model_type, context_window, max_tokens, is_free
        FROM model_config 
        WHERE provider = ? AND is_enabled = 1 AND model_type = 'text' AND context_window >= ?
        ORDER BY context_window DESC, is_free DESC LIMIT 1
    """, (provider_code, min_context_window))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {"model_id": row[0], "model_name": row[1], "model_type": row[2], "context_window": row[3], "max_tokens": row[4], "is_free": row[5]}

def call_model(provider: Dict, model: Dict, prompt: str, max_tokens: int = 1024) -> Optional[str]:
    try:
        payload = {"model": model["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7, "stream": False}
        if provider["code"] == "aliyun":
            url = f"{provider['base_url'].replace('/api/v1', '/compatible-mode/v1')}/chat/completions"
        else:
            url = f"{provider['base_url']}/chat/completions"
        headers = {"Authorization": f"Bearer {provider['api_key']}", "Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[SymphonyAdapter] {provider['name']} {model['model_name']} failed: {e}")
        return None

def symphony_call(prompt: str, min_context_window: int = 2048, max_tokens: int = 1024) -> Optional[str]:
    """统一入口：所有技能AI调用经由symphony调度"""
    providers = get_enabled_providers()
    for provider in providers:
        model = get_suitable_model(provider["code"], min_context_window)
        if not model:
            continue
        result = call_model(provider, model, prompt, max_tokens)
        if result:
            return result
    return None

# ==================== 技能集成接口 ====================

def skill_explain_code(code: str, context: str = "") -> dict:
    """explain-code技能：对代码进行可视化解释"""
    prompt = f"用图表和类比解释以下代码的工作原理：\n```{code}```"
    if context:
        prompt += f"\n\n上下文：{context}"
    result = symphony_call(prompt, min_context_window=8192, max_tokens=2048)
    return {"success": result is not None, "result": result, "skill": "explain-code"}

def skill_code_review(code: str, language: str = "通用") -> dict:
    """code-review-fix技能：代码审查"""
    prompt = f"对以下{language}代码进行审查，指出潜在问题和改进建议：\n```{code}```"
    result = symphony_call(prompt, min_context_window=8192, max_tokens=2048)
    return {"success": result is not None, "result": result, "skill": "code-review-fix"}

def skill_task_plan(task: str, constraints: str = "") -> dict:
    """任务规划：分解复杂任务为可执行步骤"""
    prompt = f"将以下任务分解为详细的执行步骤（包含先后顺序和依赖关系）：\n{task}"
    if constraints:
        prompt += f"\n\n约束条件：{constraints}"
    result = symphony_call(prompt, min_context_window=4096, max_tokens=2048)
    return {"success": result is not None, "result": result, "skill": "task-planning"}

def skill_search_analyze(search_results: str, query: str) -> dict:
    """搜索结果AI分析总结"""
    prompt = f"根据以下搜索查询和结果，进行分析和总结：\n查询：{query}\n\n结果：{search_results}"
    result = symphony_call(prompt, min_context_window=4096, max_tokens=2048)
    return {"success": result is not None, "result": result, "skill": "search-analysis"}

def skill_automation_design(task_description: str) -> dict:
    """自动化工作流设计"""
    prompt = f"为以下重复性任务设计自动化工作流（包括触发条件、步骤、错误处理）：\n{task_description}"
    result = symphony_call(prompt, min_context_window=4096, max_tokens=2048)
    return {"success": result is not None, "result": result, "skill": "automation-design"}

if __name__ == "__main__":
    print("[SymphonyAdapter V2] 序境技能适配层 - 调度测试")
    result = symphony_call("Reply with exactly 'OK' in one word", max_tokens=20)
    if result:
        print(f"SUCCESS: {result}")
    else:
        print("FAILED: All providers returned errors")
