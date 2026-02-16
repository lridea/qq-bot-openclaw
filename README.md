# QQ Bot - OpenClaw

一个基于 NoneBot2 的 QQ 群聊机器人，可以接入 OpenClaw AI 助手。

## 🎯 功能特性

- ✅ 在 QQ 群聊中使用 OpenClaw AI 助手
- ✅ 支持日常对话、问题解答
- ✅ 支持文件访问、命令执行（通过 OpenClaw API）
- ✅ 支持 Windows/Linux/Mac 跨平台运行
- ✅ 完整的部署文档和启动脚本
- ✅ **智能触发模式**：自动检测群中的疑问和求助，主动回复
- ✅ **群组定制配置**：不同群聊可设置不同的触发规则
- ✅ **超级管理员控制**：灵活管理智能触发功能
- ✅ **简洁回复模式**：让机器人回复更简短高效，避免冗余

## 📋 系统要求

- Python 3.8 或更高版本
- Windows 10/11 或 Linux 或 macOS
- 网络连接（用于调用 OpenClaw API）
- QQ 账号（用于登录机器人）

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/YOUR_USERNAME/qq-bot-openclaw.git
cd qq-bot-openclaw
```

### 2. 安装依赖

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：
```ini
# OpenClaw API 配置
OPENCLAW_API_URL=https://your-server.com/api/openclaw/chat
OPENCLAW_API_KEY=your_api_key_here

# 机器人配置
HOST=127.0.0.1
PORT=8080
SUPERUSERS=["你的QQ号"]

# NapCat 配置
NAPCAT_WS_URL=ws://127.0.0.1:3001
```

### 4. 安装 NapCat

详见 [NapCat 配置指南](docs/NAPCAT.md)

### 5. 启动机器人

**Windows:**
```cmd
start.bat
```

**Linux/Mac:**
```bash
bash start.sh
```

### 6. 在 QQ 群中测试

```
@机器人 你好
@机器人 帮我读取文件 README.md
```

## 📁 项目结构

```
qq-bot-openclaw/
├── .env                    # 环境变量配置
├── .env.example            # 环境变量示例
├── .gitignore              # Git 忽略文件
├── README.md               # 项目文档
├── requirements.txt        # Python 依赖
├── bot.py                  # 机器人入口
├── pyproject.toml          # 项目配置
├── start.bat               # Windows 启动脚本
├── start.sh                # Linux/Mac 启动脚本
├── config.py               # 配置文件
├── plugins/                # 插件目录
│   ├── __init__.py
│   └── openclaw_chat/      # OpenClaw 聊天插件
│       ├── __init__.py
│       ├── chat.py         # 聊天处理器（含智能触发）
│       ├── intelligent_trigger.py  # 智能触发检测模块
│       ├── ai_processor.py # AI 处理模块
│       ├── image_processor.py  # 图片处理模块
│       └── vision_client.py # Vision AI 客户端
├── group_configs.json      # 群组智能触发配置（自动生成）
├── group_configs.example.json  # 群组配置示例
└── docs/                   # 文档目录
    ├── DEPLOYMENT.md       # 详细部署指南
    ├── NAPCAT.md           # NapCat 配置指南
    ├── INTELLIGENT_TRIGGER.md  # 智能触发详细文档
    ├── INTELLIGENT_TRIGGER_TEST.md  # 智能触发测试指南
    ├── FAQ.md              # 常见问题
    ├── IMAGE_RECOGNITION_DEV.md    # 图片识别开发记录
    └── MULTI_MODEL.md      # 多模型配置文档
```

## 🔧 配置说明

### 智能触发模式 ⭐ 新功能

机器人可以自动检测群中的疑问和求助，并主动回复，无需 @机器人。

**默认触发条件：**
- 包含问号（？或?）
- 包含疑问词：有人、谁、怎么、如何、为什么
- 包含求助词：求、帮、解答、请教
- 显式触发：@机器人、@AUTO、@BOT

**环境变量配置（.env 文件）：**

```ini
# ========== 智能触发配置 ==========
# 是否启用智能触发模式（true/false）
INTELLIGENT_TRIGGER_ENABLED=true

