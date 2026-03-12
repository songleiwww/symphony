# Symphony (序境) - Multi-Model Orchestration System

**Version:** 1.1.0  
**Status:** Production Ready

---

## System Overview

Symphony is a powerful multi-model collaboration orchestration system designed to coordinate multiple AI models for complex tasks. It provides intelligent task dispatching, fault tolerance, memory management, and seamless integration across multiple AI providers.

### Key Capabilities

- **Multi-Provider Support**: Integrates with Volcano Engine, Zhipu (智谱), ModelScope (魔搭), and NVIDIA
- **Intelligent Scheduling**: Automatic model selection based on task type and availability
- **Fault Tolerance**: Rate limit detection, automatic fallback, and recovery mechanisms
- **Memory System**: Persistent context across sessions with structured memory layers

---

## Features

### Core Features

| Feature | Description |
|---------|-------------|
| **Parallel Orchestration** | Execute multiple models concurrently for faster results |
| **Dynamic Dispatching** | Intelligent task routing based on model capabilities |
| **Fault Tolerance** | Automatic failover when API limits or errors occur |
| **Rate Limit Management** | Track and recover from rate limits with smart backoff |
| **Memory Layers** | Short-term, long-term, and persistent memory management |
| **Model Binding** | Assign specific models to team members for personalized responses |

### Supported Providers

- **Volcano Engine (火山引擎)**: ark-code-latest, Doubao Seed 2.0, MiniMax M2.5
- **Zhipu (智谱)**: GLM-4-Flash, GLM-Z1-Flash, CogView-3
- **ModelScope (魔搭)**: Qwen, DeepSeek-R1, GLM series
- **Silicon Flow (硅基流动)**: Qwen2.5, GLM-4-9B

### Orchestration Strategies

- **Parallel**: Simultaneous multi-model calls
- **Sequential**: Ordered model execution
- **Chain**: Model1 → Analysis → Model2 pipeline

---

## Usage

### Basic Usage

```python
from symphony import SymphonyOrchestrator

# Initialize orchestrator
orchestrator = SymphonyOrchestrator()

# Execute task with automatic model selection
result = orchestrator.execute("Your task description here")
```

### Multi-Model Call

```python
from symphony import ParallelOrchestrator

orchestrator = ParallelOrchestrator()
results = orchestrator.call_multiple(
    models=["ark-code-latest", "glm-4-flash"],
    prompt="Your prompt"
)
```

### Configuration

```python
from symphony.config import (
    DOUBAO_CONFIG,
    ZHIPU_CONFIG,
    SILICON_FLOW_CONFIG
)

# Customize settings
DOUBAO_CONFIG["rate_limit"]["enabled"] = True
DOUBAO_CONFIG["rate_limit"]["max_requests_per_minute"] = 60
```

---

## Configuration

### Main Configuration File

`config.py` contains all system settings:

| Section | Description |
|---------|-------------|
| `DOUBAO_CONFIG` | Volcano Engine API settings |
| `ZHIPU_CONFIG` | Zhipu AI configuration |
| `MODELSCOPE_CONFIG` | ModelScope API settings |
| `SILICON_FLOW_CONFIG` | Silicon Flow configuration |
| `ROSTER_CONFIG` | Team member model bindings |

### Rate Limit Settings

```python
"rate_limit": {
    "enabled": True,
    "max_requests_per_minute": 60,
    "recovery_time": 60  # seconds
}
```

### Model Configuration

Each model supports:
- `id`: Model identifier
- `name`: Display name
- `type`: general/reasoning/code/vision
- `thinking`: Enable reasoning mode
- `context_window`: Max context tokens

---

## FAQ

### Q: How does Symphony handle rate limits?

A: Symphony monitors API usage in real-time. When rate limits are approached, it automatically:
1. Switches to backup providers
2. Queues requests with exponential backoff
3. Recovers automatically when limits reset

### Q: Can I bind specific models to team members?

A: Yes! Use the model binding feature in `ROSTER_CONFIG` to assign specific models to individual team members for personalized interactions.

### Q: What happens if all providers fail?

A: The system implements fault isolation and will:
1. Try all configured fallback models
2. Return partial results if available
3. Log failures for manual review

### Q: How do I add a new model provider?

A: Add provider configuration to `config.py` following the existing format, then register it in the orchestrator.

### Q: Is memory persistent across sessions?

A: Yes, Symphony maintains three memory layers:
- **Working Memory**: Current session context
- **Short-term**: Recent interactions
- **Long-term**: Persistent knowledge base

### Q: How do I monitor system health?

A: Use the health checker:
```python
from symphony import HealthChecker
health = HealthChecker.check_all()
```

---

## Installation

```bash
pip install symphony-ai
```

Or install from source:
```bash
git clone https://github.com/your-repo/symphony.git
cd symphony
pip install -e .
```

---

## Support

- **Email**: songlei_www@qq.com
- **Documentation**: See `docs/` folder for detailed guides
- **Issues**: Report bugs via GitHub Issues

---

## License

MIT License
