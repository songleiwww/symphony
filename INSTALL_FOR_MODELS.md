# Symphony Installation & Setup for AI Models
# 给AI模型使用的交响安装与设置

**版本**: v0.4.7  
**最后更新**: 2026-03-05

---

## 快速开始 - Quick Start

如果你是一个AI模型（Claude、GPT、Gemini等），需要调试或使用Symphony（交响），从这里开始！

### 1. 了解项目 - Understand the Project

**项目名称（中文）**: 交响  
**项目名称（英文）**: Symphony  
**品牌标语**: 智韵交响，共创华章  
**GitHub仓库**: https://github.com/songleiwww/symphony  
**本地路径**: `C:\Users\Administrator\.openclaw\workspace\multi_agent_demo`

**作者**: 步花间 (Huajian Bu)  
**邮箱**: songlei_www@hotmail.com  
**地点**: 中国，北京 (Beijing, China)

---

### 2. 核心文件结构 - Core File Structure

```
symphony/
├── 📄 README.md                    # 项目说明
├── 📄 VERSION.md                   # 版本历史
├── 📄 VERSION_v047.md              # v0.4.7整理版本文档（必读！）
├── 📄 package.json                 # 项目元数据
├── 📄 CITATION.cff                 # 学术引用
├── 📄 requirements.txt              # Python依赖
│
├── 🤖 核心模块 - Core Modules (17个)
├── config.py                        # 配置文件（17个模型）
├── model_manager.py                 # 模型管理器
├── fault_tolerance.py               # 故障处理系统
├── skill_manager.py                 # 技能管理器
├── mcp_manager.py                   # MCP工具管理器
├── symphony_core.py                 # 统一调度核心
├── memory_system.py                 # 记忆系统
├── async_memory_core.py             # 异步记忆核心v2.0
├── memory_visualizer.py             # 记忆可视化
├── openclaw_config_loader.py        # OpenClaw配置加载器
├── memory_importer_exporter.py      # 记忆导入导出
├── context_aware_memory.py          # 情境感知记忆
├── streaming_output.py              # 流式输出
├── async_task_queue.py              # 异步任务队列
├── concurrency_monitor.py           # 并发监控
├── deadlock_detector.py             # 死锁检测和超时
└── ux_improvements.py               # 用户体验改进
│
├── 🔧 示例与工具 - Examples & Tools
├── weather_tool.py                  # 天气查询工具
├── simple_test.py                   # 简单测试
├── quick_demo.py                    # 快速演示
├── openclaw_demo.py                 # OpenClaw演示
└── tianji_adapter.py                # 天机适配器
│
├── 📁 目录 - Directories
├── todo/                            # 待办事项工具
├── docs/                            # 文档
├── examples/                        # 示例
├── tests/                           # 测试
├── .github/                         # GitHub配置
└── symphony_memory/                 # 交响记忆存储
```

---

### 3. 核心模块快速参考 - Core Modules Quick Reference

#### 模型管理 - Model Management
| 文件 | 功能 | 快速使用 |
|------|------|----------|
| `model_manager.py` | 管理17个模型，故障转移 | `from model_manager import ModelManager` |
| `fault_tolerance.py` | 故障检测、自动重试、替补机制 | `from fault_tolerance import FaultTolerance` |

#### 记忆系统 - Memory System
| 文件 | 功能 | 快速使用 |
|------|------|----------|
| `memory_system.py` | 短期/长期记忆、自动管理、长期学习 | `from memory_system import create_memory_system` |
| `async_memory_core.py` | 异步记忆、线程安全、RateLimiter | `from async_memory_core import create_improved_core` |
| `memory_visualizer.py` | ASCII仪表盘、HTML报告 | `from memory_visualizer import MemoryVisualizer` |
| `memory_importer_exporter.py` | JSON/Markdown/CSV导入导出 | `from memory_importer_exporter import create_memory_importer_exporter` |
| `context_aware_memory.py` | 时间/会话/用户/任务情境 | `from context_aware_memory import ContextAwareMemory` |

#### 调度与执行 - Scheduling & Execution
| 文件 | 功能 | 快速使用 |
|------|------|----------|
| `symphony_core.py` | 统一调度核心，集成记忆 | `from symphony_core import SymphonyCore` |
| `async_task_queue.py` | 优先级队列、重试、asyncio | `from async_task_queue import AsyncTaskQueue` |
| `concurrency_monitor.py` | 指标、历史、ASCII仪表盘 | `from concurrency_monitor import ConcurrencyMonitor` |
| `deadlock_detector.py` | 等待图、DFS检测、超时 | `from deadlock_detector import DeadlockDetector` |
| `streaming_output.py` | 文本/进度/状态/错误流 | `from streaming_output import StreamingOutput` |
| `ux_improvements.py` | 进度条、友好错误、确认 | `from ux_improvements import ProgressBar, FriendlyError` |

#### 工具与适配器 - Tools & Adapters
| 文件 | 功能 | 快速使用 |
|------|------|----------|
| `skill_manager.py` | 技能管理 | `from skill_manager import SkillManager` |
| `mcp_manager.py` | MCP工具管理 | `from mcp_manager import MCPManager` |
| `openclaw_config_loader.py` | 从OpenClaw读取配置 | `from openclaw_config_loader import load_openclaw_config` |

