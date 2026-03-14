# 📁 data/ 数据目录

## ⚠️ 重要说明

此目录包含数据库文件，**不包含实际API Key**。

---

## 文件说明

| 文件 | 说明 | 是否发布 |
|------|------|----------|
| `symphony.db` | 本地数据库(含真实Key) | ❌ 不发布 |
| `symphony_template.db` | 模板数据库 | ✅ 发布 |

---

## 如何使用模板

### 1. 复制模板

```bash
cp symphony_template.db symphony.db
```

### 2. 配置API Key

#### 方法A: 使用SQLite命令

```bash
sqlite3 symphony.db
sqlite> UPDATE 模型配置表 SET key = '你的API密钥';
```

#### 方法B: 使用Python脚本

```python
import sqlite3

conn = sqlite3.connect('symphony.db')
cursor = conn.cursor()

# 更新各服务商Key
keys = {
    '火山引擎': 'your_volcano_key',
    '硅基流动': 'your_silicon_key', 
    '英伟达': 'your_nvidia_key',
    '魔搭': 'your_modelscope_key',
}

for provider, key in keys.items():
    cursor.execute('UPDATE 模型配置表 SET key = ? WHERE 服务商 = ?', (key, provider))

conn.commit()
conn.close()
```

---

## 数据结构

### 核心表

| 表名 | 说明 |
|------|------|
| 官署表 | 12个行政机构 |
| 官属角色表 | 65个人员角色 |
| 模型配置表 | 65个AI模型 |
| 内核规则表 | 3条核心规则 |

---

## ⚠️ 安全提醒

- **不要**将包含真实API Key的数据库提交到GitHub
- 使用 `.gitignore` 排除 `symphony.db`
- 模板文件 `symphony_template.db` 不含真实Key，可安全发布
