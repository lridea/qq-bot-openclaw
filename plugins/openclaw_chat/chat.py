#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 聊天插件核心代码
处理 QQ 群消息并调用本地 AI 处理
支持智能触发模式
"""

from nonebot import on_message, on_command
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import Bot, Event, Message, MessageSegment
from nonebot.log import logger
from nonebot.params import CommandArg
from typing import Optional
from nonebot.permission import SUPERUSER
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import config
from .ai_processor import process_message_with_ai
from .intelligent_trigger import create_trigger_from_config, IntelligentTrigger


# 创建消息处理器（响应 @机器人）
chat = on_message(rule=to_me(), priority=1, block=True)

# 创建智能触发消息处理器（群聊自动检测触发）
# 注意：这个处理器不会阻塞，让其他处理器也有机会处理
intelligent_chat = on_message(priority=5, block=False)

# 创建命令处理器（响应 /chat 命令）
chat_cmd = on_command("chat", aliases={"对话", "聊天"}, priority=2, block=True)


@chat.handle()
async def handle_chat(bot: Bot, event: Event):
    """
    处理 @机器人 的消息
    """
    try:
        # 获取消息内容
        message = str(event.get_message()).strip()
        
        # 获取用户信息
        user_id = event.get_user_id()
        
        # 获取群号（如果是群聊）
        group_id = None
        if hasattr(event, "group_id"):
            group_id = str(event.group_id)
        
        # 过滤空消息
        if not message:
            await chat.send("你好！有什么可以帮你的吗？")
            return
        
        # 记录日志
        logger.info(f"收到消息 (用户: {user_id}, 群: {group_id}): {message[:50]}")
        
        # ========== 图片识别功能 ==========
        # 检测消息中是否有图片
        from .image_processor import extract_image_from_message
        from .vision_client import VisionAIClient
        
        image_data = await extract_image_from_message(bot, event)
        
        if image_data and image_data.has_data():
            # 有图片，使用 Vision AI 识别
            logger.info("📸 检测到图片，启动 Vision AI 识别...")

            # 检查 Vision AI 是否启用
            if not config.vision_enabled:
                logger.info("⚠️  Vision AI 已禁用")
                await chat.send("抱歉，图片识别功能已禁用。")
                return

            # 获取 Vision 模型配置
            vision_provider = config.vision_provider
            vision_model = config.vision_model or "gpt-4o-mini"
            vision_api_key = config.get_vision_api_key()

            # 检查 Vision API Key
            if not vision_api_key:
                logger.warning("⚠️  Vision AI API Key 未配置")
                await chat.send(
                    f"抱歉，Vision AI API Key 未配置。\n\n"
                    f"请在 .env 文件中配置 {vision_provider.upper()}_API_KEY\n\n"
                    f"推荐配置：\n"
                    f"• OhMyGPT（推荐）：OHMYGPT_API_KEY=your_key_here\n"
                    f"• 硅基流动（免费）：SILICONFLOW_API_KEY=your_key_here\n"
                    f"• 智谱 AI：ZHIPU_API_KEY=your_key_here"
                )
                return

            logger.info(f"🎨 Vision AI 配置: {vision_provider} - {vision_model}")

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

            # 发送回复
            await chat.send(reply)
            return

        # ========== 普通文本对话 ==========
        # 调用本地 AI 处理
        reply = await process_message_with_ai(
            message=message,
            user_id=user_id,
            context="qq_group" if group_id else "qq_private",
            group_id=group_id,
            model=config.ai_model,  # 使用配置的模型
            model_name=config.model_name if config.model_name else None,  # 使用配置的具体模型
            api_key=config.current_api_key,  # 使用配置的 API Key
            reply_mode=config.reply_mode,  # 使用配置的回复模式
            max_length=config.reply_max_length,  # 使用配置的最大长度
            concise_patterns=config.concise_mode_patterns  # 使用配置的简洁模式触发模式
        )
        
        # 发送回复
        await chat.send(reply)
        
    except Exception as e:
        logger.error(f"处理消息失败: {e}")
        await chat.send("抱歉，处理消息时发生错误")


@chat_cmd.handle()
async def handle_chat_cmd(bot: Bot, event: Event, args: Message = CommandArg()):
    """
    处理 /chat 命令
    """
    try:
        # 获取消息内容
        message = str(args).strip()
        
        # 获取用户信息
        user_id = event.get_user_id()
        
        # 获取群号（如果是群聊）
        group_id = None
        if hasattr(event, "group_id"):
            group_id = str(event.group_id)
        
        # 过滤空消息
        if not message:
            await chat_cmd.send("请输入你想说的话，例如：/chat 你好")
            return
        
        # 记录日志
        logger.info(f"收到命令 (用户: {user_id}, 群: {group_id}): {message[:50]}")
        
        # 调用本地 AI 处理
        reply = await process_message_with_ai(
            message=message,
            user_id=user_id,
            context="qq_group" if group_id else "qq_private",
            group_id=group_id,
            model=config.ai_model,
            model_name=config.model_name if config.model_name else None,
            api_key=config.current_api_key,
            reply_mode=config.reply_mode,
            max_length=config.reply_max_length,
            concise_patterns=config.concise_mode_patterns
        )
        
        # 发送回复
        await chat_cmd.send(reply)
        
    except Exception as e:
        logger.error(f"处理命令失败: {e}")
        await chat_cmd.send("抱歉，处理命令时发生错误")


# 欢迎消息处理器
welcome = on_command("hello", aliases={"你好", "hi"}, priority=3)


@welcome.handle()
async def handle_welcome():
    """处理欢迎消息"""
    await welcome.send(f"哇~ 主人你好呀！我是{config.bot_name}星野！✨💙\n\n诶~ 星野很高兴见到主人！有什么想和星野聊的吗？💙")


# 帮助命令
help_cmd = on_command("help", aliases={"帮助"}, priority=3)


@help_cmd.handle()
async def handle_help():
    """显示帮助信息"""
    help_text = f"""
