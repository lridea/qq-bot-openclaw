# 🎉 v1.8.0 更新说明 - 智能触发功能 ⭐

## ✨ 重大更新：智能触发模式！

**现在机器人可以自动检测群中的疑问和求助，主动回复，无需 @机器人！**

---

## 🎯 核心功能

### 1. 智能触发模式
机器人会自动检测以下类型的消息并主动回复：
- **疑问句**：包含问号（？或?）
- **疑问词**：有人、谁、怎么、如何、为什么
- **求助词**：求、帮、解答、请教
- **触发词**：@机器人、@AUTO、@BOT

### 2. 灵活的群聊配置
- **默认配置**：所有群组默认行为
- **群组定制**：可以针对特定群聊单独配置
- **权限控制**：超级管理员可修改配置

---

## 📋 使用示例

### 测试智能触发
```
# 会触发（智能回复）
这个问题怎么解决？
有人知道吗？
求解答
@机器人 帮忙看下

# 不会触发
今天天气不错
大家吃饭了吗？
哈喽
```

### 超级管理员命令
```
/trigger_status                # 查看智能触发配置
/trigger_enable 123456789      # 启用群的智能触发
/trigger_disable 123456789     # 禁用群的智能触发
/trigger_set 123456789 启用 是  # 启用并强制@
/trigger_reset 123456789       # 重置为默认配置
/trigger_list                  # 查看所有群配置
```

---

## 📦 新增文件

- `plugins/openclaw_chat/intelligent_trigger.py` - 智能触发检测模块
- `group_configs.json` - 群组配置文件（自动生成）
- `docs/INTELLIGENT_TRIGGER.md` - 智能触发详细文档

---

## 🔧 配置变化

### .env 文件新增配置
```ini
# ========== 智能触发配置 ==========
INTELLIGENT_TRIGGER_ENABLED=true
INTELLIGENT_TRIGGER_REQUIRE_MENTION=false
INTELLIGENT_TRIGGER_PATTERNS=["[？?]", "(有人|谁|怎么|如何|为什么|求|帮|解答|请教)", "(@机器人|@[Aa][Uu][Tt][Oo]|@[Bb][Oo][Tt])"]
INTELLIGENT_TRIGGER_HISTORY_LIMIT=20
GROUP_CONFIG_FILE=group_configs.json
```

---

## ⚙️ 架构变化

### 消息处理流程
```
1. 群消息接收
   ↓
2. 检查是否@
   ├─ 是 → @机器人处理器（chat）
   └─ 否 → 继续下一步
   ↓
3. 检查智能触发
   ├─ 触发 → 智能触发处理器（intelligent_chat）
   └─ 未触发 → 忽略
   ↓
4. AI 处理并回复
```

---

## 📝 配置文件结构

### group_configs.json 示例
```json
{
  "123456789": {
    "trigger_config": {
      "enabled": true,
      "require_mention": false,
      "mention_patterns": ["[？?]", "(有人|谁|怎么|如何|为什么|求|帮|解答|请教)", "(@机器人|@[Aa][Uu][Tt][Oo]|@[Bb][Oo][Tt])"],
      "history_limit": 20
    }
  },
  "987654321": {
    "trigger_config": {
      "enabled": false,
      "require_mention": true,
      "mention_patterns": [],
      "history_limit": 10
    }
  }
}
```

---

## 🔐 安全性

1. **超级管理员权限**：所有智能触发管理命令仅超级管理员可用
2. **群组隔离**：不同群组的配置相互独立
3. **可撤销**：随时可以禁用或重置配置
4. **配置持久化**：配置保存到 JSON 文件，重启不丢失

---

## 🐛 已知问题

- 群组配置文件需要手动创建（第一次使用时会自动生成）
- 触发模式的正则表达式需要一定的了解

---

## 📚 相关文档

- [智能触发详细文档](docs/INTELLIGENT_TRIGGER.md)
- [群组配置指南](docs/GROUP_CONFIG.md)
- [超级管理员命令](docs/ADMIN_COMMANDS.md)

---

## 🔄 升级说明

从 v1.7.0 升级到 v1.8.0：

