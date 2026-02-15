# 快速入门指南

5 分钟快速部署 QQ Bot - OpenClaw！

## 🚀 快速开始（Windows）

### 1. 下载项目
```cmd
git clone https://github.com/YOUR_USERNAME/qq-bot-openclaw.git
cd qq-bot-openclaw
```

### 2. 配置
```cmd
copy .env.example .env
notepad .env
```

填写以下配置：
```ini
OPENCLAW_API_URL=https://your-server.com/api/openclaw/chat
OPENCLAW_API_KEY=your_api_key_here
SUPERUSERS=["你的QQ号"]
```

### 3. 启动
```cmd
start.bat
```

### 4. 安装 NapCat
- 下载：https://github.com/NapNeko/NapCatQQ/releases
- 配置 `napcat.json`
- 运行 `napcat.exe`

### 5. 测试
在 QQ 群中发送：
```
@机器人 你好
```

---

## 🚀 快速开始（Linux/Mac）

### 1. 下载项目
```bash
git clone https://github.com/YOUR_USERNAME/qq-bot-openclaw.git
cd qq-bot-openclaw
```

### 2. 配置
```bash
cp .env.example .env
nano .env
```

### 3. 启动
```bash
chmod +x start.sh
./start.sh
```

### 4. 安装 NapCat
```bash
wget https://github.com/NapNeko/NapCatQQ/releases/latest/download/NapCat.Shell.linux-x64.tar.gz
tar -xzf NapCat.Shell.linux-x64.tar.gz
chmod +x napcat
./napcat
```

---

## 📝 最小配置

只需要配置 3 项即可运行：

```ini
OPENCLAW_API_URL=https://your-server.com/api/openclaw/chat
OPENCLAW_API_KEY=your_api_key_here
SUPERUSERS=["123456789"]
```

其他配置使用默认值即可！

---

## ✅ 验证安装

### 1. 检查 Python
```bash
python --version
# 应显示：Python 3.8.x 或更高
```

### 2. 检查依赖
```bash
pip show nonebot2
# 应显示：Name: nonebot2
```

### 3. 检查配置
```bash
python config.py
# 应显示：机器人配置加载完成
```

### 4. 检查 NapCat
```bash
./napcat
# 应显示：登录成功
```

---

## 🎯 常用命令

### 在 QQ 群中

```
@机器人 你好          # 与机器人对话
/help                # 显示帮助
/hello               # 打招呼
/chat 你好            # 使用命令对话
```

---

## 🐛 快速故障排查

### 问题：机器人不响应
1. 检查是否 @机器人
2. 检查 NapCat 是否运行
3. 检查 NoneBot 是否运行

### 问题：API 调用失败
1. 检查 API Key 是否正确
2. 检查网络连接
3. 联系 OpenClaw

### 问题：无法登录 QQ
1. 尝试扫码登录
2. 检查账号是否正常
3. 查看日志排查

---

## 📚 详细文档

需要更多信息？查看详细文档：

- [部署指南](docs/DEPLOYMENT.md)
- [NapCat 配置](docs/NAPCAT.md)
- [常见问题](docs/FAQ.md)

---

## 💬 获取帮助

遇到问题？

1. 查看 [FAQ](docs/FAQ.md)
2. 提交 GitHub Issue
3. 联系 OpenClaw

---

**祝你使用愉快！** 🦞