# 是否强制要求 @ 机器人（true/false）
INTELLIGENT_TRIGGER_REQUIRE_MENTION=false

# 触发模式（正则表达式列表）
INTELLIGENT_TRIGGER_PATTERNS=["[？?]", "(有人|谁|怎么|如何|为什么|求|帮|解答|请教)", "(@机器人|@[Aa][Uu][Tt][Oo]|@[Bb][Oo][Tt])"]

# 查看最近多少条消息作为上下文
INTELLIGENT_TRIGGER_HISTORY_LIMIT=20

# 群组配置文件路径
GROUP_CONFIG_FILE=group_configs.json
```

**测试示例：**
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

### 超级管理员配置

**SUPERUSERS**: 超级管理员 QQ 号列表，可以执行管理命令

**超级管理员专用命令：**

| 命令 | 说明 |
|--------|------|
| `/status` | 查看系统状态（模型、配置、运行信息）|
| `/switch <模型>` | 切换 AI 供应商（如 siliconflow、deepseek）|
| `/set_model <模型名>` | 设置具体的 AI 模型（如 gpt-4o-mini）|
| `/restart` | 重启机器人 |
| `/admin` | 查看管理员帮助 |
| `/trigger_status` | 查看智能触发配置 |
| `/trigger_enable <群号>` | 启用群的智能触发 |
| `/trigger_disable <群号>` | 禁用群的智能触发 |
| `/trigger_set <群号> <启用/禁用> [强制@]` | 设置群触发规则 |
| `/trigger_reset <群号>` | 重置群为默认配置 |
| `/trigger_list` | 查看所有群配置 |

**使用示例：**
```
/status                        # 查看系统状态
/switch deepseek               # 切换到 DeepSeek
/set_model gpt-4o-mini         # 设置为 GPT-4o-mini
/restart                       # 重启机器人
/trigger_status                # 查看智能触发配置
/trigger_enable 123456789       # 启用群的智能触发
/trigger_disable 123456789      # 禁用群的智能触发
/trigger_set 123456789 启用 是  # 启用并强制@
/trigger_reset 123456789       # 重置为默认配置
/trigger_list                  # 查看所有群配置
```

### 简洁回复模式 ⭐ 新功能

机器人可以以更简短、高效的方式回复消息，减少冗余内容。

**环境变量配置（.env 文件）：**

```ini
# ========== 简洁模式配置 ==========
# 回复模式：normal（正常）/ concise（简洁）/ detailed（详细）
REPLY_MODE=normal

# 回复最大字符数（简洁模式下生效）
REPLY_MAX_LENGTH=500

# 简洁模式触发模式（正则表达式列表）
# 匹配这些模式时自动使用简洁模式回复
CONCISE_MODE_PATTERNS=["[？?]", "(怎么|如何|为什么)"]
```

**回复模式说明：**

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| `normal` | 正常模式，根据消息内容判断是否简洁 | 日常聊天、私聊 |
| `concise` | 全局简洁模式，所有回复都简短 | 技术群、高效沟通群 |
| `detailed` | 详细模式，提供全面解答 | 学习群、新手引导群 |

**示例对比：**

```
# Normal 模式
用户：怎么用 Git？
回复：诶~ 主人想学 Git 呢！星野来帮你~ 💙

Git 是一个很厉害的版本控制系统哦！

基本使用步骤是：
1. `git init` - 初始化仓库
2. `git add .` - 添加所有文件
3. `git commit -m "提交信息"` - 提交更改
4. `git push` - 推送到远程仓库

主人还想了解 Git 的其他功能吗？✨

