import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
from brainstorm_panel_v2 import BrainstormPanel

panel = BrainstormPanel()

print("Symphony Team Report")

tasks = [
    {"name": "Lin Siyuan", "nickname": "ForestWalker", "position": "Architect", "model": "glm-4-flash", "prompt": "Your expertise is system architecture design. Say your expertise in one sentence."},
    {"name": "Chen Meiqi", "nickname": "StarDreamer", "position": "Engineer", "model": "glm-4-flash", "prompt": "Your expertise is testing and debugging. Say your expertise in one sentence."},
    {"name": "Wang Haoran", "nickname": "CloudChaser", "position": "PM", "model": "glm-4-flash", "prompt": "Your expertise is product planning. Say your expertise in one sentence."}
]

results = []
for task in tasks:
    r = panel.call_model(prompt=task["prompt"], model_id=task["model"], max_tokens=100)
    exp = r.response[:50] if r.success else "FAIL"
    results.append({"name": task["name"], "nickname": task["nickname"], "position": task["position"], "model": task["model"], "status": "OK" if r.success else "FAIL", "tokens": r.tokens, "expertise": exp})

print("\n| Name | Nickname | Position | Model | Status | Tokens | Expertise |")
print(f"|------|----------|----------|-------|--------|--------|-----------|")
total = 0
for r in results:
    total += r["tokens"]
    print(f"| {r['name']} | {r['nickname']} | {r['position']} | {r['model']} | {r['status']} | {r['tokens']} | {r['expertise']} |")
print(f"| **Total** | | | | | **{total}** | |")