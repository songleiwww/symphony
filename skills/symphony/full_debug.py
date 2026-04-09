# -*- coding: utf-8 -*-
"""序境系统全链路深度Debug - 4月10日凌晨"""
import sys, os, time, json, sqlite3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print(" 序境系统 - 全链路深度Debug")
print("=" * 70)

DB_PATH = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"

# ===== 1. DB路径一致性 =====
print("\n[1] 数据库路径一致性检查")
SYM_SCHEDULER_DB = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"
MODEL_FED_DB = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"  # 已修复
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM sqlite_sequence")
model_count = cur.execute("SELECT COUNT(*) FROM model_config WHERE is_enabled=1").fetchone()[0]
provider_count = cur.execute("SELECT COUNT(*) FROM provider_registry WHERE is_enabled=1").fetchone()[0]
tool_count = cur.execute("SELECT COUNT(*) FROM tool_registry WHERE is_enabled=1").fetchone()[0]
print(f"  model_config: {model_count} 个启用模型")
print(f"  provider_registry: {provider_count} 个启用服务商")
print(f"  tool_registry: {tool_count} 个启用工具")
conn.close()

# ===== 2. Provider API Key检查 =====
print("\n[2] 服务商API Key有效性检测")
import requests
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("SELECT provider_code, base_url, api_key FROM provider_registry WHERE is_enabled=1")
providers = cur.fetchall()
conn.close()

provider_status = {}
for code, base_url, api_key in providers:
    url = base_url.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5}
    
    # 特殊处理阿里云
    if code == "aliyun":
        url = url.replace("/api/v1", "/compatible-mode/v1")
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        status = "OK" if resp.status_code == 200 else f"HTTP {resp.status_code}"
    except Exception as e:
        status = f"ERR: {str(e)[:30]}"
    provider_status[code] = status
    print(f"  {code}: {status}")

# ===== 3. Symphony_scheduler直接调用测试 =====
print("\n[3] symphony_scheduler直接调用测试")
from symphony_scheduler import symphony_scheduler
test_result = symphony_scheduler("What is 1+1? Reply with one number.", model_type="text")
print(f"  结果: {test_result}")

# ===== 4. Model Federation检查 =====
print("\n[4] Model Federation状态")
try:
    from Kernel.model_federation import ModelFederation, get_federation
    fed = get_federation()
    print(f"  提供商数: {len(fed.provider_pools)}")
    for name, pool in fed.provider_pools.items():
        print(f"  {name}: {len(pool.models)} models, 当前并发: {pool.current_concurrent}")
except Exception as e:
    print(f"  ERROR: {e}")

# ===== 5. Strategy Scheduler检查 =====
print("\n[5] IntelligentStrategyScheduler状态")
try:
    from Kernel.intelligent_strategy_scheduler import IntelligentStrategyScheduler
    sched = IntelligentStrategyScheduler()
    print(f"  策略数: {len(sched.strategies)}")
    print(f"  策略列表: {list(sched.strategies.keys())}")
    # 测试调度
    test_task = {"type": "general", "prompt": "hello"}
    result = sched.schedule(test_task)
    print(f"  调度测试: strategy={result.get('strategy')}, model={result.get('selected_model')}")
except Exception as e:
    print(f"  ERROR: {e}")

# ===== 6. Detect-Then-Team检查 =====
print("\n[6] Detect-Then-Team系统状态")
try:
    from Kernel.multi_agent.detect_then_team import DetectThenTeamSystem
    dtt = DetectThenTeamSystem()
    print(f"  提供商配置数: {len(dtt.provider_config)}")
    
    # 在线模型检测
    detection = dtt.detect_all_models()
    total_online = detection['summary']['online']
    total_tested = detection['summary']['total']
    print(f"  在线模型: {total_online}/{total_tested}")
    for p, data in detection['providers'].items():
        online = [m for m in data['models'] if m['status'] == 'online']
        if online:
            print(f"  {p}: {len(online)} online - {[m['model_id'] for m in online]}")
    
    # 完整执行测试
    print("\n  执行测试: What is 1+1? Reply with one number.")
    exec_result = dtt.execute("What is 1+1? Reply with one number.", team_size=2)
    print(f"  成功: {exec_result['success_count']}/{len(exec_result['results'])}")
    for r in exec_result['results']:
        print(f"    {r['model']}: {str(r.get('content', r.get('error', '')))[:50]}")
    print(f"  最终结果: {exec_result['final_result']}")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()

# ===== 7. Multi-Agent Orchestrator检查 =====
print("\n[7] Multi-Agent Orchestrator检查")
try:
    from Kernel.multi_agent.multi_agent_orchestrator import MultiAgentCoordinator, AgentRole, OrchestrationMode
    coord = MultiAgentCoordinator()
    print(f"  Coordinator: OK")
    
    # 注册Agent
    agent1_id = coord.register_agent("执行专家", AgentRole.EXECUTOR, "glm-4-flash", ["代码编写"])
    print(f"  注册Agent: {agent1_id}")
except Exception as e:
    print(f"  ERROR: {e}")

# ===== 8. FineGrainedWorkflow检查 =====
print("\n[8] FineGrainedWorkflow检查")
try:
    from Kernel.workflow.fine_grained_workflow import WorkflowBuilder
    wf = WorkflowBuilder.text_to_voice_workflow("测试语音")
    print(f"  text_to_voice工作流: {len(wf.steps)} 步骤")
    for s in wf.steps:
        print(f"    - {s.step_type}: {s.name}")
except Exception as e:
    print(f"  ERROR: {e}")

# ===== 9. 工具注册表完整性检查 =====
print("\n[9] 工具注册表完整性")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("SELECT tool_name, config, is_enabled FROM tool_registry")
tools = cur.fetchall()
conn.close()
print(f"  已注册工具数: {len(tools)}")
for name, config, enabled in tools:
    try:
        cfg = json.loads(config)
        provider = cfg.get("provider", "unknown")
        print(f"  {name}: provider={provider}, enabled={enabled}")
    except:
        print(f"  {name}: enabled={enabled}")

# ===== 10. 自适应配置检查 =====
print("\n[10] AdaptiveConfig检查")
try:
    from Kernel.adaptive_config import AdaptiveConfigManager
    cfg = AdaptiveConfigManager()
    print(f"  AdaptiveConfigManager: OK")
    # 测试存取
    cfg.set("test_key", "test_value", "测试键值")
    val = cfg.get("test_key")
    print(f"  存取测试: {val}")
except Exception as e:
    print(f"  ERROR: {e}")

# ===== 11. 待修复项汇总 =====
print("\n" + "=" * 70)
print(" 诊断总结")
print("=" * 70)
print(f"  DB路径: {'一致' if SYM_SCHEDULER_DB == MODEL_FED_DB else '不一致'}")
print(f"  API Key状态: {provider_status}")
print(f"  在线模型: {total_online}/{total_tested}")
print("\n  待完成项:")
print("  1. Whisper ASR集成到OpenClaw工具链")
print("  2. 语音气泡自动回复（Gateway TTS配置）")
print("  3. 端到端语音对话（ASR→LLM→TTS）")
print("=" * 70)
