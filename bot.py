#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ Bot - OpenClaw
基于 NoneBot2 的 QQ 群聊机器人
支持对话记忆功能
"""

import nonebot
from nonebot.log import logger, default_format
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 初始化 NoneBot
nonebot.init(
    session_expire_timeout=120
)

# 注册适配器
driver = nonebot.get_driver()

# 导入 OneBot 适配器
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter
driver.register_adapter(OneBotV11Adapter)

# 导入自定义配置
from config import Config

# 加载配置
config = Config()
logger.info(f"机器人配置加载完成: {config.bot_name}")

# 加载插件（必须先加载插件，再导入插件模块）
nonebot.load_builtin_plugins("echo")
nonebot.load_from_toml("pyproject.toml")

# ========== 初始化对话记忆（插件加载后） ==========
if config.memory_enabled:
    try:
        from plugins.openclaw_chat.conversation_memory import init_memory_manager

        # 初始化记忆管理器
        init_memory_manager(
            memory_dir=config.memory_dir,
            short_term_length=config.memory_short_term_length,
            long_term_expire_days=config.memory_long_term_expire_days,
            auto_clean=config.memory_auto_clean
        )

        logger.info(f"✅ 对话记忆已启用: {config.memory_dir}")
        logger.info(f"   • 短期记忆长度: {config.memory_short_term_length}")
        logger.info(f"   • 长期记忆过期: {config.memory_long_term_expire_days} 天")
        logger.info(f"   • 自动清理: {'是' if config.memory_auto_clean else '否'}")
    except Exception as e:
        logger.error(f"❌ 对话记忆初始化失败: {e}")
else:
    logger.info("⚠️  对话记忆已禁用")

# 启动机器人
if __name__ == "__main__":
    logger.info("正在启动 QQ Bot - OpenClaw...")
    logger.info(f"监听地址: {config.host}:{config.port}")
    logger.info(f"超级管理员: {config.superusers}")
    logger.info(f"OpenClaw API: {config.openclaw_api_url}")

    nonebot.run()
