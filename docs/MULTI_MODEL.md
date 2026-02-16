# 多模型配置指南

OpenClaw QQ Bot 支持多种 AI 模型，包括免费和付费选项。

---

## 📋 支持的模型

| 模型 | 免费额度 | 推荐度 | 说明 |
|------|---------|--------|------|
| **智谱 AI (zhipu)** | ❌ 无 | ⭐⭐⭐ | 国内领先大模型，需要充值 |
| **DeepSeek** | ✅ 有 | ⭐⭐⭐⭐⭐ | 强烈推荐，有免费额度 |
| **硅基流动 (siliconflow)** | ✅ 完全免费 | ⭐⭐⭐⭐⭐ | 强烈推荐，完全免费 |
| **Moonshot (Kimi)** | ✅ 有 | ⭐⭐⭐⭐ | 长文本能力强，有免费额度 |
| **OhMyGPT** | ⚠️ 按量计费 | ⭐⭐⭐⭐ | GPT 系列模型中转服务 |
| **Ollama 本地** | ✅ 完全免费 | ⭐⭐⭐⭐⭐ | 本地运行，完全免费，无需网络 |

---

## 🚀 快速开始

### 1. 硅基流动（推荐，完全免费）⭐⭐⭐⭐⭐

**获取 API Key：**
1. 访问：https://siliconflow.cn/
2. 注册账号（支持微信/手机号）
3. 进入"API 密钥"页面
4. 创建新的 API Key

**配置 .env：**
```ini
AI_MODEL=siliconflow
SILICONFLOW_API_KEY=your_siliconflow_api_key_here
```

**特点：**
- ✅ 完全免费
- ✅ 支持多种开源模型
- ✅ 无需充值
- ✅ 性能不错

---

### 2. DeepSeek（推荐，有免费额度）⭐⭐⭐⭐⭐

**获取 API Key：**
1. 访问：https://platform.deepseek.com/
2. 注册账号
3. 进入"API Keys"页面
4. 创建新的 API Key

**配置 .env：**
```ini
AI_MODEL=deepseek
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

**特点：**
- ✅ 每月有免费额度
- ✅ 性能优秀
- ✅ 价格便宜
- ✅ 适合长期使用

---

### 3. Ollama 本地模型（推荐，完全免费）⭐⭐⭐⭐⭐

**安装 Ollama：**
1. 访问：https://ollama.com/
2. 下载并安装 Ollama
3. 下载模型：
   ```bash
   # 下载 Qwen2 模型（推荐）
   ollama pull qwen2
   
   # 或下载其他模型
   ollama pull llama3
   ollama pull glm4
   ```

**配置 .env：**
```ini
AI_MODEL=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2
```

**特点：**
- ✅ 完全免费
- ✅ 无需网络
- ✅ 数据完全本地
- ⚠️ 需要一定的硬件资源

**推荐模型：**
- `qwen2` - 通义千问2，中文效果好（推荐）
- `llama3` - Meta Llama 3，英文效果好
- `glm4` - 智谱 GLM-4
- `mistral` - Mistral 模型

---

### 4. Moonshot Kimi（有免费额度）⭐⭐⭐⭐

**获取 API Key：**
1. 访问：https://platform.moonshot.cn/
2. 注册账号
3. 进入"API Key 管理页面"
4. 创建新的 API Key

**配置 .env：**
```ini
AI_MODEL=moonshot
MOONSHOT_API_KEY=your_moonshot_api_key_here
```

**特点：**
- ✅ 有免费试用额度
- ✅ 长文本能力强（支持 128k 上下文）
- ✅ 适合需要长文本的场景

---

### 5. OhMyGPT（GPT 中转服务）⭐⭐⭐⭐

**获取 API Key：**
1. 访问：https://www.ohmygpt.com/
2. 注册账号
3. 进入"API Keys"页面
4. 创建新的 API Key

**配置 .env：**
```ini
AI_MODEL=ohmygpt
OHMYGPT_API_KEY=your_ohmygpt_api_key_here
```

**特点：**
- ✅ 支持 GPT-3.5、GPT-4、GPT-4-turbo、GPT-4o 等模型
- ✅ 中转服务，访问稳定
- ⚠️ 按使用量计费
- ✅ 适合需要 GPT 系列模型的场景

**支持模型：**
- `gpt-4o-mini` - 推荐使用，性价比高
- `gpt-3.5-turbo` - 速度快，价格便宜
- `gpt-4` - 性能最强
- `gpt-4-turbo` - GPT-4 增强版
- `gpt-4o` - OpenAI 最新模型

---

### 6. 智谱 AI（需要充值）⭐⭐⭐

**获取 API Key：**
1. 访问：https://open.bigmodel.cn/
2. 注册/登录账号
3. 进入控制台 → API Keys
4. 复制你的 API Key

**配置 .env：**
```ini
AI_MODEL=zhipu
OPENCLAW_API_KEY=your_zhipu_api_key_here
```

**特点：**
- ❌ 需要充值（10元起）
- ✅ 性能优秀
- ✅ 国产领先大模型

---

## 🔧 详细配置

### .env 文件示例

```ini
# 选择要使用的模型
AI_MODEL=siliconflow

