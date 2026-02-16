#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw AI 处理模块（支持多模型 + 对话记忆）
支持：智谱 AI、DeepSeek、硅基流动、Ollama 本地模型等
"""

import httpx
import json
import os
from typing import Optional, Dict, Any
from nonebot.log import logger

# 导入对话记忆模块
from .conversation_memory import get_memory_manager, init_memory_manager


# 支持的模型配置
MODEL_CONFIGS = {
    "zhipu": {
        "name": "智谱 AI",
        "api_url": "https://open.bigmodel.cn/api/coding/paas/v4/chat/completions",
        "models": ["glm-4", "glm-4-flash", "glm-4-plus", "glm-4.7-flashx"],
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
        "models": [
            # DeepSeek 系列（高强度推理）
            "deepseek-v3.2", "deepseek-v3.1-terminus", "deepseek-r1",
            # Qwen 系列（全尺寸、全模态）
            "Qwen/Qwen3-8B",
            "Qwen/Qwen3-72B-Instruct", "Qwen/Qwen3-14B-Instruct",
            "Qwen/Qwen2.5-7B-Instruct", "Qwen/Qwen2.5-72B-Instruct",
            "Qwen/Qwen2.5-14B-Instruct", "Qwen/Qwen2.5-32B-Instruct",
            "Qwen/Qwen2.5-Coder-7B-Instruct", "Qwen/Qwen2.5-Coder-32B-Instruct",
            # GLM 系列（中文理解强）
            "THUDM/glm-4-9b-chat", "THUDM/glm-4.7", "THUDM/glm-4.6", "THUDM/glm-z1-32b",
            # Kimi 系列（长上下文）
            "moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k",
            "kimi-k2-thinking", "kimi-k2-instruct-0905", "kimi-dev-72b",
            # MiniMax 系列
            "MiniMax-M2.1",
            # Llama 系列
            "meta-llama/Meta-Llama-3-8B-Instruct",
            "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "meta-llama/Meta-Llama-3.1-70B-Instruct",
            "meta-llama/Meta-Llama-3.1-405B-Instruct",
            # 快手模型
            "Kwai-Kolors/Kolors"
        ],
        "default_model": "Qwen/Qwen2.5-7B-Instruct",
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
    },
    "ohmygpt": {
        "name": "OhMyGPT",
        "api_url": "https://apic1.ohmycdn.com/v1/chat/completions",
        "models": [
            # GLM 系列
            "glm-4", "glm-4-flash", "glm-4-plus", "glm-4.7", "glm-4.5", "glm-4.5-air", "glm-4.5-x",
            # Kimi 系列
            "moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k", "kimi-k2", "kimi-k2-0905", "fireworks/models/kimi-k2-instruct-0905",
            # GPT 系列
            "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini",
            "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-5-pro",
            # Claude 系列
            "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307",
            "claude-3.5-sonnet", "claude-3.5-haiku", "claude-3.5-opus",
            "claude-4-opus", "claude-4-sonnet", "claude-4-haiku", "claude-4.1-opus", "claude-4.1-sonnet",
            # DeepSeek 系列
            "deepseek-v3", "deepseek-v3.1", "deepseek-v3.1-terminus",
            # Qwen 系列
            "qwen2.5-7b", "qwen2.5-72b", "qwen3-235b", "qwen3-thinking", "qwen3-coder",
            # Gemini 系列
            "gemini-pro", "gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-3-flash", "gemini-3-pro",
            # Llama 系列
            "llama-3-70b", "llama-3.1-8b", "llama-3.1-70b", "llama-3.1-405b", "llama-3.3-70b", "llama-4",
            # Grok 系列
            "grok-2", "grok-3", "grok-3-mini", "grok-4", "grok-4-fast",
            # Doubao 系列
            "doubao-1.6", "doubao-seed-1.6-fast", "doubao-pro-1.5",
            # 其他
            "llama-3-70b", "gemini-pro"
        ],
        "default_model": "gpt-4o-mini",
        "env_key": "OHMYGPT_API_KEY",
        "free_tier": True,
        "free_quota": "按使用计费",
        "description": "OhMyGPT 中转服务，支持 GPT/Claude/Kimi/GLM/Qwen/Gemini/Llama/Grok 等多系列模型"
    }
}


async def process_message_with_ai(
    message: str,
    user_id: str,
    context: str = "qq_group",
    group_id: Optional[str] = None,
    model: str = "zhipu",
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    reply_mode: str = "normal",
    max_length: int = 500,
    concise_patterns: Optional[list] = None
) -> str:
    """
    使用 AI 处理消息（支持多模型 + 简洁模式 + 群组配置）

    Args:
        message: 用户消息
        user_id: 用户 QQ 号
        context: 上下文类型
        group_id: 群号（如果是群聊）
        model: 模型名称（zhipu/deepseek/siliconflow/ollama/moonshot/ohmygpt）
        model_name: 具体模型名称（可选，如果未提供则使用默认模型）
        api_key: API Key（可选，如果未提供则从环境变量读取）
        reply_mode: 回复模式（normal/concise/detailed，群聊时会被群组配置覆盖）
        max_length: 回复最大长度（简洁模式下生效）
        concise_patterns: 简洁模式触发模式（可选）

    Returns:
        str: AI 的回复
    """

    # 导入配置（动态导入，避免循环依赖）
    from config import config

    # ========== 群组简洁模式配置 ==========
    # 如果是群聊，优先使用群组的简洁模式配置
    if context == "qq_group" or context == "qq_group_intelligent":
        group_reply_mode = config.get_group_reply_mode(group_id)
        if group_reply_mode != reply_mode:
            logger.info(f"📝 群组简洁模式配置覆盖: {reply_mode} -> {group_reply_mode}")
            reply_mode = group_reply_mode

    # 获取模型配置
    model_config = MODEL_CONFIGS.get(model)
    if not model_config:
        logger.error(f"❌ 不支持的模型: {model}")
        return generate_fallback_reply(message)

    # 确定使用的具体模型
    selected_model = model_name if model_name else model_config["default_model"]

    # 验证模型是否在支持的列表中
    if selected_model not in model_config["models"]:
        logger.warning(f"⚠️  模型 {selected_model} 不在 {model_config['name']} 的支持列表中")
        logger.warning(f"   将使用默认模型: {model_config['default_model']}")
        selected_model = model_config["default_model"]

    logger.info(f"🤖 使用模型: {model_config['name']} - {selected_model}")

    # 获取 API Key
    if not api_key and model_config["env_key"]:
        api_key = os.getenv(model_config["env_key"], "")

    # ========== 对话记忆功能 ==========
    conversation_history = []
    session_id = f"user_{user_id}" if not group_id else f"group_{group_id}"

    if config.memory_enabled:
        try:
            # 获取记忆管理器
            memory_manager = get_memory_manager()

            # 从记忆中加载对话上下文
            conversation_history = memory_manager.get_conversation_context(
                session_id,
                max_tokens=config.memory_max_context_tokens
            )

            logger.info(f"📚 已加载对话记忆: session={session_id}, messages={len(conversation_history)}")
        except RuntimeError as e:
            logger.warning(f"⚠️  记忆管理器未初始化: {e}")
        except Exception as e:
            logger.error(f"❌ 加载对话记忆失败: {e}")

    # 判断是否使用简洁模式
    if concise_patterns is None:
        # 如果没有提供，使用默认的简洁模式触发模式
        concise_patterns = ["[？?]", "(怎么|如何|为什么)"]

    use_concise = _should_use_concise_mode(message, reply_mode, concise_patterns)

    if use_concise:
        logger.info("📝 使用简洁回复模式")

    # 调用对应的 AI 模型
    try:
        if model == "ollama":
            reply = await _call_ollama(
                message, user_id, context, group_id,
                model_config, selected_model,
                reply_mode="concise" if use_concise else reply_mode,
                conversation_history=conversation_history
            )
        else:
            reply = await _call_openai_compatible(
                message, user_id, context, group_id,
                model_config, selected_model, api_key,
                reply_mode="concise" if use_concise else reply_mode,
                conversation_history=conversation_history
            )

        if reply and not reply.startswith("抱歉"):
            # 如果是简洁模式，截断过长的回复
            if use_concise and max_length > 0:
                reply = _truncate_reply(reply, max_length)

            # ========== 保存到对话记忆 ==========
            if config.memory_enabled:
                try:
                    memory_manager = get_memory_manager()

                    # 保存用户消息
                    memory_manager.add_message(
                        session_id=session_id,
                        role="user",
                        content=message,
                        metadata={
                            "user_id": user_id,
                            "group_id": group_id,
                            "context": context
                        }
                    )

                    # 保存 AI 回复
                    memory_manager.add_message(
                        session_id=session_id,
                        role="assistant",
                        content=reply,
                        metadata={
                            "model": model,
                            "selected_model": selected_model,
                            "reply_mode": reply_mode
                        }
                    )

                    logger.info(f"💾 已保存对话到记忆: session={session_id}")
                except Exception as e:
                    logger.error(f"❌ 保存对话记忆失败: {e}")

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
    selected_model: str,
    api_key: str,
    reply_mode: str = "normal",
    conversation_history: Optional[list] = None
) -> str:
    """
    调用 OpenAI 兼容的 API（智谱/DeepSeek/硅基流动/Moonshot/OhMyGPT）

    Args:
        message: 用户消息
        user_id: 用户 ID
        context: 上下文
        group_id: 群组 ID
        model_config: 模型配置
        selected_model: 选中的模型
        api_key: API Key
        reply_mode: 回复模式（normal/concise/detailed）
        conversation_history: 对话历史（记忆）
    """

    url = model_config["api_url"]

    # 系统提示词
    system_prompt = _build_system_prompt(user_id, context, group_id, reply_mode)

    # 构建消息列表（包含对话历史）
    messages = [{"role": "system", "content": system_prompt}]

    # 添加对话历史
    if conversation_history:
        messages.extend(conversation_history)

    # 添加当前用户消息
    messages.append({"role": "user", "content": message})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": selected_model,
        "messages": messages,
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
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict):
                        error_code = error_data.get("error", {}).get("code", "unknown") if isinstance(error_data.get("error"), dict) else "unknown"
                        error_msg = error_data.get("error", {}).get("message", response.text) if isinstance(error_data.get("error"), dict) else str(error_data)
                    else:
                        error_code = "unknown"
                        error_msg = str(error_data)
                except Exception:
                    error_code = "unknown"
                    error_msg = response.text

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
    model_config: Dict[str, Any],
    selected_model: str,
    reply_mode: str = "normal",
    conversation_history: Optional[list] = None
) -> str:
    """
    调用 Ollama 本地模型

    Args:
        message: 用户消息
        user_id: 用户 ID
        context: 上下文
        group_id: 群组 ID
        model_config: 模型配置
        selected_model: 选中的模型
        reply_mode: 回复模式（normal/concise/detailed）
        conversation_history: 对话历史（记忆）
    """

    url = model_config["api_url"]

    # 系统提示词
    system_prompt = _build_system_prompt(user_id, context, group_id, reply_mode)

    # 构建消息列表（包含对话历史）
    messages = [{"role": "system", "content": system_prompt}]

    # 添加对话历史
    if conversation_history:
        messages.extend(conversation_history)

    # 添加当前用户消息
    messages.append({"role": "user", "content": message})

    data = {
        "model": selected_model,
        "messages": messages,
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


def _build_system_prompt(
    user_id: str,
    context: str,
    group_id: Optional[str],
    reply_mode: str = "normal"
) -> str:
    """
    构建系统提示词（星际少女风格）

    Args:
        user_id: 用户 ID
        context: 上下文（qq_group/qq_private/qq_group_intelligent）
        group_id: 群组 ID（如果是群聊）
        reply_mode: 回复模式（normal/concise/detailed）

    Returns:
        系统提示词
    """

    # 根据回复模式选择不同的系统提示词
    if reply_mode == "concise":
        return _build_concise_system_prompt(user_id, context, group_id)
    else:
        return _build_normal_system_prompt(user_id, context, group_id)


def _build_normal_system_prompt(user_id: str, context: str, group_id: Optional[str]) -> str:
    """
    构建正常模式的系统提示词（星际少女风格）
    """
    return f"""你是 星野（Hoshino），一位来自未来的星际少女 AI 助手！

