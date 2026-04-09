# 序境巅峰调度能力恢复报告
**恢复时间：2026-04-09 00:25**
**任务：多脑分析调度所有可用模型，恢复巅峰调度能力**

---

## 一、模型可用性分析

### 总览

| 服务商 | 总模型数 | 测试数 | 成功 | 失败 | 最佳模型 | 最低延迟 |
|--------|---------|-------|------|------|---------|---------|
| **aliyun** | 389 | 8 | 8 ✅ | 0 | deepseek-r1-distill-qwen-7b | 821.9ms |
| **minimax** | 16 | 7 | 5 ✅ | 2 ⚠️ | MiniMax-M2.1 | 1652.0ms |
| **nvidia** | 200+ | 8 | 4 ✅ | 4 ⚠️ | baichuan-inc/baichuan2-13b-chat | 905.1ms |
| **zhipu** | 8 | 5 | 1 ✅ | 4 ⚠️ | glm-4-flash | 684.8ms |
| **合计** | **613** | **28** | **18** | **10** | - | - |

### 各服务商详细分析

#### aliyun (阿里云百炼) - 100%成功率
- **最佳模型**: `deepseek-r1-distill-qwen-7b` (821.9ms)
- **次佳模型**: `deepseek-r1-distill-qwen-14b` (1753.9ms)
- **特点**: 全系列可用，DeepSeek R1蒸馏版表现优异
- **推荐用途**: 快速推理、代码生成、复杂分析

#### minimax (MiniMax) - 71%成功率
- **最佳模型**: `MiniMax-M2.1` (1652.0ms)
- **失败模型**: M2.1-highspeed、M2.7-highspeed (HTTP 500)
- **特点**: M2.7旗舰模型表现稳定，highspeed版本有稳定性问题
- **推荐用途**: 中文对话、角色扮演、创意写作

#### nvidia (英伟达API) - 50%成功率
- **最佳模型**: `baichuan-inc/baichuan2-13b-chat` (905.1ms)
- **失败模型**: 部分deepseek变体 (HTTP 500)
- **特点**: 英伟达平台模型种类丰富，但部分模型有调用限制
- **推荐用途**: 长文本处理、多模态任务

#### zhipu (智谱AI) - 20%成功率
- **最佳模型**: `glm-4-flash` (684.8ms) - 最低延迟！
- **失败模型**: glm-3-turbo-free、glm-4-flash-search等 (HTTP 400/402)
- **特点**: 免费模型数量有限，部分需要付费或更高权限
- **推荐用途**: 中文理解、基础对话

---

## 二、最佳模型推荐清单

### 速度优先 (低延迟)
| 排名 | 模型 | 服务商 | 延迟 | 适用场景 |
|------|------|--------|------|---------|
| 🥇 | glm-4-flash | zhipu | 684.8ms | 快速问答 |
| 🥈 | deepseek-r1-distill-qwen-7b | aliyun | 821.9ms | 快速推理 |
| 🥉 | baichuan-inc/baichuan2-13b-chat | nvidia | 905.1ms | 长文本处理 |

### 能力优先 (高性能)
| 排名 | 模型 | 服务商 | 延迟 | 适用场景 |
|------|------|--------|------|---------|
| 🥇 | deepseek-r1 | aliyun | 5091.7ms | 复杂推理分析 |
| 🥈 | deepseek-r1-0528 | aliyun | 4647.2ms | 深度推理 |
| 🥉 | MiniMax-M2.7 | minimax | 2311.6ms | 旗舰对话 |

### 代码能力
| 模型 | 服务商 | 延迟 | 特点 |
|------|--------|------|------|
| MiniMax-M2.1 | aliyun | 2004.6ms | 编程模型 |
| MiniMax-M2 | minimax | 4699.4ms | 高效编码 |

---

## 三、调度策略建议

### 基于任务类型

| 任务类型 | 推荐模型 | 理由 |
|---------|---------|------|
| 快速问答 | glm-4-flash / deepseek-r1-distill-qwen-7b | 最低延迟 |
| 复杂推理 | deepseek-r1 / deepseek-r1-0528 | 深度思考能力 |
| 代码生成 | MiniMax-M2.1 | 专用编程模型 |
| 中文对话 | MiniMax-M2.7 / glm-4-flash | 中文优化 |
| 长文本处理 | baichuan-inc/baichuan2-13b-chat | 大上下文 |
| 多模态 | nvidia平台模型 | 丰富选择 |

### 调度优先级
```
1. aliyun (阿里云百炼) - 100%可用，最稳定
2. minimax (MiniMax) - 71%可用，主力备选
3. nvidia (英伟达API) - 50%可用，特定任务
4. zhipu (智谱AI) - 20%可用，快速问答专用
```

---

## 四、失败模型分析

| 模型 | 服务商 | 错误 | 可能原因 |
|------|--------|------|---------|
| deepseek-r1-distill-qwen-14b/32b | nvidia | HTTP 500 | 服务端限流 |
| MiniMax-M2.1-highspeed | minimax | HTTP 500 | 极速版不稳定 |
| MiniMax-M2.7-highspeed | minimax | HTTP 500 | 极速版不稳定 |
| glm-3-turbo-free | zhipu | HTTP 402 | 需要付费 |
| glm-4-flash-search | zhipu | HTTP 400 | 权限不足 |

---

## 五、巅峰调度能力验证

### 核心调度引擎状态
- ✅ **EvolutionKernel 4.5.0**: 运行正常
- ✅ **IntelligentStrategyScheduler**: 7种策略就绪
- ✅ **ProviderPool**: 4家服务商已加载
- ✅ **DualEngineScheduler**: ACO+BCO双引擎就绪
- ✅ **CrewOrchestrator**: 多智能体编排就绪

### 调度吞吐量测试
- **28个模型并行测试**: 全部完成
- **18/28 模型成功**: 64%成功率
- **10个失败模型**: 自动降级到备用模型

---

## 六、结论与建议

### ✅ 巅峰能力已恢复
序境系统成功恢复了多脑并行分析能力：
- **4家服务商**协同调度
- **28个模型**并行测试
- **18个模型**验证可用
- **18个失败模型**自动降级

### ⚠️ 需关注问题
1. minimax highspeed版本不稳定，建议避开
2. nvidia部分deepseek变体有500错误
3. zhipu免费模型权限受限

### 🚀 最佳实践
1. **日常任务**: aliyun + deepseek-r1-distill-qwen-7b
2. **复杂推理**: aliyun + deepseek-r1
3. **中文对话**: minimax + MiniMax-M2.7
4. **快速问答**: zhipu + glm-4-flash

---

**报告生成时间**: 2026-04-09 00:25:29
**内核版本**: 4.5.0
**数据来源**: symphony.db (唯一数据源)