# Concise 模式
用户：怎么用 Git？
回复：`git init` 初始化，`git add .` 添加文件，`git commit -m "msg"` 提交，`git push` 推送~
```

**详细文档：** [简洁模式说明](docs/CONCISE_MODE.md)

### OpenClaw API 配置

1. **API URL**: OpenClaw API 的地址（由 OpenClaw 提供）
2. **API Key**: 访问密钥（由 OpenClaw 提供）

### NapCat 配置

详见 [NapCat 配置指南](docs/NAPCAT.md)

### 机器人配置

- **HOST**: 机器人监听地址（默认 127.0.0.1）
- **PORT**: 机器人监听端口（默认 8080）
- **SUPERUSERS**: 超级管理员 QQ 号列表

## 📖 详细文档

- [部署指南](docs/DEPLOYMENT.md) - 详细的部署步骤
- [NapCat 配置](docs/NAPCAT.md) - NapCat 协议端配置
- [智能触发功能](docs/INTELLIGENT_TRIGGER.md) - 智能触发详细文档 ⭐
- [智能触发测试](docs/INTELLIGENT_TRIGGER_TEST.md) - 智能触发测试指南 ⭐
- [常见问题](docs/FAQ.md) - 常见问题解答
- [多模型配置](docs/MULTI_MODEL.md) - 多模型支持文档
- [图片识别开发](docs/IMAGE_RECOGNITION_DEV.md) - 图片识别功能开发记录

## ⚙️ 高级功能

### 自定义插件

在 `plugins/` 目录下创建新插件：

```python
from nonebot import on_command

# 创建命令处理器
hello = on_command("hello")

@hello.handle()
async def handle_hello():
    await hello.send("你好！")
```

### 权限控制

```python
from nonebot import on_command
from nonebot.permission import SUPERUSER

