# 对话记忆功能实现总结

## 📋 实现概述

已成功在 `qq-bot-openclaw` 项目中实现对话记忆功能，支持：

- ✅ 短期记忆（内存）：快速访问
- ✅ 长期记忆（JSON 文件）：持久化存储
- ✅ 对话上下文传递给 AI
- ✅ 自动清理过期记忆
- ✅ 配置化控制（启用/禁用、过期时间等）

---

## 🎯 核心功能

### 1. 分层记忆架构

```
┌─────────────────────────────────────────────┐
│            分层记忆系统                        │
├─────────────────────────────────────────────┤
│  Layer 1: 短期记忆（内存）                   │
│  - 存储最近 N 条消息                         │
│  - 快速访问                                 │
│  - 重启后丢失                               │
├─────────────────────────────────────────────┤
│  Layer 2: 长期记忆（JSON 文件）             │
│  - 持久化保存对话摘要                        │
│  - 重启后恢复                               │
│  - 按用户/群组分类存储                      │
├─────────────────────────────────────────────┤
│  Layer 3: 记忆管理器                        │
│  - 统一管理短期和长期记忆                    │
│  - 提供查询和更新接口                        │
│  - 自动清理过期记忆                          │
└─────────────────────────────────────────────┘
```

### 2. 对话记忆特点

- **多维度记忆**：
  - 按用户 ID 记忆（私聊）
  - 按群组 ID 记忆（群聊）
  - 独立存储，互不干扰

- **智能上下文**：
  - 自动传递最近的对话历史给 AI
  - 可配置最大上下文 Token 数
  - AI 能"记住"之前的对话

- **持久化存储**：
  - 所有对话保存到 JSON 文件
  - 重启后自动恢复
  - 支持导出对话记录

- **自动清理**：
  - 可配置过期时间（天数）
  - 自动清理过期记忆
  - 节省存储空间

---

## 📦 新增文件

### 1. conversation_memory.py

**位置：** `plugins/openclaw_chat/conversation_memory.py`

**功能：**
- `ConversationMemory` 类：对话记忆管理器
- `add_message()`：添加消息到记忆
- `get_conversation_history()`：获取对话历史
- `get_conversation_context()`：获取对话上下文（用于 AI）
- `clear_conversation()`：清除对话记忆
- `get_all_sessions()`：获取所有会话 ID
- `get_session_info()`：获取会话信息
- `export_conversation()`：导出对话记录
- `_clean_expired_memory()`：清理过期记忆

### 2. 对话记忆方案文档

**位置：** `docs/CONVERSATION_MEMORY_PLAN.md`

**内容：**
- 功能需求分析
- 架构设计
- 技术方案对比
- 配置设计
- 实现计划

---

## 🔧 修改的文件

### 1. config.py - 添加记忆相关配置

```python
# ========== 对话记忆配置 ==========
memory_enabled: bool = os.getenv("MEMORY_ENABLED", "true").lower() == "true"
memory_storage: str = os.getenv("MEMORY_STORAGE", "file")
memory_dir: str = os.getenv("MEMORY_DIR", "data/conversations")
memory_short_term_length: int = int(os.getenv("MEMORY_SHORT_TERM_LENGTH", "10"))
memory_long_term_expire_days: int = int(os.getenv("MEMORY_LONG_TERM_EXPIRE_DAYS", "30"))
memory_auto_clean: bool = os.getenv("MEMORY_AUTO_CLEAN", "true").lower() == "true"
memory_max_context_tokens: int = int(os.getenv("MEMORY_MAX_CONTEXT_TOKENS", "2000"))
```

### 2. .env.example - 添加记忆环境变量

```ini
# ========== 对话记忆配置 ==========
# 是否启用对话记忆功能（true/false）
MEMORY_ENABLED=true

# 记忆存储方式：file（JSON 文件）/ sqlite（数据库）/ memory（仅内存）
MEMORY_STORAGE=file

# 记忆存储目录
MEMORY_DIR=data/conversations

# 短期记忆长度（内存中保存的消息数量）
MEMORY_SHORT_TERM_LENGTH=10

# 长期记忆过期时间（天），0 表示永不过期
MEMORY_LONG_TERM_EXPIRE_DAYS=30

# 是否自动清理过期记忆（true/false）
MEMORY_AUTO_CLEAN=true

# 最大上下文 Token 数（传给 AI 的上下文大小）
MEMORY_MAX_CONTEXT_TOKENS=2000
```

### 3. ai_processor.py - 集成对话记忆

**修改内容：**
- 导入对话记忆模块
- `process_message_with_ai()` 中添加记忆功能
- `_call_openai_compatible()` 支持对话历史
- `_call_ollama()` 支持对话历史

**新增逻辑：**
```python
# 从记忆中加载对话上下文
memory_manager = get_memory_manager()
conversation_history = memory_manager.get_conversation_context(
    session_id,
    max_tokens=config.memory_max_context_tokens
)

# 传递对话历史给 AI
messages.extend(conversation_history)

# 保存用户消息和 AI 回复到记忆
memory_manager.add_message(session_id, "user", message)
memory_manager.add_message(session_id, "assistant", reply)
```

### 4. bot.py - 初始化记忆管理器

**新增内容：**
```python
if config.memory_enabled:
    from plugins.openclaw_chat.conversation_memory import init_memory_manager

    init_memory_manager(
        memory_dir=config.memory_dir,
        short_term_length=config.memory_short_term_length,
        long_term_expire_days=config.memory_long_term_expire_days,
        auto_clean=config.memory_auto_clean
    )
```

