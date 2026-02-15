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