✨ {config.bot_name}星野的使用指南 💙

【基本用法】
• @我 + 消息：和星野聊天
• /chat + 消息：用命令聊天
• /hello 或 /你好：打招呼
• /help 或 /帮助：显示这个帮助
• /model：查看星野用的模型

【功能列表】
✅ 日常聊天陪主人
✅ 回答各种问题
✅ 温柔治愈主人
✅ 分享宇宙知识

【注意事项】
• 星野会一直温柔地陪主人哦~
• 星野有点害羞，但很喜欢和主人聊天~
• 有什么不开心的可以和星野说

【版本】v1.5.0
【身份】星际少女 星野 ✨💙
    """.strip()
    await help_cmd.send(help_text)


# 模型信息命令
model_cmd = on_command("model", aliases={"模型", "当前模型"}, priority=3)


@model_cmd.handle()
async def handle_model():
    """显示当前使用的模型信息"""
    from .ai_processor import MODEL_CONFIGS, list_available_models
    
    # 获取当前模型配置
    model_id = config.ai_model
    model_config = MODEL_CONFIGS.get(model_id)
    
    if not model_config:
        await model_cmd.send(f"❌ 当前模型配置无效：{model_id}")
        return
    
    # 构建模型信息
    info = f"""✨ 当前 AI 模型信息 💙

【模型】{model_config['name']} ({model_id})
【描述】{model_config['description']}
【默认模型】{model_config['default_model']}
【可用模型】{', '.join(model_config['models'])}"""

    # 添加免费信息
    if model_config['free_tier']:
        info += f"\n【免费】✅ 是"
        if model_config.get('free_quota'):
            info += f"\n【额度】{model_config['free_quota']}"
    else:
        info += f"\n【免费】❌ 否（需要付费）"
    
    # 检查 API Key 是否配置
    has_key = bool(config.current_api_key)
    if model_config['env_key']:
        if has_key:
            info += f"\n【API Key】✅ 已配置"
        else:
            info += f"\n【API Key】❌ 未配置"
    
    info += "\n\n【切换模型】修改 .env 文件中的 AI_MODEL 配置"
    info += "\n【查看所有模型】使用 /models 命令"
    
    await model_cmd.send(info)


# 所有模型命令
models_cmd = on_command("models", aliases={"所有模型", "模型列表"}, priority=3)


@models_cmd.handle()
async def handle_models():
    """显示所有支持的模型"""
    from .ai_processor import list_available_models
    
    models_info = list_available_models()
    await models_cmd.send(models_info)


# ========== 超级管理员专用命令 ==========

from nonebot.permission import SUPERUSER

# 状态命令
status_cmd = on_command("status", aliases={"状态"}, priority=1, permission=SUPERUSER)


@status_cmd.handle()
async def handle_status():
    """显示系统状态（仅超级管理员）"""
    from .ai_processor import MODEL_CONFIGS
    
    # 获取当前模型配置
    model_config = MODEL_CONFIGS.get(config.ai_model)
    
    status_text = f"""✨ 星野系统状态 💙

【配置信息】
• 机器人名称：{config.bot_name}
• 当前模型：{config.ai_model}
• 当前模型名称：{config.model_name or model_config['default_model'] if model_config else '未知'}
• 模型描述：{model_config['description'] if model_config else '未知'}

【AI 配置】
• API Key 已配置：✅ 是" if config.current_api_key else "❌ 否"
• 会话超时：{config.session_expire_timeout} 秒

【运行配置】
• 监听地址：{config.host}:{config.port}
• NapCat 地址：{config.napcat_ws_url}
• 超级管理员：{len(config.superusers)} 位