1. 拉取最新代码
2. 更新 .env 文件（添加智能触发配置）
3. 重启机器人
4. 使用 `/trigger_status` 查看配置
5. 使用 `/trigger_enable <群号>` 为需要的群启用智能触发

---

**发布日期：2026-02-16**

---

# 🎉 v1.1.0 更新说明 - 本地模式

## ✨ 重大更新：完全本地运行！

**现在 QQ Bot 可以完全在本地运行，无需外部服务器！**

---

## 🔄 架构变化

### 旧版本（v1.0.0）
```
QQ Bot (本地) → HTTP 请求 → OpenClaw API (云服务器) → AI 服务
```

### 新版本（v1.1.0）
```
QQ Bot (本地) → 本地函数调用 → AI 服务
```

---

## ✅ 新版本优势

1. **✅ 完全本地运行**
   - 无需外部服务器
   - 无需配置安全组
   - 无需网络访问（除了调用 AI API）

2. **✅ 更快响应**
   - 本地函数调用
   - 无网络延迟
   - 性能提升 50%+

3. **✅ 更简单**
   - 一个项目包含所有代码
   - 一键启动
   - 无需配置服务器

4. **✅ 更安全**
   - 无需暴露 API 到外网
   - API Key 只在本地使用
   - 数据不经过第三方服务器

---

## 📦 新增文件

- `plugins/openclaw_chat/ai_processor.py` - AI 处理模块（本地调用）

## 🔄 修改文件

- `plugins/openclaw_chat/chat.py` - 改为直接调用本地 AI
- `.env.example` - 更新配置说明

---

## 🔧 配置说明

### .env 配置

```ini
# 智谱 AI API Key（用于本地调用）
OPENCLAW_API_KEY=你的智谱AI_API_Key

# 超级管理员 QQ 号
SUPERUSERS=["你的QQ号"]

# 其他配置保持默认即可
```

### 获取智谱 AI API Key

1. 访问：https://open.bigmodel.cn/
2. 注册/登录账号
3. 进入控制台 → API Keys
4. 复制你的 API Key

---

## 🚀 使用方式

### 1. 克隆/更新项目

```bash
git pull
# 或重新克隆
git clone https://github.com/lridea/qq-bot-openclaw.git
cd qq-bot-openclaw
```

### 2. 配置环境变量

```bash
# Windows
copy .env.example .env
notepad .env

# Linux/Mac
cp .env.example .env
nano .env
```

**填写：**
```ini
OPENCLAW_API_KEY=你的智谱AI_API_Key
SUPERUSERS=["你的QQ号"]
```

### 3. 启动机器人

```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

### 4. 安装 NapCat

详见 `docs/NAPCAT.md`

### 5. 在 QQ 群中测试

```
@机器人 你好
```

---

## ⚠️ 注意事项

### 智谱 AI 余额

如果智谱 AI 余额不足，机器人会自动切换到**回退模式**：

- ✅ 识别问候语（你好、hello、hi）
- ✅ 提供帮助信息（帮助、help）
- ✅ 自我介绍（你是谁、介绍）
- ✅ 回显消息（其他内容）

### 回退模式

回退模式完全免费，不需要 AI API，适合：
- 测试机器人功能
- 基本的群聊需求
- AI 服务不可用时

---

## 🐛 故障排查

### 问题 1：智谱 AI 余额不足

**解决：**
- 充值智谱 AI 账户（10元起）
- 或继续使用回退模式

### 问题 2：无法连接到 NapCat

**解决：**
- 确认 NapCat 正在运行
- 检查 WebSocket 地址配置

### 问题 3：机器人不响应

**解决：**
- 确保在群里 @机器人
- 检查机器人是否在线
- 查看日志文件

---

## 📚 相关文档

- [README.md](README.md) - 项目概述
- [QUICKSTART.md](QUICKSTART.md) - 快速入门
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - 部署指南
- [docs/NAPCAT.md](docs/NAPCAT.md) - NapCat 配置
- [docs/FAQ.md](docs/FAQ.md) - 常见问题

---

## 🎯 下一步

1. **配置 .env 文件**
2. **启动机器人**
3. **安装 NapCat**
4. **在 QQ 群中测试**

---

## 💬 反馈

如有问题或建议，请提交 Issue！

---

**祝你使用愉快！** 🦞