# 只有超级管理员可用
admin_cmd = on_command("admin", permission=SUPERUSER)
```

## 🐛 故障排查

### 问题 1: 无法连接到 NapCat

检查 NapCat 是否正常运行，确认 WebSocket 地址配置正确。

### 问题 2: API 调用失败

检查 API Key 是否正确，网络连接是否正常。

### 问题 3: 机器人不响应

检查是否在群里 @机器人，或者私聊机器人。

## 📝 更新日志

### v1.11.0 (2026-02-16) 🎨 Vision AI 独立配置
- 🎯 将 Vision AI 模型配置从文本对话模型配置中分离
- ✨ 支持独立的 Vision AI 配置系统
- 🔧 添加 Vision AI 管理员命令（/vision_status, /vision_enable, /vision_disable, /vision_set）
- 📚 创建 Vision AI 配置文档（docs/VISION_CONFIG.md）
- 🔑 添加 get_vision_api_key() 方法，自动选择供应商的 API Key
- 🛡️ 优化 Vision AI 调用逻辑，添加启用/禁用检查
- 📝 更新 .env.example 添加 Vision AI 环境变量
- 💡 支持动态切换 Vision 供应商和模型，无需重启
- 💰 支持灵活配置，降低 Vision AI 成本

### v1.10.0 (2026-02-16) 💬 对话记忆功能
- 🧠 实现分层记忆架构（短期记忆 + 长期记忆）
- 💾 支持对话历史传递给 AI，机器人能记住之前的对话
- 📁 支持持久化存储（JSON 文件），重启后不丢失
- 🗑️ 支持自动清理过期记忆，节省存储空间
- 🔧 支持配置化控制（启用/禁用、过期时间等）
- 👥 按用户/群组独立存储记忆，互不干扰
- 📤 支持导出对话记录（JSON 格式）
- 📚 创建对话记忆模块（conversation_memory.py）和详细文档

### v1.9.0 (2026-02-16) 📝 简洁回复模式
- ✨ 添加简洁回复模式：让机器人回复更简短高效
- 🎯 三种回复模式：normal（正常）、concise（简洁）、detailed（详细）
- 🤖 智能触发简洁模式：根据消息内容自动判断（疑问句、求助词）
- ✂️ 自动截断功能：超过最大长度时自动截断
- 🔧 支持自定义触发模式和最大长度
- 📊 回复对比：Normal 模式详细友好，Concise 模式简洁直接
- 📚 创建简洁模式详细文档和实现总结

### v1.8.0 (2026-02-16) ⭐ 智能触发功能
- 🎯 添加智能触发模式：自动检测群中的疑问和求助，主动回复
- 🔧 支持群组定制配置：不同群聊可设置不同的触发规则
- 🛡️ 超级管理员控制：灵活管理智能触发功能
- 📝 创建智能触发检测模块（intelligent_trigger.py）
- 📚 创建详细的智能触发文档和测试指南
- ✨ 支持正则表达式触发模式（疑问句、求助词、显式触发）
- 📊 支持查看群组配置列表和状态
- 🔄 支持动态启用/禁用群组智能触发

### v1.7.0 (2026-02-16)
- 📸 添加图片识别功能（Vision AI）
- 🎨 创建独立的图片处理模块（image_processor.py）
- 🤖 创建 Vision AI 客户端（vision_client.py）
- ✨ 支持多种 Vision 模型（GPT-4V、Claude 3、GLM-4V、Gemini、Qwen-VL）
- 🔧 使用 OneBot API 提取图片（URL/Base64/本地文件）
- 📝 创建测试用例和开发记录文档
- 🏗️ 模块化设计，便于后续扩展维护

### v1.6.0 (2026-02-16)
- 🔐 添加超级管理员专用命令系统
- 📊 添加 /status 命令查看系统状态
- 🔄 添加 /switch 命令动态切换 AI 供应商
- ⚙️ 添加 /set_model 命令设置具体模型
- 🔧 添加 /restart 命令重启机器人
- 📚 添加 /admin 命令查看管理员帮助
- 🛡️ 所有管理员命令仅超级管理员可用（permission=SUPERUSER）

### v1.5.0 (2026-02-16)
- ✨ 大幅扩展硅基流动模型列表（从 3 个扩展到 30+ 个）
- 🎯 添加 DeepSeek V3.2、V3.1-Terminus、R1 系列
- 🚀 添加 Qwen3 和 Qwen2.5 全系列模型
- 💡 添加 GLM-4.7、GLM-4.6、GLM-Z1 系列
- 🌙 添加 Kimi K2 系列（Thinking、Instruct-0905）
- 🔧 添加 MiniMax-M2.1 和 Llama 3.1 系列

### v1.4.0 (2026-02-16)
- ✨ 大幅扩展 OhMyGPT 模型列表（50+ 模型）
- 🎯 添加 GLM-4.7、Kimi K2 0905 等最新模型
- 🚀 添加 GPT-5、Claude 4.1、Qwen3、Gemini 3 等前沿模型
- 📚 更新文档，展示所有可用模型系列

### v1.3.0 (2026-02-16)
- ✨ 扩展 OhMyGPT 支持 GPT/Claude/Kimi/GLM/Gemini/Llama 等多系列模型
- ⚙️ 添加 MODEL_NAME 配置项，支持指定具体模型
- 📚 完善多模型配置文档，添加 MODEL_NAME 详细说明
- 🔧 更新所有 AI 调用函数，支持用户指定模型

### v1.2.0 (2026-02-16)
- ✨ 添加 OhMyGPT 模型支持（支持 GPT-3.5、GPT-4、GPT-4o 等模型）
- 💫 更新机器人人设为"星野（Hoshino）"星际少女风格
- 🎨 天蓝色长发、星空眼眸、温柔乖巧的性格设定
- 📚 完善多模型配置文档
- 🔧 更新所有回退回复为星野风格

### v1.1.0 (2026-02-16)
- ✨ 添加多模型支持（智谱 AI、DeepSeek、硅基流动、Moonshot、Ollama）
- 🎁 支持完全免费的模型（硅基流动、Ollama）
- 📊 添加 /model 和 /models 命令
- 📚 创建详细的多模型配置文档
- 🔧 实现自动回退机制

### v1.0.0 (2026-02-15)
- ✨ 初始版本发布
- ✅ 支持 QQ 群聊接入 OpenClaw
- ✅ 支持 Windows/Linux/Mac 跨平台
- ✅ 完整的部署文档

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 💬 联系方式

如有问题，请提交 Issue 或联系 OpenClaw。

---

**Powered by NoneBot2 & 星野（Hoshino）** ✨💙
