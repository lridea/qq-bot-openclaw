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
# 可选：指定具体模型
MODEL_NAME=Qwen/Qwen2.5-7B-Instruct
```

**特点：**
- ✅ 完全免费
- ✅ 支持多种开源模型
- ✅ 无需充值
- ✅ 性能不错

**支持模型：**

**DeepSeek 系列（高强度推理）：**
- `deepseek-v3.2` - DeepSeek V3.2 最新版本（推荐）
- `deepseek-v3.1-terminus` - DeepSeek V3.1 Terminus（增强版）
- `deepseek-r1` - DeepSeek R1 推理模型

**Qwen 系列（全尺寸、全模态）：**
- `Qwen/Qwen3-72B-Instruct` - Qwen3 72B（最强）
- `Qwen/Qwen3-14B-Instruct` - Qwen3 14B（平衡）
- `Qwen/Qwen2.5-7B-Instruct` - Qwen 2.5 7B（轻量）
- `Qwen/Qwen2.5-72B-Instruct` - Qwen 2.5 72B（最强）
- `Qwen/Qwen2.5-32B-Instruct` - Qwen 2.5 32B（平衡）
- `Qwen/Qwen2.5-Coder-7B-Instruct` - Qwen 代码模型
- `Qwen/Qwen2.5-Coder-32B-Instruct` - Qwen 代码增强版

**GLM 系列（中文理解强）：**
- `THUDM/glm-4.7` - GLM 4.7 最新旗舰（推荐）
- `THUDM/glm-4.6` - GLM 4.6
- `THUDM/glm-4-9b-chat` - GLM 4 9B 轻量版
- `THUDM/glm-z1-32b` - GLM Z1 32B

**Kimi 系列（长上下文）：**
- `kimi-k2-thinking` - Kimi K2 思维模型
- `kimi-k2-instruct-0905` - Kimi K2 0905 指令模型（推荐）
- `kimi-dev-72b` - Kimi Dev 72B
- `moonshot-v1-8k` - Kimi V1 8K
- `moonshot-v1-32k` - Kimi V1 32K
- `moonshot-v1-128k` - Kimi V1 128K（超长文本）

**MiniMax 系列：**
- `MiniMax-M2.1` - MiniMax M2.1 Agent 专用模型

**Llama 系列：**
- `meta-llama/Meta-Llama-3-8B-Instruct` - Llama 3 8B
- `meta-llama/Meta-Llama-3.1-8B-Instruct` - Llama 3.1 8B
- `meta-llama/Meta-Llama-3.1-70B-Instruct` - Llama 3.1 70B
- `meta-llama/Meta-Llama-3.1-405B-Instruct` - Llama 3.1 405B（最强）

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
# 可选：指定具体模型
MODEL_NAME=gpt-4o-mini
```

**特点：**
- ✅ 支持 GPT、Claude、Kimi、GLM 等多系列模型
- ✅ 中转服务，访问稳定
- ⚠️ 按使用量计费
- ✅ 适合需要多种模型切换的场景

**支持模型：**

**GPT 系列：**
- `gpt-4o-mini` - 推荐使用，性价比高
- `gpt-3.5-turbo` - 速度快，价格便宜
- `gpt-4` - 性能最强
- `gpt-4-turbo` - GPT-4 增强版
- `gpt-4o` - OpenAI 最新模型
- `gpt-4.1` - GPT-4.1 增强版
- `gpt-4.1-mini` - GPT-4.1 轻量版
- `gpt-5` - GPT-5 最新旗舰模型
- `gpt-5-mini` - GPT-5 轻量版
- `gpt-5-nano` - GPT-5 最快版本

**GLM 系列：**
- `glm-4.7` - 智谱最新旗舰模型（推荐）
- `glm-4.5` - GLM-4.5 智能体模型
- `glm-4.5-air` - GLM-4.5 高速推理版
- `glm-4.5-x` - GLM-4.5 性能增强版
- `glm-4` - GLM-4 标准版
- `glm-4-flash` - GLM-4 快速版
- `glm-4-plus` - GLM-4 增强版

**Kimi 系列：**
- `kimi-k2-0905` - Kimi K2 最新版本（推荐）
- `kimi-k2` - Kimi K2 混合专家模型
- `moonshot-v1-8k` - 8k 上下文
- `moonshot-v1-32k` - 32k 上下文
- `moonshot-v1-128k` - 128k 上下文（超长文本）

