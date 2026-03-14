import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
from brainstorm_panel_v2 import BrainstormPanel

panel = BrainstormPanel()

print("=" * 80)
print("Symphony Tool Improvement Review")
print("=" * 80)

# 2个模型检查交响工具
tasks = [
    {"name": "林思远", "nickname": "林间远行者", "position": "架构师", "model": "glm-4-flash", "prompt": "请检查 C:\\Users\\Administrator\\.openclaw\\workspace\\skills\\symphony 目录下的交响工具项目，找出需要改善的地方。用中文详细列出问题和建议。"},
    {"name": "陈美琪", "nickname": "星海织梦师", "position": "工程师", "model": "glm-4-flash", "prompt": "请检查 C:\\Users\\Administrator\\.openclaw\\workspace\\skills\\symphony 目录下的交响工具代码，找出可能存在的bug和需要优化的地方。用中文详细列出。"}
]

results = []
for task in tasks:
    print(f"\n[{task['name']}] {task['position']} - {task['model']}")
    r = panel.call_model(prompt=task["prompt"], model_id=task["model"], max_tokens=800)
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
        print(f"  Review: {r['response'][:500]}...")

print(f"\nTotal: {total} Tokens")
print("=" * 80)