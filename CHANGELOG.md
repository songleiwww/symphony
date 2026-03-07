# Symphony v1.1.0-beta 发布说明

## 版本信息
- **版本号**: 1.1.0-beta
- **发布日期**: 2026-03-07
- **GitHub**: https://github.com/songleiwww/symphony

## 一、多种安装方式

### 方式1: Linux/macOS一键安装
```bash
curl -sL https://raw.githubusercontent.com/songleiwww/symphony/main/install.sh | bash
# 或
bash install.sh
```

### 方式2: Windows PowerShell
```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

### 方式3: Docker
```bash
docker build -t symphony .
docker run -it symphony
```

### 方式4: pip安装
```bash
pip install symphony-ai
```

### 方式5: 手动安装
```bash
git clone https://github.com/songleiwww/symphony.git
cd symphony
pip install -r requirements.txt
```

## 二、核心功能

| 功能 | 说明 |
|------|------|
| 多模型协作 | 6个模型并行调用 |
| 智能调度 | 根据意图动态选择模型 |
| 故障隔离 | CircuitBreaker模式 |
| 服务降级 | Fallback机制 |
| 记忆协调 | OpenClaw同步 |

## 三、项目结构

```
symphony/
├── 核心模块/
│   ├── symphony_core.py     # 核心引擎
│   ├── model_manager.py    # 模型管理
│   ├── fault_isolator.py   # 故障隔离
│   ├── fallback.py         # 降级策略
│   └── memory_coordinator.py
├── 配置/
│   └── config.py
├── 安装脚本/
│   ├── install.sh          # Linux/macOS
│   ├── install.ps1         # Windows
│   └── Dockerfile
└── 文档/
    ├── README.md
    └── CHANGELOG.md
```

## 四、配置说明

编辑 `config.py`，填入API Key：

```python
MODEL_CHAIN = [
    {
        "name": "your_model",
        "api_key": "YOUR_API_KEY",
        "enabled": True
    }
]
```

## 五、使用示例

```python
from symphony import Symphony

s = Symphony(config)
result = s.call("你好")
print(result)
```

## 六、版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.1.0-beta | 2026-03-07 | 多种安装方式 |
| 1.0.0-beta | 2026-03-07 | 首次公测 |

## 七、注意事项

1. 需要有效的API Key
2. 部分模型可能有调用限制
3. 建议先测试再生产使用

---

**品牌标语**: "智韵交响，共创华章！"
