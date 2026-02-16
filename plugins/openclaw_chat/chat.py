#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 聊天插件核心代码
处理 QQ 群消息并调用本地 AI 处理
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


# 创建消息处理器（响应 @机器人）
chat = on_message(rule=to_me(), priority=1, block=True)

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
            
            # 获取 Vision 模型配置
            vision_model = config.model_name or "gpt-4o-mini"
            
            # 创建 Vision AI 客户端
            vision_client = VisionAIClient(
                api_key=config.current_api_key,
                provider=config.ai_model,
                base_url=None  # 使用默认 URL
            )
            
            # 识别图片
            prompt = f"请识别这张图片，并结合用户的问题回答：{message}" if message else "请描述这张图片的内容"
            reply = await vision_client.recognize_image(
                image_data=image_data,
                prompt=prompt,
                model=vision_model
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
            api_key=config.current_api_key  # 使用配置的 API Key
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
            api_key=config.current_api_key
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

【信息查询】
• /models - 查看所有可用模型
• /model - 查看当前模型信息

【权限说明】
⚠️ 以上命令仅超级管理员可以使用
📝 超级管理员配置在 .env 文件的 SUPERUSERS

💡 提示：使用 /help 查看所有命令
"""
    await admin_help_cmd.send(help_text)


