# ⚡ 快速入门指南

## 5分钟上手天气查询工具

### 第一步: 获取API Key (2分钟)

1. 访问 https://www.weatherapi.com/
2. 点击右上角 "Sign Up"
3. 填写邮箱和密码注册
4. 登录后在 Dashboard 复制你的 API Key

### 第二步: 配置 (1分钟)

用文本编辑器打开 `config.py`，把你的API Key填进去：

```python
# 把这行:
API_KEY = "YOUR_API_KEY_HERE"

# 改成你的API Key，比如:
API_KEY = "a1b2c3d4e5f6g7h8i9j0"
```

### 第三步: 安装依赖 (30秒)

```bash
pip install requests
```

### 第四步: 运行 (30秒)

```bash
python weather_tool.py
```

### 第五步: 查询天气!

输入城市名，比如: `北京` 或 `Tokyo`

---

## 🎯 常见问题

**Q: 为什么需要API Key？**
A: WeatherAPI.com 提供免费的天气数据，需要注册获取Key来使用。

**Q: API Key收费吗？**
A: 免费版每月100万次请求，足够个人使用。

**Q: 支持哪些城市？**
A: 全球几乎所有城市都支持，中英文都可以。

**Q: 程序打不开？**
A: 确认已安装Python 3.7+，并安装了requests库。

---

## 💡 使用技巧

- 输入 `q` 或 `quit` 随时退出
- 可以输入城市的英文名，如 `London`
- 程序会自动重试网络请求
- 天气数据每小时更新一次

---

**就这么简单！开始查询天气吧！** 🌤️
