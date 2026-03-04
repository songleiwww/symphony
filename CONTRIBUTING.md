# 贡献指南

感谢你对 Symphony 项目的兴趣！我们欢迎所有形式的贡献。

---

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发流程](#开发流程)
- [代码规范](#代码规范)
- [提交信息规范](#提交信息规范)
- [Pull Request 流程](#pull-request-流程)
- [问题报告](#问题报告)

---

## 🤝 行为准则

### 我们的承诺

为了营造开放和友好的环境，我们承诺：
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

### 不可接受的行为

- 使用性化的语言或图像
- 恶意评论或人身攻击
- 公开或私下骚扰
- 未经许可发布他人的私人信息
- 其他不专业或不恰当的行为

---

## 💡 如何贡献

### 1. 报告 Bug 🐛

如果你发现了 Bug，请：

1. 先检查 [Issues](https://github.com/yourusername/symphony/issues) 确认是否已经报告
2. 如果没有，创建一个新的 Issue，使用 Bug 报告模板
3. 包含以下信息：
   - 清晰的标题
   - 复现步骤
   - 预期行为
   - 实际行为
   - 环境信息（操作系统、Python 版本等）
   - 截图（如果适用）

### 2. 提交新功能 ✨

如果你有新功能的想法：

1. 先创建一个 Issue 讨论你的想法
2. 等待社区反馈
3. 获得认可后开始开发
4. 提交 Pull Request

### 3. 改进文档 📚

文档改进也是重要的贡献！你可以：
- 修复拼写错误
- 改进说明的清晰度
- 添加缺失的示例
- 翻译文档

### 4. 审查代码 👀

查看开放的 Pull Request 并提供反馈也是很好的贡献方式。

---

## 🛠️ 开发流程

### 环境设置

1. **Fork 仓库**
```bash
# 在 GitHub 上 Fork 本仓库
```

2. **克隆你的 Fork**
```bash
git clone https://github.com/你的用户名/symphony.git
cd symphony
```

3. **添加上游仓库**
```bash
git remote add upstream https://github.com/yourusername/symphony.git
```

4. **创建虚拟环境**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

5. **安装开发依赖**
```bash
pip install -r requirements.txt
pip install black pytest flake8  # 开发工具
```

### 保持同步

定期同步上游仓库的更改：

```bash
git checkout main
git fetch upstream
git merge upstream/main
```

---

## 📝 代码规范

### Python 代码

我们使用以下工具确保代码质量：

- **black** - 代码格式化
- **flake8** - 代码检查
- **pytest** - 测试框架

#### 代码格式化

在提交代码前运行：

```bash
black .
```

#### 代码检查

```bash
flake8 .
```

#### 运行测试

```bash
pytest tests/
```

### 代码风格指南

- 使用 4 个空格缩进（不要使用 Tab）
- 每行不超过 120 个字符
- 使用有意义的变量名
- 函数和类添加文档字符串
- 复杂逻辑添加注释

### 文档字符串示例

```python
def fetch_weather(city: str) -> dict:
    """获取指定城市的天气信息。

    Args:
        city: 城市名称（中文或英文）

    Returns:
        包含天气信息的字典

    Raises:
        APIError: 当 API 请求失败时
        NetworkError: 当网络连接失败时
    """
    pass
```

---

## 📋 提交信息规范

我们使用约定式提交（Conventional Commits）规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

- `feat`: 新功能
- `fix`: 修复 Bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具相关

### 示例

```
feat(weather): 添加摄氏度/华氏度切换功能

- 添加温度单位配置选项
- 更新 UI 显示逻辑
- 添加单元测试

Closes #123
```

```
fix(api): 修复网络重试逻辑

修复在特定网络条件下重试失败的问题
添加更详细的错误日志

Fixes #456
```

---

## 🔄 Pull Request 流程

### 创建 PR 前检查清单

- [ ] 我已经阅读了贡献指南
- [ ] 我的代码遵循项目的代码规范
- [ ] 我已经运行了 `black` 和 `flake8`
- [ ] 我已经添加了必要的测试
- [ ] 所有测试都通过了
- [ ] 我已经更新了相关文档
- [ ] 我的提交信息符合规范

### PR 流程

1. **创建特性分支**
```bash
git checkout -b feature/你的功能名
```

2. **提交更改**
```bash
git add .
git commit -m "feat: 添加新功能"
```

3. **推送到你的 Fork**
```bash
git push origin feature/你的功能名
```

4. **创建 Pull Request**
   - 访问你的 Fork 仓库
   - 点击 "Compare & pull request"
   - 填写 PR 模板
   - 提交 PR

### PR 模板

请在 PR 中包含以下信息：

```markdown
## 变更描述
简要描述你的变更。

## 相关 Issue
Closes #123

## 变更类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 破坏性变更
- [ ] 文档更新

## 测试
- [ ] 我已添加测试
- [ ] 所有现有测试通过

## 截图（如适用）
```

### 审查流程

1. 至少需要一个维护者审查
2. 可能需要修改和重新提交
3. 通过后会被合并

---

## 🐛 问题报告

### 创建 Issue

当你报告问题时，请提供：

1. **清晰的标题** - 用一句话概括问题
2. **复现步骤** - 详细的步骤让我们能够复现
3. **预期行为** - 你期望发生什么
4. **实际行为** - 实际发生了什么
5. **环境信息** - 操作系统、Python 版本、依赖版本等
6. **日志输出** - 相关的错误日志
7. **截图** - 如果有帮助的话

### Issue 模板

```markdown
## 问题描述
清晰简洁地描述问题。

## 复现步骤
1. 步骤 1
2. 步骤 2
3. 步骤 3

## 预期行为
你期望发生什么？

## 实际行为
实际发生了什么？

## 环境信息
- 操作系统：Windows 10 / macOS 12 / Ubuntu 20.04
- Python 版本：3.9.x
- 项目版本：v0.1.0

## 日志输出
```
粘贴相关日志
```

## 截图（如适用）
```

---

## 🎯 好的首次贡献

如果你是第一次贡献，可以查看标记为 `good first issue` 的 Issue：

- 文档改进
- 简单的 Bug 修复
- 添加测试用例
- 代码注释改进

---

## 📞 获取帮助

如果你需要帮助：

- 查看 [文档](README.md)
- 在 [Discussions](https://github.com/yourusername/symphony/discussions) 提问
- 加入我们的社区聊天

---

## 🙏 感谢

每一份贡献都很重要，感谢你花时间改进这个项目！

---

**让我们一起创造更好的 Symphony！** 🎼