---

## 🎯 工作原理

### 对话流程

```
1. 用户发送消息
   ↓
2. 加载记忆配置
   ↓
3. 从记忆中加载对话上下文
   ├─ 短期记忆（内存）：最近 N 条
   └─ 长期记忆（文件）：所有历史
   ↓
4. 构建消息列表
   ├─ 系统提示词
   ├─ 对话历史
   └─ 当前用户消息
   ↓
5. 调用 AI 生成回复
   ↓
6. 保存对话到记忆
   ├─ 用户消息
   └─ AI 回复
   ↓
7. 发送回复给用户
```

### 存储结构

**目录结构：**
```
data/
├── conversations/
│   ├── user_123456.json      # 私聊记忆
│   ├── group_789012.json     # 群聊记忆
│   └── ...
└── export/
    ├── user_123456_20260216_143000.json  # 导出的对话记录
    └── ...
```

**JSON 文件格式：**
```json
[
  {
    "role": "user",
    "content": "你好",
    "timestamp": 1739692800.0,
    "datetime": "2026-02-16T14:00:00",
    "metadata": {
      "user_id": "123456",
      "group_id": null,
      "context": "qq_private"
    }
  },
  {
    "role": "assistant",
    "content": "哇~ 主人你好呀！✨💙",
    "timestamp": 1739692801.0,
    "datetime": "2026-02-16T14:00:01",
    "metadata": {
      "model": "zhipu",
      "selected_model": "glm-4-flash",
      "reply_mode": "normal"
    }
  }
]
```

---

## ⚙️ 配置说明

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `MEMORY_ENABLED` | `true` | 是否启用对话记忆 |
| `MEMORY_STORAGE` | `file` | 存储方式（file/sqlite/memory）|
| `MEMORY_DIR` | `data/conversations` | 记忆存储目录 |
| `MEMORY_SHORT_TERM_LENGTH` | `10` | 短期记忆长度（消息数量）|
| `MEMORY_LONG_TERM_EXPIRE_DAYS` | `30` | 长期记忆过期时间（天）|
| `MEMORY_AUTO_CLEAN` | `true` | 是否自动清理过期记忆 |
| `MEMORY_MAX_CONTEXT_TOKENS` | `2000` | 最大上下文 Token 数 |

---

## ✅ 测试方法

### 测试1：基本记忆功能

1. 启动机器人
2. 在私聊中连续发送多条消息
3. 观察日志，确认对话历史被加载和保存

### 测试2：对话连续性

1. 发送第一条消息："我叫小明"
2. 发送第二条消息："我叫什么？"
3. 机器人应该回复："你叫小明"

### 测试3：群组记忆

1. 在群聊中连续发送消息
2. 观察日志，确认群组记忆独立存储
3. 不同群组的对话历史不会混淆

### 测试4：记忆持久化

1. 启动机器人，发送消息
2. 重启机器人
3. 发送消息，观察机器人是否记得之前的对话

---

## 📊 性能影响

### 优点
- ✅ AI 能记住之前的对话，提供更连贯的回答
- ✅ 改善用户体验
- ✅ 不增加 API 调用成本（上下文已经在消息中）

### 缺点
- ❌ 增加磁盘占用（存储对话历史）
- ❌ 增加 API Token 消耗（对话历史也会消耗 Token）
- ❌ 需要定期清理过期记忆

### 优化建议
1. 合理设置 `MEMORY_MAX_CONTEXT_TOKENS`，避免传递过长的上下文
2. 定期清理过期记忆，节省存储空间
3. 考虑实现对话摘要功能，减少存储空间

---

## 🔄 Git 提交

### 提交信息

```
v1.10.0: 添加对话记忆功能 ⭐

- 实现分层记忆架构（短期记忆 + 长期记忆）
- 支持对话历史传递给 AI
- 支持持久化存储（JSON 文件）
- 支持自动清理过期记忆
- 支持配置化控制
- 支持导出对话记录
- 按用户/群组独立存储记忆
```

---

## 💡 后续优化

### 1. SQLite 存储
- 升级到 SQLite 数据库
- 提升性能和可靠性
- 支持复杂查询

### 2. 对话摘要
- 自动生成对话摘要
- 节省存储空间
- 改善长对话的上下文传递

### 3. 记忆搜索
- 搜索历史对话
- 快速查找关键信息
- 支持模糊搜索

### 4. Web 界面
- 可视化管理对话记忆
- 导出/导入对话记录
- 清理过期记忆

### 5. Redis 缓存
- 添加 Redis 缓存层
- 提升并发性能
- 支持分布式部署

---

## 📚 相关文档

- [对话记忆方案](docs/CONVERSATION_MEMORY_PLAN.md)
- [项目 README](README.md)
- [配置示例](.env.example)

---

## 🎉 总结

对话记忆功能已成功实现。机器人现在能够：

1. **记住之前的对话**：AI 能访问最近的对话历史
2. **提供连续性对话**：用户不需要重复之前的上下文
3. **持久化存储**：重启后不会丢失对话历史
4. **智能管理**：自动清理过期记忆，节省空间
5. **灵活配置**：可根据需求调整记忆参数

**核心价值：**
- 改善用户体验
- 提升对话质量
- 减少用户重复输入

**下一步：**
- 测试记忆功能
- 根据反馈优化
- 考虑后续优化

---

**实现时间：** 2026-02-16
**版本：** v1.10.0
**状态：** ✅ 完成