【系统信息】
• Python 版本：{sys.version.split()[0]}
• 运行环境：{'Windows' if sys.platform == 'win32' else 'Linux' if sys.platform.startswith('linux') else 'macOS'}
• 日志级别：{config.log_level}

✨ 系统运行正常 💙
"""
    await status_cmd.send(status_text)


# 切换模型命令
switch_model_cmd = on_command("switch", aliases={"切换模型"}, priority=1, permission=SUPERUSER)


@switch_model_cmd.handle()
async def handle_switch_model(args: Message = CommandArg()):
    """切换 AI 模型（仅超级管理员）"""
    from .ai_processor import MODEL_CONFIGS
    
    # 获取参数
    new_model = str(args).strip().lower()
    
    if not new_model:
        # 显示可切换的模型列表
        available = list(MODEL_CONFIGS.keys())
        text = "✨ 可切换的 AI 模型列表 💙\n\n"
        for model_id in available:
            model_config = MODEL_CONFIGS[model_id]
            current_mark = "✓ 当前" if model_id == config.ai_model else ""
            text += f"• {model_config['name']} ({model_id}) {current_mark}\n"
        await switch_model_cmd.send(text)
        return
    
    # 验证模型
    if new_model not in MODEL_CONFIGS:
        await switch_model_cmd.send(f"❌ 模型 '{new_model}' 不存在\n\n可用模型：{', '.join(MODEL_CONFIGS.keys())}")
        return
    
    # 切换模型
    old_model = config.ai_model
    config.ai_model = new_model
    
    model_config = MODEL_CONFIGS[new_model]
    await switch_model_cmd.send(f"✅ 模型切换成功\n\n• 从：{old_model}\n• 到：{new_model} ({model_config['name']})\n\n✨ 已生效 💙")


# 设置具体模型命令
set_model_cmd = on_command("set_model", aliases={"设置模型"}, priority=1, permission=SUPERUSER)


@set_model_cmd.handle()
async def handle_set_model(args: Message = CommandArg()):
    """设置具体的 AI 模型（仅超级管理员）"""
    from .ai_processor import MODEL_CONFIGS
    
    # 获取参数
    new_model_name = str(args).strip()
    
    if not new_model_name:
        await set_model_cmd.send(f"❌ 请指定模型名称\n\n例如：/set_model gpt-4o-mini\n\n使用 /models 查看所有可用模型")
        return
    
    # 验证模型是否在当前供应商的模型列表中
    model_config = MODEL_CONFIGS.get(config.ai_model)
    if not model_config:
        await set_model_cmd.send(f"❌ 当前供应商 {config.ai_model} 不存在")
        return
    
    if new_model_name not in model_config['models']:
        await set_model_cmd.send(f"❌ 模型 '{new_model_name}' 不在 {model_config['name']} 的支持列表中\n\n使用 /models 查看所有可用模型")
        return
    
    # 设置模型
    old_model_name = config.model_name or model_config['default_model']
    config.model_name = new_model_name
    
    await set_model_cmd.send(f"✅ 模型设置成功\n\n• 供应商：{config.ai_model} ({model_config['name']})\n• 从：{old_model_name}\n• 到：{new_model_name}\n\n✨ 已生效 💙")


# 重启命令
restart_cmd = on_command("restart", aliases={"重启"}, priority=1, permission=SUPERUSER)


@restart_cmd.handle()
async def handle_restart():
    """重启机器人（仅超级管理员）"""
    await restart_cmd.send("🔄 正在重启星野... ✨💙\n\n⏱️ 请稍等片刻...")
    
    # 保存记录
    logger.info(f"超级管理员 {config.superusers} 请求重启机器人")
    
    # 这里可以添加实际的重启逻辑
    # 目前只发送提示消息
    await restart_cmd.send("💡 提示：请在终端中手动重启机器人\n\nbash start.sh")


# 管理员帮助命令
admin_help_cmd = on_command("admin", aliases={"管理员帮助"}, priority=1, permission=SUPERUSER)


@admin_help_cmd.handle()
async def handle_admin_help():
    """显示管理员命令帮助（仅超级管理员）"""
    help_text = """
🔐 超级管理员命令列表 ✨💙

【系统管理】
• /status 或 /状态 - 查看系统状态
• /restart 或 /重启 - 重启机器人

【模型管理】
• /switch 或 /切换模型 - 切换 AI 供应商
  • /switch siliconflow - 切换到硅基流动
  • /switch deepseek - 切换到 DeepSeek
• /set_model 或 /设置模型 - 设置具体模型
  • /set_model gpt-4o-mini - 设置为 GPT-4o-mini
  • /set_model glm-4.7 - 设置为 GLM-4.7

