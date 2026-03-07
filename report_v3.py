import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
from brainstorm_panel_v2 import BrainstormPanel

panel = BrainstormPanel()

print("=" * 90)
print("交响团队开发工作述职报告")
print("=" * 90)

tasks = [
    {"name": "林思远", "nickname": "林间远行者", "position": "架构师", "model": "deepseek-ai/DeepSeek-R1-0528", "prompt": "你是一位系统架构师，专长是系统架构设计和优化。请用一句话介绍你的专长。"},
    {"name": "陈美琪", "nickname": "星海织梦师", "position": "工程师", "model": "glm-4-flash", "prompt": "你是一位高级工程师，专长是测试和调试。请用一句话介绍你的专长。"},
    {"name": "王浩然", "nickname": "云端追光者", "position": "产品经理", "model": "deepseek-ai/DeepSeek-V3.2", "prompt": "你是一位产品经理，专长是需求分析和产品规划。请用一句话介绍你的专长。"}
]

results = []
for task in tasks:
    r = panel.call_model(prompt=task["prompt"], model_id=task["model"], max_tokens=200)
    expertise = r.response[:100] if r.success else "调用失败"
    results.append({"name": task["name"], "nickname": task["nickname"], "position": task["position"], "model": task["model"], "status": "OK" if r.success else "FAIL", "tokens": r.tokens, "expertise": expertise})

print("\n| 姓名 | 网名 | 岗位 | 模型 | 状态 | Tokens | 擅长 |")
print(f"|------|------|------|------|------|--------|------|")
total = 0
for r in results:
    total += r["tokens"]
    exp = r["expertise"].replace("|", "-")
    print(f"| {r['name']} | {r['nickname']} | {r['position']} | {r['model']} | {r['status']} | {r['tokens']} | {exp} |")
print(f"| **总计** | | | | | **{total}** | |")

print("\n" + "=" * 90)
print(f"Total: {total} Tokens")
print("=" * 90)