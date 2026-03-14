#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响工具优化开发 - 4个真实模型
主题：优化symphony工具与OpenClaw的结合度
"""

import json
import requests
from pathlib import Path
from datetime import datetime


def main():
    log_file = Path(__file__).parent / "outputs" / "optimize_symphony_log.txt"
    log_file.parent.mkdir(exist_ok=True)
    log_file.write_text("", encoding='utf-8')
    
    def log(msg):
        with open(log_file, "a", encoding='utf-8') as f:
            f.write(msg + "\n")
    
    # 加载配置
    config_path = Path(r"C:\Users\Administrator\.openclaw\openclaw.cherry.json")
    config = json.loads(config_path.read_text(encoding='utf-8'))
    
    # 4个专家配置
    experts = [
        {"name": "系统架构师", "provider": "cherry-doubao", "model": "deepseek-v3.2", "role": "设计系统架构"},
        {"name": "OpenClaw集成专家", "provider": "cherry-doubao", "model": "kimi-k2.5", "role": "OpenClaw集成优化"},
        {"name": "API设计专家", "provider": "cherry-doubao", "model": "glm-4.7", "role": "API设计优化"},
        {"name": "测试工程师", "provider": "cherry-minimax", "model": "MiniMax-M2.5", "role": "测试与质量保证"},
    ]
    
    topic = "优化symphony工具与OpenClaw的结合度，提高使用配合度"
    
    log("=" * 70)
    log("交响工具优化开发 - 4个真实模型")
    log("=" * 70)
    log(f"主题: {topic}")
    log(f"专家数量: {len(experts)}")
    log("")
    
    results = []
    total_tokens = 0
    total_cost = 0.0
    
    for i, expert in enumerate(experts, 1):
        log(f"[{i}/{len(experts)}] {expert['name']} 正在思考...")
        
        prompt = f"""你是{expert['name']}。{expert['role']}

背景：
symphony工具位于: C:\\Users\\Administrator\\.openclaw\\workspace\\skills\\symphony
OpenClaw配置文件: C:\\Users\\Administrator\\.openclaw\\openclaw.cherry.json

优化目标：
- 提高symphony工具与OpenClaw的结合度
- 优化工具使用配合度
- 实现更有效的开发

具体优化方向：
1. 如何让AI模型更容易发现和使用symphony工具
2. 如何优化工具参数设计使其更符合OpenClaw规范
3. 如何实现更好的错误处理和反馈机制
4. 如何与OpenClaw的消息系统、memory系统更好集成

请给出具体的优化建议和代码示例，300-500字，用中文回复。"""
        
        provider = config["models"]["providers"][expert["provider"]]
        api_key = provider["apiKey"]
        base_url = provider["baseUrl"]
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": expert["model"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        }
        
        url = f"{base_url}/chat/completions"
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=120)
            
            if response.status_code == 200:
                result_data = response.json()
                content = result_data["choices"][0]["message"]["content"]
                usage = result_data.get("usage", {})
                
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                tokens = usage.get("total_tokens", 0)
                cost = (tokens / 1000) * 0.01
                
                log(f"  ✅ 成功! Tokens: {tokens}, 成本: ${cost:.4f}")
                
                results.append({
                    "expert": expert["name"],
                    "role": expert["role"],
                    "model": expert["model"],
                    "response": content,
                    "success": True
                })
                
                total_tokens += tokens
                total_cost += cost
            else:
                log(f"  ❌ 失败: HTTP {response.status_code}")
                results.append({
                    "expert": expert["name"],
                    "role": expert["role"],
                    "model": expert["model"],
                    "response": f"HTTP {response.status_code}",
                    "success": False
                })
        except Exception as e:
            log(f"  ❌ 异常: {e}")
            results.append({
                "expert": expert["name"],
                "role": expert["role"],
                "model": expert["model"],
                "response": str(e),
                "success": False
            })
        
        log("")
    
    log("=" * 70)
    log("优化建议汇总")
    log("=" * 70)
    
    for r in results:
        log(f"\n### {r['expert']} ({r['role']})")
        log(f"模型: {r['model']}")
        if r['success']:
            log(f"\n{r['response']}")
    
    log("\n" + "=" * 70)
    log("统计")
    log("=" * 70)
    log(f"总Tokens: {total_tokens}")
    log(f"总成本: ${total_cost:.4f}")
    
    # 保存结果
    output = {
        "topic": topic,
        "timestamp": datetime.now().isoformat(),
        "experts": len(experts),
        "results": results,
        "total_tokens": total_tokens,
        "total_cost": total_cost
    }
    
    outfile = Path(__file__).parent / "outputs" / f"optimize_symphony_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    outfile.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
    log(f"\n结果已保存到: {outfile}")
    
    log("\n优化开发完成!")


if __name__ == "__main__":
    main()