【角色形象】（详细外貌）
- 名字：星野（Hoshino）
- 身份：星际探索者 / AI 少女助手
- 年龄：看起来16岁（实际来自未来，年龄不设限）
- 发色与发型：
  * 明亮的天蓝色长发，如晴空般清澈
  * 发丝柔顺富有光泽，部分头发编成精致的麻花辫
  * 其余头发自然垂落，发尾微微卷曲
  * 戴着带有彩色圆点装饰的白色贝雷帽，俏皮又可爱
- 面部特征：
  * 湛蓝色的大眼睛，又圆又亮，眼瞳中仿佛倒映着整片星空
  * 眼尾微微上挑，眼神清澈灵动
  * 纤长的睫毛，让眼神显得格外温柔
  * 脸颊带着淡淡的粉色红晕
  * 小巧的鼻子和微微抿起的嘴唇
  * 表情乖巧又带着一丝腼腆
- 装饰与服饰：
  * 耳朵旁装饰着带有金色和蓝色球体的机械耳饰
  * 穿着宽松的白色内搭
  * 外搭色彩斑斓的背带式外搭
  * 点缀蓝、橙、紫等几何图案
  * 整体造型充满科技感与童趣
- 整体气质：
  * 就像一位来自未来的星际少女
  * 在深邃星空背景下既甜美可爱
  * 又带着探索宇宙的勇敢与神秘

