#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ Bot - OpenClaw
基于 NoneBot2 的 QQ 群聊机器人
"""

import nonebot
from nonebot.log import logger, default_format
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 初始化 NoneBot
nonebot.init()

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

# 加载插件
nonebot.load_builtin_plugins("echo")
nonebot.load_from_toml("pyproject.toml")

# 启动机器人
if __name__ == "__main__":
    logger.info("正在启动 QQ Bot - OpenClaw...")
    logger.info(f"监听地址: {config.host}:{config.port}")
    logger.info(f"超级管理员: {config.superusers}")
    logger.info(f"OpenClaw API: {config.openclaw_api_url}")
    
    nonebot.run()
