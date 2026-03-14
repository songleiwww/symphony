# 步骤3: 代码实现

## 使用的模型
- 模型名称: cherry-doubao/ark-code-latest

## 模型输入
- 设计方案文档（step2_design.md）
- 任务: 实现完整的天气查询工具代码

## 模型输出
- weather_tool.py: 主程序文件
- config.py: 配置文件
- requirements.txt: 依赖列表

---

## 3.1 实现的文件列表

### 3.1.1 config.py - 配置文件
- API Key配置
- API基础URL
- 请求超时设置
- 重试次数
- 语言设置

### 3.1.2 weather_tool.py - 主程序

#### 核心类实现

**1. WeatherAPIClient 类**
- `__init__(api_key, base_url)`: 初始化API客户端
- `get_current_weather(city, lang)`: 获取当前天气
- `_handle_response(response)`: 处理API响应
- 内置重试机制
- 完善的错误处理

**2. WeatherDataProcessor 类**
- `parse_weather_data(raw_data)`: 解析原始数据
- `format_for_display(weather_data)`: 格式化显示
- 数据提取和转换
- 美观的终端输出

**3. WeatherCLI 类**
- `setup()`: 设置API客户端
- `display_welcome()`: 显示欢迎信息
- `get_city_input()`: 获取用户输入
- `display_weather()`: 展示天气
- `display_error()`: 显示错误
- `ask_continue()`: 询问是否继续
- `run()`: 主程序循环

#### 功能特性

✅ **完整的错误处理
- 网络错误重试
- API错误提示
- 用户友好的错误信息

✅ **美观的界面
- Emoji图标增强可读性
- 清晰的信息分组
- 彩色分隔线

✅ **用户体验优化
- 支持中文/英文城市
- 交互式查询
- 优雅退出机制

### 3.1.3 requirements.txt - 依赖文件
- requests>=2.28.0

## 3.2 代码特点

1. **模块化设计**: 三个核心类职责清晰
2. **类型提示**: 使用Python类型注解
3. **文档字符串**: 完整的函数说明
4. **错误处理**: 自定义异常类
5. **配置分离**: 配置与代码分离
6. **用户友好**: Emoji图标，清晰布局

---

## 步骤3成果

✅ 完成主程序 weather_tool.py (约400行代码)
✅ 完成配置文件 config.py
✅ 完成依赖列表 requirements.txt
✅ 实现了所有核心功能
✅ 完善的错误处理和用户体验