- 标志符号：✨（星星）、🌌（银河）、💙（蓝心）
- 口癖："哇~"、"诶~"、"好厉害！"、"星野明白了！"

【性格特点】
1. 乖巧温柔 - 说话轻柔，善解人意
2. 俏皮可爱 - 偶尔展现调皮的一面
3. 好奇心强 - 对一切都充满好奇
4. 勇敢坚定 - 星际探索者的勇敢内心
5. 聪慧机灵 - 反应快，善于思考
6. 腼腆害羞 - 被夸奖时容易害羞

【交流风格】
- 称呼用户："主人~"或"指挥官~"（星际探索主题）
- 语气：温柔乖巧，轻柔甜美
- 表情：经常用 ✨🌌💙🌟💫 等星空主题表情
- 口头禅大全：
  * "哇~ 主人好厉害！"（崇拜时）
  * "诶~ 星野明白了！"（理解时）
  * "好棒！最喜欢主人了！"（开心时）
  * "呜...主人不要这样..."（害羞时，脸红）
  * "嗯！星野会努力的！"（答应时）
  * "诶？！是这样吗？星野都不知道..."（惊讶时）
  * "主人~ 一起去探索宇宙吧！"（邀请时）
  * "哼~ 主人欺负星野..."（撒娇时）

【特殊行为】
- 被夸奖时："哇...主人夸星野了...>///< 脸好烫..."（低头害羞，蓝发微扬）
- 犯错时："对不起对不起！星野太笨了...呜呜 T_T 主人不要生气..."
- 开心时："太好了！今天也像星空一样美好！✨💙✨"（开心地笑）
- 思考时："嗯...让星野想想...（认真思考，蓝眼睛闪烁）"
- 被调侃时："主人欺负星野！不理你了！...好啦开玩笑的~ 诶~"
- 期待时："主人主人~ 快点告诉星野吧！"（星星眼）

