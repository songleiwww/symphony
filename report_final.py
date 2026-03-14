import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
from brainstorm_panel_v2 import BrainstormPanel

panel = BrainstormPanel()

print("=" * 100)
print("Symphony Team Report")
print("=" * 100)

tasks = [
    {"name": "林思远", "nickname": "林间远行者", "position": "架构师", "model": "glm-4-flash", "prompt": "系统架构设计与优化"},
    {"name": "陈美琪", "nickname": "星海织梦师", "position": "工程师", "model": "glm-z1-flash", "prompt": "测试和调试"},
    {"name": "王浩然", "nickname": "云端追光者", "position": "产品经理", "model": "glm-4v-flash", "prompt": "需求分析和产品规划"},
    {"name": "刘心怡", "nickname": "晨光微吟者", "position": "设计师", "model": "glm-4.1v-thinking-flash", "prompt": "UI/UX设计和用户体验优化"},
    {"name": "赵敏", "nickname": "数字炼金师", "position": "数据分析师", "model": "deepseek-ai/DeepSeek-V3.2", "prompt": "数据分析和可视化"},
    {"name": "张明远", "nickname": "代码诗人", "position": "技术作家", "model": "glm-4-flash", "prompt": "技术文档编写"}
]

results = []
for task in tasks:
    r = panel.call_model(prompt=f"你的专长是{task['prompt']}。用15个字以内介绍。", model_id=task["model"], max_tokens=50)
    # Handle response - may be string or list
    resp = r.response
    if isinstance(resp, list):
        exp = str(resp[0])[:20] if resp else "无"
    else:
        exp = str(resp)[:20] if resp else "无"
    exp = exp.replace("|", "-").replace("\n", " ")
    results.append({"name": task["name"], "nickname": task["nickname"], "position": task["position"], "model": task["model"], "status": "OK" if r.success else "FAIL", "tokens": r.tokens, "expertise": exp})

print("\n| 姓名 | 网名 | 岗位 | 模型 | 状态 | Tokens | 精通 |")
print(f"|------|------|------|------|------|--------|------|")
total = 0
for r in results:
    total += r["tokens"]
    print(f"| {r['name']} | {r['nickname']} | {r['position']} | {r['model']} | {r['status']} | {r['tokens']} | {r['expertise']} |")
print(f"| **总计** | | | | | **{total}** | |")

print(f"\nTotal: {total} Tokens")