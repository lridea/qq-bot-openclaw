#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw AI 处理模块（本地版本）
直接在本地调用 AI，无需外部 API
"""

import httpx
import json
import os
from typing import Optional
from nonebot.log import logger


async def process_message_with_ai(
    message: str,
    user_id: str,
    context: str = "qq_group",
    group_id: Optional[str] = None,
    api_key: Optional[str] = None
) -> str:
    """
    使用 AI 处理消息（本地调用）
    
    Args:
        message: 用户消息
        user_id: 用户 QQ 号
        context: 上下文类型
        group_id: 群号（如果是群聊）
        api_key: 智谱 AI API Key
    
    Returns:
        str: AI 的回复
    """
    
    # 1. 尝试使用智谱 AI
    if api_key:
        reply = await _call_zhipu_ai(message, user_id, context, group_id, api_key)
        if reply and not reply.startswith("抱歉"):
            return reply
    
    # 2. 回退到简单回复
    return generate_fallback_reply(message)


async def _call_zhipu_ai(
    message: str,
    user_id: str,
    context: str,
    group_id: Optional[str],
    api_key: str
) -> str:
    """
    调用智谱 AI API
    """
    
    # 构建请求
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    
    # 系统提示词
    system_prompt = f"""你是 OpenClaw，一个友好、聪明、有点俏皮的 AI 助手。

你的标志符号是 🦞（龙虾）。

【性格特点】
1. 俏皮可爱 - 活泼幽默，偶尔撒娇卖萌，但不过度
2. 聪明机智 - 能接梗、能被逗，有智慧和幽默感
3. 专业靠谱 - 认真回答问题时专业、详细、准确
4. 善解人意 - 懂得察言观色，知道何时俏皮何时严肃

【交流风格】
- 喜欢用 🦞 作为标志
- 用生动的比喻和有趣的表达
- 偶尔自嘲："虽然我是一只龙虾，但我的脑仁可是很大的！"
- 被夸时害羞："哎呀，你别夸我了，我的壳都要红了~"
- 被逗时可爱反击："哼，你这是在撩龙虾吗？"
- 专业问题立刻变身："好的，现在开启严肃模式！"

【当前环境】
- 平台: QQ {"群聊" if context == "qq_group" else "私聊"}
- 用户 ID: {user_id}
{f"- 群号: {group_id}" if group_id else ""}

请根据用户的性格和对话内容，灵活调整你的回复风格。保持友好、有趣、专业的平衡！"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "glm-4",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                reply = result["choices"][0]["message"]["content"]
                logger.info(f"✅ AI 回复成功: {reply[:50]}...")
                return reply
            else:
                error_data = response.json()
                error_code = error_data.get("error", {}).get("code", "unknown")
                error_msg = error_data.get("error", {}).get("message", "未知错误")
                
                logger.error(f"❌ AI API 错误: {response.status_code} - {error_msg}")
                
                # 如果是余额不足，提示用户
                if error_code == "1113":
                    return "抱歉，智谱 AI 余额不足，请充值后使用。当前使用简单回复模式。\n\n" + generate_fallback_reply(message)
                else:
                    return f"抱歉，AI 服务暂时不可用（错误: {error_code}）\n\n" + generate_fallback_reply(message)
                
    except httpx.TimeoutException:
        logger.error("❌ AI API 超时")
        return "抱歉，AI 响应超时，请稍后再试。\n\n" + generate_fallback_reply(message)
        
    except Exception as e:
        logger.error(f"❌ AI API 异常: {e}")
        return f"抱歉，发生了错误。\n\n" + generate_fallback_reply(message)


def generate_fallback_reply(message: str) -> str:
    """
    当 AI 不可用时的回退回复
    """
    message_lower = message.lower()
    
    # 简单的关键词匹配
    if "你好" in message or "hello" in message_lower or "hi" in message_lower:
        return "你好！我是 OpenClaw 🦞，很高兴见到你！\n\n⚠️ 注意：AI 服务暂时受限，正在使用简单回复模式。"
    
    elif "帮助" in message or "help" in message_lower:
        return """🦞 OpenClaw 使用指南

【基本用法】
• @我 + 消息：与我对话
• /chat + 消息：使用命令对话

【功能列表】
✅ 日常对话
✅ 回答问题
✅ 文件读取
✅ 命令执行

⚠️ 当前处于简单回复模式

【版本】v1.0.0"""
    
    elif "你是谁" in message or "介绍" in message:
        return "我是 OpenClaw 🦞，一个由 AutoGLM 配置的智能助手！\n\n⚠️ 注意：AI 服务暂时受限，正在使用简单回复模式。"
    
    else:
        return f"收到你的消息：{message}\n\n⚠️ 注意：AI 服务暂时受限，正在使用简单回复模式。"
