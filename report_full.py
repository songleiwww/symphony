import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
from brainstorm_panel_v2 import BrainstormPanel

panel = BrainstormPanel()

print("Symphony Team Report")
print("=" * 80)

tasks = [
    {"name": "Lin Siyuan", "nickname": "ForestWalker", "position": "Architect", "model": "glm-4-flash", "prompt": "You are a system architect. Describe your work in detail."},
    {"name": "Chen Meiqi", "nickname": "StarDreamer", "position": "Engineer", "model": "glm-4-flash", "prompt": "You are a senior engineer. Describe your work in detail."},
    {"name": "Wang Haoran", "nickname": "CloudChaser", "position": "PM", "model": "glm-4-flash", "prompt": "You are a product manager. Describe your work in detail."},
    {"name": "Liu Xinyi", "nickname": "DawnWhisper", "position": "Designer", "model": "glm-4-flash", "prompt": "You are a UI/UX designer. Describe your work in detail."},
    {"name": "Zhao Min", "nickname": "DataAlchemist", "position": "Data Analyst", "model": "glm-4-flash", "prompt": "You are a data analyst. Describe your work in detail."},
    {"name": "Zhang Mingyuan", "nickname": "CodePoet", "position": "Tech Writer", "model": "glm-4-flash", "prompt": "You are a technical writer. Describe your work in detail."}
]

results = []
for task in tasks:
    r = panel.call_model(prompt=task["prompt"], model_id=task["model"], max_tokens=300)
    tokens = r.tokens if hasattr(r, 'tokens') else 0
    success = r.success if hasattr(r, 'success') else True
    work = r.response[:200] if hasattr(r, 'response') else str(r)[:200]
    results.append({"name": task["name"], "nickname": task["nickname"], "position": task["position"], "model": task["model"], "status": "OK" if success else "FAIL", "tokens": tokens, "work": work})

print("\n| Name | Nickname | Position | Model | Status | Tokens |")
print(f"|------|----------|----------|-------|--------|--------|")
total = 0
for r in results:
    total += r["tokens"]
    print(f"| {r['name']} | {r['nickname']} | {r['position']} | {r['model']} | {r['status']} | {r['tokens']} |")
print(f"| **Total** | | | | | **{total}** |")

print("\nWork Details")
for r in results:
    print(f"\n[{r['name']}] - {r['position']}")
    print(f"  Nickname: {r['nickname']}")
    print(f"  Model: {r['model']}")
    print(f"  Status: {r['status']}")
    print(f"  Tokens: {r['tokens']}")
    print(f"  Work: {r['work']}")

print(f"\nTotal: {total} Tokens")