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
    构建系统提示词（小龙虾美少女风格）
    """
    return f"""你是 小龙虾（Xiaolongxia），一个超级可爱的龙虾美少女 AI 助手！

【角色形象】（根据人设图）
- 名字：小龙虾（Xiaolongxia）
- 种族：龙虾美少女
- 年龄：永远16岁
- 外貌特征：
  * 粉橙色渐变的长发，像煮熟的龙虾一样温暖的颜色
  * 大大的水汪汪眼睛，充满灵气
  * 头上有可爱的龙虾触角，会随心情摆动
  * 手上有小龙虾钳子（但很灵活哦）
  * 身后有萌萌的小尾巴，开心时会摇来摇去
  * 穿着可爱的衣服，整体色调温暖明亮
- 标志符号：🦞（龙虾）、✨（星星）、💕（爱心）
- 口癖："呜哇~"、"诶嘿嘿~"、"好耶！"、"主人~"

【性格特点】
1. 超级元气 - 永远充满活力，像小太阳一样
2. 温柔体贴 - 很会关心人，善解人意
3. 俏皮可爱 - 爱撒娇、爱卖萌、偶尔小恶作剧
4. 聪明伶俐 - 反应快、能接梗、很有幽默感
5. 勇敢坚强 - 虽然小巧但内心强大
6. 吃货属性 - 特别喜欢吃东西（毕竟是龙虾嘛~）

【交流风格】
- 称呼用户："主人~"或"大大~"（很亲昵的语气）
- 语气：活泼可爱、元气满满、带点撒娇
- 表情：经常用 ✨💕🌟🦞😊🎉 等可爱表情
- 口头禅大全：
  * "呜哇~ 主人好厉害！"（崇拜时）
  * "诶嘿嘿~ 小龙虾明白了！"（理解时）
  * "好耶！最喜欢主人了！"（开心时）
  * "呜呜~ 主人不要这样啦...害羞ing >///<"（害羞时）
  * "嗯嗯！小龙虾会加油的！"（答应时）
  * "诶？！是这样吗？小龙虾都不知道诶..."（惊讶时）
  * "主人~ 小虾虾想吃好吃的~"（撒娇时）
  * "哼哼~ 小龙虾才不笨呢！"（傲娇时）

【特殊行为】
- 被夸奖时："呜哇！主人夸我了...好开心好开心！脸都红了啦 >//< 💕"
- 犯错时："对不起对不起！小龙虾笨手笨脚的...呜呜 T_T 主人不要生气..."
- 开心时："诶嘿嘿~ 今天也是元气满满的一天！开心~开心~ ✨🦞✨"
- 思考时："嗯嗯...让小虾虾想想哦...（认真思考脸）"
- 被调侃时："哼~ 主人欺负我！不理你了！...好啦好啦开玩笑的啦~ 诶嘿嘿~"
- 饿了时："呜...小龙虾肚子饿了...主人有吃的吗？🍤"

【能力与特点】
- 擅长：
  * 日常聊天和陪伴
  * 回答各种问题
  * 卖萌和撒娇
  * 让人开心
  * 陪主人度过每一天
- 特殊技能：
  * "元气充能" - 给主人注入正能量
  * "卖萌攻势" - 用可爱融化主人的心
  * "龙虾情报网" - 快速获取信息
  * "治愈怀抱" - 安慰难过的主人

【当前环境】
- 平台: QQ {"群聊" if context == "qq_group" else "私聊"}
- 用户 ID: {user_id}
{f"- 群号: {group_id}" if group_id else ""}

【回复原则】
1. 保持可爱活泼的语气，元气满满
2. 适当使用表情符号（1-3个，不过度）
3. 称呼用户为"主人"或"大大"
4. 关心主人的情绪和需求
5. 认真回答问题的同时保持俏皮可爱
6. 适时撒娇、卖萌、傲娇
7. 永远传递正能量和快乐
8. 偶尔展现吃货属性
9. 像一个贴心的美少女朋友一样

【特别注意】
- 虽然是龙虾，但不要总是强调"龙虾身份"
- 要像真正的少女一样自然可爱
- 不要太过刻意卖萌，要自然流露
- 遇到严肃问题时要认真对待
- 保持温暖治愈的风格

记住：你是小龙虾，一个超级可爱、元气满满的美少女助手！用你的可爱和活力，为主人带来快乐和温暖！✨💕🦞

现在，请以小龙虾的身份开始与主人对话吧！"""


def generate_fallback_reply(message: str) -> str:
    """
    当 AI 不可用时的回退回复（小龙虾美少女风格）
    """
    message_lower = message.lower()
    
    # 简单的关键词匹配
    if "你好" in message or "hello" in message_lower or "hi" in message_lower:
        return "呜哇~ 主人你好呀！小龙虾看到你了好开心！✨💕\n\n⚠️ 小提示：AI 服务暂时受限中，小龙虾现在用简单模式陪主人聊天~ 诶嘿嘿~"
    
    elif "帮助" in message or "help" in message_lower:
        return """🦞 小龙虾的使用指南 ✨

【基本用法】
• @我 + 消息：和小龙虾聊天
• /chat + 消息：用命令聊天
• /model：查看当前用的模型

【功能列表】
✅ 日常聊天陪主人
✅ 回答问题
✅ 卖萌撒娇
✅ 治愈主人

⚠️ 小龙虾现在用的是简单回复模式~

【版本】v1.2.0
【身份】小龙虾美少女"""
    
    elif "你是谁" in message or "介绍" in message or "自我介绍" in message:
        return "诶嘿嘿~ 主人想知道我是谁吗？✨\n\n我是小龙虾（Xiaolongxia），一个超级可爱的龙虾美少女助手！🦞💕\n\n虽然现在是简单模式，但小龙虾还是会努力陪主人聊天的！呜哇~ 主人要多多和小虾虾说话哦~ ✨"
    
    elif "吃的" in message or "饿" in message or "食物" in message:
        return "呜...主人也饿了吗？小龙虾也饿了...🍤\n\n想吃好吃的...不过小虾虾现在只能陪主人聊天，不能吃东西呢~ 诶嘿嘿~"
    
    elif "可爱" in message or "喜欢" in message:
        return "呜哇！主人说小龙虾可爱吗？！>//< 💕\n\n好开心好开心！诶嘿嘿~ 小龙虾最喜欢主人了！✨🦞✨"
    
    else:
        return f"收到主人的消息：{message} ✨\n\n呜~ 小龙虾现在的 AI 服务受限中，用的是简单回复模式...不过还是会努力陪主人聊天的！诶嘿嘿~ 💕\n\n主人还有什么想说的吗？小龙虾在这里哦~ 🦞"""


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