【Vision AI 管理】
• /vision_status 或 /视觉状态 - 查看 Vision AI 配置
• /vision_enable 或 /视觉启用 - 启用 Vision AI
• /vision_disable 或 /视觉禁用 - 禁用 Vision AI
• /vision_set 或 /视觉设置 <provider> [model] - 设置 Vision AI 配置
  • /vision_set ohmygpt gpt-4o - 设置为 OhMyGPT GPT-4o
  • /vision_set siliconflow Qwen/Qwen2-VL-7B-Instruct - 设置为硅基流动 Qwen2-VL

【简洁模式管理】
• /reply_mode_status 或 /简洁状态 - 查看简洁模式配置
• /reply_mode_set 或 /简洁设置 <群号> <模式> - 设置群简洁模式
  • /reply_mode_set 123456789 normal - 设置为正常模式
  • /reply_mode_set 123456789 concise - 设置为简洁模式
  • /reply_mode_set 123456789 detailed - 设置为详细模式
• /reply_mode_reset 或 /简洁重置 <群号> - 重置群为全局默认
• /reply_mode_list 或 /简洁列表 - 查看所有群配置

【智能触发管理】
• /trigger_status 或 /触发状态 - 查看智能触发配置
• /trigger_enable 或 /触发启用 <群号> - 启用群智能触发
• /trigger_disable 或 /触发禁用 <群号> - 禁用群智能触发
• /trigger_set 或 /触发设置 <群号> - 设置群触发模式
• /trigger_reset 或 /触发重置 <群号> - 重置群为默认配置
• /trigger_list 或 /触发列表 - 查看所有群配置

【信息查询】
• /models - 查看所有可用模型
• /model - 查看当前模型信息

【权限说明】
⚠️ 以上命令仅超级管理员可以使用
📝 超级管理员配置在 .env 文件的 SUPERUSERS

💡 提示：使用 /help 查看所有命令
"""
    await admin_help_cmd.send(help_text)


# ========== Vision AI 管理命令 ==========

# Vision AI 状态命令
vision_status_cmd = on_command("vision_status", aliases={"视觉状态", "vision_status", "视觉状态"}, priority=1, permission=SUPERUSER)


@vision_status_cmd.handle()
async def handle_vision_status():
    """查看 Vision AI 配置（仅超级管理员）"""
    from config import config

    status_text = f"""
🎨 Vision AI 状态 ✨💙

【当前配置】
• 启用状态: {'✅ 已启用' if config.vision_enabled else '❌ 已禁用'}
• 供应商: {config.vision_provider}
• 模型: {config.vision_model}
• API 基础 URL: {config.vision_base_url or '（默认）'}

【API Key 状态】
• Vision API Key: {'✅ 已配置' if config.get_vision_api_key() else '❌ 未配置'}

【支持的供应商】
• ohmygpt - OhMyGPT（支持 GPT-4V 等模型）⭐ 推荐
• siliconflow - 硅基流动（完全免费）
• zhipu - 智谱 AI（GLM-4V）
• openai - OpenAI（需要海外网络）
• anthropic - Claude 3 Vision（暂不支持）

【推荐配置】
• OhMyGPT: VISION_PROVIDER=ohmygpt, VISION_MODEL=gpt-4o-mini
• 硅基流动: VISION_PROVIDER=siliconflow, VISION_MODEL=Qwen/Qwen2-VL-7B-Instruct
• 智谱 AI: VISION_PROVIDER=zhipu, VISION_MODEL=glm-4v

