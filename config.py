#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
从环境变量加载配置
"""

import os
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Config(BaseModel):
    """机器人配置"""
    
    # OpenClaw API 配置
    openclaw_api_url: str = os.getenv("OPENCLAW_API_URL", "https://your-server.com/api/openclaw/chat")
    openclaw_api_key: str = os.getenv("OPENCLAW_API_KEY", "")
    openclaw_api_timeout: int = int(os.getenv("OPENCLAW_API_TIMEOUT", "30"))
    
    # 机器人配置
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8080"))
    superusers: List[str] = eval(os.getenv("SUPERUSERS", "[]"))
    nickname: List[str] = eval(os.getenv("NICKNAME", "[\"OpenClaw\"]"))
    
    # NapCat 配置
    napcat_ws_url: str = os.getenv("NAPCAT_WS_URL", "ws://127.0.0.1:3001")
    
    # 日志配置
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "")
    
    # 高级配置
    command_start: List[str] = eval(os.getenv("COMMAND_START", '["/", ""]'))
    command_sep: List[str] = eval(os.getenv("COMMAND_SEP", '[\".\"]'))
    session_expire_timeout: int = int(os.getenv("SESSION_EXPIRE_TIMEOUT", "120"))
    
    @property
    def bot_name(self) -> str:
        """机器人名称"""
        return self.nickname[0] if self.nickname else "OpenClaw"
    
    def validate_config(self) -> bool:
        """验证配置是否完整"""
        try:
            if not self.openclaw_api_url or "your-server.com" in self.openclaw_api_url:
                print("错误: 未配置 OPENCLAW_API_URL")
                return False
            
            if not self.openclaw_api_key or self.openclaw_api_key == "your_api_key_here":
                print("错误: 未配置 OPENCLAW_API_KEY")
                return False
            
            if not self.superusers:
                print("警告: 未配置超级管理员")
            
            return True
        except Exception as e:
            print(f"验证配置时出错: {e}")
            return False


# 创建全局配置实例
config = Config()

# 验证配置
if not config.validate_config():
    print("\n请检查 .env 配置文件！")
    print("参考 .env.example 进行配置")
    # 不退出程序，只打印警告信息