**Claude 系列：**
- `claude-4.1-opus` - Claude 4.1 Opus（最强）
- `claude-4.1-sonnet` - Claude 4.1 Sonnet（平衡）
- `claude-4-opus` - Claude 4 Opus
- `claude-4-sonnet` - Claude 4 Sonnet
- `claude-4-haiku` - Claude 4 Haiku（最快）
- `claude-3.5-opus` - Claude 3.5 Opus
- `claude-3.5-sonnet` - Claude 3.5 Sonnet
- `claude-3.5-haiku` - Claude 3.5 Haiku

**DeepSeek 系列：**
- `deepseek-v3.1-terminus` - DeepSeek V3.1 Terminus（增强版）
- `deepseek-v3.1` - DeepSeek V3.1
- `deepseek-v3` - DeepSeek V3

**Qwen 系列：**
- `qwen3-235b` - Qwen3 最新旗舰（推荐）
- `qwen3-thinking` - Qwen3 思维模型
- `qwen3-coder` - Qwen3 代码模型
- `qwen2.5-7b` - Qwen 2.5 轻量版
- `qwen2.5-72b` - Qwen 2.5 增强版

**Gemini 系列：**
- `gemini-3-pro` - Gemini 3 Pro（最强）
- `gemini-3-flash` - Gemini 3 Flash（快速）
- `gemini-2.5-pro` - Gemini 2.5 Pro
- `gemini-2.5-flash` - Gemini 2.5 Flash
- `gemini-2.0-flash` - Gemini 2.0 Flash

**Llama 系列：**
- `llama-4` - Meta Llama 4（最新）
- `llama-3.3-70b` - Llama 3.3 70B
- `llama-3.1-405b` - Llama 3.1 405B（最强）
- `llama-3.1-70b` - Llama 3.1 70B
- `llama-3.1-8b` - Llama 3.1 8B（轻量）
- `llama-3-70b` - Llama 3 70B

**Grok 系列：**
- `grok-4` - Grok 4 最新版本
- `grok-4-fast` - Grok 4 快速版
- `grok-3` - Grok 3
- `grok-3-mini` - Grok 3 Mini
- `grok-2` - Grok 2

**Doubao 系列：**
- `doubao-pro-1.5` - Doubao 专业版
- `doubao-seed-1.6-fast` - Doubao Seed 1.6 快速版
- `doubao-1.6` - Doubao 1.6 标准版

**其他：**
- `gemini-pro` - Google Gemini Pro

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

# 可选：指定具体模型（不填则使用默认模型）
MODEL_NAME=Qwen/Qwen2-7B-Instruct

# 硅基流动（推荐）
SILICONFLOW_API_KEY=sk-xxxxxxxxxxxxxxxx

# 或者使用 DeepSeek
# AI_MODEL=deepseek
# DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx

# 或者使用 OhMyGPT（支持多系列模型）
# AI_MODEL=ohmygpt
# OHMYGPT_API_KEY=sk-xxxxxxxxxxxxxxxx
# MODEL_NAME=gpt-4o-mini  # 可以指定 GPT/Claude/Kimi/GLM 等模型

# 或者使用 Ollama 本地
# AI_MODEL=ollama
# OLLAMA_MODEL=qwen2

# 超级管理员 QQ 号
SUPERUSERS=["123456789"]
```

### MODEL_NAME 配置说明

**MODEL_NAME** 是可选配置项，用于指定具体使用的模型。

**使用场景：**

1. **OhMyGPT - 切换不同系列模型**
   ```ini
   AI_MODEL=ohmygpt
   MODEL_NAME=gpt-4o           # 使用 GPT-4o
   # MODEL_NAME=claude-3-opus  # 或使用 Claude
   # MODEL_NAME=glm-4          # 或使用 GLM
   # MODEL_NAME=moonshot-v1-128k  # 或使用 Kimi
   ```

2. **硅基流动 - 选择不同开源模型**
   ```ini
   AI_MODEL=siliconflow
   MODEL_NAME=Qwen/Qwen2-7B-Instruct  # 通义千问
   # MODEL_NAME=THUDM/glm-4-9b-chat   # 或使用 GLM
   # MODEL_NAME=meta-llama/Meta-Llama-3-8B-Instruct  # 或使用 Llama
   ```

3. **智谱 AI - 选择不同 GLM 模型**
   ```ini
   AI_MODEL=zhipu
   MODEL_NAME=glm-4-flash  # 快速版本
   # MODEL_NAME=glm-4      # 标准版本
   # MODEL_NAME=glm-4-plus # 增强版本
   ```

**如果不配置 MODEL_NAME：**
- 会使用供应商的默认模型
- 例如：OhMyGPT 默认使用 `gpt-4o-mini`

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