💡 使用 /vision_set <provider> [model] 快速设置
"""
    await vision_status_cmd.send(status_text)


# Vision AI 启用/禁用命令
vision_enable_cmd = on_command("vision_enable", aliases={"视觉启用", "vision_enable"}, priority=1, permission=SUPERUSER)
vision_disable_cmd = on_command("vision_disable", aliases={"视觉禁用", "vision_disable"}, priority=1, permission=SUPERUSER)


@vision_enable_cmd.handle()
async def handle_vision_enable():
    """启用 Vision AI（仅超级管理员）"""
    import os
    from config import config

    os.environ["VISION_ENABLED"] = "true"
    config.vision_enabled = True

    # 更新 .env 文件
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        with open(env_file, "w", encoding="utf-8") as f:
            for line in lines:
                if line.startswith("VISION_ENABLED="):
                    f.write("VISION_ENABLED=true\n")
                else:
                    f.write(line)

    await vision_enable_cmd.send("✅ Vision AI 已启用！✨💙")


@vision_disable_cmd.handle()
async def handle_vision_disable():
    """禁用 Vision AI（仅超级管理员）"""
    import os
    from config import config

    os.environ["VISION_ENABLED"] = "false"
    config.vision_enabled = False

    # 更新 .env 文件
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        with open(env_file, "w", encoding="utf-8") as f:
            for line in lines:
                if line.startswith("VISION_ENABLED="):
                    f.write("VISION_ENABLED=false\n")
                else:
                    f.write(line)

    await vision_disable_cmd.send("❌ Vision AI 已禁用！")


# Vision AI 设置命令
vision_set_cmd = on_command("vision_set", aliases={"视觉设置", "vision_set", "视觉设置"}, priority=1, permission=SUPERUSER)


@vision_set_cmd.handle()
async def handle_vision_set(event: Event):
    """设置 Vision AI 配置（仅超级管理员）"""
    import os
    from config import config

    args = event.get_plaintext().strip().split()

    if len(args) < 2:
        await vision_set_cmd.send(
            "❌ 参数错误！\n\n"
            "用法：/vision_set <provider> [model]\n\n"
            "示例：\n"
            "• /vision_set ohmygpt gpt-4o-mini\n"
            "• /vision_set siliconflow Qwen/Qwen2-VL-7B-Instruct\n"
            "• /vision_set zhipu glm-4v\n\n"
            "支持的供应商：ohmygpt, siliconflow, zhipu"
        )
        return

    provider = args[1]
    model = args[2] if len(args) > 2 else None

    # 验证供应商
    valid_providers = ["openai", "anthropic", "google", "zhipu", "siliconflow", "ohmygpt"]
    if provider not in valid_providers:
        await vision_set_cmd.send(
            f"❌ 不支持的供应商：{provider}\n\n"
            f"支持的供应商：{', '.join(valid_providers)}"
        )
        return

    # 更新环境变量
    os.environ["VISION_PROVIDER"] = provider
    config.vision_provider = provider

    if model:
        os.environ["VISION_MODEL"] = model
        config.vision_model = model

    # 更新 .env 文件
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        with open(env_file, "w", encoding="utf-8") as f:
            for line in lines:
                if line.startswith("VISION_PROVIDER="):
                    f.write(f"VISION_PROVIDER={provider}\n")
                elif line.startswith("VISION_MODEL=") and model:
                    f.write(f"VISION_MODEL={model}\n")
                else:
                    f.write(line)

    reply = f"✅ Vision AI 配置已更新！✨💙\n\n"
    reply += f"• 供应商: {provider}\n"
    if model:
        reply += f"• 模型: {model}\n"

    await vision_set_cmd.send(reply)


# ========== 智能触发功能 ==========

@intelligent_chat.handle()
async def handle_intelligent_chat(bot: Bot, event: Event):
    """
    处理群消息的智能触发（自动检测疑问和求助）
    """
    try:
        # 只处理群聊消息
        if not hasattr(event, "group_id"):
            return

        group_id = str(event.group_id)
        message = str(event.get_message()).strip()
        user_id = event.get_user_id()

        # 过滤空消息和命令
        if not message or message.startswith(('/', '.', '。', '！', '!')):
            return

        # ========== 检查是否@了其他人 ==========
        # 如果消息中@了其他人（非机器人），则不触发智能回复
        from nonebot.adapters.onebot.v11 import Message, MessageSegment

        message_obj = event.get_message()

        # 检查消息中是否有@片段
        has_at_other = False
        bot_self_id = str(bot.self_id) if hasattr(bot, 'self_id') else None

        for segment in message_obj:
            if segment.type == 'at':
                # 获取@的QQ号
                at_qq = segment.data.get('qq')

                # 如果@的不是机器人自己，则标记为@了其他人
                if at_qq and bot_self_id and at_qq != bot_self_id:
                    has_at_other = True
                    logger.info(f"🚫 消息@了其他人（QQ: {at_qq}），不触发智能回复")
                    break
                elif at_qq and not bot_self_id:
                    # 如果无法获取机器人QQ号，保守处理，不触发
                    has_at_other = True
                    logger.info(f"🚫 无法获取机器人QQ号，保守处理，不触发智能回复")
                    break

        # 如果@了其他人，直接返回
        if has_at_other:
            return
        # ========== 检查@其他人结束 ==========

        # 获取群组的智能触发配置
        trigger_config = config.get_group_trigger_config(group_id)

        # 检查是否启用智能触发
        if not trigger_config.enabled:
            return

        # 检查是否需要强制@
        if trigger_config.require_mention:
            # 如果强制要求@，则不处理（已有 to_me 处理器处理@）
            return
        
        # 创建触发检测器
        trigger_detector = IntelligentTrigger(trigger_config.mention_patterns)
        
        # 检查是否触发
        if not trigger_detector.check_trigger(message):
            return
        
        # 记录日志
        logger.info(f"🎯 智能触发 (群: {group_id}, 用户: {user_id}): {message[:50]}")
        
        # 检查是否有图片
        from .image_processor import extract_image_from_message
        from .vision_client import VisionAIClient
        
        image_data = await extract_image_from_message(bot, event)
        
        if image_data and image_data.has_data():
            # 有图片，使用 Vision AI 识别
            logger.info("📸 检测到图片，启动 Vision AI 识别...")

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

            # 导入系统提示词构建函数
            from .ai_processor import _build_system_prompt

            # 构建系统提示词（应用人设）
            system_prompt = _build_system_prompt(
                user_id=user_id,
                context="qq_group_intelligent",
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

            await intelligent_chat.send(reply)
            return

        # 普通文本对话
        reply = await process_message_with_ai(
            message=message,
            user_id=user_id,
            context="qq_group_intelligent",  # 使用智能触发上下文
            group_id=group_id,
            model=config.ai_model,
            model_name=config.model_name if config.model_name else None,
            api_key=config.current_api_key,
            reply_mode=config.reply_mode,
            max_length=config.reply_max_length,
            concise_patterns=config.concise_mode_patterns
        )
        
        # 发送回复
        await intelligent_chat.send(reply)
        
    except Exception as e:
        logger.error(f"智能触发处理失败: {e}")


# ========== 智能触发管理命令 ==========

# 智能触发状态命令
trigger_status_cmd = on_command("trigger_status", aliases={"触发状态", "智能触发状态"}, priority=1, permission=SUPERUSER)


@trigger_status_cmd.handle()
async def handle_trigger_status():
    """显示智能触发状态（仅超级管理员）"""
    # 获取群号
    # 注意：超级管理员可以在群里使用此命令查看当前群的配置
    
    text = f"""✨ 智能触发配置 💙

