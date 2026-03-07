import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
from brainstorm_panel_v2 import BrainstormPanel

panel = BrainstormPanel()

print("=" * 80)
print("交响团队开发工作述职报告")
print("=" * 80)

tasks = [
    {"name": "林思远", "nickname": "林间远行者", "position": "架构师", "model": "deepseek-ai/DeepSeek-R1-0528", "prompt": "你是一位系统架构师。分析交响调度引擎的核心架构设计，用中文回复。"},
    {"name": "陈美琪", "nickname": "星海织梦师", "position": "工程师", "model": "glm-4-flash", "prompt": "你是一位高级工程师。测试交响工具的模型调用能力，用中文回复。"},
    {"name": "王浩然", "nickname": "云端追光者", "position": "产品经理", "model": "deepseek-ai/DeepSeek-V3.2", "prompt": "你是一位产品经理。分析用户需求并规划产品功能，用中文回复。"}
]

results = []
for task in tasks:
    r = panel.call_model(prompt=task["prompt"], model_id=task["model"], max_tokens=500)
    results.append({"name": task["name"], "nickname": task["nickname"], "position": task["position"], "model": task["model"], "status": "OK" if r.success else "FAIL", "tokens": r.tokens, "response": r.response if r.success else ""})

print("\n| 姓名 | 网名 | 岗位 | 模型 | 状态 | Tokens |")
print(f"|------|------|------|------|------|--------|")
total = 0
for r in results:
    total += r["tokens"]
    print(f"| {r['name']} | {r['nickname']} | {r['position']} | {r['model']} | {r['status']} | {r['tokens']} |")
print(f"| **总计** | | | | | **{total}** |")

print("\n[详细工作内容]")
for r in results:
    print(f"\n[{r['name']}] - {r['position']}")
    print(f"  Nickname: {r['nickname']}")
    print(f"  Model: {r['model']}")
    print(f"  Status: {r['status']}")
    print(f"  Tokens: {r['tokens']}")
    if r["response"]:
        print(f"  Work: {r['response'][:200]}")

print(f"\nTotal: {total} Tokens")