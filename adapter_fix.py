#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
适配器架构师补救任务 - 开发通用适配器层代码
"""

import json
import requests
from pathlib import Path
from datetime import datetime


def main():
    log_file = Path(__file__).parent / "outputs" / "adapter_fix_log.txt"
    log_file.parent.mkdir(exist_ok=True)
    log_file.write_text("", encoding='utf-8')
    
    def log(msg):
        with open(log_file, "a", encoding='utf-8') as f:
            f.write(msg + "\n")
    
    # 加载配置
    config_path = Path(r"C:\Users\Administrator\.openclaw\openclaw.cherry.json")
    config = json.loads(config_path.read_text(encoding='utf-8'))
    
    topic = "symphony通用适配器层代码开发"
    
    log("=" * 70)
    log("🎼 适配器架构师补救任务")
    log("=" * 70)
    log("任务: 开发通用适配器层代码")
    log("")
    
    prompt = """你是适配器架构师。

symphony工具路径: C:\\Users\\Administrator\\.openclaw\\workspace\\skills\\symphony

任务：开发通用适配器层代码

约束条件：
- 只能从symphony端开发，不能修改OpenClaw文件
- 开发一个适配器层作为桥梁

参考信息：
1. JSON Schema已定义输入输出模型
2. 事件总线架构师已给出事件Schema和目录结构建议

请给出：
1. 完整的文件结构设计
2. 每个核心文件的代码实现
3. 如何与现有BrainstormPanel系统集成

请用中文回复，包含完整的Python代码示例。"""
    
    expert = {"provider": "cherry-doubao", "model": "glm-4.7"}
    provider = config["models"]["providers"][expert["provider"]]
    api_key = provider["apiKey"]
    base_url = provider["baseUrl"]
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": expert["model"], "messages": [{"role": "user", "content": prompt}], "max_tokens": 2000}
    
    url = f"{base_url}/chat/completions"
    
    log("【适配器架构师】开发中...")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=180)
        if response.status_code == 200:
            result_data = response.json()
            content = result_data["choices"][0]["message"]["content"]
            usage = result_data.get("usage", {})
            tokens = usage.get("total_tokens", 0)
            
            log(f"  ✅ 完成! Tokens: {tokens}")
            
            log("\n" + "=" * 70)
            log("🎯 通用适配器层代码")
            log("=" * 70)
            log(content)
            
            # 保存结果
            output = {
                "topic": topic,
                "timestamp": datetime.now().isoformat(),
                "result": content,
                "tokens": tokens,
                "success": True
            }
            
            outfile = Path(__file__).parent / "outputs" / f"adapter_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            outfile.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
            log(f"\n\n结果已保存到: {outfile}")
            
        else:
            log(f"  ❌ 失败: HTTP {response.status_code}")
    except Exception as e:
        log(f"  ❌ 异常: {e}")
    
    log("\n🎼 补救任务完成!")


if __name__ == "__main__":
    main()