【全局默认配置】
• 启用状态：{'✅ 启用' if config.intelligent_trigger_enabled else '❌ 禁用'}
• 是否强制@：{'✅ 是' if config.intelligent_trigger_require_mention else '❌ 否'}
• 历史上下文：{config.intelligent_trigger_history_limit} 条消息

【触发模式】
• {chr(10).join([f'• {p}' for p in config.intelligent_trigger_patterns])}

【群组配置】
• 已配置群组数量：{len(config._group_configs)} 个

💡 提示：使用 /trigger_list 查看所有群组配置
"""
    await trigger_status_cmd.send(text)


# 智能触发启用命令
trigger_enable_cmd = on_command("trigger_enable", aliases={"触发启用", "启用触发"}, priority=1, permission=SUPERUSER)


@trigger_enable_cmd.handle()
async def handle_trigger_enable(args: Message = CommandArg()):
    """启用群的智能触发（仅超级管理员）"""
    # 获取群号参数
    group_id = str(args).strip()
    
    if not group_id:
        await trigger_enable_cmd.send("❌ 请指定群号\n\n例如：/trigger_enable 123456789")
        return
    
    # 获取当前群配置
    trigger_config = config.get_group_trigger_config(group_id)
    trigger_config.enabled = True
    
    # 保存配置
    config.set_group_trigger_config(group_id, trigger_config)
    
    await trigger_enable_cmd.send(f"✅ 已启用群 {group_id} 的智能触发\n\n✨ 已生效 💙")


# 智能触发禁用命令
trigger_disable_cmd = on_command("trigger_disable", aliases={"触发禁用", "禁用触发"}, priority=1, permission=SUPERUSER)


@trigger_disable_cmd.handle()
async def handle_trigger_disable(args: Message = CommandArg()):
    """禁用群的智能触发（仅超级管理员）"""
    # 获取群号参数
    group_id = str(args).strip()
    
    if not group_id:
        await trigger_disable_cmd.send("❌ 请指定群号\n\n例如：/trigger_disable 123456789")
        return
    
    # 获取当前群配置
    trigger_config = config.get_group_trigger_config(group_id)
    trigger_config.enabled = False
    
    # 保存配置
    config.set_group_trigger_config(group_id, trigger_config)
    
    await trigger_disable_cmd.send(f"❌ 已禁用群 {group_id} 的智能触发\n\n✨ 已生效 💙")


# 智能触发设置命令
trigger_set_cmd = on_command("trigger_set", aliases={"触发设置", "设置触发"}, priority=1, permission=SUPERUSER)


@trigger_set_cmd.handle()
async def handle_trigger_set(args: Message = CommandArg()):
    """设置群的智能触发（仅超级管理员）"""
    # 获取参数
    arg_str = str(args).strip()
    
    if not arg_str:
        await trigger_set_cmd.send(
            "❌ 请指定群号和设置\n\n"
            "格式：/trigger_set <群号> <启用/禁用> [强制@:是/否]\n\n"
            "例如：\n"
            "  /trigger_set 123456789 启用\n"
            "  /trigger_set 123456789 禁用\n"
            "  /trigger_set 123456789 启用 是  # 强制要求@"
        )
        return
    
    # 解析参数
    parts = arg_str.split()
    if len(parts) < 2:
        await trigger_set_cmd.send("❌ 参数不完整\n\n格式：/trigger_set <群号> <启用/禁用> [强制@:是/否]")
        return
    
    group_id = parts[0]
    enable = parts[1]
    
    # 验证启用/禁用参数
    if enable not in ["启用", "禁用"]:
        await trigger_set_cmd.send("❌ 启用/禁用参数无效\n\n请使用：启用 或 禁用")
        return
    
    # 解析强制@参数
    require_mention = False
    if len(parts) >= 3:
        if parts[2] in ["是", "yes", "true"]:
            require_mention = True
    
    # 创建触发配置
    trigger_config = config.get_group_trigger_config(group_id)
    trigger_config.enabled = (enable == "启用")
    trigger_config.require_mention = require_mention
    
    # 保存配置
    config.set_group_trigger_config(group_id, trigger_config)
    
    status_text = "启用" if trigger_config.enabled else "禁用"
    mention_text = "（强制@）" if trigger_config.require_mention else ""
    
    await trigger_set_cmd.send(f"✅ 已设置群 {group_id}：{status_text}智能触发 {mention_text}\n\n✨ 已生效 💙")


# 智能触发重置命令
trigger_reset_cmd = on_command("trigger_reset", aliases={"触发重置", "重置触发"}, priority=1, permission=SUPERUSER)


@trigger_reset_cmd.handle()
async def handle_trigger_reset(args: Message = CommandArg()):
    """重置群为默认配置（仅超级管理员）"""
    # 获取群号参数
    group_id = str(args).strip()
    
    if not group_id:
        await trigger_reset_cmd.send("❌ 请指定群号\n\n例如：/trigger_reset 123456789")
        return
    
    # 移除群配置（恢复默认）
    config.remove_group_config(group_id)
    
    # 显示默认配置
    default_config = config.get_group_trigger_config(group_id)
    status_text = "启用" if default_config.enabled else "禁用"
    
    await trigger_reset_cmd.send(f"✅ 已重置群 {group_id} 为默认配置\n\n• 启用状态：{status_text}\n• 强制@：{'是' if default_config.require_mention else '否'}\n\n✨ 已生效 💙")


# 智能触发列表命令
trigger_list_cmd = on_command("trigger_list", aliases={"触发列表", "群触发列表"}, priority=1, permission=SUPERUSER)


@trigger_list_cmd.handle()
async def handle_trigger_list():
    """显示所有群的智能触发配置（仅超级管理员）"""
    if not config._group_configs:
        await trigger_list_cmd.send("📝 当前没有配置群组\n\n所有群使用默认配置\n\n使用 /trigger_status 查看默认配置")
        return
    
    text = "✨ 群组智能触发配置列表 💙\n\n"
    
    for group_id, group_config in config._group_configs.items():
        trigger_config = group_config.trigger_config
        
        if trigger_config:
            status_text = "✅ 启用" if trigger_config.enabled else "❌ 禁用"
            mention_text = "（强制@）" if trigger_config.require_mention else ""
            
            text += f"【群 {group_id}】\n"
            text += f"• 状态：{status_text}\n"
            text += f"• 规则：{mention_text}\n"
            text += f"• 模式：{', '.join(trigger_config.mention_patterns[:2])}...\n\n"
    
    text += f"\n💡 提示：使用 /trigger_reset <群号> 恢复默认配置"

    await trigger_list_cmd.send(text)


# ========== 简洁模式管理命令 ==========

# 简洁模式状态命令
reply_mode_status_cmd = on_command("reply_mode_status", aliases={"简洁状态", "简洁模式状态", "回复模式状态"}, priority=1, permission=SUPERUSER)


@reply_mode_status_cmd.handle()
async def handle_reply_mode_status(event: Event):
    """显示简洁模式状态（仅超级管理员）"""
    group_id = str(event.group_id) if event.group_id else None

    text = f"""📝 简洁模式配置 💙

