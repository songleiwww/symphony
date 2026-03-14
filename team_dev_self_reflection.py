#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境团队并行开发 - 自我反思机制 + 协作优化 + 递归改进
使用真实模型API调用
"""

import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 团队成员配置
TEAM = {
    "沈清弦": {"role": "架构师", "model": "ark-code-latest", "api_key": "3b922877-3fbe-45d1-a298-53f2231c5224", "url": "https://ark.cn-beijing.volces.com/api/coding/v3"},
    "沈怀秋": {"role": "安全", "model": "deepseek-v3.2", "api_key": "3b922877-3fbe-45d1-a298-53f2231c5224", "url": "https://ark.cn-beijing.volces.com/api/coding/v3"},
    "苏云渺": {"role": "开发", "model": "doubao-seed-2.0-code", "api_key": "3b922877-3fbe-45d1-a298-53f2231c5224", "url": "https://ark.cn-beijing.volces.com/api/coding/v3"},
    "陆鸣镝": {"role": "测试", "model": "glm-4.7", "api_key": "16cf0a4a775c46cfa1684abcf4b802d0.rtb4oMgpFocBy87y", "url": "https://open.bigmodel.cn/api/paas/v4"},
    "顾清歌": {"role": "运维", "model": "kimi-k2.5", "api_key": "3b922877-3fbe-45d1-a298-53f2231c5224", "url": "https://ark.cn-beijing.volces.com/api/coding/v3"},
    "沈轻罗": {"role": "策划", "model": "MiniMax-M2.5", "api_key": "3b922877-3fbe-45d1-a298-53f2231c5224", "url": "https://ark.cn-beijing.volces.com/api/coding/v3"},
}

# 任务分配
TASKS = {
    "沈清弦": "设计自我反思机制的架构方案，包括核心类、接口、流程。直接给出架构设计。",
    "沈怀秋": "设计递归改进框架的安全机制，包括权限控制、审计日志、回滚机制。直接给出设计。",
    "苏云渺": "设计团队协作优化模块，包括任务分配、状态同步、冲突解决。直接给出设计。",
    "陆鸣镝": "为上述三个模块设计测试用例，包括单元测试、集成测试、边界测试。直接给出测试用例。",
    "顾清歌": "设计部署方案，包括容器化、配置管理、监控告警。直接给出部署设计。",
    "沈轻罗": "分析需求，输出产品需求文档，包括功能列表、优先级、验收标准。直接给出PRD。",
}

def call_api(member, config, task):
    """调用模型API"""
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": config["model"],
        "messages": [{"role": "user", "content": f"你是{member}（古风名字），序境{config['role']}。{task}直接给出结果，不要多余的寒暄。"}],
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    try:
        start = time.time()
        r = requests.post(f"{config['url']}/chat/completions", headers=headers, json=payload, timeout=60)
        elapsed = time.time() - start
        
        if r.status_code == 200:
            result = r.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {"member": member, "status": "success", "content": content, "elapsed": elapsed}
        else:
            return {"member": member, "status": "error", "error": f"HTTP {r.status_code}: {r.text[:200]}", "elapsed": elapsed}
    except Exception as e:
        return {"member": member, "status": "error", "error": str(e)[:200], "elapsed": 0}

def main():
    results = []
    output_lines = []
    
    output_lines.append("=" * 60)
    output_lines.append("序境最高团队开发 - 并行调用6个真实模型")
    output_lines.append("=" * 60)
    
    # 并行调用
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(call_api, member, config, TASKS[member]): member 
            for member, config in TEAM.items()
        }
        
        for future in as_completed(futures):
            member = futures[future]
            try:
                result = future.result()
                results.append(result)
                output_lines.append(f"\n[{member}] {result['status']} ({result.get('elapsed', 0):.1f}s)")
            except Exception as e:
                output_lines.append(f"\n[{member}] error: {e}")
    
    # 输出结果
    output_lines.append("\n" + "=" * 60)
    output_lines.append("团队开发结果汇总")
    output_lines.append("=" * 60)
    
    success_count = sum(1 for r in results if r["status"] == "success")
    output_lines.append(f"\n[OK] 成功: {success_count}/6")
    
    for r in results:
        output_lines.append(f"\n--- {r['member']} ({r['status']}) ---")
        if r["status"] == "success":
            output_lines.append(r["content"][:1500])
        else:
            output_lines.append(f"错误: {r.get('error', 'Unknown')}")
    
    # 保存到文件
    with open("team_dev_result.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    
    # 打印
    for line in output_lines:
        print(line)
    
    return results

if __name__ == "__main__":
    main()
