#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw AI 处理模块（支持多模型）
支持：智谱 AI、DeepSeek、硅基流动、Ollama 本地模型等
"""

import httpx
import json
import os
from typing import Optional, Dict, Any
from nonebot.log import logger


# 支持的模型配置
MODEL_CONFIGS = {
    "zhipu": {
        "name": "智谱 AI",
        "api_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "models": ["glm-4", "glm-4-flash", "glm-4-plus"],
        "default_model": "glm-4-flash",
        "env_key": "ZHIPU_API_KEY",
        "free_tier": False,
        "description": "智谱 AI GLM-4 系列模型"
    },
    "deepseek": {
        "name": "DeepSeek",
        "api_url": "https://api.deepseek.com/v1/chat/completions",
        "models": ["deepseek-chat", "deepseek-coder"],
        "default_model": "deepseek-chat",
        "env_key": "DEEPSEEK_API_KEY",
        "free_tier": True,
        "free_quota": "每月免费额度",
        "description": "DeepSeek 大语言模型，有免费额度"
    },
    "siliconflow": {
        "name": "硅基流动",
        "api_url": "https://api.siliconflow.cn/v1/chat/completions",
        "models": ["Qwen/Qwen2-7B-Instruct", "THUDM/glm-4-9b-chat", "meta-llama/Meta-Llama-3-8B-Instruct"],
        "default_model": "Qwen/Qwen2-7B-Instruct",
        "env_key": "SILICONFLOW_API_KEY",
        "free_tier": True,
        "free_quota": "完全免费",
        "description": "硅基流动，完全免费的开源模型平台"
    },
    "ollama": {
        "name": "Ollama 本地",
        "api_url": "http://localhost:11434/api/chat",
        "models": ["llama3", "qwen2", "glm4", "mistral"],
        "default_model": "qwen2",
        "env_key": None,  # Ollama 不需要 API Key
        "free_tier": True,
        "free_quota": "完全免费",
        "description": "Ollama 本地模型，完全免费，无需网络"
    },
    "moonshot": {
        "name": "Moonshot (Kimi)",
        "api_url": "https://api.moonshot.cn/v1/chat/completions",
        "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        "default_model": "moonshot-v1-8k",
        "env_key": "MOONSHOT_API_KEY",
        "free_tier": True,
        "free_quota": "免费试用额度",
        "description": "Moonshot Kimi 长文本模型"
    }
}


async def process_message_with_ai(
    message: str,
    user_id: str,
    context: str = "qq_group",
    group_id: Optional[str] = None,
    model: str = "zhipu",
    api_key: Optional[str] = None
) -> str:
    """
    使用 AI 处理消息（支持多模型）
    
    Args:
        message: 用户消息
        user_id: 用户 QQ 号
        context: 上下文类型
        group_id: 群号（如果是群聊）
        model: 模型名称（zhipu/deepseek/siliconflow/ollama/moonshot）
        api_key: API Key（可选，如果未提供则从环境变量读取）
    
    Returns:
        str: AI 的回复
    """
    
    # 获取模型配置
    model_config = MODEL_CONFIGS.get(model)
    if not model_config:
        logger.error(f"❌ 不支持的模型: {model}")
        return generate_fallback_reply(message)
    
    # 获取 API Key
    if not api_key and model_config["env_key"]:
        api_key = os.getenv(model_config["env_key"], "")
    
    # 调用对应的 AI 模型
    try:
        if model == "ollama":
            reply = await _call_ollama(message, user_id, context, group_id, model_config)
        else:
            reply = await _call_openai_compatible(
                message, user_id, context, group_id, 
                model_config, api_key
            )
        
        if reply and not reply.startswith("抱歉"):
            return reply
    except Exception as e:
        logger.error(f"❌ AI 调用失败: {e}")
    
    # 回退到简单回复
    return generate_fallback_reply(message)


async def _call_openai_compatible(
    message: str,
    user_id: str,
    context: str,
    group_id: Optional[str],
    model_config: Dict[str, Any],
    api_key: str
) -> str:
    """
    调用 OpenAI 兼容的 API（智谱/DeepSeek/硅基流动/Moonshot）
    """
    
    url = model_config["api_url"]
    model_name = model_config["default_model"]
    
    # 系统提示词
    system_prompt = _build_system_prompt(user_id, context, group_id)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model_name,
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
                logger.info(f"✅ {model_config['name']} 回复成功: {reply[:50]}...")
                return reply
            else:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                error_code = error_data.get("error", {}).get("code", "unknown")
                error_msg = error_data.get("error", {}).get("message", response.text)
                
                logger.error(f"❌ {model_config['name']} API 错误: {response.status_code} - {error_msg}")
                
                # 根据错误类型返回不同提示
                if error_code == "1113" or "余额不足" in error_msg:
                    return f"抱歉，{model_config['name']} 余额不足，请充值后使用。\n\n" + generate_fallback_reply(message)
                elif response.status_code == 401:
                    return f"抱歉，{model_config['name']} API Key 无效，请检查配置。\n\n" + generate_fallback_reply(message)
                else:
                    return f"抱歉，{model_config['name']} 服务暂时不可用（错误: {response.status_code}）\n\n" + generate_fallback_reply(message)
                
    except httpx.TimeoutException:
        logger.error(f"❌ {model_config['name']} API 超时")
        return f"抱歉，{model_config['name']} 响应超时，请稍后再试。\n\n" + generate_fallback_reply(message)
        
    except Exception as e:
        logger.error(f"❌ {model_config['name']} API 异常: {e}")
        return f"抱歉，发生了错误。\n\n" + generate_fallback_reply(message)


async def _call_ollama(
    message: str,
    user_id: str,
    context: str,
    group_id: Optional[str],
    model_config: Dict[str, Any]
) -> str:
    """
    调用 Ollama 本地模型
    """
    
    url = model_config["api_url"]
    model_name = model_config["default_model"]
    
    # 系统提示词
    system_prompt = _build_system_prompt(user_id, context, group_id)
    
    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
        "stream": False
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                reply = result["message"]["content"]
                logger.info(f"✅ Ollama 回复成功: {reply[:50]}...")
                return reply
            else:
                logger.error(f"❌ Ollama 错误: {response.status_code}")
                return f"抱歉，Ollama 本地模型响应失败。\n\n" + generate_fallback_reply(message)
                
    except httpx.ConnectError:
        logger.error("❌ 无法连接到 Ollama，请确保 Ollama 正在运行")
        return f"抱歉，无法连接到 Ollama 本地模型。\n请确保已安装并运行 Ollama：ollama serve\n\n" + generate_fallback_reply(message)
        
    except Exception as e:
        logger.error(f"❌ Ollama 异常: {e}")
        return f"抱歉，发生了错误。\n\n" + generate_fallback_reply(message)


def _build_system_prompt(user_id: str, context: str, group_id: Optional[str]) -> str:
    """
    构建系统提示词
    """
    return f"""你是 OpenClaw，一个友好、聪明、有点俏皮的 AI 助手。

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

【版本】v1.1.0"""
    
    elif "你是谁" in message or "介绍" in message:
        return "我是 OpenClaw 🦞，一个由 AutoGLM 配置的智能助手！\n\n⚠️ 注意：AI 服务暂时受限，正在使用简单回复模式。"
    
    else:
        return f"收到你的消息：{message}\n\n⚠️ 注意：AI 服务暂时受限，正在使用简单回复模式。"


def list_available_models() -> str:
    """
    列出所有可用的模型
    """
    result = "🦞 OpenClaw 支持的 AI 模型：\n\n"
    
    for model_id, config in MODEL_CONFIGS.items():
        free_badge = "✅ 免费" if config["free_tier"] else "💰 付费"
        result += f"**{config['name']}** ({model_id}) {free_badge}\n"
        result += f"  {config['description']}\n"
        if config.get("free_quota"):
            result += f"  🎁 {config['free_quota']}\n"
        result += f"  可用模型: {', '.join(config['models'])}\n\n"
    
    return result
