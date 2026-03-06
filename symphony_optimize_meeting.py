#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响工具优化会议 - 3个真实模型
主题：优化symphony工具与OpenClaw的结合度
"""

import json
import requests
from pathlib import Path
from datetime import datetime


def main():
    log_file = Path(__file__).parent / "outputs" / "symphony_optimize_meeting_log.txt"
    log_file.parent.mkdir(exist_ok=True)
    log_file.write_text("", encoding='utf-8')
    
    def log(msg):
        with open(log_file, "a", encoding='utf-8') as f:
            f.write(msg + "\n")
    
    # 加载配置
    config_path = Path(r"C:\Users\Administrator\.openclaw\openclaw.cherry.json")
    config = json.loads(config_path.read_text(encoding='utf-8'))
    
    # 3个专家配置
    experts = [
        {"name": "系统架构师", "provider": "cherry-doubao", "model": "deepseek-v3.2", "focus": "系统架构设计"},
        {"name": "OpenClaw集成专家", "provider": "cherry-doubao", "model": "kimi-k2.5", "focus": "OpenClaw深度集成"},
        {"name": "API设计专家", "provider": "cherry-doubao", "model": "glm-4.7", "focus": "API设计优化"},
    ]
    
    topic = "symphony工具与OpenClaw结合度优化"
    
    log("=" * 70)
    log("🎼 交响工具优化会议 - 3个真实模型")
    log("=" * 70)
    log(f"主题: {topic}")
    log(f"参与专家: {len(experts)}位")
    log("")
    
    # 第一轮：各自发表观点
    log("\n" + "=" * 70)
    log("第一轮：各专家发表观点")
    log("=" * 70 + "\n")
    
    first_round_results = []
    
    for i, expert in enumerate(experts, 1):
        log(f"【{expert['name']}】发言中...")
        
        prompt = f"""你是{expert['name']}，专注于{expert['focus']}。

symphony工具路径: C:\\Users\\Administrator\\.openclaw\\workspace\\skills\\symphony
OpenClaw配置: C:\\Users\\Administrator\\.openclaw\\openclaw.cherry.json

会议主题：优化symphony工具与OpenClaw的结合度

请从你的专业角度提出具体的优化建议，包括：
1. 当前存在的问题
2. 具体的优化方案
3. 实施优先级

请用中文回复，300-400字。"""
        
        provider = config["models"]["providers"][expert["provider"]]
        api_key = provider["apiKey"]
        base_url = provider["baseUrl"]
        
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        data = {"model": expert["model"], "messages": [{"role": "user", "content": prompt}], "max_tokens": 800}
        
        url = f"{base_url}/chat/completions"
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=120)
            if response.status_code == 200:
                result_data = response.json()
                content = result_data["choices"][0]["message"]["content"]
                usage = result_data.get("usage", {})
                tokens = usage.get("total_tokens", 0)
                
                log(f"  ✅ 完成! Tokens: {tokens}")
                first_round_results.append({"expert": expert["name"], "response": content, "success": True})
            else:
                log(f"  ❌ 失败: HTTP {response.status_code}")
                first_round_results.append({"expert": expert["name"], "response": f"HTTP {response.status_code}", "success": False})
        except Exception as e:
            log(f"  ❌ 异常: {e}")
            first_round_results.append({"expert": expert["name"], "response": str(e), "success": False})
        
        log("")
    
    # 显示第一轮结果
    log("\n" + "=" * 70)
    log("第一轮发言汇总")
    log("=" * 70)
    
    for r in first_round_results:
        log(f"\n### {r['expert']}")
        if r['success']:
            log(r['response'][:500] + "..." if len(r['response']) > 500 else r['response'])
    
    # 第二轮：讨论与综合
    log("\n\n" + "=" * 70)
    log("第二轮：综合讨论与总结")
    log("=" * 70 + "\n")
    
    # 汇总所有观点
    summary_prompt = f"""你是OpenClaw集成专家。请综合以下3位专家的建议，给出最终的优化方案：

"""
    
    for r in first_round_results:
        if r['success']:
            summary_prompt += f"【{r['expert']}】\n{r['response'][:300]}\n\n"
    
    summary_prompt += """
请给出：
1. 最关键的3个优化点（按优先级排序）
2. 每个优化点的具体实施步骤
3. 预期的效果

请用中文回复，400-500字。"""
    
    # 让最后一个专家做总结
    final_expert = experts[-1]
    log(f"【{final_expert['name']}】总结中...")
    
    provider = config["models"]["providers"][final_expert["provider"]]
    api_key = provider["apiKey"]
    base_url = provider["baseUrl"]
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": final_expert["model"], "messages": [{"role": "user", "content": summary_prompt}], "max_tokens": 1000}
    
    url = f"{base_url}/chat/completions"
    
    final_result = {}
    try:
        response = requests.post(url, headers=headers, json=data, timeout=120)
        if response.status_code == 200:
            result_data = response.json()
            content = result_data["choices"][0]["message"]["content"]
            usage = result_data.get("usage", {})
            tokens = usage.get("total_tokens", 0)
            
            log(f"  ✅ 总结完成! Tokens: {tokens}")
            final_result = {"success": True, "response": content, "tokens": tokens}
        else:
            log(f"  ❌ 失败: HTTP {response.status_code}")
            final_result = {"success": False}
    except Exception as e:
        log(f"  ❌ 异常: {e}")
        final_result = {"success": False}
    
    # 显示最终总结
    if final_result.get("success"):
        log("\n" + "=" * 70)
        log("🎯 最终优化方案")
        log("=" * 70)
        log(final_result["response"])
    
    # 保存结果
    output = {
        "topic": topic,
        "timestamp": datetime.now().isoformat(),
        "first_round": first_round_results,
        "final_result": final_result
    }
    
    outfile = Path(__file__).parent / "outputs" / f"symphony_optimize_meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    outfile.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
    log(f"\n\n会议记录已保存到: {outfile}")
    
    log("\n🎼 优化会议完成!")


if __name__ == "__main__":
    main()