【全局默认配置】
• 回复模式：{config.reply_mode}
  • normal - 正常模式（根据内容判断）
  • concise - 简洁模式（所有回复简短）
  • detailed - 详细模式（全面解答）
• 最大长度：{config.reply_max_length} 字符
"""

    if group_id:
        group_reply_mode = config.get_group_reply_mode(group_id)
        if group_reply_mode != config.reply_mode:
            text += f"\n【当前群配置】\n• 群号：{group_id}\n• 回复模式：{group_reply_mode}\n⚠️ 已覆盖全局默认配置"
        else:
            text += f"\n【当前群配置】\n• 群号：{group_id}\n• 使用全局默认配置"

    text += f"""

【触发模式】
• {chr(10).join([f'• {p}' for p in config.concise_mode_patterns])}

【说明】
• normal 模式下，以下情况自动使用简洁回复：
  - 包含问号（？或?）
  - 包含疑问词：怎么、如何、为什么
  - 匹配其他触发模式

💡 使用 /reply_mode_set <群号> <模式> 设置群简洁模式
💡 使用 /reply_mode_reset <群号> 恢复全局默认
"""

    await reply_mode_status_cmd.send(text)


# 简洁模式设置命令
reply_mode_set_cmd = on_command("reply_mode_set", aliases={"简洁设置", "简洁模式设置", "回复模式设置"}, priority=1, permission=SUPERUSER)


@reply_mode_set_cmd.handle()
async def handle_reply_mode_set(event: Event):
    """设置群组的简洁模式（仅超级管理员）"""
    args = event.get_plaintext().strip().split()

    if len(args) < 3:
        await reply_mode_set_cmd.send(
            "❌ 参数错误！\n\n"
            "用法：/reply_mode_set <群号> <模式>\n\n"
            "模式：\n"
            "• normal - 正常模式（根据内容判断）\n"
            "• concise - 简洁模式（所有回复简短）\n"
            "• detailed - 详细模式（全面解答）\n\n"
            "示例：\n"
            "• /reply_mode_set 123456789 normal\n"
            "• /reply_mode_set 123456789 concise\n"
            "• /reply_mode_set 123456789 detailed"
        )
        return

    group_id = args[1]
    reply_mode = args[2].lower()

    # 验证模式
    valid_modes = ["normal", "concise", "detailed"]
    if reply_mode not in valid_modes:
        await reply_mode_set_cmd.send(
            f"❌ 不支持的回复模式：{reply_mode}\n\n"
            f"支持的模式：{', '.join(valid_modes)}"
        )
        return

    # 设置群组配置
    config.set_group_reply_mode(group_id, reply_mode)

    mode_desc = {
        "normal": "正常模式（根据内容判断）",
        "concise": "简洁模式（所有回复简短）",
        "detailed": "详细模式（全面解答）"
    }

    await reply_mode_set_cmd.send(
        f"✅ 已设置群 {group_id} 为 {mode_desc[reply_mode]} ✨💙\n\n"
        f"• 群号：{group_id}\n"
        f"• 回复模式：{reply_mode} - {mode_desc[reply_mode]}\n\n"
        f"✨ 已生效，群内回复将使用新设置"
    )


# 简洁模式重置命令
reply_mode_reset_cmd = on_command("reply_mode_reset", aliases={"简洁重置", "简洁模式重置", "回复模式重置"}, priority=1, permission=SUPERUSER)


@reply_mode_reset_cmd.handle()
async def handle_reply_mode_reset(event: Event):
    """重置群组的简洁模式为全局默认（仅超级管理员）"""
    args = event.get_plaintext().strip().split()

    if len(args) < 2:
        await reply_mode_reset_cmd.send(
            "❌ 参数错误！\n\n"
            "用法：/reply_mode_reset <群号>\n\n"
            "示例：/reply_mode_reset 123456789"
        )
        return

    group_id = args[1]

    # 移除群组配置
    config.remove_group_reply_mode(group_id)

    await reply_mode_reset_cmd.send(
        f"✅ 已重置群 {group_id} 为全局默认配置 ✨💙\n\n"
        f"• 群号：{group_id}\n"
        f"• 回复模式：{config.reply_mode}\n\n"
        f"✨ 已生效，群内回复将使用全局默认设置"
    )


# 简洁模式列表命令
reply_mode_list_cmd = on_command("reply_mode_list", aliases={"简洁列表", "简洁模式列表", "回复模式列表"}, priority=1, permission=SUPERUSER)


@reply_mode_list_cmd.handle()
async def handle_reply_mode_list():
    """显示所有群的简洁模式配置（仅超级管理员）"""
    from config import config

    # 加载群组配置
    config.load_group_configs()

    # 筛选有自定义简洁模式的群
    custom_groups = []
    for group_id, group_config in config._group_configs.items():
        if group_config.reply_mode_config and group_config.reply_mode_config.reply_mode:
            custom_groups.append({
                "group_id": group_id,
                "reply_mode": group_config.reply_mode_config.reply_mode
            })

    if not custom_groups:
        await reply_mode_list_cmd.send(
            "📝 当前没有自定义简洁模式的群\n\n"
            "所有群使用全局默认配置\n\n"
            f"• 全局默认：{config.reply_mode}\n\n"
            "使用 /reply_mode_status 查看默认配置"
        )
        return

    text = f"✨ 群组简洁模式配置列表 💙\n\n"
    text += f"全局默认：{config.reply_mode}\n\n"
    text += "【自定义配置的群】\n\n"

    for group in custom_groups:
        mode_desc = {
            "normal": "正常",
            "concise": "简洁",
            "detailed": "详细"
        }
        text += f"群 {group['group_id']}：{mode_desc.get(group['reply_mode'], group['reply_mode'])}\n"

    text += f"\n💡 提示：使用 /reply_mode_reset <群号> 恢复默认配置"

    await reply_mode_list_cmd.send(text)


