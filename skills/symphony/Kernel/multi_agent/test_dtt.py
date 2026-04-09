# -*- coding: utf-8 -*-
import sys, os
# Add Kernel directory to path
kernel_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, kernel_dir)

print("=" * 60)
print(" Detect-Then-Team System Test")
print("=" * 60)

from multi_agent.detect_then_team import DetectThenTeamSystem

system = DetectThenTeamSystem()

# Detection test
print("\n[1] Model Detection...")
detection = system.detect_all_models()
print(f"  Total tested: {detection['summary']['total']}")
print(f"  Online: {detection['summary']['online']}")
for p, data in detection['providers'].items():
    online = [m for m in data['models'] if m['status'] == 'online']
    print(f"  {p}: {len(online)}/{data['tested']} online")
    for m in online:
        print(f"    - {m['model_id']} ({m['latency_ms']}ms)")

# Team building test
print("\n[2] Team Building...")
task = "What is 1+1? Reply with one number."
team_info = system.build_team(task, team_size=2)
print(f"  Task: {task}")
print(f"  Task type: {team_info['task_type']}")
print(f"  Online models: {team_info['online_count']}")
print(f"  Team size: {team_info['team_size']}")
for m in team_info["team"]:
    print(f"    - {m['model_id']} ({m['score']}pts)")

# Execution test
print("\n[3] Team Execution...")
result = system.execute(task, team_size=2)
print(f"  Success: {result['success_count']}/{len(result['results'])}")
for r in result['results']:
    status = "OK" if r['status'] == 'success' else "FAIL"
    print(f"    [{status}] {r['model']}: {str(r.get('content', r.get('error', '')))[:60]}")
print(f"\n  Final result: {result['final_result'][:80]}")

print("\n" + "=" * 60)
print(" Test Complete")
print("=" * 60)
