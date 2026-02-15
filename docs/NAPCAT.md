# NapCat 配置指南

NapCat 是一个现代化的 QQ 协议实现，用于让机器人登录 QQ。

## 📋 目录

1. [NapCat 简介](#napcat-简介)
2. [Windows 安装](#windows-安装)
3. [Linux 安装](#linux-安装)
4. [配置说明](#配置说明)
5. [登录验证](#登录验证)
6. [常见问题](#常见问题)

---

## NapCat 简介

### 什么是 NapCat？

NapCat 是一个基于 NTQQ（新版 QQ）的开源协议实现，特点：
- ✅ 支持最新版 QQ 协议
- ✅ 兼容 OneBot 11 标准
- ✅ 支持扫码和密码登录
- ✅ 支持多平台（Windows/Linux）
- ✅ 开源免费

### 为什么选择 NapCat？

| 对比项 | NapCat | go-cqhttp | Mirai |
|--------|--------|-----------|-------|
| 最新协议 | ✅ | ❌ | ⚠️ |
| 稳定性 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 易用性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 社区活跃度 | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |

---

## Windows 安装

### 1. 下载 NapCat

1. 访问 GitHub Release 页面：
   https://github.com/NapNeko/NapCatQQ/releases

2. 下载最新版本：
   - 文件名类似：`NapCat.Shell.zip`
   - 大小约 50-100 MB

### 2. 解压文件

```
解压到任意目录，建议：
C:\NapCat
或
D:\Tools\NapCat
```

### 3. 首次运行

```cmd
cd C:\NapCat
napcat.exe
```

首次运行会：
- 创建配置文件 `napcat.json`
- 生成必要的数据目录

### 4. 配置 NapCat

编辑 `napcat.json`：

```json
{
  "qq": 3932455749,
  "password": "123456zdd",
  "protocol": 1,
  "ws_reverse": {
    "enable": true,
    "urls": ["ws://127.0.0.1:8080/onebot/v11/ws"]
  },
  "http": {
    "enable": true,
    "host": "127.0.0.1",
    "port": 3000
  },
  "ws": {
    "enable": true,
    "host": "127.0.0.1",
    "port": 3001
  }
}
```

### 5. 登录 QQ

```cmd
napcat.exe
```

**扫码登录：**
- 会显示二维码
- 用手机 QQ 扫码登录

**密码登录：**
- 自动使用配置文件中的密码
- 首次登录可能需要验证

---

## Linux 安装

### 1. 下载 NapCat

```bash
# 创建目录
mkdir -p ~/NapCat
cd ~/NapCat

# 下载最新版本
wget https://github.com/NapNeko/NapCatQQ/releases/latest/download/NapCat.Shell.linux-x64.tar.gz

# 解压
tar -xzf NapCat.Shell.linux-x64.tar.gz

# 添加执行权限
chmod +x napcat
```

### 2. 安装依赖

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y libicu-dev
```

**CentOS/RHEL:**
```bash
sudo yum install -y libicu
```

### 3. 配置 NapCat

```bash
# 首次运行生成配置
./napcat

# 编辑配置
nano napcat.json
```

### 4. 登录 QQ

```bash
./napcat
```

---

## 配置说明

### napcat.json 配置项

```json
{
  "qq": 3932455749,          // QQ 号
  "password": "123456zdd",    // 密码（可选，留空则扫码登录）
  "protocol": 1,              // 协议：1=安卓手机, 2=安卓平板, 3=安卓手表
  
  // 反向 WebSocket（连接 NoneBot）
  "ws_reverse": {
    "enable": true,
    "urls": ["ws://127.0.0.1:8080/onebot/v11/ws"]
  },
  
  // HTTP 服务（可选）
  "http": {
    "enable": true,
    "host": "127.0.0.1",
    "port": 3000
  },
  
  // 正向 WebSocket（可选）
  "ws": {
    "enable": true,
    "host": "127.0.0.1",
    "port": 3001
  },
  
  // 日志配置
  "log": {
    "level": "info",
    "file": "napcat.log"
  }
}
```

### 协议选择

| 协议 | 说明 | 推荐度 |
|------|------|--------|
| 1 | 安卓手机 | ⭐⭐⭐⭐⭐ |
| 2 | 安卓平板 | ⭐⭐⭐⭐ |
| 3 | 安卓手表 | ⭐⭐⭐ |

**推荐使用协议 1（安卓手机）**

---

## 登录验证

### 首次登录

1. **扫码登录（推荐）**
   - 运行 `napcat.exe`
   - 用手机 QQ 扫描二维码
   - 确认登录

2. **密码登录**
   - 在配置文件中填写密码
   - 运行 `napcat.exe`
   - 自动使用密码登录

### 验证码处理

如果出现验证码：
1. **滑块验证**
   - 会弹出滑块验证窗口
   - 完成滑块验证

2. **短信验证**
   - 可能需要短信验证码
   - 输入收到的验证码

3. **设备锁**
   - 首次登录可能需要设备锁验证
   - 在手机 QQ 上确认

### 登录成功

看到以下日志表示成功：
```
✅ 登录成功
✅ 加载好友列表完成
✅ 加载群列表完成
✅ 开始加载消息
```

---

## 常见问题

### 问题 1: 登录失败

**错误：** "密码错误"

**解决：**
1. 确认账号密码正确
2. 尝试扫码登录
3. 检查账号是否被锁定

### 问题 2: 风控拦截

**错误：** "当前账号存在风险"

**解决：**
1. 使用新注册的 QQ 号
2. 先在手机 QQ 上登录一次
3. 完善账号信息（绑定手机、实名认证）

### 问题 3: 无法连接 NoneBot

**错误：** "WebSocket 连接失败"

**解决：**
1. 确认 NoneBot 已启动
2. 检查 WebSocket 地址是否正确
3. 确认端口没有被防火墙拦截

### 问题 4: 频繁掉线

**原因：**
- 网络不稳定
- 腾讯风控

**解决：**
1. 检查网络连接
2. 降低消息发送频率
3. 使用稳定的网络环境

### 问题 5: Linux 权限错误

**错误：** "Permission denied"

**解决：**
```bash
chmod +x napcat
chmod 755 -R ~/NapCat
```

---

## 后台运行

### Windows

创建 `start-napcat.bat`：
```cmd
@echo off
cd C:\NapCat
start /min napcat.exe
```

### Linux

使用 `screen`：
```bash
# 创建会话
screen -S napcat

# 运行 NapCat
./napcat

# 退出会话（Ctrl+A, D）
# 重新连接：screen -r napcat
```

使用 `systemd`：
```bash
# 创建服务文件
sudo nano /etc/systemd/system/napcat.service

# 内容：
[Unit]
Description=NapCat QQ Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/NapCat
ExecStart=/home/your-username/NapCat/napcat
Restart=always

[Install]
WantedBy=multi-user.target

# 启动服务
sudo systemctl daemon-reload
sudo systemctl start napcat
sudo systemctl enable napcat
```

---

## 更新 NapCat

### Windows

1. 备份配置：
   ```cmd
   copy napcat.json napcat.json.backup
   ```

2. 下载新版本并解压

3. 恢复配置：
   ```cmd
   copy napcat.json.backup napcat.json
   ```

### Linux

```bash
# 停止 NapCat
./napcat --stop

# 备份配置
cp napcat.json napcat.json.backup

# 下载新版本
wget https://github.com/NapNeko/NapCatQQ/releases/latest/download/NapCat.Shell.linux-x64.tar.gz

# 解压
tar -xzf NapCat.Shell.linux-x64.tar.gz

# 恢复配置
cp napcat.json.backup napcat.json

# 启动
./napcat
```

---

## 安全建议

1. **使用新 QQ 号**
   - 不要使用主 QQ 号
   - 使用专门的机器人账号

2. **保护密码**
   - 不要将密码提交到 Git
   - 定期更换密码

3. **限制权限**
   - 不要给予机器人过多权限
   - 设置合理的消息频率限制

4. **监控日志**
   - 定期检查日志文件
   - 发现异常立即处理

---

## 下一步

- [返回部署指南](DEPLOYMENT.md)
- [常见问题](FAQ.md)
- [开始使用机器人](../README.md#在-qq-群中测试)

---

**NapCat 配置完成后，请返回部署指南继续配置机器人！** 🦞
