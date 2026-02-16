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