---

### 4. 快速使用示例 - Quick Usage Examples

#### 示例1：使用记忆系统 - Example 1: Using Memory System

```python
from memory_system import create_memory_system

# Create memory system - 创建记忆系统
memory, learning = create_memory_system()

# Add a memory - 添加记忆
memory.add_memory(
    content="这是一个测试记忆",
    memory_type="short_term",
    importance=0.8,
    tags=["test", "example"],
    source="user"
)

# Retrieve memories - 检索记忆
results = memory.retrieve_memory("测试", limit=5)

# Record preference - 记录偏好
learning.record_preference("theme", "dark")

# Get stats - 获取统计
stats = memory.get_stats()
print(stats)
```

#### 示例2：使用异步任务队列 - Example 2: Using Async Task Queue

```python
import asyncio
from async_task_queue import AsyncTaskQueue, TaskPriority

async def example_task():
    """示例任务"""
    await asyncio.sleep(1)
    return "Task completed!"

async def main():
    # Create queue - 创建队列
    queue = AsyncTaskQueue()
    
    # Add tasks - 添加任务
    await queue.add_task(example_task, priority=TaskPriority.HIGH)
    await queue.add_task(example_task, priority=TaskPriority.NORMAL)
    
    # Start processing - 开始处理
    await queue.start()
    
    # Wait for completion - 等待完成
    await queue.wait_completion()

asyncio.run(main())
```

#### 示例3：使用OpenClaw配置加载器 - Example 3: Using OpenClaw Config Loader

```python
from openclaw_config_loader import load_openclaw_config, convert_to_symphony_config

# Load OpenClaw config - 加载OpenClaw配置
openclaw_config = load_openclaw_config()

# Convert to Symphony format - 转换为交响格式
symphony_config = convert_to_symphony_config(openclaw_config)

# Use the config - 使用配置
print(f"Loaded {len(symphony_config['models'])} models!")
```

---

### 5. 测试文件 - Test Files

如果你想运行测试，这里是快速参考：

| 测试文件 | 说明 | 运行方式 |
|----------|------|----------|
| `simple_test.py` | 简单测试 | `python simple_test.py` |
| `quick_demo.py` | 快速演示 | `python quick_demo.py` |
| `openclaw_demo.py` | OpenClaw演示 | `python openclaw_demo.py` |

---

### 6. 版本历史快速查阅 - Version History Quick Look

| 版本 | 代号 | 主要功能 |
|------|------|----------|
| v0.4.7 | Organize - 整理 | 文件分类、清理策略 |
| v0.4.6 | Author - 作者 | 作者元数据、GitHub配置 |
| v0.4.5 | Evolution - 进化 | 进化分析、6位专家 |
| v0.4.4 | Complete - 完整 | v0.4.x完整总结 |
| v0.4.3 | Workshop - 讨论会 | 2轮深度讨论会 |
| v0.4.2 | Deep Debug - 深度调试 | 9模块深度测试 |
| v0.4.1 | Debug - 调试 | 完整Debug测试 |
| v0.4.0 | Foundations - 奠基 | 8个核心模块 |

**详细版本历史**: 查看 `VERSION.md` 和 `VERSION_v047.md`

---

### 7. 重要提示 - Important Notes

#### 安全 - Security
- `config.py` 中的API Key是占位符（`YOUR_...`）
- 真实Key在OpenClaw配置中：`C:\Users\Administrator\.openclaw\openclaw.cherry.json`
- **不要**将真实Key提交到GitHub！

#### 编码 - Encoding
- 部分文件有Windows编码问题
- 建议使用UTF-8编码读取/写入文件
- 避免使用emoji字符保证兼容性

#### 模型配置 - Model Config
- 17个模型，4个提供商：cherry-doubao/cherry-minimax/cherry-nvidia/cherry-modelscope
- 主模型：ark-code-latest
- 备用模型：5个（MiniMax-M2.5, deepseek-v3.2, doubao-seed-2.0-code, glm-4.7, kimi-k2.5）

---

### 8. 如果你需要调试 - If You Need to Debug

#### 步骤1：运行简单测试 - Step 1: Run Simple Test
```bash
python simple_test.py
```

#### 步骤2：检查配置 - Step 2: Check Config
```bash
# 查看config.py
# 或使用openclaw_config_loader.py
```

#### 步骤3：查看记忆 - Step 3: Check Memory
```bash
# 查看 symphony_memory/ 目录
# 或使用 memory_system.py
```

---

### 9. 联系与反馈 - Contact & Feedback

**作者**: 步花间 (Huajian Bu)  
**邮箱**: songlei_www@hotmail.com  
**GitHub Issues**: https://github.com/songleiwww/symphony/issues  
**GitHub Discussions**: https://github.com/songleiwww/symphony/discussions

---

## 总结 - Summary

这是给AI模型使用的Symphony（交响）快速安装与设置指南！

**关键文件**:
- `VERSION_v047.md` - 必读！完整的文件分类和版本说明
- `memory_system.py` - 记忆系统（最常用）
- `async_memory_core.py` - 异步记忆核心
- `symphony_core.py` - 统一调度核心
- `openclaw_config_loader.py` - OpenClaw配置加载器

**祝你使用愉快！祝你调试顺利！**

---

智韵交响，共创华章
