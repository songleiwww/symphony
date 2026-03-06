from brainstorm_panel_v2 import BrainstormPanel
panel = BrainstormPanel()

print('[Task 2] Creating Configuration Manager...')
r2 = panel.call_model(
    prompt="""You are a senior Python architect. Create a complete implementation for:

1. ConfigManager - Centralized configuration management
2. StructuredLogger - Structured logging with different levels
3. PerformanceMonitor - Real-time performance monitoring

Use Python dataclasses, typing. Include:
- YAML/JSON configuration file support
- Environment variable overrides
- Performance metrics tracking (latency, tokens, errors)
- Structured log format (JSON)

Write the complete code in a single code block.""",
    model_id="deepseek-ai/DeepSeek-V3.2",
    max_tokens=2000
)
print(f'  Status: {"Success" if r2.success else "Failed"}')
if r2.success:
    print(r2.response[:2000])
else:
    print(f'Error: {r2.error}')
