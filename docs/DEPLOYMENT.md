# 部署指南

本文档提供详细的部署步骤，帮助你在 Windows/Linux/Mac 上部署 QQ Bot - OpenClaw。

## 📋 目录

1. [准备工作](#准备工作)
2. [安装步骤](#安装步骤)
3. [配置说明](#配置说明)
4. [安装 NapCat](#安装-napcat)
5. [启动运行](#启动运行)
6. [测试验证](#测试验证)
7. [故障排查](#故障排查)

---

## 准备工作

### 系统要求

| 操作系统 | 版本要求 |
|---------|---------|
| Windows | 10 或更高版本 |
| Linux | Ubuntu 18.04+ 或其他发行版 |
| macOS | 10.14+ |

### 软件要求

| 软件 | 版本要求 | 用途 |
|------|---------|------|
| Python | 3.8+ | 运行机器人 |
| Git | 最新版 | 克隆项目 |
| QQ 账号 | 任意 | 机器人登录 |

### 账号准备

1. **QQ 账号**
   - 准备一个 QQ 号用于机器人登录
   - 建议使用新注册的 QQ 号
   - 确保账号可以正常登录

2. **OpenClaw API**
   - 联系 OpenClaw 获取 API URL 和 API Key
   - 保存好 API Key，不要泄露

---

## 安装步骤

### Windows 安装

#### 1. 安装 Python

1. 访问 [Python 官网](https://www.python.org/downloads/)
2. 下载 Python 3.8 或更高版本
3. 安装时勾选 **"Add Python to PATH"**
4. 验证安装：
   ```cmd
   python --version
   ```

#### 2. 克隆项目

```cmd
git clone https://github.com/YOUR_USERNAME/qq-bot-openclaw.git
cd qq-bot-openclaw
```

#### 3. 配置环境

```cmd
REM 复制配置文件
copy .env.example .env

REM 编辑 .env 文件
notepad .env
```

#### 4. 启动机器人

```cmd
REM 双击运行
start.bat

REM 或者命令行运行
python bot.py
```

---

### Linux/Mac 安装

#### 1. 安装 Python

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**macOS (使用 Homebrew):**
```bash
brew install python3
```

#### 2. 克隆项目

```bash
git clone https://github.com/YOUR_USERNAME/qq-bot-openclaw.git
cd qq-bot-openclaw
```

#### 3. 配置环境

```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env 文件
nano .env  # 或使用其他编辑器
```

#### 4. 启动机器人

```bash
# 添加执行权限
chmod +x start.sh

# 运行
./start.sh
```

---

## 配置说明

### .env 配置文件

编辑 `.env` 文件，填写以下配置：

```ini
# ========== OpenClaw API 配置 ==========
# OpenClaw API 地址（由 OpenClaw 提供）
OPENCLAW_API_URL=https://your-server.com/api/openclaw/chat

# OpenClaw API 密钥（由 OpenClaw 提供）
OPENCLAW_API_KEY=your_api_key_here

# API 超时时间（秒）
OPENCLAW_API_TIMEOUT=30

# ========== 机器人配置 ==========
# 机器人监听地址
HOST=127.0.0.1

# 机器人监听端口
PORT=8080

# 超级管理员 QQ 号（多个用逗号分隔）
SUPERUSERS=["你的QQ号"]

# 昵称（机器人被@时的称呼）
NICKNAME=["OpenClaw", "小爪"]

# ========== NapCat 配置 ==========
# NapCat WebSocket 地址
NAPCAT_WS_URL=ws://127.0.0.1:3001
```

### 配置项说明

| 配置项 | 说明 | 必填 |
|--------|------|------|
| OPENCLAW_API_URL | OpenClaw API 地址 | ✅ 是 |
| OPENCLAW_API_KEY | OpenClaw API 密钥 | ✅ 是 |
| SUPERUSERS | 超级管理员 QQ 号 | ⚠️ 建议 |
| NICKNAME | 机器人昵称 | ❌ 否 |

---

## 安装 NapCat

NapCat 是 QQ 协议实现，用于让机器人登录 QQ。

### Windows 安装

1. **下载 NapCat**
   - 访问 [NapCat Release](https://github.com/NapNeko/NapCatQQ/releases)
   - 下载最新版本的 Windows 版本

2. **解压文件**
   ```
   解压到任意目录，例如：C:\NapCat
   ```

3. **配置 NapCat**
   - 运行一次 `napcat.exe`
   - 在生成的配置文件 `napcat.json` 中填写：
     ```json
     {
       "qq": 3932455749,
       "password": "123456zdd",
       "ws_reverse_url": "ws://127.0.0.1:8080/onebot/v11/ws"
     }
     ```

4. **登录 QQ**
   - 运行 `napcat.exe`
   - 扫码或输入密码登录
   - 首次登录可能需要验证

### Linux 安装

详见 [NapCat 配置指南](NAPCAT.md)

---

## 启动运行

### 启动顺序

1. **启动 NapCat**
   ```cmd
   # Windows
   cd C:\NapCat
   napcat.exe
   
   # Linux
   ./napcat
   ```

2. **启动机器人**
   ```cmd
   # Windows
   cd qq-bot-openclaw
   start.bat
   
   # Linux/Mac
   ./start.sh
   ```

### 后台运行（Linux/Mac）

使用 `screen` 或 `systemd` 让机器人后台运行：

```bash
# 使用 screen
screen -S qq-bot
./start.sh
# 按 Ctrl+A, D 退出

# 重新连接
screen -r qq-bot
```

---

## 测试验证

### 1. 检查 NapCat 连接

在机器人日志中查找：
```
✅ OneBot V11 | WebSocket 连接成功
```

### 2. 测试机器人响应

在 QQ 群中发送：
```
@机器人 你好
```

机器人应该回复：
```
你好！我是 OpenClaw，有什么可以帮你的吗？
```

### 3. 测试命令

```
/help
/hello
/chat 你好
```

---

## 故障排查

### 问题 1: 无法连接到 NapCat

**症状：**
```
❌ OneBot V11 | WebSocket 连接失败
```

**解决方案：**
1. 检查 NapCat 是否正在运行
2. 确认 WebSocket 地址配置正确
3. 检查端口是否被占用

### 问题 2: API 调用失败

**症状：**
```
❌ OpenClaw API 错误: HTTP 401
```

**解决方案：**
1. 检查 API Key 是否正确
2. 联系 OpenClaw 重新获取 Key

### 问题 3: 机器人不响应

**症状：**
发送消息后无回复

**解决方案：**
1. 确保在群里 @机器人
2. 检查机器人是否在线
3. 查看日志文件排查错误

### 问题 4: Python 版本不对

**症状：**
```
SyntaxError: invalid syntax
```

**解决方案：**
1. 确认 Python 版本 >= 3.8
   ```bash
   python --version
   ```
2. 如果版本过低，升级 Python

---

## 进阶配置

### 自定义日志

在 `.env` 中配置：
```ini
LOG_LEVEL=DEBUG
LOG_FILE=logs/bot.log
```

### 多群支持

机器人默认支持所有群聊，无需额外配置。

### 权限控制

在插件中使用权限检查：
```python
from nonebot.permission import SUPERUSER

# 超级管理员专用命令
# /status - 查看系统状态
# /switch - 切换 AI 供应商
# /set_model - 设置具体模型
# /restart - 重启机器人
# /admin - 管理员帮助

@cmd.handle(permission=SUPERUSER)
async def handle():
    # 只有超级管理员可用
    pass
```

**超级管理员命令列表：**

| 命令 | 说明 | 权限 |
|--------|------|--------|
| `/status` | 查看系统状态 | 超级管理员 |
| `/switch <模型>` | 切换 AI 供应商 | 超级管理员 |
| `/set_model <模型名>` | 设置具体模型 | 超级管理员 |
| `/restart` | 重启机器人 | 超级管理员 |
| `/admin` | 查看管理员帮助 | 超级管理员 |

**使用示例：**
```
/status                # 查看系统状态
/switch deepseek       # 切换到 DeepSeek
/set_model gpt-4o-mini  # 设置为 GPT-4o-mini
/restart              # 重启机器人
/admin                # 查看管理员帮助
```

---

## 更新机器人

```bash
cd qq-bot-openclaw
git pull
pip install -r requirements.txt --upgrade
```

---

## 备份配置

定期备份以下文件：
- `.env`
- `data/` (如果有)

---

## 下一步

- [NapCat 配置指南](NAPCAT.md) - 详细的 NapCat 配置
- [常见问题](FAQ.md) - 查看常见问题解答
- [自定义插件](../README.md#自定义插件) - 开发自定义功能

---

**部署完成后，请将机器人拉入 QQ 群，开始使用！** 🦞
