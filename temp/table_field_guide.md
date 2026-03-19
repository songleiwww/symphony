# 序境系统 - 三大基础表字段说明

> **重要**: 以下字段说明用于防止误判，不可修改表结构

---

## 1. 官署表 (Government Offices)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT | 官署唯一标识，如 jianben, zhongshang |
| 名称 | TEXT | 官署名，如 少府监、中尚署 |
| 级别 | INTEGER | 官署等级，1=监级 |
| 职位 | TEXT | 官署主职位 |
| 官品 | TEXT | 官品等级，如 从三品 |
| 职责 | TEXT | 官署职责描述 |
| 父级 | TEXT | 上级官署ID |
| 状态 | TEXT | 状态：正常/停用 |

### 官署ID对照
- jianben → 少府监
- zhongshang → 中尚署
- zuoshang → 左尚署
- youshang → 右尚署
- zhiran → 织染署
- zhangye → 掌冶署

---

## 2. 官署角色表 (Officials/Roles)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT | 角色唯一ID，如 role-1 |
| 姓名 | TEXT | 官员姓名，如 陆念昭 |
| 官职 | TEXT | 官职名称，如 少府监、中尚令 |
| 职务 | TEXT | 具体职务描述 |
| 所属官署 | TEXT | 关联官署表.id (不是官署名!) |
| 职责 | TEXT | 角色职责描述 |
| 角色等级 | INTEGER | 等级：1-5 |
| 状态 | TEXT | 在职/离职 |
| 创建时间 | TIMESTAMP | 创建时间 |
| 更新时间 | TIMESTAMP | 更新时间 |
| 模型配置表_ID | TEXT | 关联模型配置表.id (不是模型名!) |

### 重要关联
```
官署角色表.所属官署 = 官署表.id (如 jianben)
官署角色表.模型配置表_ID = 模型配置表.id (如 56)
```

---

## 3. 模型配置表 (Model Configuration)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT | 模型唯一ID，如 56 |
| 模型名称 | TEXT | 显示名称，如 ark-code-latest |
| 模型标识符 | TEXT | API调用用标识符，如 doubao-seed-2.0-pro |
| 模型类型 | TEXT | 类型：聊天/嵌入/重排/视觉等 |
| 服务商 | TEXT | 供应商：火山引擎/英伟达/智谱等 |
| API地址 | TEXT | 调用端点URL |
| API密钥 | TEXT | 认证密钥 |
| 是否在线 | TEXT | 在线状态：是/否 |
| 使用规则 | TEXT | 使用限制说明 |
| 创建时间 | TIMESTAMP | 创建时间 |
| 更新时间 | TIMESTAMP | 更新时间 |

### 服务商ID对照
- 火山引擎
- 英伟达
- 智谱
- 魔搭
- 硅基流动

---

## 调度时正确用法

### ❌ 错误用法
```sql
-- 错误：直接用官署名作为所属官署
SELECT * FROM 官署角色表 WHERE 所属官署 = '少府监'

-- 错误：直接用模型名作为模型配置ID
SELECT * FROM 官署角色表 WHERE 模型配置表_ID = 'ark-code-latest'
```

### ✅ 正确用法
```sql
-- 正确：通过JOIN获取官署名
SELECT r.姓名, o.名称 as 官署, m.模型名称
FROM 官署角色表 r
JOIN 官署表 o ON r.所属官署 = o.id
JOIN 模型配置表 m ON r.模型配置表_ID = m.id
WHERE r.id = 'role-1'
```

---

*最后更新: 2026-03-17 15:12*
