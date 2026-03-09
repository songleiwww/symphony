# Symphony v2.1.2 - 智能多模型协作系统

## 简介
Symphony（交响）是一个智能多模型协作系统，支持多模型并行调用、团队协作、工具共享等功能。

## 安装

### Windows
```bat
install.bat
```

### Linux/Mac
```bash
chmod +x install.sh
./install.sh
```

### 手动安装
1. 复制 `symphony/` 目录到你的 AI 系统的 skills 目录
2. 复制 `config.template.py` 为 `config.py`
3. 编辑 `config.py`，填写你的 API 密钥

## API 配置

### 火山引擎 (推荐)
- 基础URL: `https://ark.cn-beijing.volces.com/api/coding/v3`
- API密钥: 你的火山引擎密钥

### 可用模型
| 模型ID | 说明 |
|--------|------|
| ark-code-latest | 默认引擎 |
| DeepSeek-V3.2 | 深度思考 |
| Doubao-Seed-2.0-Code | 代码专家 |
| GLM-4.7 | 智谱GLM |
| Kimi-K2.5 | 长文本 |

## 给 AI 助手的安装说明

> 复制 symphony/ 到你的 skills 目录
> 复制 config.template.py 为 config.py
> 填写 API_KEY 即可使用
> 呼叫"交响"开始对话

## 首次使用示例

> "交响你好！"
> "交响，帮我安排一个6人团队讨论"
> "交响团队有哪些人？"

## 团队
- 交响团队 (6人)
- 青丘狐族 (6人)

**品牌**: "智韵交响，共创华章"

---
版本: 2.1.2 | 发布日期: 2026-03-09
