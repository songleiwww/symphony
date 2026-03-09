# 交响 (Symphony) v2.0.0

智韵交响，共创华章

## 概述

Symphony（交响）是一个多模型协作调度系统，支持同时调用多个AI模型进行并行处理。

## 特性

- 🚀 **多引擎支持**: 火山引擎、智谱、魔搭、英伟达
- 📊 **30+模型**: 推理、代码、视觉、图像生成
- ⚡ **并发调用**: 多模型并行执行
- 📈 **实时监控**: 彩色监控面板
- 🔄 **跨程序监控**: 独立程序间数据共享

## 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置API

复制 `config.template.py` 为 `config.py`，填入你的API Key：

```python
# config.py
API_CONFIGS = {
    "zhipu": {
        "api_key": "你的智谱API Key",
        "base_url": "https://open.bigmodel.cn/api/paas/v4"
    },
    "doubao": {
        "api_key": "你的火山引擎API Key",
        "base_url": "https://ark.cn-beijing.volces.com/api/coding/v3"
    },
    "modelscope": {
        "api_key": "你的魔搭API Key",
        "base_url": "https://api-inference.modelscope.cn/v1"
    },
    "nvidia": {
        "api_key": "你的英伟达API Key",
        "base_url": "https://integrate.api.nvidia.com/v1"
    }
}
```

### 3. 运行

```bash
python symphony.py
```

### 4. 菜单选项

- **1**: 单模型对话
- **2**: 多模型并行调用
- **3**: 查看监控数据
- **4**: 快速测试
- **5**: 实时监控（自动刷新）
- **0**: 退出

## 配置模板

见 `config.template.py`

## 架构

```
symphony.py      - 主程序（控制台+监控）
config.py        - API配置
genesis.py       - 基因故事
monitor_data.json - 监控数据文件
```

## 模型列表

### 火山引擎 (9模型)
- ark-code-latest, Doubao-Seed-2.0-pro, Doubao-Seed-2.0-Code
- Doubao-Seed-2.0-lite, Doubao-Seed-Code, MiniMax-M2.5
- Kimi-K2.5, GLM-4.7, DeepSeek-V3.2

### 智谱 (6模型)
- glm-4-flash, glm-z1-flash, glm-4.1v-thinking-flash
- glm-4v-flash, cogview-3-flash, cogvideox-flash

### 魔搭 (5模型)
- ZhipuAI/GLM-4.7-Flash, Tongyi-MAI/Z-Image-Turbo
- deepseek-ai/DeepSeek-V3.2, Qwen/Qwen3-Coder-480B-A35B-Instruct
- Qwen/Qwen3-235B-A22B-Instruct-2507

### 英伟达 (10模型)
- meta/llama-3.1-405b-instruct, deepseek-ai/deepseek-v3.2
- moonshotai/kimi-k2.5, z-ai/glm4.7, qwen/qwen3-coder-480b-a35b-instruct
- qwen/qwen3.5-397b-a17b, minimaxai/minimax-m2.5, z-ai/glm5
- openai/gpt-oss-20b, nvidia/llama-3.1-nemotron-70b-instruct

## 许可证

MIT

## 作者

Symphony Team