# 硅基流动（推荐）
SILICONFLOW_API_KEY=sk-xxxxxxxxxxxxxxxx

# 或者使用 DeepSeek
# AI_MODEL=deepseek
# DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx

# 或者使用 Ollama 本地
# AI_MODEL=ollama
# OLLAMA_MODEL=qwen2

# 超级管理员 QQ 号
SUPERUSERS=["123456789"]
```

---

## 📊 模型对比

### 性能对比

| 模型 | 速度 | 质量 | 中文能力 | 英文能力 | 推荐指数 |
|------|------|------|---------|---------|----------|
| 硅基流动 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| DeepSeek | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Ollama 本地 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Moonshot | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| OhMyGPT | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 智谱 AI | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

### 成本对比

| 模型 | 免费额度 | 付费价格 | 月度成本 |
|------|---------|---------|---------|
| 硅基流动 | ✅ 完全免费 | - | ¥0 |
| DeepSeek | ✅ 每月免费 | 很便宜 | ¥0-10 |
| Ollama 本地 | ✅ 完全免费 | - | ¥0 |
| Moonshot | ✅ 免费试用 | 中等 | ¥0-20 |
| OhMyGPT | ❌ 无 | 按量计费 | ¥10-100+ |
| 智谱 AI | ❌ 无 | 中等 | ¥10-50 |

---

## 🎯 推荐配置

### 方案 1：完全免费（强烈推荐）⭐⭐⭐⭐⭐

```
硅基流动 + Ollama 本地
```

**配置：**
```ini
AI_MODEL=siliconflow
SILICONFLOW_API_KEY=your_key
```

**优点：**
- ✅ 完全免费
- ✅ 无需充值
- ✅ 性能不错

---

### 方案 2：高性价比

```
DeepSeek
```

**配置：**
```ini
AI_MODEL=deepseek
DEEPSEEK_API_KEY=your_key
```

**优点：**
- ✅ 有免费额度
- ✅ 性能优秀
- ✅ 价格便宜

---

### 方案 3：本地完全离线

```
Ollama 本地模型
```

**配置：**
```ini
AI_MODEL=ollama
OLLAMA_MODEL=qwen2
```

**优点：**
- ✅ 完全免费
- ✅ 无需网络
- ✅ 数据安全

---

## 🐛 常见问题

### Q1: 如何切换模型？

**A:** 修改 .env 文件中的 `AI_MODEL` 配置，然后重启机器人。

```ini
AI_MODEL=deepseek  # 改为想要的模型
```

---

### Q2: 可以同时配置多个模型吗？

**A:** 可以！你可以在 .env 中配置所有模型的 API Key，然后通过修改 `AI_MODEL` 来切换。

```ini
# 配置所有模型
AI_MODEL=siliconflow  # 当前使用的模型
SILICONFLOW_API_KEY=xxx
DEEPSEEK_API_KEY=xxx
ZHIPU_API_KEY=xxx
```

---

### Q3: Ollama 需要什么配置？

**A:** Ollama 需要一定的硬件资源：

**最低配置：**
- CPU: 4 核
- 内存: 8 GB
- 硬盘: 10 GB

**推荐配置：**
- CPU: 8 核+
- 内存: 16 GB+
- GPU: NVIDIA GPU（可选，但会更快）

---

### Q4: 哪个模型最好？

**A:** 推荐顺序：

1. **硅基流动** - 完全免费，性能不错
2. **DeepSeek** - 有免费额度，性能优秀
3. **Ollama 本地** - 完全免费，无需网络
4. **Moonshot** - 长文本能力强
5. **OhMyGPT** - 支持 GPT 系列，性能强但需付费
6. **智谱 AI** - 性能最好，但需要充值

---

## 📚 相关文档

- [README.md](README.md) - 项目概述
- [QUICKSTART.md](QUICKSTART.md) - 快速入门
- [CHANGELOG.md](CHANGELOG.md) - 更新日志
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - 部署指南

---

**选择适合你的模型，开始使用吧！** ✨💙
