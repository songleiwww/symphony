# -*- coding: utf-8 -*-
import sys, os, sqlite3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print(" Symphony Logic Loop Diagnosis")
print("=" * 60)

DB_PATH_1 = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"
DB_PATH_2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/symphony_kernel.db")

print("\n[1] DB Path Check")
print(f"  symphony_scheduler DB: {DB_PATH_1}")
print(f"  model_federation DB:  {DB_PATH_2}")
same = DB_PATH_1.replace('\\', '/') == DB_PATH_2.replace('\\', '/')
print(f"  Match: {'OK' if same else 'MISMATCH!'}")

print("\n[2] Providers")
conn = sqlite3.connect(DB_PATH_1)
cur = conn.cursor()
cur.execute("SELECT provider_code, is_enabled FROM provider_registry")
providers = {r[0]: r[1] for r in cur.fetchall()}
print(f"  Providers: {list(providers.keys())}")
print(f"  Enabled: {providers}")
conn.close()

print("\n[3] Models by provider")
conn = sqlite3.connect(DB_PATH_1)
cur = conn.cursor()
cur.execute("SELECT provider, COUNT(*) FROM model_config WHERE is_enabled=1 GROUP BY provider")
counts = {r[0]: r[1] for r in cur.fetchall()}
print(f"  Enabled models: {counts}")
conn.close()

print("\n[4] Tools")
conn = sqlite3.connect(DB_PATH_1)
cur = conn.cursor()
cur.execute("SELECT tool_name, is_enabled FROM tool_registry")
tools = {r[0]: r[1] for r in cur.fetchall()}
print(f"  Registered tools: {list(tools.keys())}")
conn.close()

print("\n[5] ASR Tool")
has_asr = 'whisper_asr' in tools or 'asr' in tools
print(f"  Whisper ASR registered: {'YES' if has_asr else 'NO'}")

print("\n[6] Model Federation")
try:
    from model_federation import get_federation
    fed = get_federation()
    print(f"  Federation: OK, providers: {len(fed.provider_pools)}")
except Exception as e:
    print(f"  Federation: ERROR - {e}")

print("\n[7] Strategy Scheduler")
try:
    from intelligent_strategy_scheduler import IntelligentStrategyScheduler
    sched = IntelligentStrategyScheduler()
    print(f"  Strategies: {len(sched.strategies)}, list: {list(sched.strategies.keys())}")
except Exception as e:
    print(f"  Strategy Scheduler: ERROR - {e}")

print("\n[8] DetectThenTeam")
try:
    from multi_agent.detect_then_team import DetectThenTeamSystem
    dtt = DetectThenTeamSystem()
    print(f"  DetectThenTeam: OK, providers: {len(dtt.provider_config)}")
except Exception as e:
    print(f"  DetectThenTeam: ERROR - {e}")

print("\n[9] FineGrainedWorkflow")
try:
    from workflow.fine_grained_workflow import WorkflowBuilder
    wf = WorkflowBuilder.text_to_voice_workflow("test")
    print(f"  Workflow: OK, steps: {len(wf.steps)}")
except Exception as e:
    print(f"  Workflow: ERROR - {e}")

print("\n[10] Symphony Scheduler - Direct Call Test")
from symphony_scheduler import symphony_scheduler, get_enabled_providers
providers_list = get_enabled_providers()
print(f"  Enabled providers: {[p['code'] for p in providers_list]}")

print("\n" + "=" * 60)
print(" Diagnosis Complete")
print("=" * 60)
