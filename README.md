# QQ Bot - OpenClaw

一个基于 NoneBot2 的 QQ 群聊机器人，可以接入 OpenClaw AI 助手。

## 🎯 功能特性

- ✅ 在 QQ 群聊中使用 OpenClaw AI 助手
- ✅ 支持日常对话、问题解答
- ✅ 支持文件访问、命令执行（通过 OpenClaw API）
- ✅ 支持 Windows/Linux/Mac 跨平台运行
- ✅ 完整的部署文档和启动脚本

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
│       └── chat.py
└── docs/                   # 文档目录
    ├── DEPLOYMENT.md       # 详细部署指南
    ├── NAPCAT.md           # NapCat 配置指南
    └── FAQ.md              # 常见问题
```

## 🔧 配置说明

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

**使用示例：**
```
/status                # 查看系统状态
/switch deepseek       # 切换到 DeepSeek
/set_model gpt-4o-mini  # 设置为 GPT-4o-mini
/restart              # 重启机器人
```

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
- [常见问题](docs/FAQ.md) - 常见问题解答

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
