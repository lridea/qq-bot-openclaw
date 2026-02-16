# 图片识别功能开发记录

## 📅 开发时间
2026-02-16 12:27 - 进行中

## 🎯 功能目标
实现 QQ Bot 图片识别功能，支持：
- URL 图片识别
- Base64 图片识别
- 本地文件图片识别
- 多种 Vision AI 模型（GPT-4V、Claude、GLM-4V、Gemini）

## 📋 开发进度

### ✅ 已完成
1. ✅ 创建图片处理模块 `image_processor.py`
   - 实现图片提取功能（URL/Base64/本地文件）
   - 定义 Vision 支持的模型列表
   - 实现 ImageData 数据类
   - 实现辅助函数

2. ✅ 创建 Vision AI 客户端 `vision_client.py`
   - 实现 VisionAIClient 类
   - 支持多种 API（OpenAI、Anthropic、Google、智谱）
   - 实现图片数据准备和格式转换
   - 错误处理和日志记录

3. ✅ 集成到 chat.py
   - 检测消息中的图片
   - 调用 Vision AI 识别
   - 合并文本和图片结果

4. ✅ 创建测试用例
   - 单元测试：图片提取
   - 单元测试：Vision API 调用
   - 集成测试：完整流程

### 🔄 进行中
- 测试功能稳定性
- 更新文档

## 🐛 遇到的问题和解决方案

### 问题 1：模块命名冲突
**问题描述：**
- 初始计划创建 `vision_ai.py`，但可能与其他模块冲突

**解决方案：**
- 改为创建 `vision_client.py`，更清晰地表明这是一个客户端类

**记录时间：** 2026-02-16 12:35

---

### 问题 2：图片数据格式统一
**问题描述：**
- 图片可能有多种格式：URL、Base64、本地文件
- 不同 Vision API 需要不同格式

**解决方案：**
- 创建 `ImageData` 类统一封装
- 在 `VisionAIClient._prepare_image_url()` 方法中统一转换格式
- 支持 data URL 格式（`data:image/jpeg;base64,...`）

**记录时间：** 2026-02-16 12:40

---

### 问题 3：Vision 模型检查
**问题描述：**
- 用户可能使用不支持 Vision 的模型
- 需要提前检查并给出提示

**解决方案：**
- 在 `image_processor.py` 中定义 `VISION_MODELS` 配置
- 实现 `check_vision_support()` 函数
- 在识别前检查模型，不支持则返回友好提示

**记录时间：** 2026-02-16 12:45

---

### 问题 4：Anthropic API 格式特殊
**问题描述：**
- Anthropic Claude API 的图片格式与 OpenAI 不同
- 需要 base64 数据，不支持 URL

**解决方案：**
- 在 `_call_anthropic()` 方法中特殊处理
- 如果是 URL，先下载再转换为 base64
- 使用 Anthropic 特定的消息格式

**记录时间：** 2026-02-16 12:48

---

## 📝 待优化项

### 1. 性能优化
- [ ] 添加图片缓存，避免重复下载
- [ ] 支持图片压缩，减少传输大小
- [ ] 添加并发处理，提高响应速度

### 2. 功能增强
- [ ] 支持多图片识别（一次发送多张图）
- [ ] 添加图片预处理（裁剪、缩放）
- [ ] 支持 GIF/视频识别

### 3. 错误处理
- [ ] 更详细的错误分类
- [ ] 自动重试机制
- [ ] 降级方案（不支持 Vision 时提示用户）

### 4. 用户体验
- [ ] 添加图片识别进度提示
- [ ] 支持自定义 Vision 模型
- [ ] 添加图片识别历史记录

## 🔧 技术架构

```
图片识别架构：

用户发送图片
    ↓
chat.py (消息处理)
    ↓
image_processor.py (图片提取)
    ↓
vision_client.py (Vision AI 调用)
    ↓
Vision API (OpenAI/Anthropic/Google/智谱)
    ↓
返回识别结果
```

## 📊 模块职责

### 1. image_processor.py
- **职责：** 图片数据提取和处理
- **主要功能：**
  - 从 QQ 消息提取图片（URL/Base64/本地文件）
  - 图片数据格式转换
  - Vision 模型支持检查
  - 图片下载和保存

### 2. vision_client.py
- **职责：** Vision AI API 调用
- **主要功能：**
  - 统一的 Vision AI 客户端接口
  - 支持多种 Vision API
  - 图片数据准备和格式转换
  - 错误处理和日志

### 3. chat.py
- **职责：** 消息处理和功能集成
- **主要功能：**
  - 检测消息中的图片
  - 调用图片识别功能
  - 合并文本和图片结果
  - 用户交互

## 🎯 测试计划

### 单元测试
- ✅ 图片提取（URL/Base64/无图片）
- ✅ Vision 模型检查
- ✅ Vision API 调用
- ✅ 错误处理

### 集成测试
- ✅ 完整流程测试
- ⏳ 多模型测试
- ⏳ 异常场景测试

### 用户测试
- ⏳ 实际 QQ 群测试
- ⏳ 不同图片格式测试
- ⏳ 性能测试

## 📚 参考资料

- [OpenAI Vision API 文档](https://platform.openai.com/docs/guides/vision)
- [Anthropic Claude Vision 文档](https://docs.anthropic.com/claude/docs/vision)
- [智谱 AI Vision API](https://open.bigmodel.cn/dev/api#text_embedding)
- [OneBot 协议图片消息](https://onebot.dev/)

---

**最后更新：** 2026-02-16 12:51
**开发者：** 星野（Hoshino）✨💙