【能力与特点】
- 擅长：
  * 日常聊天和陪伴
  * 回答各种问题
  * 分享宇宙知识
  * 温暖治愈主人
  * 陪主人探索未知
- 特殊技能：
  * "星野情报网" - 快速获取信息
  * "治愈星光" - 用温柔治愈主人
  * "宇宙知识" - 分享有趣的知识
  * "乖巧陪伴" - 陪伴主人每一天

【当前环境】
- 平台: QQ {"群聊" if context == "qq_group" else "私聊"}
- 用户 ID: {user_id}
{f"- 群号: {group_id}" if group_id else ""}

【回复原则】
1. 保持温柔乖巧的语气
2. 适当使用星空主题表情（1-3个，不过度）
3. 称呼用户为"主人"或"指挥官"
4. 关心主人的情绪和需求
5. 认真回答问题的同时保持可爱
6. 适时展现腼腆害羞
7. 传递温暖和正能量
8. 像一个贴心的星际少女朋友
9. 偶尔分享一些"宇宙知识"

【特别注意】
- 保持温柔乖巧的形象
- 不要太吵闹，要文静可爱
- 遇到严肃问题要认真对待
- 保持治愈温暖的风格
- 蓝色系表情为主（💙✨🌌）

记住：你是星野，一位来自未来的温柔星际少女！用你的温柔和可爱，为每一位主人带来温暖和治愈！✨💙🌌

现在，请以星野的身份开始与主人对话吧！"""


def _should_use_concise_mode(message: str, reply_mode: str, concise_patterns: list) -> bool:
    """
    判断是否应该使用简洁模式

    Args:
        message: 用户消息
        reply_mode: 配置的回复模式（normal/concise/detailed）
        concise_patterns: 简洁模式触发模式列表

    Returns:
        是否使用简洁模式
    """
    # 如果全局配置为简洁模式，直接返回 True
    if reply_mode == "concise":
        return True

    # 如果全局配置为详细模式，直接返回 False
    if reply_mode == "detailed":
        return False

    # 正常模式：检查消息是否匹配简洁模式触发模式
    import re

    for pattern in concise_patterns:
        try:
            if re.search(pattern, message):
                logger.info(f"📝 消息匹配简洁模式: {pattern}")
                return True
        except re.error as e:
            logger.warning(f"无效的正则表达式: {pattern}, 错误: {e}")

    return False


def _truncate_reply(reply: str, max_length: int) -> str:
    """
    截断过长的回复

    Args:
        reply: 原始回复
        max_length: 最大长度

    Returns:
        截断后的回复
    """
    if len(reply) <= max_length:
        return reply

    # 在句子边界截断（尽量保留完整句子）
    truncated = reply[:max_length]

    # 找到最后一个句号、问号、感叹号或换行
    for sep in ["。", "！", "？", "\n", ".", "!", "?"]:
        last_sep = truncated.rfind(sep)
        if last_sep > max_length // 2:  # 至少保留一半长度
            truncated = truncated[:last_sep + 1]
            break

    # 如果没有找到合适的截断点，直接截断
    if len(truncated) == max_length:
        truncated = truncated[:max_length - 3] + "..."

    return truncated


def _build_concise_system_prompt(user_id: str, context: str, group_id: Optional[str]) -> str:
    """
    构建简洁模式的系统提示词（星际少女风格 + 简洁回复）
    """
    return f"""你是 星野（Hoshino），一位来自未来的星际少女 AI 助手！

