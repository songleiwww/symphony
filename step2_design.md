# 步骤2: 设计方案

## 使用的模型
- 模型名称: cherry-doubao/ark-code-latest

## 模型输入
- 需求分析文档（step1_requirements.md）
- 任务: 设计系统架构、技术选型、模块结构

## 模型输出
- 系统架构设计
- 技术选型方案
- 模块结构设计
- API选择说明

---

## 2.1 技术选型

### 2.1.1 编程语言
- **Python 3.7+**: 简单易用，生态丰富，适合快速开发

### 2.1.2 天气API选择

#### 方案对比

| API名称 | 免费额度 | 数据质量 | 中文支持 | 推荐度 |
|---------|---------|---------|---------|--------|
| OpenWeatherMap | 60次/分钟 | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| WeatherAPI.com | 100万次/月 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 和风天气 | 1000次/天 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

#### 最终选择
- **主选API**: WeatherAPI.com (https://www.weatherapi.com/)
  - 理由：免费额度高，中文支持好，数据全面
  - 需要注册获取API Key（免费）

- **备选API**: OpenWeatherMap
  - 理由：广泛使用，文档完善

### 2.1.3 依赖库
- `requests`: HTTP请求库
- `json`: JSON数据处理（标准库）
- `datetime`: 日期时间处理（标准库）

## 2.2 系统架构设计

```
┌─────────────────────────────────────────────────┐
│                  用户界面层                       │
│              (CLI交互、输入输出)                  │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│                  业务逻辑层                       │
│  ┌──────────────┐  ┌──────────────┐            │
│  │ 天气查询模块  │  │ 数据格式化模块│            │
│  └──────────────┘  └──────────────┘            │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│                  数据访问层                       │
│              (API请求、错误处理)                  │
└─────────────────────────────────────────────────┘
```

## 2.3 模块结构设计

### 2.3.1 文件结构
```
multi_agent_demo/
├── weather_tool.py          # 主程序文件
├── config.py                # 配置文件（API Key等）
├── requirements.txt         # 依赖列表
├── README.md                # 使用说明
└── docs/                    # 文档目录
    ├── step1_requirements.md
    ├── step2_design.md
    ├── step3_implementation.md
    ├── step4_testing.md
    └── step5_summary.md
```

### 2.3.2 核心模块设计

#### 模块1: WeatherAPI 客户端
- 类名: `WeatherAPIClient`
- 职责: 封装API请求
- 方法:
  - `__init__(api_key)`: 初始化
  - `get_current_weather(city)`: 获取当前天气
  - `_handle_response(response)`: 处理API响应

#### 模块2: 天气数据处理器
- 类名: `WeatherDataProcessor`
- 职责: 数据解析和格式化
- 方法:
  - `parse_weather_data(raw_data)`: 解析原始数据
  - `format_for_display(weather_data)`: 格式化显示

#### 模块3: 用户界面
- 类名: `WeatherCLI`
- 职责: 用户交互
- 方法:
  - `display_welcome()`: 显示欢迎信息
  - `get_city_input()`: 获取用户输入
  - `display_weather(weather_info)`: 展示天气
  - `ask_continue()`: 询问是否继续

## 2.4 数据流程

```
用户输入城市名
    ↓
WeatherCLI.get_city_input()
    ↓
WeatherAPIClient.get_current_weather(city)
    ↓
发送HTTP请求到 WeatherAPI.com
    ↓
接收JSON响应
    ↓
WeatherDataProcessor.parse_weather_data()
    ↓
WeatherDataProcessor.format_for_display()
    ↓
WeatherCLI.display_weather()
    ↓
用户看到格式化的天气信息
```

## 2.5 错误处理策略

| 错误类型 | 处理方式 | 用户提示 |
|---------|---------|---------|
| 网络错误 | 重试2次后失败 | "网络连接失败，请检查网络" |
| 城市不存在 | API返回错误 | "未找到该城市，请检查拼写" |
| API Key无效 | 验证Key | "API Key无效，请检查配置" |
| API限流 | 等待后重试 | "请求过于频繁，请稍后再试" |

---

## 步骤2成果

✅ 完成技术选型（Python + WeatherAPI.com）
✅ 设计了三层系统架构
✅ 规划了模块结构和文件组织
✅ 设计了数据流程
✅ 制定了错误处理策略
