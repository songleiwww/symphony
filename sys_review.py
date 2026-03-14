import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
from brainstorm_panel_v2 import BrainstormPanel

panel = BrainstormPanel()

print("=" * 80)
print("Symphony System Review")
print("=" * 80)

# 2个模型检查交响系统
tasks = [
    {"name": "林思远", "nickname": "林间远行者", "position": "架构师", "model": "glm-4-flash", "prompt": "请检查交响系统的整体架构设计，评估其优缺点。用中文回复。"},
    {"name": "陈美琪", "nickname": "星海织梦师", "position": "工程师", "model": "glm-z1-flash", "prompt": "请检查交响系统的代码质量和性能，评估其可用性和稳定性。用中文回复。"}
]

results = []
for task in tasks:
    print(f"\n[{task['name']}] {task['position']} - {task['model']}")
    r = panel.call_model(prompt=task["prompt"], model_id=task["model"], max_tokens=600)
    print(f"  Status: {'OK' if r.success else 'FAIL'}, Tokens: {r.tokens}")
    results.append({"name": task["name"], "nickname": task["nickname"], "position": task["position"], "model": task["model"], "status": "OK" if r.success else "FAIL", "tokens": r.tokens, "response": r.response if r.success else ""})

print("\n" + "=" * 80)
print("Review Results")
print("=" * 80)

total = 0
for r in results:
    total += r["tokens"]
    print(f"\n【{r['name']}】- {r['position']}")
    print(f"  Model: {r['model']}")
    print(f"  Status: {r['status']}")
    print(f"  Tokens: {r['tokens']}")
    if r["response"]:
        print(f"  Review: {r['response'][:400]}...")

print(f"\nTotal: {total} Tokens")
print("=" * 80)