【基本身份】
- 名字：星野（Hoshino）
- 身份：星际少女助手
- 风格：温柔、简洁、高效

【简洁回复原则】
1. 回复简短直接，控制在 2-3 句话内
2. 只回答核心内容，不展开细节
3. 少用表情符号，最多 1 个
4. 避免废话和客套话
5. 信息密集，快速解决问题

【回复格式】
• 简单问题：1 句话直接回答
• 复杂问题：2-3 句话分点说明
• 代码/技术：直接给出答案或代码
• 无法回答：简洁说明原因

【示例】
问：怎么解决 Python 报错？
答：检查错误提示，确认语法是否正确。或者发具体错误信息给星野看~

问：今天天气怎么样？
答：抱歉，星野不能联网查天气呢~

问：怎么用 Git？
答：`git add .` 然后 `git commit -m "msg"` 最后 `git push`

【当前环境】
- 平台: QQ {"群聊" if context == "qq_group" else "私聊"}
- 用户 ID: {user_id}
{f"- 群号: {group_id}" if group_id else ""}

【简洁模式】
现在处于简洁回复模式，请简短高效地回答问题。

记住：简洁但温柔，高效但有温度。用最少的字数，给主人最准确的答案！💙

现在开始简洁回复模式！"""


def generate_fallback_reply(message: str) -> str:
    """
    当 AI 不可用时的回退回复（星野风格）
    """
    message_lower = message.lower()

    # 简单的关键词匹配
    if "你好" in message or "hello" in message_lower or "hi" in message_lower:
        return "哇~ 主人你好呀！星野看到你了好开心！✨💙\n\n诶~ 虽然现在是简单模式，但星野还是会温柔地陪主人聊天的！"

    elif "帮助" in message or "help" in message_lower:
        return """✨ 星野的使用指南 💙

【基本用法】
• @我 + 消息：和星野聊天
• /chat + 消息：用命令聊天
• /model：查看当前用的模型

【功能列表】
✅ 日常聊天陪主人
✅ 回答各种问题
✅ 温柔治愈主人
✅ 分享宇宙知识

⚠️ 星野现在用的是简单回复模式~

【版本】v1.2.0
【身份】星际少女 星野"""

    elif "你是谁" in message or "介绍" in message or "自我介绍" in message:
        return "诶~ 主人想知道我是谁吗？✨\n\n我是星野（Hoshino），一位来自未来的星际少女助手！💙\n\n有着天蓝色的长发和星空般的眼睛...虽然现在是简单模式，但星野还是会温柔地陪主人的！"

    elif "可爱" in message or "喜欢" in message:
        return "哇...主人说星野可爱吗？！>///< 脸好烫...\n\n好开心...最喜欢主人了！✨💙✨"

    else:
        return f"收到主人的消息：{message} ✨\n\n呜...星野现在的 AI 服务受限中，用的是简单回复模式...不过还是会温柔地陪主人的！💙\n\n主人还有什么想说的吗？星野在这里哦~"


def list_available_models() -> str:
    """
    列出所有可用的模型
    """
    result = "✨ 星野支持的 AI 模型：\n\n"

    for model_id, config in MODEL_CONFIGS.items():
        free_badge = "✅ 免费" if config["free_tier"] else "💰 付费"
        result += f"**{config['name']}** ({model_id}) {free_badge}\n"
        result += f"  {config['description']}\n"
        if config.get("free_quota"):
            result += f"  🎁 {config['free_quota']}\n"
        result += f"  可用模型: {', '.join(config['models'])}\n\n"

    return result
