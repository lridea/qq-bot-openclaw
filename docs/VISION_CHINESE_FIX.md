# Vision AI 中文回复修复说明

## 📋 问题描述

**现象：** Vision AI 在识别图片时，有时会回复英文，导致用户体验不佳。

**原因：** Vision AI 模型（如 GPT-4V、GPT-4o 等）默认可能会根据图片内容或用户提示用英文回复，即使提示词是中文。

---

## 🔧 解决方案

### 1. 修改提示词

在调用 Vision AI 时，明确要求用中文回复：

```python
# 修改前
prompt = f"请识别这张图片，并结合用户的问题回答：{message}" if message else "请描述这张图片的内容"

# 修改后
if message:
    prompt = f"请用中文识别这张图片，并结合用户的问题回答：{message}\n\n重要：请务必用中文回复，不要用英文。"
else:
    prompt = "请用中文描述这张图片的内容。\n\n重要：请务必用中文回复，不要用英文。"
```

### 2. 修改位置

**修改文件：** `plugins/openclaw_chat/chat.py`

**修改位置：**

1. **普通对话中的 Vision AI 调用**（第 100-114 行）
2. **智能触发中的 Vision AI 调用**（第 680-720 行）

---

## 📝 修改内容

### 修改1：普通对话（第 100-114 行）

```python
# 创建 Vision AI 客户端
vision_client = VisionAIClient(
    api_key=vision_api_key,
    provider=vision_provider,
    base_url=config.vision_base_url or None
)

# 识别图片（明确要求用中文回复）
if message:
    prompt = f"请用中文识别这张图片，并结合用户的问题回答：{message}\n\n重要：请务必用中文回复，不要用英文。"
else:
    prompt = "请用中文描述这张图片的内容。\n\n重要：请务必用中文回复，不要用英文。"

logger.info(f"🎨 Vision AI 提示词: {prompt}")

reply = await vision_client.recognize_image(
    image_data=image_data,
    prompt=prompt,
    model=vision_model
)
```

### 修改2：智能触发（第 680-720 行）

```python
# 检查 Vision AI 是否启用
if not config.vision_enabled:
    logger.info("⚠️  Vision AI 已禁用")
    await intelligent_chat.send("抱歉，图片识别功能已禁用。")
    return

# 获取 Vision 模型配置
vision_provider = config.vision_provider
vision_model = config.vision_model or "gpt-4o-mini"
vision_api_key = config.get_vision_api_key()

# 检查 Vision API Key
if not vision_api_key:
    logger.warning("⚠️  Vision AI API Key 未配置")
    await intelligent_chat.send(
        f"抱歉，Vision AI API Key 未配置。\n\n"
        f"请在 .env 文件中配置 {vision_provider.upper()}_API_KEY"
    )
    return

logger.info(f"🎨 Vision AI 配置: {vision_provider} - {vision_model}")

vision_client = VisionAIClient(
    api_key=vision_api_key,
    provider=vision_provider,
    base_url=config.vision_base_url or None
)

# 识别图片（明确要求用中文回复）
if message:
    prompt = f"请用中文识别这张图片，并结合用户的问题回答：{message}\n\n重要：请务必用中文回复，不要用英文。"
else:
    prompt = "请用中文描述这张图片的内容。\n\n重要：请务必用中文回复，不要用英文。"

logger.info(f"🎨 Vision AI 提示词: {prompt}")

reply = await vision_client.recognize_image(
    image_data=image_data,
    prompt=prompt,
    model=vision_model
)
```

---

## ✅ 效果对比

### 修改前

**用户：** [发送一张猫咪图片]
**Vision AI：** "This is a cute cat sitting on a couch. The cat has orange fur and green eyes."

❌ **问题：** 回复了英文

---

### 修改后

**用户：** [发送一张猫咪图片]
**Vision AI：** "这是一只可爱的猫，它正坐在沙发上。这只猫有橙色的毛发和绿色的眼睛。"

✅ **效果：** 用中文回复

---

## 💡 技术要点

### 1. 双重中文提示

提示词中使用了双重中文提示：
- "请用中文识别..." - 开头明确要求
- "\n\n重要：请务必用中文回复，不要用英文。" - 结尾再次强调

### 2. 智能触发同步修复

不仅修复了普通对话中的 Vision AI 调用，还同步修复了智能触发中的 Vision AI 调用，确保所有场景都能正确用中文回复。

### 3. 添加日志

添加了 `logger.info(f"🎨 Vision AI 提示词: {prompt}")`，方便调试和查看实际的提示词内容。

---

## 🧪 测试方法

### 测试1：纯图片描述

**操作：** 发送一张风景图片（不带文字）
**预期：** 用中文描述图片内容

---

### 测试2：图片 + 问题

**操作：** 发送一张图片，并问问题："这是什么？"
**预期：** 用中文识别图片并回答问题

---

### 测试3：智能触发

**操作：** 在群聊中发送图片并问："这是什么？"
**预期：** 机器人自动触发，用中文回复

---

## 📊 修改文件列表

### 核心代码
- ✅ `plugins/openclaw_chat/chat.py` - 修改 Vision AI 提示词（2处）

---

## 🔄 Git 提交

**提交信息：**
```
fix: 修复 Vision AI 回复英文问题

- 修改 Vision AI 提示词，明确要求用中文回复
- 同步修复普通对话和智能触发中的 Vision AI 调用
- 添加日志输出，方便调试
- 改进提示词，使用双重中文提示
```

---

## 🎉 总结

### 修复的核心问题

1. ✅ **明确中文要求**：提示词中明确要求用中文回复
2. ✅ **双重提示**：开头和结尾都强调用中文
3. ✅ **同步修复**：普通对话和智能触发都修复
4. ✅ **添加日志**：方便调试和查看

### 用户收益

- 🌐 **改善体验**：不再出现英文回复
- 🎯 **更准确**：中文回复更符合用户期望
- 📊 **便于调试**：添加日志，方便排查问题

---

## 💡 后续优化

### 1. 语言检测和翻译（可选）

如果用户希望在某些场景下允许英文回复，可以添加语言检测和翻译功能：

```python
def is_chinese(text: str) -> bool:
    """检测文本是否包含中文"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))

if not is_chinese(reply):
    # 如果不是中文，翻译为中文
    reply = translate_to_chinese(reply)
```

### 2. 多语言支持（可选）

如果需要支持多语言，可以添加语言配置：

```ini
# Vision AI 语言设置
VISION_LANGUAGE=zh  # zh（中文）/ en（英文）/ auto（自动）
```

### 3. 个性化提示词（可选）

根据群组或用户设置不同的提示词：

```python
# 群组 A：严格中文
prompt = "请用中文..."

# 群组 B：允许中英混合
prompt = "请识别..."
```

---

**文档版本：** 1.0.0
**最后更新：** 2026-02-16
