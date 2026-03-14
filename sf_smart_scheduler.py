#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Model Scheduler - Provider Policy + API Health + History
"""
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List

API_KEY = "3b922877-3fbe-45d1-a298-53f2231c5224"
URL = "https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions"

# Provider policies
PROVIDER_POLICIES = {
    "火山引擎": {"priority": 1, "rate": "unlimited", "cost": "subscription", "fallback": ["硅基流动", "智谱"]},
    "智谱": {"priority": 2, "rate": "tiered", "cost": "tiered", "fallback": ["火山引擎", "硅基流动"]},
    "魔搭": {"priority": 3, "rate": "2000/day", "cost": "free", "fallback": ["火山引擎", "硅基流动"]},
    "英伟达": {"priority": 4, "rate": "100/min", "cost": "pay", "fallback": ["火山引擎", "智谱"]},
    "魔力方舟": {"priority": 5, "rate": "100/day", "cost": "free", "fallback": ["火山引擎", "魔搭"]},
    "硅基流动": {"priority": 2, "rate": "1M/day", "cost": "free", "fallback": ["火山引擎", "智谱"]},
    "OpenRouter": {"priority": 6, "rate": "20/min", "cost": "free", "fallback": ["火山引擎", "智谱"]}
}

class SmartScheduler:
    def __init__(self):
        self.data_dir = Path(r"C:\Users\Administrator\.openclaw\workspace\skills\symphony")
        self.roster_file = self.data_dir / "sf_team_roster.json"
        self.api_health_file = self.data_dir / "sf_api_health.json"
        self.history_file = self.data_dir / "sf调度_history.json"
        
    def check_api(self, provider):
        configs = {
            "火山引擎": {"url": URL, "key": API_KEY, "model": "ark-code-latest"},
            "智谱": {"url": "https://open.bigmodel.cn/api/paas/v4/chat/completions", "key": "16cf0a4a775c46cfa1684abcf4b802d0.rtb4oMgpFocBy87y", "model": "glm-4"},
            "硅基流动": {"url": "https://api.siliconflow.cn/v1/chat/completions", "key": "sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc", "model": "Qwen/Qwen2.5-7B-Instruct"}
        }
        if provider not in configs:
            return {"status": "unknown", "latency": 0}
        cfg = configs[provider]
        try:
            start = datetime.now()
            resp = requests.post(cfg["url"], headers={"Authorization": f"Bearer {cfg['key']}", "Content-Type": "application/json"},
                json={"model": cfg["model"], "messages": [{"role": "user", "content": "hi"}], "max_tokens": 10}, timeout=10)
            latency = (datetime.now() - start).total_seconds()
            return {"status": "正常" if resp.status_code == 200 else f"错误{resp.status_code}", "latency": latency}
        except Exception as e:
            return {"status": "失败", "latency": 0}
    
    def update_health(self):
        health = {"providers": {}, "updated": datetime.now().isoformat()}
        for p in PROVIDER_POLICIES:
            health["providers"][p] = self.check_api(p)
        self.api_health_file.write_text(json.dumps(health, ensure_ascii=False, indent=2), encoding="utf-8")
        return health
    
    def update_roster_status(self):
        roster = json.loads(self.roster_file.read_text(encoding="utf-8"))
        health = self.update_health()
        
        for m in roster.get("team", []):
            provider = m.get("服务商", "")
            if provider in PROVIDER_POLICIES:
                policy = PROVIDER_POLICIES[provider]
                h = health.get("providers", {}).get(provider, {})
                status = h.get("status", "未知")
                m["状态"] = status
                m["当前策略"] = f"切换{policy.get('fallback', ['无'])[0]}" if status == "限流" else "正常"
            else:
                m["状态"] = "未知"
                m["当前策略"] = "默认"
        
        roster["version"] = "10.0"
        roster["updated"] = datetime.now().isoformat()
        self.roster_file.write_text(json.dumps(roster, ensure_ascii=False, indent=2), encoding="utf-8")
        return roster

def main():
    print("="*50)
    print("Smart Model Scheduler")
    print("="*50)
    s = SmartScheduler()
    h = s.update_health()
    for p, st in h.get("providers", {}).items():
        print(f"{p}: {st.get('status')} ({st.get('latency', 0):.2f}s)")
    r = s.update_roster_status()
    print(f"\nUpdated {len(r['team'])} members")
    for m in r["team"][:3]:
        print(f"  {m['name']}: 状态={m.get('状态')}, 策略={m.get('当前策略')}")
    print("="*50)

if __name__ == "__main__":
    main()
