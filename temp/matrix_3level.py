#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统 - 3级矩阵 + 组合技能
真实模型调用 + 多技能组合
"""
import sqlite3
import requests
from datetime import datetime

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

# ==================== 技能层 ====================

class Skill:
    """技能基类"""
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    def execute(self, context):
        raise NotImplementedError

class WebSearchSkill(Skill):
    """搜索技能"""
    def __init__(self):
        super().__init__("web_search", "网络搜索")
    
    def execute(self, context):
        query = context.get("query", "")
        # 模拟搜索
        return {"skill": self.name, "result": f"搜索结果: {query}的相关信息"}

class LLMCallSkill(Skill):
    """LLM调用技能"""
    def __init__(self):
        super().__init__("llm_call", "大模型调用")
    
    def execute(self, context):
        model_id = context.get("model_id", 56)
        prompt = context.get("prompt", "")
        
        # 获取模型配置
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT 模型名称, 模型标识符, 服务商, API地址, API密钥 FROM 模型配置表 WHERE id = ?", (model_id,))
        row = c.fetchone()
        conn.close()
        
        if not row:
            return {"skill": self.name, "error": "No model config"}
        
        model_name, api_id, provider, api_url, api_key = row
        
        # 调用API
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": api_id, "messages": [{"role": "user", "content": prompt}], "max_tokens": 100}
        
        try:
            resp = requests.post(api_url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                result = resp.json()
                content = result["choices"][0]["message"]["content"]
                return {"skill": self.name, "result": content, "model": model_name, "provider": provider}
            else:
                return {"skill": self.name, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"skill": self.name, "error": str(e)}

class MemorySkill(Skill):
    """记忆技能"""
    def __init__(self):
        super().__init__("memory", "记忆存储")
    
    def execute(self, context):
        content = context.get("content", "")
        # 记录到记忆表
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO 记忆表 (content, memory_type, created_at, last_accessed) VALUES (?, 'short_term', ?, ?)", 
                  (content, datetime.now().timestamp(), datetime.now().timestamp()))
        conn.commit()
        conn.close()
        return {"skill": self.name, "result": "记忆已存储"}

# 技能注册
SKILLS = {
    "search": WebSearchSkill(),
    "llm": LLMCallSkill(),
    "memory": MemorySkill()
}

# ==================== Agent层 ====================

class Agent:
    """Agent大脑 - 任务规划与技能调度"""
    
    def __init__(self):
        self.name = "陆念昭"
        self.role = "少府监"
    
    def plan(self, user_input):
        """任务规划 - 识别需要哪些技能"""
        skills = []
        
        # 简单关键词匹配
        if any(w in user_input for w in ["搜索", "找", "查"]):
            skills.append("search")
        if any(w in user_input for w in ["分析", "回答", "解释"]):
            skills.append("llm")
        if any(w in user_input for w in ["记住", "存储"]):
            skills.append("memory")
        
        # 默认启用LLM
        if not skills:
            skills.append("llm")
        
        return skills
    
    def execute(self, user_input):
        """执行任务"""
        print("=" * 60)
        print("🔄 序境3级矩阵 - 组合技能调用")
        print("=" * 60)
        
        # 1集: 模型治理 - 选择Agent
        print(f"\n📡 第1集: 模型治理 - 选中{self.name}({self.role})")
        
        # 2集: 架构优化 - 技能规划
        plan = self.plan(user_input)
        print(f"\n🛡️ 第2集: 架构优化 - 技能规划")
        print(f"   需要技能: {', '.join(plan)}")
        
        # 3集: 组合技能执行
        print(f"\n⚡ 第3集: 组合技能执行")
        
        context = {"query": user_input, "prompt": user_input, "model_id": 56}
        results = []
        
        for skill_name in plan:
            skill = SKILLS.get(skill_name)
            if skill:
                print(f"   🔧 执行技能: {skill.name}")
                result = skill.execute(context)
                results.append(result)
                if "result" in result:
                    print(f"      ✅ {result.get('result', '')[:50]}...")
        
        print("\n" + "=" * 60)
        print("✅ 组合技能执行完成")
        print("=" * 60)
        
        return results

# ==================== 执行 ====================

if __name__ == "__main__":
    agent = Agent()
    
    # 测试组合技能
    test_input = "搜索最新AI新闻并回答问题，然后记住这个任务"
    results = agent.execute(test_input)
    
    print("\n=== 执行结果 ===")
    for r in results:
        print(f"  {r}")
