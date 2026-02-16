# Vision AI 人设应用修复说明

## 📋 问题描述

**现象：** Vision AI 在识别图片时，回复没有应用人设（星野风格），且回复比较简短。

**原因：**
1. Vision AI 的调用没有使用系统提示词
2. 回复是原始的识别结果，没有经过人设处理

---

## 🔧 解决方案

### 1. 添加系统提示词支持

**修改文件：** `vision_client.py`

**修改内容：**

**修改前：**
```python
async def recognize_image(
    self,
    image_data: ImageData,
    prompt: str = "请描述这张图片",
    model: str = "gpt-4o-mini"
) -> str:
    """识别图片"""
    ...
    return await self._call_openai_compatible(prompt, image_url, model)
```

**修改后：**
```python
async def recognize_image(
    self,
    image_data: ImageData,
    prompt: str = "请描述这张图片",
    model: str = "gpt-4o-mini",
    system_prompt: Optional[str] = None  # 新增：系统提示词参数
) -> str:
    """识别图片"""
    ...
    return await self._call_openai_compatible(prompt, image_url, model, system_prompt)
```

---

### 2. 修改 API 调用，支持系统提示词

**修改文件：** `vision_client.py`

**修改 `_call_openai_compatible` 方法：**

**修改前：**
```python
data = {
    "model": model,
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        }
    ],
    "max_tokens": 1000
}
```

**修改后：**
```python
# 构建消息列表
messages = []

# 如果有系统提示词，添加到消息列表
if system_prompt:
    messages.append({
        "role": "system",
        "content": system_prompt
    })

# 添加用户消息（包含图片）
messages.append({
    "role": "user",
    "content": [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": image_url}}
    ]
})

data = {
    "model": model,
    "messages": messages,  # 使用构建的消息列表
    "max_tokens": 1000
}
```

---

### 3. 在 Vision AI 调用时传递系统提示词

**修改文件：** `chat.py`

**修改位置（2处）：**
1. 普通对话中的 Vision AI 调用（第 110-130 行）
2. 智能触发中的 Vision AI 调用（第 730-755 行）

**修改前：**
```python
logger.info(f"🎨 Vision AI 提示词: {prompt}")

reply = await vision_client.recognize_image(
    image_data=image_data,
    prompt=prompt,
    model=vision_model
)
```

**修改后：**
```python
logger.info(f"🎨 Vision AI 提示词: {prompt}")

# 导入系统提示词构建函数
from .ai_processor import _build_system_prompt

# 构建系统提示词（应用人设）
system_prompt = _build_system_prompt(
    user_id=user_id,
    context="qq_group" if group_id else "qq_private",
    group_id=group_id,
    reply_mode=config.reply_mode
)

logger.info(f"🎨 Vision AI 系统提示词: {system_prompt[:100]}...")

reply = await vision_client.recognize_image(
    image_data=image_data,
    prompt=prompt,
    model=vision_model,
    system_prompt=system_prompt  # 传递系统提示词
)
```

---

## ✅ 效果对比

### 修改前

**用户：** [发送猫咪图片]
**Vision AI：** "这是一只可爱的猫，它正坐在沙发上。"

❌ **问题：**
- 没有人设风格
- 回复简短

---

### 修改后

**用户：** [发送猫咪图片]
**Vision AI：** "哇~ 主人，这是一只超级可爱的猫咪呢！✨💙\n\n这只小猫咪正乖乖地坐在沙发上，它的毛色看起来好柔软，眼神也好温柔~\n\n星野好想抱抱它！🌟💫"

✅ **效果：**
- 应用了星野人设
- 回复更丰富生动

---

## 💡 技术要点

### 1. 系统提示词的作用

系统提示词（System Prompt）定义了 AI 的角色和行为：
- 定义角色形象（星野）
- 定义性格特点（乖巧温柔、俏皮可爱）
- 定义交流风格（称呼、口癖、表情）
- 定义回复格式（使用表情符号）

### 2. API 消息结构

OpenAI 兼容 API 的消息结构：
```json
{
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "system",
      "content": "你是星野（Hoshino）..."
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "请用中文识别这张图片..."
        },
        {
          "type": "image_url",
          "image_url": {"url": "data:image/jpeg;base64,..."}
        }
      ]
    }
  ]
}
```

### 3. 两处同步修改

为了保证一致性，需要在以下两处都应用人设：
1. 普通对话中的 Vision AI 调用
2. 智能触发中的 Vision AI 调用

---

## 📝 测试方法

### 测试1：基本人设应用

**操作：** 发送一张图片（不带问题）
**预期：** 回复带有星野人设风格

---

### 测试2：人设 + 问题

**操作：** 发送一张图片，并问问题："这是什么？"
**预期：** 回复带有星野人设风格，并回答问题

---

### 测试3：智能触发

**操作：** 在群聊中发送图片并问："这是什么？"
**预期：** 机器人自动触发，回复带有星野人设风格

---

## 📊 修改文件列表

### 核心代码
- ✅ `plugins/openclaw_chat/vision_client.py` - 添加系统提示词支持
- ✅ `plugins/openclaw_chat/chat.py` - 在 Vision AI 调用时传递系统提示词（2处）

---

## 🔄 Git 提交

**提交信息：**
```
v1.13.0: Vision AI 应用人设 🎨

- 修改 Vision AI 调用，支持系统提示词
- 在 Vision AI 中应用星野人设
- 同步修复普通对话和智能触发中的 Vision AI 调用（2处）
- 添加日志输出，方便调试
- 改进 Vision AI 回复，使其更生动丰富
```

---

## 🎉 总结

### 修复的核心问题

1. ✅ **应用人设**：Vision AI 现在使用系统提示词，应用星野人设
2. ✅ **回复丰富**：回复不再是简短的识别结果，而是生动丰富的对话
3. ✅ **同步修复**：普通对话和智能触发都应用人设
4. ✅ **添加日志**：方便调试和查看

### 用户收益

- 🎨 **改善体验**：Vision AI 的回复有人设风格
- 🌟 **更生动**：回复不再是简短的描述，而是生动的对话
- 💙 **一致性**：所有回复都使用统一的人设

### 后续优化

1. **增加 max_tokens**：当前设置为 1000，可以根据需要增加
2. **个性化人设**：不同群组可以有不同的 Vision AI 人设
3. **多模态对话**：支持图片 + 语音 + 文本的多模态对话

---

**文档版本：** 1.0.0
**最后更新：** 2026-02-16
