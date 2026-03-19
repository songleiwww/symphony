# 序境长期记忆系统详细报告

## 一、系统概述

### 1.1 基本信息
| 项目 | 内容 |
|------|------|
| **名称** | 序境3.0记忆系统 (Memory System V2) |
| **作者** | 少府监·翰林学士 孟浩然 |
| **版本** | 3.0 |
| **文件位置** | `Kernel/evolution/memory_system_v2.py` |

### 1.2 设计理念
```
┌─────────────────────────────────────┐
│         序境记忆系统架构              │
├─────────────────────────────────────┤
│  工作记忆 (Working Memory)          │
│  - 短期高频访问                      │
│  - 当前会话上下文                    │
│  - 容量有限(默认100条)              │
│  - LRU缓存 + 访问频率权重           │
├─────────────────────────────────────┤
│  长期记忆 (Long-term Memory)        │
│  - 持久化存储                       │
│  - 语义关联                         │
│  - JSON文件存储                     │
│  - 语义图谱支持                     │
├─────────────────────────────────────┤
│  索引记忆 (Index Memory)            │
│  - 元数据索引                       │
│  - 快速检索                         │
│  - 多维度查询                       │
└─────────────────────────────────────┘
```

---

## 二、核心模块详解

### 2.1 记忆类型 (MemoryType)

| 类型 | 英文 | 说明 | 示例 |
|------|------|------|------|
| **情景记忆** | EPISODIC | 具体事件 | 用户提问、会议记录 |
| **语义记忆** | SEMANTIC | 知识概念 | 技术文档、事实信息 |
| **程序记忆** | PROCEDURAL | 技能流程 | 开发流程、操作步骤 |
| **情感记忆** | EMOTIONAL | 情感关联 | 用户偏好、情绪状态 |

### 2.2 记忆优先级 (MemoryPriority)

| 优先级 | 值 | 说明 | 清理策略 |
|--------|-----|------|----------|
| CRITICAL | 3 | 关键记忆 | 永久保存 |
| HIGH | 2 | 高优先级 | 优先保留 |
| NORMAL | 1 | 普通记忆 | 默认 |
| LOW | 0 | 低优先级 | 可被清理 |

---

## 三、核心功能

### 3.1 WorkingMemory (工作记忆)

**特性：**
- 高频访问
- 容量有限（默认100条）
- 时间衰减机制
- 快速检索
- LRU缓存策略

**核心方法：**
```python
add(memory)      # 添加记忆
get(memory_id)   # 获取记忆
search_by_content(query, top_k)  # 内容搜索
search_by_tags(tags, top_k)       # 标签搜索
evict()          # 淘汰低优先级记忆
```

### 3.2 LongTermMemory (长期记忆)

**特性：**
- 持久化存储（JSON文件）
- 语义图谱关联
- 时间范围查询
- 类型分类检索

**核心方法：**
```python
add(memory)           # 添加记忆
get(memory_id)        # 获取记忆
delete(memory_id)     # 删除记忆
search_by_semantics(query, top_k)  # 语义搜索
get_related(memory_id, max_related)  # 获取关联记忆
get_by_timerange(start_time, end_time)  # 时间范围查询
get_by_type(memory_type)  # 类型查询
```

### 3.3 IndexMemory (索引记忆)

**特性：**
- 多维度索引
- 快速检索
- 标签索引
- 类型索引
- 时间索引
- 优先级索引

**核心方法：**
```python
search_by_type(memory_type)    # 类型搜索
search_by_priority(priority)    # 优先级搜索
search_by_keyword(keyword)     # 关键词搜索
search(query, memory_type, priority)  # 组合搜索
```

---

## 四、MemorySystemV2 统一接口

### 4.1 核心方法

```python
# 存储记忆
store(content, tags, memory_type, priority) -> memory_id

# 检索记忆
retrieve(memory_id) -> MemoryBlock

# 搜索记忆
search(query, top_k) -> List[Tuple[float, MemoryBlock]]

# 获取关联记忆
get_related(memory_id, max_related) -> List[MemoryBlock]

# 删除记忆
delete(memory_id) -> bool

# 获取状态
get_stats() -> Dict

# 合并记忆
consolidate() -> None
```

### 4.2 使用示例

```python
from evolution import create_memory_system

# 创建记忆系统
ms = create_memory_system(working_capacity=100)

# 存储记忆
mem_id = ms.store(
    content="用户偏好深色模式",
    tags=["偏好", "UI"],
    memory_type=MemoryType.EMOTIONAL,
    priority=MemoryPriority.HIGH
)

# 搜索记忆
results = ms.search("用户界面偏好", top_k=5)

# 获取关联记忆
related = ms.get_related(mem_id, max_related=3)
```

---

## 五、集成状态

### 5.1 已集成到内核
- 文件：`Kernel/evolution/__init__.py`
- 类：`XujingEvolution`
- 方法：`store_memory()`, `search_memory()`

### 5.2 配置参数
| 参数 | 默认值 | 说明 |
|------|--------|------|
| memory_capacity | 100 | 工作记忆容量 |
| memory_storage_path | ./xujing_memory | 存储路径 |

---

## 六、结论与建议

### ✅ 现有功能完整
- 三层记忆架构已实现
- 语义搜索已支持
- 持久化存储已支持
- 多维度索引已支持

### 📋 下一步建议
1. 启用现有记忆系统
2. 对接用户对话数据
3. 优化语义向量化
4. 增强可视化界面
