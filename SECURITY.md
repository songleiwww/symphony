# Symphony 安全使用指南

## 敏感信息保护

### 配置文件

本项目包含敏感API密钥，请注意以下事项：

#### 1. 模板文件 (config.py.d)
- `config.py.d` 是配置文件模板，不包含真实API密钥
- 使用前请复制为 `config.py` 并填入您的真实API密钥

#### 2. 安全使用原则

```bash
# 复制模板
cp config.py.d config.py

# 编辑配置文件，替换以下占位符：
YOUR_ZHIPU_API_KEY_HERE    # 智谱API Key
YOUR_MODELSCOPE_API_KEY_HERE # ModelScope API Key
```

#### 3. 禁止上传的内容

请勿将以下内容上传到公开仓库：
- `config.py` (包含真实API密钥)
- 任何包含真实API密钥的文件
- 包含Token或密码的文件

#### 4. 推荐的保护方式

1. **环境变量** (推荐)
```python
import os
api_key = os.environ.get('SYMPHONY_ZHIPU_KEY')
```

2. **.gitignore**
```
config.py
*.key
.env
```

## 获取API Key

### 智谱API
- 注册: https://open.bigmodel.cn/
- API控制台: https://open.bigmodel.cn/usercenter/apikeys

### ModelScope
- 注册: https://modelscope.cn/
- API控制台: https://modelscope.cn/my/token

### 火山引擎 (Volcengine)
- 注册: https://www.volcengine.com/
- API控制台: https://console.volcengine.com/ark/

---

**安全第一，请勿泄露您的API密钥！**
