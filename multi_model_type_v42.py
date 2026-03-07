#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v4.2 - Multi-Model Type Correct Usage
Focus: Image models, Vector models, Ranking models
"""
import sys
import json
import time
import requests
import threading
from datetime import datetime
from config import MODEL_CHAIN

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# 按模型类型分组
MODEL_TYPES = {"text": [], "vision": [], "image_gen": [], "video_gen": [], "reasoning": []}

for i, m in enumerate(MODEL_CHAIN):
    if m.get("enabled"):
        if m.get("is_vision"):
            MODEL_TYPES["vision"].append({"index": i, **m})
        elif m.get("is_image_gen"):
            MODEL_TYPES["image_gen"].append({"index": i, **m})
        elif m.get("is_video_gen"):
            MODEL_TYPES["video_gen"].append({"index": i, **m})
        elif m.get("is_reasoning"):
            MODEL_TYPES["reasoning"].append({"index": i, **m})
        else:
            MODEL_TYPES["text"].append({"index": i, **m})

print("=" * 70)
print("Symphony v4.2 - Multi-Model Type Correct Usage")
print("=" * 70)

print("\n模型类型分类:")
for mtype, models in MODEL_TYPES.items():
    print("\n  [{}] 共 {} 个模型:".format(mtype.upper(), len(models)))
    for m in models:
        print("    - {} (idx:{})".format(m.get("alias", m.get("name")), m["index"]))

MODELS = [
    {"name": "Model-Text", "role": "文本模型专家", "emoji": "TEXT", "model_index": 0, "type": "text"},
    {"name": "Model-Vision", "role": "视觉模型专家", "emoji": "VISION", "model_index": 3, "type": "vision"},
    {"name": "Model-Image", "role": "图像生成专家", "emoji": "IMG", "model_index": 4, "type": "image_gen"},
    {"name": "Model-Reason", "role": "推理模型专家", "emoji": "REASON", "model_index": 1, "type": "reasoning"},
    {"name": "Model-Vector", "role": "向量模型专家", "emoji": "VECTOR", "model_index": 0, "type": "text"},
    {"name": "Model-Rank", "role": "排序模型专家", "emoji": "RANK", "model_index": 0, "type": "text"},
]


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_config, prompt, max_tokens=300):
    url = model_config["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model_config["api_key"], "Content-Type": "application/json"}
    data = {"model": model_config["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    t0 = time.time()
    try:
        r = requests.post(url, headers=headers, json=data, timeout=20)
        elapsed = time.time() - t0
        if r.status_code == 200:
            j = r.json()
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": j.get("usage", {}).get("total_tokens", 0), "time": elapsed}
        else:
            return {"success": False, "error": "HTTP " + str(r.status_code), "detail": r.text[:100]}
    except Exception as e:
        return {"success": False, "error": str(e)}


def test_model_capability(model_index, test_type):
    enabled = get_enabled_models()
    if model_index >= len(enabled):
        return {"success": False, "error": "Index out of range"}
    config = enabled[model_index]
    
    prompts = {
        "vision": "请描述这张图片的内容",
        "image_gen": "生成一张赛博朋克风格的都市图片",
        "video_gen": "生成一段科幻短视频描述",
        "reasoning": "解这道数学题：123 * 456 = ?",
        "text": "用一句话介绍自己",
    }
    
    prompt = prompts.get(test_type, prompts["text"])
    
    if test_type == "image_gen" and not config.get("is_image_gen"):
        return {"success": False, "error": "模型不支持图像生成", "note": "需要使用专门的图像生成模型"}
    elif test_type == "vision" and not config.get("is_vision"):
        return {"success": False, "error": "模型不支持视觉理解", "note": "需要使用专门的视觉模型"}
    elif test_type == "video_gen" and not config.get("is_video_gen"):
        return {"success": False, "error": "模型不支持视频生成", "note": "需要使用专门的视频生成模型"}
    
    return call_api(config, prompt)


enabled = get_enabled_models()
for m in MODELS:
    idx = m["model_index"]
    if idx < len(enabled):
        cfg = enabled[idx]
        m["model_name"] = cfg["alias"]
        m["provider"] = cfg["provider"]
        m["capabilities"] = []
        if cfg.get("is_vision"): m["capabilities"].append("vision")
        if cfg.get("is_image_gen"): m["capabilities"].append("image_gen")
        if cfg.get("is_video_gen"): m["capabilities"].append("video_gen")
        if cfg.get("is_reasoning"): m["capabilities"].append("reasoning")
        m["capabilities"].append("text")

print("\n" + "=" * 70)
print("模型能力分配:")
print("=" * 70)
for m in MODELS:
    print("  {} {} -> {} ({}): {}".format(m["emoji"], m["role"], m.get("model_name", "N/A"), m.get("provider", "N/A"), ", ".join(m.get("capabilities", []))))

# Round 1: 模型错误调用测试
print("\n" + "=" * 70)
print("Round 1: 模型类型正确性测试")
print("=" * 70)

results1 = []
for m in MODELS:
    print("\n  Testing {} ({}):".format(m["role"], m.get("model_name", "N/A")))
    result = test_model_capability(m["model_index"], m["type"])
    results1.append({"model": m["role"], "result": result})
    if result.get("success"):
        print("    OK: {} tokens".format(result.get("tokens", 0)))
    else:
        print("    ERROR: {}".format(result.get("error", "Unknown")))
        if result.get("note"):
            print("    NOTE: {}".format(result.get("note")))

# Round 2: 正确协作
print("\n" + "=" * 70)
print("Round 2: 正确模型协作测试")
print("=" * 70)

collab_prompts = [
    "作为文本模型专家，解释文本处理流程",
    "作为视觉模型专家，说明图像识别应用场景",
    "作为图像生成专家，描述图像生成流程",
    "作为推理模型专家，展示推理能力",
    "作为向量模型专家，解释向量搜索原理",
    "作为排序模型专家，说明排序算法原理"
]

collab_indices = [m["model_index"] for m in MODELS]
results2 = []
threads = []

def call_model(idx, i, prompt):
    enabled = get_enabled_models()
    if idx < len(enabled):
        r = call_api(enabled[idx], prompt)
        results2.append({"model": MODELS[i]["role"], "result": r})

for i, (prompt, idx) in enumerate(zip(collab_prompts, collab_indices)):
    t = threading.Thread(target=call_model, args=(idx, i, prompt))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("\n协作测试结果:")
total_tokens = 0
for r in results2:
    if r.get("result", {}).get("success"):
        total_tokens += r["result"].get("tokens", 0)
        print("\n  {}: OK ({} tokens)".format(r["model"], r["result"].get("tokens", 0)))
    else:
        print("\n  {}: FAILED".format(r["model"]))

# Round 3: 解决方案
print("\n" + "=" * 70)
print("Round 3: 解决方案建议")
print("=" * 70)

solutions = [
    {"type": "vision", "solution": "使用GLM-4V-Flash进行图像理解"},
    {"type": "image_gen", "solution": "使用CogView-3-Flash生成图像"},
    {"type": "video_gen", "solution": "使用CogVideoX-Flash生成视频"},
    {"type": "reasoning", "solution": "使用GLM-Z1-Flash进行推理"},
    {"type": "vector", "solution": "使用文本模型模拟向量计算"},
    {"type": "rank", "solution": "使用文本模型模拟排序功能"}
]

for s in solutions:
    print("\n  [{}] -> {}".format(s["type"], s["solution"]))

print("\n" + "=" * 70)
print("Report")
print("=" * 70)
print("\n模型类型使用情况:")
for mtype, models in MODEL_TYPES.items():
    print("  {}: {} models".format(mtype, len(models)))
print("\n总Token消耗: {}".format(total_tokens))

report = {
    "title": "Symphony v4.2 Multi-Model Type Correct Usage",
    "version": "4.2",
    "datetime": datetime.now().isoformat(),
    "model_types": {k: len(v) for k, v in MODEL_TYPES.items()},
    "solutions": solutions,
    "summary": {"total_tokens": total_tokens}
}

with open("model_type_usage_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("\nReport saved: model_type_usage_report.json")
print("\nSymphony - 智韵交响，共创华章！")
