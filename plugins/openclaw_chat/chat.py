#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 聊天插件核心代码
处理 QQ 群消息并调用 OpenClaw API
"""

from nonebot import on_message, on_command
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import Bot, Event, Message, MessageSegment
from nonebot.log import logger
from nonebot.params import CommandArg
import httpx
import json
from typing import Optional
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import config


# 创建消息处理器（响应 @机器人）
chat = on_message(rule=to_me(), priority=1, block=True)

# 创建命令处理器（响应 /chat 命令）
chat_cmd = on_command("chat", aliases={"对话", "聊天"}, priority=2, block=True)


async def call_openclaw_api(message: str, user_id: str, group_id: Optional[str] = None) -> str:
    """
    调用 OpenClaw API
    
    Args:
        message: 用户消息
        user_id: 用户 QQ 号
        group_id: 群号（如果是群聊）
    
    Returns:
        str: OpenClaw 的回复
    """
    try:
        # 准备请求数据
        request_data = {
            "message": message,
            "user_id": user_id,
            "context": "qq_group" if group_id else "qq_private",
        }
        
        if group_id:
            request_data["group_id"] = group_id
        
        # 调用 OpenClaw API
        async with httpx.AsyncClient(timeout=config.openclaw_api_timeout) as client:
            response = await client.post(
                config.openclaw_api_url,
                json=request_data,
                headers={
                    "Authorization": f"Bearer {config.openclaw_api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                reply = result.get("reply", "抱歉，我暂时无法回应")
                logger.info(f"OpenClaw API 调用成功: {message[:20]} -> {reply[:20]}")
                return reply
            else:
                error_msg = f"OpenClaw API 错误: HTTP {response.status_code}"
                logger.error(error_msg)
                return f"抱歉，服务暂时不可用（错误代码: {response.status_code}）"
                
    except httpx.TimeoutException:
        logger.error("OpenClaw API 超时")
        return "抱歉，请求超时，请稍后再试"
        
    except httpx.RequestError as e:
        logger.error(f"OpenClaw API 连接错误: {e}")
        return "抱歉，网络连接失败，请检查网络"
        
    except Exception as e:
        logger.error(f"OpenClaw API 未知错误: {e}")
        return "抱歉，发生了未知错误"


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
        
        # 调用 OpenClaw API
        reply = await call_openclaw_api(message, user_id, group_id)
        
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
        
        # 调用 OpenClaw API
        reply = await call_openclaw_api(message, user_id, group_id)
        
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
    await welcome.send(f"你好！我是 {config.bot_name}，很高兴见到你！\n你可以 @我 与我对话，或者使用 /chat 命令。")


# 帮助命令
help_cmd = on_command("help", aliases={"帮助"}, priority=3)


@help_cmd.handle()
async def handle_help():
    """显示帮助信息"""
    help_text = f"""
🦞 {config.bot_name} 使用指南

【基本用法】
• @我 + 消息：与我对话
• /chat + 消息：与我对话
• /hello 或 /你好：打招呼
• /help 或 /帮助：显示此帮助

【功能列表】
✅ 日常对话
✅ 回答问题
✅ 文件读取
✅ 命令执行
✅ 数据分析
✅ 编程帮助

【注意事项】
• 请友善使用
• 不要发送垃圾信息
• 复杂任务可能需要较长时间

【版本】v1.0.0
【作者】OpenClaw
    """.strip()
    await help_cmd.send(help_text)
