# Symphony v1.0.0 公测版发布说明

## 版本信息
- **版本号**: 1.0.0-beta
- **发布日期**: 2026-03-07
- **项目地址**: https://github.com/songleiwww/symphony

## 一、什么是Symphony（交响）？

Symphony（交响）是一个多模型协作系统，通过并行调用多个AI模型，实现更强大的任务处理能力。

## 二、核心特性

### 1. 真正多模型协作
- 使用不同模型并行调用
- 每个模型只扮演一个角色
- 禁止角色扮演

### 2. 模型类型支持
- 文本模型 (Text)
- 视觉模型 (Vision) 
- 图像生成 (Image Gen)
- 视频生成 (Video Gen)
- 推理模型 (Reasoning)

### 3. 被动触发引擎
- 多模式智能触发
- P0-P4优先级配置

### 4. 调度容错
- 错误自动处理
- API限流降级

## 三、快速安装（一步到位）

### Linux/macOS
```bash
# 一键安装
curl -s https://raw.githubusercontent.com/songleiwww/symphony/main/install.sh | bash
```

### Windows
```powershell
# 下载安装脚本
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/songleiwww/symphony/main/install.ps1" -OutFile "install.ps1"
# 运行安装
.\install.ps1
```

## 四、配置说明

编辑 `config.py`，填入你的API Key：

```python
MODEL_CHAIN = [
    {
        "name": "your_model",
        "api_key": "你的API Key",
        "enabled": True
    }
]
```

## 五、使用方法

```python
from symphony import Symphony

# 初始化
s = Symphony(config)

# 调用
result = s.call("你好，Symphony!")
print(result)
```

## 六、已实现的进化能力

| 能力 | 描述 |
|------|------|
| 被动触发引擎 | 多模式智能触发 |
| 真正多模型协作 | 并行调用不同模型 |
| 模型验证系统 | 真实API调用验证 |
| 技能有效性验证 | 技能测试与优化 |
| 多模型类型正确使用 | 图像/向量/排序模型 |

## 七、版本历史

- v1.0.0-beta (2026-03-07) - 首次公测发布

## 八、注意事项

1. 需要有效的API Key才能使用
2. 部分模型可能有API调用限制
3. 建议先测试再生产使用

## 九、反馈与支持

- GitHub Issues: https://github.com/songleiwww/symphony/issues
- 问题反馈: 请提交Issue

---

**品牌标语**: "智韵交响，共创华章！"
