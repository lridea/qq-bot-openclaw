# Vision AI 配置指南

## 📋 功能概述

QQ Bot 的 Vision AI 功能支持图片识别，可以识别用户发送的图片并生成描述或回答相关问题。

**注意：** Vision AI 和文本对话使用**独立的模型配置**，可以分别设置。

---

## 🎯 为什么要分开配置？

### 原因分析

1. **不同的需求**
   - 文本对话：主要处理文本，使用语言模型（如 DeepSeek、GLM-4）
   - 图片识别：需要 Vision 模型（如 GPT-4V、Claude 3 Vision、GLM-4V）

2. **成本控制**
   - Vision 模型通常比纯文本模型贵
   - 分开配置可以灵活控制成本
   - 可以用便宜的 Vision 模型 + 强大的文本模型

3. **灵活性**
   - 不同场景可能需要不同的组合
   - 技术群：用硅基流动 Vision + DeepSeek 文本
   - 普通群：用 GPT-4V Vision + GLM-4 文本

---

## ⚙️ 配置说明

### 环境变量配置（.env）

```ini
# ========== Vision AI 配置 ==========
# 是否启用 Vision AI（true/false）
VISION_ENABLED=true

# Vision 供应商：openai/anthropic/google/zhipu/siliconflow/ohmygpt
# 推荐：ohmygpt（支持 GPT-4V，通过中转服务）/ siliconflow（完全免费）/ zhipu（GLM-4V）
VISION_PROVIDER=ohmygpt

# Vision 模型名称
# OhMyGPT 推荐：gpt-4o, gpt-4o-mini
# 硅基流动推荐：Qwen/Qwen2-VL-7B-Instruct, Qwen/Qwen2-VL-72B-Instruct
# 智谱推荐：glm-4v
VISION_MODEL=gpt-4o-mini

# Vision API 基础 URL（可选，留空则使用默认）
VISION_BASE_URL=

# ========== 文本对话模型配置（与 Vision 独立）==========
# AI 供应商：zhipu/deepseek/siliconflow/ollama/moonshot/ohmygpt
AI_MODEL=siliconflow

# 具体模型名称（可选）
MODEL_NAME=Qwen/Qwen3-72B-Instruct
```

### 配置项说明

| 配置项 | 默认值 | 说明 | 推荐值 |
|--------|--------|------|--------|
| `VISION_ENABLED` | `true` | 是否启用 Vision AI | `true` |
| `VISION_PROVIDER` | `openai` | Vision AI 供应商 | `ohmygpt` 或 `siliconflow` |
| `VISION_MODEL` | `gpt-4o-mini` | Vision 模型名称 | 根据供应商选择 |
| `VISION_BASE_URL` | `""` | 自定义 API URL（可选） | 留空 |

---

## 🎨 Vision 供应商选择

### 1. OhMyGPT（推荐）⭐⭐⭐⭐⭐

**特点：**
- ✅ 支持 GPT-4V、GPT-4o-mini 等最新模型
- ✅ 国内可访问（中转服务）
- ✅ 支持多种 Vision 模型
- ❌ 需要购买 API Key

**支持的模型：**
- `gpt-4o` - 最新 GPT-4o 模型
- `gpt-4o-mini` - GPT-4o 精简版（性价比高）
- `gpt-4-vision-preview` - GPT-4 Vision 预览版

**配置示例：**
```ini
VISION_PROVIDER=ohmygpt
VISION_MODEL=gpt-4o-mini
OHMYGPT_API_KEY=your_api_key_here
```

---

### 2. 硅基流动（完全免费）⭐⭐⭐⭐⭐

**特点：**
- ✅ 完全免费，无需充值
- ✅ 国内可访问
- ✅ 支持 Qwen2-VL 系列
- ✅ 性能优秀

**支持的模型：**
- `Qwen/Qwen2-VL-7B-Instruct` - 轻量级，速度快
- `Qwen/Qwen2-VL-72B-Instruct` - 强大版本，识别准确

**配置示例：**
```ini
VISION_PROVIDER=siliconflow
VISION_MODEL=Qwen/Qwen2-VL-7B-Instruct
SILICONFLOW_API_KEY=your_api_key_here
```

**获取 API Key：**
1. 访问 https://siliconflow.cn/
2. 注册账号
3. 获取 API Key（完全免费）

---

### 3. 智谱 AI（GLM-4V）⭐⭐⭐⭐

**特点：**
- ✅ GLM-4V 是国产优秀的 Vision 模型
- ✅ 中文理解能力强
- ❌ 需要充值使用

**支持的模型：**
- `glm-4v` - GLM-4 Vision 模型
- `glm-4v-plus` - GLM-4V 增强版

**配置示例：**
```ini
VISION_PROVIDER=zhipu
VISION_MODEL=glm-4v
ZHIPU_API_KEY=your_api_key_here
```

