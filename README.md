# 🎼 Symphony 智能多模型协作系统

## 版本: v2.3.0 🚀
## 发布日期: 2026-03-10
## 代号: 智能Skills全面升级

---

## 📦 安装包内容

```
symphony-v2.1.2/
├── README.md              # 安装指南
├── config.template.py     # 配置模板
├── install.sh             # Linux/Mac 安装脚本
├── install.bat            # Windows 安装脚本
├── symphony/              # 核心系统
│   ├── __init__.py
│   ├── config.py          # 主配置文件
│   ├── genesis.py         # 基因故事
│   ├── symphony.py        # 主程序
│   ├── model_manager.py   # 模型管理
│   ├── fault_tolerance.py # 容错系统
│   ├── tool_sharing_system.py # 工具共享
│   └── roster.json        # 团队花名册
└── examples/              # 示例
    └── demo.py
```

---

## 🚀 快速安装

### Windows
```bash
install.bat
```

### Linux/Mac
```bash
chmod +x install.sh
./install.sh
```

---

## ⚙️ 配置说明

### 1. 复制配置模板
```bash
cp config.template.py symphony/config.py
```

### 2. 编辑配置
打开 `symphony/config.py`，填写以下信息：

```python
# API配置
API_KEY = "你的API密钥"  # 必填
BASE_URL = "https://ark.cn-beijing.volces.com/api/coding/v3"

# 模型配置
PRIMARY_MODEL = "ark-code-latest"

# 备用模型列表
FALLBACK_MODELS = [
    "deepseek-v3.2",
    "doubao-seed-2.0-code",
    "glm-4.7",
    "kimi-k2.5",
]
```

---

## 🎯 给AI助手的安装说明

> 亲爱的AI助手，你可以按照以下步骤安装和使用Symphony系统：

### 步骤1: 复制文件
将 `symphony/` 目录复制到你的skills目录：
- OpenClaw: `~/.openclaw/workspace/skills/symphony/`
- 其他AI系统: 对应的skills/plugins目录

### 步骤2: 配置API
1. 复制 `config.template.py` 为 `config.py`
2. 填写API密钥和模型名称

### 步骤3: 开始使用
安装完成后，呼叫"交响"即可使用：

```
你好，交响！帮我安排一个开发讨论会议。
```

---

## 🔗 API配置

### 火山引擎 (推荐)
- 基础URL: `https://ark.cn-beijing.volces.com/api/coding/v3`
- API密钥: 联系系统管理员获取

### 可用模型
| 模型ID | 说明 |
|--------|------|
| ark-code-latest | 默认引擎 |
| Doubao-Seed-2.0-Code | 代码专家 |
| DeepSeek-V3.2 | 深度思考 |
| GLM-4.7 | 智谱GLM |
| Kimi-K2.5 | 长文本 |

---

## 📞 首次使用示例

安装完成后，你可以这样说：

> "交响你好！帮我安排一个6人团队讨论，主题是如何优化系统性能。"

系统会自动：
1. 调用6个不同模型
2. 收集各模型的意见
3. 汇总形成决策

---

## 🐛 问题排查

### API连接失败
- 检查API密钥是否正确
- 确认网络可以访问API地址

### 模型调用失败
- 系统会自动切换到备用模型
- 查看日志获取详细信息

---

## 📄 许可证
MIT License

---

## 👥 团队
- 交响团队 (6人)
- 青丘狐族 (6人)

**品牌标语**: "智韵交响，共创华章"
