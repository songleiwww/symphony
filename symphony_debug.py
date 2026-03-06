#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony Debug任务 - 3个真实模型
"""

import json
import requests
from pathlib import Path
from datetime import datetime


def main():
    log_file = Path(__file__).parent / "outputs" / "debug_task_log.txt"
    log_file.parent.mkdir(exist_ok=True)
    log_file.write_text("", encoding='utf-8')
    
    def log(msg):
        with open(log_file, "a", encoding='utf-8') as f:
            f.write(msg + "\n")
    
    config_path = Path(r"C:\Users\Administrator\.openclaw\openclaw.cherry.json")
    config = json.loads(config_path.read_text(encoding='utf-8'))
    
    # 3个专家
    experts = [
        {"name": "测试工程师", "provider": "cherry-doubao", "model": "deepseek-v3.2", "task": "Debug测试BrainstormPanel"},
        {"name": "代码审查员", "provider": "cherry-doubao", "model": "kimi-k2.5", "task": "识别模拟相关代码并列出需删除文件"},
        {"name": "架构师", "provider": "cherry-doubao", "model": "glm-4.7", "task": "整合修复方案并验证"},
    ]
    
    log("=" * 70)
    log("🎼 Symphony Debug任务 - 3个真实模型")
    log("=" * 70)
    log("任务: Debug测试 + 修复 + 清理模拟代码")
    log("")
    
    results = []
    
    # 第一轮：Debug测试
    log("\n【第一轮】Debug测试\n")
    
    prompt1 = f"""你是测试工程师。

symphony工具路径: C:\\Users\\Administrator\\.openclaw\\workspace\\skills\\symphony

任务：对BrainstormPanel进行Debug测试

1. 首先列出symphony目录下的所有Python文件
2. 检查每个文件是否有模拟/模拟调用相关的代码
3. 尝试运行brainstorm_panel_v2.py测试真实模型调用
4. 列出发现的问题

请详细检查并报告。"""
    
    expert1 = experts[0]
    provider = config["models"]["providers"][expert1["provider"]]
    headers = {"Authorization": f"Bearer {provider['apiKey']}", "Content-Type": "application/json"}
    data = {"model": expert1["model"], "messages": [{"role": "user", "content": prompt1}], "max_tokens": 1500}
    
    log(f"【{expert1['name']}】测试中...")
    try:
        response = requests.post(f"{provider['baseUrl']}/chat/completions", headers=headers, json=data, timeout=120)
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            tokens = response.json().get("usage", {}).get("total_tokens", 0)
            log(f"  ✅ 完成! Tokens: {tokens}")
            results.append({"expert": expert1["name"], "task": expert1["task"], "result": content, "success": True})
        else:
            log(f"  ❌ 失败: HTTP {response.status_code}")
            results.append({"expert": expert1["name"], "task": expert1["task"], "result": f"HTTP {response.status_code}", "success": False})
    except Exception as e:
        log(f"  ❌ 异常: {e}")
        results.append({"expert": expert1["name"], "task": expert1["task"], "result": str(e), "success": False})
    
    log("")
    
    # 第二轮：识别需删除文件
    log("\n【第二轮】识别模拟代码和需删除文件\n")
    
    prompt2 = f"""你是代码审查员。

symphony工具目录: C:\\Users\\Administrator\\.openclaw\\workspace\\skills\\symphony

基于以下测试报告，请：
1. 列出所有包含模拟/simulated/mock相关代码的文件
2. 列出所有可以删除的测试文件或无用文件
3. 给出具体的删除建议

测试报告：
{results[0].get('result', '无')[:1000]}

请用中文详细列出。"""
    
    expert2 = experts[1]
    provider = config["models"]["providers"][expert2["provider"]]
    headers = {"Authorization": f"Bearer {provider['apiKey']}", "Content-Type": "application/json"}
    data = {"model": expert2["model"], "messages": [{"role": "user", "content": prompt2}], "max_tokens": 1500}
    
    log(f"【{expert2['name']}】分析中...")
    try:
        response = requests.post(f"{provider['baseUrl']}/chat/completions", headers=headers, json=data, timeout=120)
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            tokens = response.json().get("usage", {}).get("total_tokens", 0)
            log(f"  ✅ 完成! Tokens: {tokens}")
            results.append({"expert": expert2["name"], "task": expert2["task"], "result": content, "success": True})
        else:
            log(f"  ❌ 失败: HTTP {response.status_code}")
            results.append({"expert": expert2["name"], "task": expert2["task"], "result": f"HTTP {response.status_code}", "success": False})
    except Exception as e:
        log(f"  ❌ 异常: {e}")
        results.append({"expert": expert2["name"], "task": expert2["task"], "result": str(e), "success": False})
    
    log("")
    
    # 第三轮：整合修复方案
    log("\n【第三轮】整合修复方案\n")
    
    prompt3 = f"""你是架构师。

symphony工具目录: C:\\Users\\Administrator\\.openclaw\\workspace\\skills\\symphony

请基于以下分析，给出：
1. 具体的修复步骤
2. 需要删除的文件列表（带文件路径）
3. 需要修改的文件和修改内容
4. 修复后的目录结构

分析报告：
{results[1].get('result', '无')[:1000]}

请用中文详细列出修复方案。"""
    
    expert3 = experts[2]
    provider = config["models"]["providers"][expert3["provider"]]
    headers = {"Authorization": f"Bearer {provider['apiKey']}", "Content-Type": "application/json"}
    data = {"model": expert3["model"], "messages": [{"role": "user", "content": prompt3}], "max_tokens": 1500}
    
    log(f"【{expert3['name']}】整合方案中...")
    try:
        response = requests.post(f"{provider['baseUrl']}/chat/completions", headers=headers, json=data, timeout=120)
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            tokens = response.json().get("usage", {}).get("total_tokens", 0)
            log(f"  ✅ 完成! Tokens: {tokens}")
            results.append({"expert": expert3["name"], "task": expert3["task"], "result": content, "success": True})
        else:
            log(f"  ❌ 失败: HTTP {response.status_code}")
            results.append({"expert": expert3["name"], "task": expert3["task"], "result": f"HTTP {response.status_code}", "success": False})
    except Exception as e:
        log(f"  ❌ 异常: {e}")
        results.append({"expert": expert3["name"], "task": expert3["task"], "result": str(e), "success": False})
    
    # 显示所有结果
    log("\n" + "=" * 70)
    log("Debug结果汇总")
    log("=" * 70)
    
    for r in results:
        log(f"\n### {r['expert']}")
        if r['success']:
            log(r['result'][:2000])
    
    # 保存结果
    output = {
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    
    outfile = Path(__file__).parent / "outputs" / f"debug_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    outfile.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
    log(f"\n\n结果已保存到: {outfile}")
    
    log("\n🎼 Debug任务完成!")


if __name__ == "__main__":
    main()