**获取 API Key：**
1. 访问 https://open.bigmodel.cn/
2. 注册账号并充值
3. 获取 API Key

---

### 4. OpenAI（海外）⭐⭐⭐

**特点：**
- ✅ 官方 GPT-4V 模型
- ❌ 需要海外网络
- ❌ 需要海外支付方式

**支持的模型：**
- `gpt-4o` - 最新模型
- `gpt-4-vision-preview` - Vision 预览版

**配置示例：**
```ini
VISION_PROVIDER=openai
VISION_MODEL=gpt-4o
OPENAI_API_KEY=your_api_key_here
```

---

## 🔧 管理员命令

### 查看配置

```
/visual_status  # 查看 Vision AI 配置
```

### 启用/禁用

```
/visual_enable    # 启用 Vision AI
/visual_disable   # 禁用 Vision AI
```

### 设置配置

```
/visual_set <provider> [model]

# 示例：
/visual_set ohmygpt gpt-4o-mini
/visual_set siliconflow Qwen/Qwen2-VL-7B-Instruct
/visual_set zhipu glm-4v
```

---

## 📊 推荐配置方案

### 方案1：成本优先（免费）

```ini
# Vision AI
VISION_PROVIDER=siliconflow
VISION_MODEL=Qwen/Qwen2-VL-7B-Instruct
SILICONFLOW_API_KEY=your_key

# 文本对话
AI_MODEL=siliconflow
MODEL_NAME=Qwen/Qwen3-72B-Instruct
```

**优点：** 完全免费
**缺点：** Vision 模型稍弱

---

### 方案2：性能优先（推荐）

```ini
# Vision AI
VISION_PROVIDER=ohmygpt
VISION_MODEL=gpt-4o-mini
OHMYGPT_API_KEY=your_key

# 文本对话
AI_MODEL=siliconflow
MODEL_NAME=Qwen/Qwen3-72B-Instruct
```

**优点：** Vision 和文本都是最佳性价比
**缺点：** 需要购买 OhMyGPT API Key

---

### 方案3：最强配置（土豪）

```ini
# Vision AI
VISION_PROVIDER=ohmygpt
VISION_MODEL=gpt-4o
OHMYGPT_API_KEY=your_key

# 文本对话
AI_MODEL=ohmygpt
MODEL_NAME=gpt-4o
```

**优点：** 全部使用最强模型
**缺点：** 成本最高

---

## 🎯 使用场景

### 场景1：技术讨论群

**需求：** 快速识别代码截图、错误信息

**推荐配置：**
```ini
VISION_PROVIDER=ohmygpt
VISION_MODEL=gpt-4o-mini
AI_MODEL=deepseek
```

---

### 场景2：日常聊天群

**需求：** 识别风景、美食、表情包

**推荐配置：**
```ini
VISION_PROVIDER=siliconflow
VISION_MODEL=Qwen/Qwen2-VL-7B-Instruct
AI_MODEL=siliconflow
```

---

### 场景3：工作群

**需求：** 识别文档、图表、截图

**推荐配置：**
```ini
VISION_PROVIDER=ohmygpt
VISION_MODEL=gpt-4o
AI_MODEL=gpt-4o
```

---

## 📝 常见问题

### Q1：为什么 Vision AI 和文本模型要分开配置？

**A：** 因为两者的需求不同：
- Vision 模型需要支持图片识别
- 文本模型专注于文本处理
- 分开配置可以灵活选择，控制成本

---

### Q2：如何选择 Vision 供应商？

**A：** 根据需求选择：
- **免费：** 硅基流动
- **性价比：** OhMyGPT（gpt-4o-mini）
- **最强：** OhMyGPT（gpt-4o）

---

### Q3：Vision API Key 和文本 API Key 可以不同吗？

**A：** 可以！例如：
- Vision 用 OhMyGPT API Key
- 文本用硅基流动 API Key

---

### Q4：图片识别失败怎么办？

**A：** 检查以下几点：
1. Vision AI 是否启用：`/vision_status`
2. Vision API Key 是否配置
3. 网络连接是否正常
4. 模型名称是否正确

---

### Q5：可以同时使用多个 Vision 供应商吗？

**A：** 目前不支持。只能选择一个 Vision 供应商。如果需要切换，使用 `/vision_set` 命令。

---

## 🎉 总结

**核心要点：**
1. ✅ Vision AI 和文本对话使用独立的模型配置
2. ✅ 推荐使用 OhMyGPT（性价比）或硅基流动（免费）
3. ✅ 支持动态切换配置，无需重启
4. ✅ 提供完整的管理员命令

**下一步：**
1. 在 `.env` 文件中配置 Vision AI
2. 启动机器人：`bash start.sh`
3. 测试图片识别功能

---

**文档版本：** 1.0.0
**最后更新：** 2026-02-16
