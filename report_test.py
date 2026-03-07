import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
from brainstorm_panel_v2 import BrainstormPanel

panel = BrainstormPanel()

print("=" * 70)
print("交响团队开发工作述职报告")
print("=" * 70)

# 3个模型工作
print("\n[1] 架构师 - 林思远 (林间远行者)")
r1 = panel.call_model(prompt="你是一位系统架构师。分析交响调度引擎的核心架构设计，用中文回复。", model_id="deepseek-ai/DeepSeek-R1-0528", max_tokens=500)
status1 = "OK" if r1.success else "FAIL"
print(f"    Status: {status1} | Tokens: {r1.tokens}")

print("\n[2] 工程师 - 陈美琪 (星海织梦师)")
r2 = panel.call_model(prompt="你是一位高级工程师。测试交响工具的模型调用能力，用中文回复。", model_id="glm-4-flash", max_tokens=500)
status2 = "OK" if r2.success else "FAIL"
print(f"    Status: {status2} | Tokens: {r2.tokens}")

print("\n[3] 产品经理 - 王浩然 (云端追光者)")
r3 = panel.call_model(prompt="你是一位产品经理。分析用户需求并规划产品功能，用中文回复。", model_id="deepseek-ai/DeepSeek-V3.2", max_tokens=500)
status3 = "OK" if r3.success else "FAIL"
print(f"    Status: {status3} | Tokens: {r3.tokens}")

# 述职报告
print("\n" + "=" * 70)
print("述职报告")
print("=" * 70)

total_tokens = sum(r.tokens for r in [r1, r2, r3] if r.success)

for name, role, username, r, s in [
    ("林思远", "架构师", "林间远行者", r1, status1),
    ("陈美琪", "工程师", "星海织梦师", r2, status2),
    ("王浩然", "产品经理", "云端追光者", r3, status3)
]:
    print(f"\n[{name}]")
    print(f"  Name: {name}")
    print(f"  Nickname: {username}")
    print(f"  Position: {role}")
    print(f"  Status: {s}")
    print(f"  Tokens: {r.tokens}")
    if r.success:
        content = r.response[:200].replace('\n', ' ')
        print(f"  Work: {content}...")

print(f"\n{'=' * 70}")
print(f"Total Tokens: {total_tokens}")
print("=" * 70)