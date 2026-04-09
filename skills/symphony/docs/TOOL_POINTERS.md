# 序境系统 - 工具指向说明 v1.0.0

> 生成时间: 2026-04-04
> 版本: Symphony v4.3.0

---

## 一、系统架构

```
用户查询 → 自然语言理解 → 工具匹配 → 参数提取 → 权限校验 → 工具执行 → 结果返回
```

---

## 二、支持的工具清单

### 2.1 文件操作类

| 工具名称 | 功能 | 危险等级 | 权限要求 |
|---------|------|---------|---------|
| `read` | 读取文件内容 | 低 | basic |
| `write` | 写入内容到文件（覆盖） | **高** | elevated |
| `edit` | 编辑文件（精确替换） | **高** | elevated |

### 2.2 执行控制类

| 工具名称 | 功能 | 危险等级 | 权限要求 |
|---------|------|---------|---------|
| `exec` | 执行Shell命令 | **高** | elevated |
| `process` | 管理运行中的会话 | 中 | basic |
| `pdf` | 分析PDF文档 | 低 | basic |

### 2.3 Web交互类

| 工具名称 | 功能 | 危险等级 | 权限要求 |
|---------|------|---------|---------|
| `web_search` | DuckDuckGo搜索 | 低 | basic |
| `web_fetch` | 提取URL内容 | 低 | basic |
| `browser` | 控制浏览器 | 中 | basic |

### 2.4 飞书集成类

| 工具名称 | 功能 | 危险等级 | 权限要求 |
|---------|------|---------|---------|
| `feishu_doc` | 飞书文档操作 | 中 | basic |
| `feishu_drive` | 飞书云存储 | 中 | basic |
| `feishu_wiki` | 飞书知识库 | 中 | basic |
| `feishu_chat` | 飞书聊天操作 | 中 | basic |
| `feishu_bitable_*` | 飞书多维表格 | 中 | basic |
| `feishu_app_scopes` | 查询应用权限 | 低 | basic |

### 2.5 媒体类

| 工具名称 | 功能 | 危险等级 | 权限要求 |
|---------|------|---------|---------|
| `image` | 分析图片 | 低 | basic |
| `image_generate` | 生成图片 | 低 | basic |
| `tts` | 文字转语音 | 低 | basic |
| `canvas` | 控制画布 | 低 | basic |

### 2.6 会话管理类

| 工具名称 | 功能 | 危险等级 | 权限要求 |
|---------|------|---------|---------|
| `message` | 发送消息 | 中 | basic |
| `sessions_list` | 列出会话 | 低 | basic |
| `sessions_history` | 获取历史 | 低 | basic |
| `sessions_send` | 发送消息到其他会话 | 中 | basic |
| `sessions_spawn` | 创建子会话 | 中 | basic |
| `subagents` | 管理子代理 | 中 | basic |

---

## 三、危险工具说明

以下工具被标记为`DANGEROUS_TOOLS`，执行前需要额外权限校验：

### 3.1 exec（Shell命令执行）
- **风险**: 可执行任意系统命令
- **权限等级**: `elevated`
- **使用场景**: 仅用于安全审核、系统维护任务

### 3.2 write/edit（文件写入）
- **风险**: 可覆盖或修改任意文件
- **权限等级**: `elevated`
- **使用场景**: 仅用于已确认的文件操作

### 3.3 feishu_bitable_create_record / feishu_bitable_update_record
- **风险**: 可能造成数据污染
- **权限等级**: `elevated`
- **使用场景**: 仅用于明确的数据同步任务

---

## 四、工具调用流程

```
1. 用户输入自然语言查询
2. ToolCaller 解析查询意图
3. 匹配最佳工具（基于关键词/语义）
4. 提取工具参数（自动类型转换）
5. 权限校验（检查 dangerous_tools 列表）
6. 执行工具调用
7. 记录调用日志到 memory_db
8. 返回结构化结果
```

---

## 五、日志追溯

所有工具调用都会记录到 `memory_db`，包括：

| 字段 | 说明 |
|------|------|
| `trace_id` | 唯一追踪ID |
| `tool_name` | 工具名称 |
| `parameters` | 调用参数 |
| `success` | 是否成功 |
| `result` | 返回结果 |
| `error` | 错误信息 |
| `execution_time` | 执行耗时 |

---

## 六、快速参考

### 读取文件
```
自然语言: "帮我看看 config.json 的内容"
工具映射: read(path="config.json")
```

### 写入文件
```
自然语言: "把结果保存到 output.txt"
工具映射: write(path="output.txt", content="...")
```

### 执行命令
```
自然语言: "检查 Gateway 健康状态"
工具映射: exec(command="curl -s http://127.0.0.1:18789/health")
```

### 飞书文档
```
自然语言: "更新飞书文档，添加项目进度"
工具映射: feishu_doc(action="append", doc_token="xxx", content="...")
```

---

## 七、配置位置

- 工具Schema定义: `Kernel/tool_caller.py`
- 工具调用日志: SQLite `memory` 表
- 权限配置: `config/default_role_config.json`

---

_本说明文档由交交自动生成_
