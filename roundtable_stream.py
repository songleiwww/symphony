#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境圆桌讨论引擎 - 流式版本
支持实时流式输出，增强对话真实感
"""
import sqlite3
import requests
import json
from typing import List, Dict, Generator

class RoundTableStreamEngine:
    """序境圆桌讨论流式引擎"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            import os
            self.db_path = os.path.join(
                os.path.dirname(__file__), "..", "data", "symphony.db"
            )
        else:
            self.db_path = db_path
    
    def get_participants(self, count: int = 4) -> List[Dict]:
        """获取讨论参与者"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT r.姓名, r.官职, o.名称 as 官署, m.模型名称, m.API地址, m.API密钥
            FROM 官署角色表 r
            JOIN 官署表 o ON r.所属官署 = o.id
            JOIN 模型配置表 m ON r.模型配置表_ID = m.id
            WHERE m.服务商 = '英伟达' 
            AND (m.模型名称 LIKE '%Llama 3.1%' OR m.模型名称 LIKE '%DeepSeek%')
            LIMIT {count}
        ''')
        
        participants = []
        for row in cursor.fetchall():
            participants.append({
                "name": row[0],
                "title": row[1],
                "office": row[2],
                "model": row[3],
                "api": row[4],
                "key": row[5]
            })
        conn.close()
        return participants
    
    def stream_generate(self, participant: Dict, prompt: str, context: str = "") -> Generator[str, None, None]:
        """流式生成回复"""
        headers = {
            "Authorization": "Bearer " + participant["key"],
            "Content-Type": "application/json"
        }
        
        model_map = {
            "Llama 3.1 70B": "meta/llama-3.1-70b-instruct",
            "Llama 3.1 8B": "meta/llama-3.1-8b-instruct",
            "DeepSeek R1": "deepseek-ai/deepseek-r1",
        }
        api_model = model_map.get(participant["model"], "meta/llama-3.1-70b-instruct")
        
        messages = [
            {"role": "system", "content": "你是序境官员，参与圆桌讨论。请针对前一位的观点进行回应，简洁有力。"}
        ]
        
        if context:
            messages.append({"role": "user", "content": f"上一位说：「{context}」\n\n{prompt}"})
        else:
            messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": api_model,
            "messages": messages,
            "stream": True
        }
        
        try:
            resp = requests.post(participant["api"], headers=headers, json=payload, stream=True, timeout=60)
            if resp.status_code == 200:
                for line in resp.iter_lines():
                    if line and line.startswith(b"data: "):
                        data = line[6:]
                        if data == b"[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except:
                            pass
        except Exception as e:
            yield f"[错误: {str(e)[:30]}]"
    
    def discuss(self, topic: str, participants_count: int = 4) -> Dict:
        """开始圆桌讨论（流式输出）"""
        participants = self.get_participants(participants_count)
        
        if not participants:
            return {"status": "error", "message": "No participants available"}
        
        print("=== 序境圆桌会议 (流式) ===")
        print(f"主题: {topic}")
        print(f"参与者: {len(participants)}人\n")
        
        results = []
        context = ""
        
        for i, p in enumerate(participants):
            print(f"【{p['name']}】{p['title']} ({p['office']})")
            print("  → ", end="", flush=True)
            
            if i == 0:
                prompt = topic
            else:
                prompt = "请针对上一位的观点进行补充或辩论。"
            
            full_response = ""
            for chunk in self.stream_generate(p, prompt, context):
                print(chunk, end="", flush=True)
                full_response += chunk
            
            print("\n")
            context = full_response[:200]
            results.append({
                "participant": p,
                "content": full_response
            })
        
        return {
            "status": "ok",
            "topic": topic,
            "participants": len(results),
            "results": results
        }


if __name__ == "__main__":
    engine = RoundTableStreamEngine()
    result = engine.discuss("如何让对话更加优雅时尚？", 3)
    print(f"\n=== 讨论结束 ({result.get('participants', 0)}人参与) ===")
